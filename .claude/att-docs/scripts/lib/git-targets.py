"""Where each branch-mutating git command in a shell command acts.

guard-main-checkout.sh judges a shell command by the checkout its git commands
change, which is not always the directory the command starts in. A `cd` moves
every command after it, and `git -C <path>` moves its own. This file reads the
command as the shell would split it and prints one line per git invocation
whose verb changes the checked-out branch or the working tree, naming the
directory that invocation acts on. A fast-forward-only pull, in a checkout on
main that tracks origin's main, is left out so the main checkout can be kept
current:

    python3 scripts/lib/git-targets.py <cwd> <<<"$lines"

A directory the text cannot settle, such as `cd "$WT"` or `cd -`, is printed as
the starting directory, which is how the guard judged every command before it
read `cd` at all. A command shlex cannot split is read line by line for a bare
git verb, judged from the starting directory.
"""

import os
import re
import shlex
import subprocess
import sys

VERBS = {'checkout', 'switch', 'restore', 'stash', 'reset', 'merge', 'rebase', 'pull'}

SEPARATORS = {';', '&', '&&', '|', '||', '|&', ';;'}

# Words that run the command after them, so git still starts the command.
PREFIXES = {'command', 'env', 'exec', 'nohup', 'time', 'sudo'}

ASSIGNMENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')

# git's global options that take their value as the next word.
VALUE_OPTIONS = {'-c', '--namespace', '--exec-path', '--config-env'}


def settled(path):
    # A path the text alone can name, with no expansion left for the shell.
    return not any(c in path for c in '$`*?[')


def move(base, path):
    # The directory `path` names from `base`, or None when it cannot be told.
    if not settled(path):
        return None
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return os.path.realpath(path)
    if base is None:
        return None
    return os.path.realpath(os.path.join(base, path))


def git_target(words, here):
    # The verb of a git invocation and the directory it acts on.
    target = here
    i = 1
    while i < len(words):
        word = words[i]
        if word == '-C' and i + 1 < len(words):
            target = move(target, words[i + 1])
            i += 2
        elif word.startswith('-C') and len(word) > 2:
            target = move(target, word[2:])
            i += 1
        elif word in ('--work-tree', '--git-dir') and i + 1 < len(words):
            target = move(target, words[i + 1])
            i += 2
        elif word.startswith(('--work-tree=', '--git-dir=')):
            target = move(target, word.split('=', 1)[1])
            i += 1
        elif word in VALUE_OPTIONS:
            i += 2
        elif word.startswith('-'):
            i += 1
        else:
            return word, target, words[1:i], words[i + 1:]
    return None, target, words[1:], []


# The one pull the main checkout takes: a fast-forward of its own main from
# origin, with nothing that could merge, rebase, or name another branch.
FF_FLAGS = {'--ff-only', '-q', '--quiet', '-v', '--verbose', '--prune'}
FF_SOURCES = ([], ['origin'], ['origin', 'main'])

# A redirection such as `2>&1`, `&>out`, or `>` with its file in the next word.
REDIRECT = re.compile(r'^(\d*|&)(>>?|<)')
OPERATOR = re.compile(r'^\d*(>>?|<)$')

# Stands in for an `&` the lexer cannot read as a separator or a redirection.
AMBIGUOUS = object()

# A hook holds the command it judges, so a git that hangs is cut off.
GIT_TIMEOUT_SECONDS = 5

TRACKING = ['branch.main.merge refs/heads/main', 'branch.main.remote origin']


def git_lines(target, *args):
    # The output lines of a git command in `target`, or None when it fails.
    try:
        done = subprocess.run(['git', '-C', target, *args], capture_output=True,
                              text=True, timeout=GIT_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.splitlines() if done.returncode == 0 else None


def on_main(target):
    # Whether `target` has main checked out, tracking main, and only main, on
    # origin. A second branch.main.merge value would be merged as well.
    head = git_lines(target, 'symbolic-ref', '-q', '--short', 'HEAD')
    tracking = git_lines(target, 'config', '--get-regexp', r'^branch\.main\.(remote|merge)$')
    return head == ['main'] and tracking is not None and sorted(tracking) == TRACKING


def fast_forward(target, options, args):
    # Whether a pull only fast-forwards main from origin. A global option
    # other than -C, such as `-c branch.main.merge=...`, can point the pull at
    # another branch or remote, so it rules the pull out.
    if target is None:
        return False
    i = 0
    while i < len(options):
        if options[i] == '-C':
            i += 2
        elif options[i].startswith('-C'):
            i += 1
        else:
            return False
    flags = [arg for arg in args if arg.startswith('-')]
    rest = [arg for arg in args if not arg.startswith('-')]
    return ('--ff-only' in flags and set(flags) <= FF_FLAGS and rest in FF_SOURCES
            and on_main(target))


def unredirected(words):
    # The words of a command without its redirections. A bare operator such
    # as `>` or `2>` takes the next word as its file.
    kept = []
    i = 0
    while i < len(words):
        found = REDIRECT.match(words[i])
        if found:
            i += 2 if found.end() == len(words[i]) else 1
        else:
            kept.append(words[i])
            i += 1
    return kept


def redirections(tokens):
    # The shell reads `2>&1`, `>&2`, and `>|out` as one redirection, but the
    # lexer splits each at its `&` or `|`, which would end the command there
    # and start the words after it as a command of their own. An `&` before
    # `>out` reads as `&>out` or as `& >out`, and the lexer cannot tell which,
    # so it ends the command and rules a pull before it out of the exemption.
    merged = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        following = tokens[i + 1] if i + 1 < len(tokens) else None
        joined = merged and isinstance(merged[-1], str) and OPERATOR.match(merged[-1])
        if token in ('&', '|') and following and joined:
            merged[-1] += token + following
            i += 2
        elif token == '&' and following and following.startswith('>'):
            merged.append(AMBIGUOUS)
            i += 1
        else:
            merged.append(token)
            i += 1
    return merged


def targets(text, cwd):
    # A newline ends a command, and a comment ends at the newline. A
    # backslash before the newline joins the two lines into one command.
    text = text.replace('\\\n', ' ').replace('\n', '\n;')
    lexer = shlex.shlex(text, posix=True, punctuation_chars=';&|()')
    lexer.whitespace_split = True
    tokens = redirections(list(lexer))

    found = []
    here = cwd
    outer = []
    words = []
    # Only a `cd` may come before an exempt pull. Any other command, such as
    # `git config`, `git remote set-url`, or `export GIT_DIR=...`, can point
    # the pull somewhere the checks below never see.
    first = True

    def command(words, exempt=True):
        nonlocal here, first
        words = unredirected(words)
        runner = False
        # An assignment or a runner before git, such as GIT_CONFIG_* or
        # `env GIT_WORK_TREE=...`, can point a pull anywhere.
        prefixed = bool(words) and (ASSIGNMENT.match(words[0]) or words[0] in PREFIXES)
        exempt = exempt and first and not prefixed
        if words and words[0] != 'cd':
            first = False
        while words and (ASSIGNMENT.match(words[0]) or words[0] in PREFIXES):
            runner = runner or words[0] in PREFIXES
            words = words[1:]
        # A runner's own options, such as `env -i` or `sudo -u me`, sit
        # between it and git, so the command starts at the first git word.
        if runner and words and words[0].startswith('-'):
            words = next((words[i:] for i, word in enumerate(words)
                          if word == 'git' or word.endswith('/git')), [])
        if not words:
            return
        name = words[0]
        if name == 'cd':
            arg = words[1] if len(words) > 1 else '~'
            here = None if arg == '-' else move(here, arg)
        elif name == 'git' or name.endswith('/git'):
            verb, target, options, args = git_target(words, here)
            if verb == 'pull' and exempt and fast_forward(target, options, args):
                return
            if verb in VERBS:
                found.append(target)

    for token in tokens:
        if token == AMBIGUOUS:
            command(words, exempt=False)
            words = []
        elif token in SEPARATORS:
            command(words)
            words = []
        elif token == '(':
            command(words)
            words = []
            outer.append(here)
        elif token == ')':
            command(words)
            words = []
            if outer:
                here = outer.pop()
        else:
            words.append(token)
    command(words)
    return found


def bare_verbs(text):
    # The reading the guard falls back on when the command will not split.
    verbs = '|'.join(sorted(VERBS))
    pattern = re.compile(r'(^|[;&|] *)git +(-c +\S+ +)*(' + verbs + r')( |$)')
    return any(pattern.search(line) for line in text.splitlines())


def main():
    cwd = os.path.realpath(sys.argv[1])
    text = sys.stdin.read()
    try:
        found = targets(text, cwd)
    except ValueError:
        found = [cwd] if bare_verbs(text) else []
    for target in found:
        print(target if target is not None else cwd)


if __name__ == '__main__':
    main()
