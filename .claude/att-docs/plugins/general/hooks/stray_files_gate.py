#!/usr/bin/env python3
"""PreToolUse hook on Bash that keeps build artifacts and junk out of a commit.

usage: python3 stray_files_gate.py [--config <extension.json>] < hook-input.json

Three calls are refused, for the session that makes them and for any agent it delegates to,
since a hook runs for both:

  git add -A | --all | .      stages whatever the tree holds. Stage the files the change
                              meant to touch, by name.
  git add <junk path>         names a file that is an artifact or junk, such as
                              __pycache__/x.pyc, even with -f.
  git commit ...              while the index holds such a file. The files are listed, with
                              how to unstage them.

A path is junk when one of its folders, or the path itself, is named __pycache__,
node_modules, coverage, htmlcov, test-results, playwright-report, .nyc_output,
.pytest_cache, .mypy_cache, .ruff_cache or .idea, or its file name matches *.pyc, *.pyo,
.coverage, .coverage.*, .DS_Store, Thumbs.db, *.swp, *.swo, *~, *.log, *.tmp, *.temp,
*.orig or *.rej. Only a file the index adds, copies or renames counts: a file the repository
already tracks is kept on purpose, and a staged deletion of junk is fine.

The hook is on in every repository. The `strayFiles` section of the extension file is
optional: a missing file or section means every default, `false` turns the hook off, and
an object sets the keys below, all optional:

  patterns       more junk: a word ending in `/` names a folder, a word with a `/` in it is
                 matched against the whole path from the repository root, and any other
                 word is matched against the file name. Glob syntax, `*` matching a slash.
  allow          paths to let through although they match, with the same glob syntax,
                 matched against the whole path. A fixture that is a log on purpose goes
                 here.
  allowBulkAdd   true to let `git add -A` and `git add .` through. The junk checks stay.

The checks read the repository the call runs in: the hook's working directory, moved by a
`cd` earlier in the same command and by `git -C <dir>`. A hook runs before the command, so
`git add <folder>` is checked through git's own dry run of that add, which makes
`git add src && git commit` safe in one call. `git commit -a` also stages tracked files,
which this does not look at.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys

from pr_testing_gate import ASSIGNMENT, segments

TIMEOUT = 20
EXIT_USAGE = 64

# Cheap test on the raw command, so every other Bash call returns before any parsing.
MAYBE = re.compile(r'\bgit\b.*\b(add|commit)\b', re.S)
GIT_OPTIONS_WITH_VALUE = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path'}
BULK = {'-A', '--all', '.', './', ':/'}

DIR_NAMES = {
    '__pycache__', 'node_modules', 'coverage', 'htmlcov', 'test-results', 'playwright-report',
    '.nyc_output', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.idea',
}
FILE_GLOBS = [
    '*.pyc', '*.pyo', '.coverage', '.coverage.*', '.DS_Store', 'Thumbs.db', '*.swp', '*.swo',
    '*~', '*.log', '*.tmp', '*.temp', '*.orig', '*.rej',
]


def shell_segments(command):
    """`segments(command)`, or its parsable lines when the whole text does not parse, as
    with an apostrophe in a heredoc body."""
    try:
        yield from list(segments(command))
        return
    except ValueError:
        pass
    for line in command.split('\n'):
        try:
            yield from list(segments(line))
        except ValueError:
            continue


def git_calls(command):
    """Yields (subcommand, its arguments, directory or None) for each git call.

    The directory is the `-C` value joined onto where the command's own `cd` calls moved
    to, relative to the hook's working directory, or None when neither applies."""
    moved = None
    for seg, _ in shell_segments(command):
        words = list(seg)
        while words and ASSIGNMENT.match(words[0]):
            words.pop(0)
        if words and words[0] == 'cd' and len(words) <= 2:
            target = words[1] if len(words) == 2 else '~'
            moved = None if target == '-' else os.path.join(moved or '', target)
            continue
        if not words or os.path.basename(words[0]) != 'git':
            continue
        cwd = moved
        i = 1
        while i < len(words) and words[i].startswith('-'):
            if words[i] in GIT_OPTIONS_WITH_VALUE and i + 1 < len(words):
                if words[i] == '-C':
                    cwd = os.path.join(cwd or '', words[i + 1])
                i += 2
            else:
                i += 1
        if i < len(words):
            yield words[i], words[i + 1:], cwd


def is_junk(path, config):
    """The pattern that makes `path` junk, or None."""
    path = path.replace('\\', '/').removeprefix('./')
    if any(fnmatch.fnmatchcase(path, pattern) for pattern in config.get('allow', [])):
        return None
    parts = path.split('/')
    dirs = set(DIR_NAMES)
    globs = list(FILE_GLOBS)
    paths = []
    for pattern in config.get('patterns', []):
        if pattern.endswith('/'):
            dirs.add(pattern.rstrip('/'))
        elif '/' in pattern:
            paths.append(pattern)
        else:
            globs.append(pattern)
    for part in parts:
        if part in dirs:
            return part + '/'
    for pattern in paths:
        if fnmatch.fnmatchcase(path, pattern):
            return pattern
    for pattern in globs:
        if fnmatch.fnmatchcase(parts[-1], pattern):
            return pattern
    return None


def add_paths(args):
    """The path arguments of `git add`, whether it stages the whole tree, whether it forces
    in ignored files, and whether it only touches tracked files (`-u`, `-p`)."""
    paths = []
    flags = []
    only_paths = False
    for arg in args:
        if only_paths or not arg.startswith('-'):
            paths.append(arg)
        elif arg == '--':
            only_paths = True
        else:
            flags.append(arg)
    longs = {f for f in flags if f.startswith('--')}
    shorts = ''.join(f[1:] for f in flags if not f.startswith('--'))
    update = bool(longs & {'--update', '--patch'}) or 'u' in shorts or 'p' in shorts
    everything = '--all' in longs or 'A' in shorts
    bulk = everything or (not update and any(p in BULK for p in paths))
    force = '--force' in longs or 'f' in shorts
    return paths, bulk, force, update


def staged_paths(cwd):
    """Paths the index adds, copies or renames against HEAD, or None when git cannot say.
    A tracked file that is only modified stays out: the repository keeps it on purpose."""
    try:
        done = subprocess.run(['git', 'diff', '--cached', '--name-status', '-z'], cwd=cwd,
                              capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    fields = done.stdout.split('\0')
    paths = []
    i = 0
    while i + 1 < len(fields):
        status = fields[i]
        if status[:1] in ('R', 'C'):
            paths.append(fields[i + 2] if i + 2 < len(fields) else fields[i + 1])
            i += 3
        else:
            if status[:1] == 'A':
                paths.append(fields[i + 1])
            i += 2
    return paths


def would_add_paths(cwd, paths, force, update=False):
    """The files `git add <paths>` would stage, from its own dry run, or [] when git fails.
    The paths come back from the repository's top directory."""
    cmd = (['git', 'add', '--dry-run'] + (['--force'] if force else [])
           + (['--update'] if update else []) + ['--'] + paths)
    try:
        done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return []
    found = []
    for line in done.stdout.splitlines():
        match = re.match(r"^add '(.*)'$", line)
        if match:
            found.append(match.group(1))
    return found


def deny(reason):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                                   'permissionDecision': 'deny',
                                   'permissionDecisionReason': reason}}


UNSTAGE = ('Unstage it with `git restore --staged <path>` (`git rm --cached <path>` in a '
           'repository with no commit yet), add its pattern to .gitignore '
           'when the pattern is not ignored yet, say which file was left out and why, then '
           'stage the files the change meant to touch by name.')


def repo_layout(where):
    """The repository's top directory and `where` below it (with a trailing slash, or ''),
    or (where, '') when git cannot say."""
    try:
        done = subprocess.run(['git', 'rev-parse', '--show-toplevel', '--show-prefix'],
                              cwd=where, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return where, ''
    lines = done.stdout.split('\n')
    if done.returncode != 0 or len(lines) < 2:
        return where, ''
    return lines[0], lines[1]


def root_relative(path, top, prefix):
    """`path` as typed in a command run `prefix` below `top`, from `top`; None outside it.
    A pathspec with magic (`:(top)x`, `:/x`) is git's to resolve and comes back as typed."""
    if path.startswith(':'):
        return path
    if os.path.isabs(path):
        joined = os.path.relpath(path, top)
    else:
        joined = os.path.normpath(os.path.join(prefix, path))
    return None if joined == '..' or joined.startswith('../') else joined


def tracked(top, path):
    """True when `path`, from the top directory, is already in the index: a file the
    repository keeps on purpose."""
    try:
        done = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path], cwd=top,
                              capture_output=True, timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def in_pending_commit(where, path):
    """True when a merge, cherry-pick or revert in progress brings `path` in, so the
    session is finishing someone else's commit rather than adding the file."""
    for ref in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD'):
        try:
            kwargs = dict(cwd=where, capture_output=True, timeout=TIMEOUT)
            if subprocess.run(['git', 'rev-parse', '-q', '--verify', ref], **kwargs).returncode:
                continue
            if subprocess.run(['git', 'cat-file', '-e', f'{ref}:{path}'], **kwargs).returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def decide(payload, config, staged=staged_paths, would_add=would_add_paths):
    """The deny output for a call that stages or commits stray files, or None."""
    if payload.get('tool_name') != 'Bash':
        return None
    tool_input = payload.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not MAYBE.search(command):
        return None
    base = payload.get('cwd') or os.getcwd()
    for sub, args, directory in git_calls(command):
        where = base if directory is None else os.path.join(base, os.path.expanduser(directory))
        if sub == 'add':
            paths, bulk, force, update = add_paths(args)
            if bulk and not config.get('allowBulkAdd'):
                return deny('`git add -A`, `git add --all` and `git add .` stage whatever the '
                            'tree holds, build artifacts and junk included. Stage the files '
                            'the change meant to touch by name: `git add <path>...`.')
            # The paths the call names, and what a folder among them would add: a hook
            # runs before the command, so `git add src && git commit` has not staged yet.
            # Every path is checked from the repository's top directory, the form that
            # `allow`, patterns and the dry run use.
            top, prefix = repo_layout(where)
            named = [r for r in (root_relative(p, top, prefix) for p in paths) if r]
            found = would_add(where, paths, force, update) if paths else []
            for path in named + found:
                pattern = is_junk(path, config)
                if pattern and not tracked(top, path):
                    return deny(f'{path} matches the stray-file pattern {pattern}, a build '
                                'artifact or junk that does not belong in a commit. Leave it '
                                'out, and add the pattern to .gitignore when it is not '
                                'ignored yet.')
        elif sub == 'commit':
            stray = [(p, is_junk(p, config)) for p in staged(where) or []]
            stray = [(p, pat) for p, pat in stray if pat and not in_pending_commit(where, p)]
            if stray:
                listing = ', '.join(f'{p} ({pat})' for p, pat in stray)
                return deny(f'The index holds build artifacts or junk: {listing}. {UNSTAGE}')
    return None


def read_config(argv):
    """The strayFiles section of the file named by `--config <file>`, with every default
    when there is no flag, no such file, or no section; False when the section is false.
    Exits 64 for an unknown argument or a file that is not usable."""
    if argv[1:] == []:
        return {}
    if len(argv) != 3 or argv[1] != '--config':
        print('usage: stray_files_gate.py [--config <extension.json>]', file=sys.stderr)
        sys.exit(EXIT_USAGE)
    try:
        with open(argv[2], encoding='utf-8') as f:
            section = json.load(f).get('strayFiles', {})
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, AttributeError) as error:
        print(f'stray_files_gate.py: cannot read {argv[2]}: {error}', file=sys.stderr)
        sys.exit(EXIT_USAGE)
    if section is False:
        return False
    if section is True:
        return {}
    if not isinstance(section, dict):
        print('stray_files_gate.py: strayFiles must be an object, true or false', file=sys.stderr)
        sys.exit(EXIT_USAGE)
    for key in ('patterns', 'allow'):
        value = section.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            print(f'stray_files_gate.py: strayFiles.{key} must be a list of strings',
                  file=sys.stderr)
            sys.exit(EXIT_USAGE)
    return section


def main(argv):
    config = read_config(argv)
    if config is False:
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    result = decide(payload if isinstance(payload, dict) else {}, config)
    if result:
        print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
