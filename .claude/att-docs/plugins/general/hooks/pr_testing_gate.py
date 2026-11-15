#!/usr/bin/env python3
"""PreToolUse hook on Bash that refuses a pull request body whose Testing section a checker cannot parse.

usage: python3 pr_testing_gate.py --config <extension.json> < hook-input.json

Matches the Bash calls that create or patch a pull request body from a file:

  gh pr create ... --body-file <path>     (also -F <path>, --body-file=<path>)
  gh pr edit ... --body-file <path>
  gh api [-X PATCH] repos/{owner}/{repo}/pulls[/<N>] -F body=@<path>

and runs the repository's own checker on that file. The checker is the `prTestingGate`
section of the extension file:

  checker        the checker as a command: a list of words, run from the repository root
                 with the body file's path added as the last word. It exits 0 when the
                 body is fine, 1 when the Testing section is malformed, anything else
                 when it could not read the file
  checkerLabel   the command to name in a denial, with <file> where the path goes;
                 defaults to the checker's words followed by the path
  failureMarker  text the checker prints when it rejects a body; when set, an exit 1
                 without it counts as a checker that could not run

A malformed Testing section (exit 1) or an unreadable file (any other nonzero exit) denies
the call with the checker's output as the reason, so the session fixes the body and
retries. A valid body, or one with no Testing section, goes through.

A body passed inline (`--body "..."`, `-f body=...`) cannot be checked from a file. It
goes through unless it carries a `## Testing` section, which is denied with a pointer at
`--body-file`. A body read from stdin (`--body-file -`) is not checked.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TIMEOUT = 60
EXIT_USAGE = 64

# Cheap test on the raw command, so every other Bash call returns before any parsing.
MAYBE = re.compile(r'\bgh\s+(pr\s+(create|edit)|api)\b')
# Every token made only of these ends a simple command: `;`, `&&`, `|`, a newline, a
# subshell parenthesis, and runs of them such as `)\n`.
SEPARATOR_CHARS = set(';&|()\n')
ASSIGNMENT = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', re.S)
VARIABLE = re.compile(r'\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))')
PULLS = re.compile(r'^/?repos/[^/]+/[^/]+/pulls(/[^/]+)?$')
TESTING = re.compile(r'^##[ \t]+Testing[ \t]*$', re.M)


def segments(command):
    """Splits a shell command into (simple command, separator after it) pairs.

    The separator is the run of `;&|()` and newline characters that ends the command, or
    '' at the end. The words list may be empty, as before a `(`.
    """
    lexer = shlex.shlex(command, posix=True, punctuation_chars='();<>|&\n')
    lexer.whitespace_split = True
    # A newline separates commands rather than words, and `#` is left in the words: a
    # comment read by shlex would swallow the newline that ends it.
    lexer.whitespace = ' \t\r'
    lexer.commenters = ''
    seg = []
    for token in lexer:
        # An empty quoted argument ('') is a word, not a separator.
        if token and set(token) <= SEPARATOR_CHARS:
            yield seg, token
            seg = []
        else:
            seg.append(token)
    yield seg, ''


def flag_values(args, longs, shorts):
    """Yields each value given to one of the flags, in any of the forms gh accepts."""
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in longs or arg in shorts:
            if i + 1 < len(args):
                yield args[i + 1]
            i += 2
            continue
        for name in longs:
            if arg.startswith(name + '='):
                yield arg[len(name) + 1:]
        for name in shorts:
            if arg.startswith(name) and len(arg) > len(name):
                yield arg[len(name):].removeprefix('=')
        i += 1


def pr_bodies(args):
    """Body sources of `gh pr create` or `gh pr edit`, given the arguments after it."""
    for path in flag_values(args, ('--body-file',), ('-F',)):
        yield ('file', path)
    for text in flag_values(args, ('--body',), ('-b',)):
        yield ('inline', text)


def api_bodies(args):
    """Body sources of `gh api` when it writes a pull request."""
    positional = [a for a in args if not a.startswith('-')]
    if not any(PULLS.match(a) for a in positional):
        return
    for field in flag_values(args, ('--field',), ('-F',)):
        if field.startswith('body=@'):
            yield ('file', field[len('body=@'):])
        elif field.startswith('body='):
            yield ('inline', field[len('body='):])
    for field in flag_values(args, ('--raw-field',), ('-f',)):
        if field.startswith('body='):
            yield ('inline', field[len('body='):])


def expand(word, env):
    """Expands `~` and `$NAME` in a path, preferring values the command itself set."""
    def value(match):
        name = match.group(1) or match.group(2)
        return env.get(name, os.environ.get(name, match.group(0)))
    return os.path.expanduser(VARIABLE.sub(value, word))


def change_dir(cd, args, env):
    """The directory after `cd <args>`, relative to the hook's cwd, or None if unknown."""
    if len(args) > 1 or args == ['-']:
        return None
    target = expand(args[0] if args else '~', env)
    if os.path.isabs(target):
        return target
    return None if cd is None else os.path.join(cd, target)


def body_sources(command):
    """Every ('file', path) or ('inline', text) body the command passes to a PR.

    A relative path is joined onto the directory an earlier `cd` in the command moved to,
    and variables the command assigned earlier are expanded in it. After a `cd` whose
    target cannot be known (`cd -`), a relative path is left unchecked.
    """
    if not MAYBE.search(command):
        return []
    try:
        segs = list(segments(command))
    except ValueError:
        # Unbalanced quoting, usually a heredoc: nothing here can be read reliably.
        return []
    found = []
    env = {}
    cd = ''
    # A subshell's `cd` and assignments end with it: `(` saves them and `)` restores them.
    saved = []
    for seg, separator in segs:
        words = command_words(seg, env)
        if words[:1] == ['cd']:
            cd = change_dir(cd, [w for w in words[1:] if w != '--'], env)
        else:
            found.extend(gh_bodies(words, env, cd))
        for char in separator:
            if char == '(':
                saved.append((cd, dict(env)))
            elif char == ')' and saved:
                cd, env = saved.pop()
    return found


def command_words(seg, env):
    """A simple command's words after `export` and `NAME=value` prefixes, kept in env."""
    if seg[:1] == ['export']:
        seg = seg[1:]
    while seg and ASSIGNMENT.match(seg[0]):
        name, value = ASSIGNMENT.match(seg[0]).groups()
        env[name] = expand(value, env)
        seg = seg[1:]
    return seg


def gh_bodies(words, env, cd):
    """Body sources of one `gh` command, with file paths expanded and joined onto cd."""
    if len(words) < 2 or words[0] != 'gh':
        return []
    if words[1] == 'pr' and len(words) > 2 and words[2] in ('create', 'edit'):
        sources = pr_bodies(words[3:])
    elif words[1] == 'api':
        sources = api_bodies(words[2:])
    else:
        return []
    found = []
    for kind, value in sources:
        if kind == 'file' and value != '-':
            value = expand(value, env)
            if not os.path.isabs(value):
                if cd is None:
                    continue
                value = os.path.join(cd, value)
        found.append((kind, value))
    return found


def resolve(path, cwd):
    return path if os.path.isabs(path) else os.path.join(cwd or os.getcwd(), path)


def checker_command(config):
    """The checker's words from the config, or None when it names none."""
    words = config.get('checker')
    if isinstance(words, list) and words and all(isinstance(w, str) for w in words):
        return words
    return None


def run_checker(path, config):
    """Runs the checker on a body file. Returns (exit code, its combined output)."""
    words = checker_command(config)
    try:
        done = subprocess.run(words + [path], cwd=os.getcwd(), capture_output=True,
                              text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as err:
        return 2, f'Could not run {words[0]}: {err}'
    return done.returncode, (done.stdout + done.stderr).strip()


def checker_label(config, path):
    label = config.get('checkerLabel')
    if isinstance(label, str) and label:
        return label.replace('<file>', path)
    return ' '.join(checker_command(config) + [path])


def deny(reason):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                                   'permissionDecision': 'deny',
                                   'permissionDecisionReason': reason}}


def decide(payload, config, run=run_checker):
    """The hook's output for one payload, or None to let the call through."""
    if payload.get('tool_name') != 'Bash' or checker_command(config) is None:
        return None
    command = (payload.get('tool_input') or {}).get('command', '')
    for kind, value in body_sources(command):
        if kind == 'inline':
            if TESTING.search(value):
                return deny('This pull request body has a `## Testing` section passed '
                            'inline, which the Testing check cannot read. Write the body '
                            'to a file and pass it with `--body-file <path>` (or '
                            '`-F body=@<path>` for `gh api`).')
            continue
        if value == '-':
            continue
        code, output = run(resolve(value, payload.get('cwd')), config)
        label = checker_label(config, value)
        marker = config.get('failureMarker')
        if code == 1 and (not marker or marker in output):
            return deny(f'The pull request body in {value} failed the Testing check '
                        f'(`{label}`):\n{output}'
                        '\nFix the body and run the command again.')
        if code != 0:
            return deny(f'The pull request body in {value} could not be checked '
                        f'(`{label}` exited {code}):\n{output}'
                        '\nFix the path or the checker (a missing dependency usually '
                        'means installing the repository\'s packages), then run the '
                        'command again.')
    return None


def read_config(argv):
    """The prTestingGate section of the file named by `--config <file>`, or exit 64."""
    if len(argv) < 3 or argv[1] != '--config':
        print('pr_testing_gate.py: --config <extension.json> is required', file=sys.stderr)
        sys.exit(EXIT_USAGE)
    try:
        with open(argv[2], encoding='utf-8') as f:
            section = json.load(f).get('prTestingGate')
    except (OSError, ValueError, AttributeError) as err:
        print(f'pr_testing_gate.py: cannot read {argv[2]}: {err}', file=sys.stderr)
        sys.exit(EXIT_USAGE)
    return section if isinstance(section, dict) else {}


def main(argv):
    config = read_config(argv)
    result = decide(json.load(sys.stdin), config)
    if result:
        print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
