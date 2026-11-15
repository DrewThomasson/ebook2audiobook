#!/usr/bin/env python3
"""File claims for sessions that work one repository at the same time.

usage: python3 claims.py <command> ... [--session ID] [--pid N]
       (--session and --pid may also come before the command)

  check <path>...                read only: is a path claimed by another live session, or
                                 changed by another open pull request? A folder matches
                                 every file under it.
  claim <path>... [--branch B] [--issue N]
                                 check, then record this session's claim on each file. All
                                 or nothing: a refused path leaves nothing recorded.
  release [path...] [--force]    drop this session's claims, or only those on the paths.
                                 --force drops a claim another session holds.
  prune                          drop claims that are stale
  list                           print every claim
  sync [base]                    fetch origin/<base> and print the files both it and this
                                 branch changed since they diverged. The base defaults to
                                 the branch origin's HEAD names, or main when it names none.

Exit codes: 0 nothing in the way, 3 a conflict was printed, 2 bad usage or no session id,
1 a git or gh call failed. A failed read is never reported as "no conflict".

Output, one line per conflict:

  CLAIM <session> <branch> <path> [issue=<N>]
                                     another live session holds the file; the issue is the
                                     one that session named when it claimed
  PR #<n> <branch> <path>            another open pull request changes the file
  SYNC <path>                        origin/<base> and this branch both changed the file

A claim is one file in <git-common-dir>/file-claims/, so every worktree of a repository
sees the same claims and nothing is added to the working tree. The file name is a hash of
the path and the record is {path, session, pid, branch, issue, ts}. Every change to the
folder happens under one exclusive lock, so two sessions racing for a file, or for the
takeover of a stale claim, have one winner. A claim holds while its process runs; a claim
whose pid has exited is stale and is dropped by the next claim or prune. A claim with no pid
holds for NO_PID_TTL seconds from when it was made.

The session is --session, else CLAUDE_CODE_SESSION_ID, else PI_SESSION_ID. The pid is --pid,
else CLAUDE_PID.
Without a session, check treats every live claim as another session's, and claim and
release refuse to run.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_CONFLICT = 3

# gh pr list returns at most this many files per pull request.
GH_FILE_LIMIT = 100
PR_LIMIT = 200
TIMEOUT = 60
# A claim is meant to last from the first edit of a file to the pull request opening. One
# with no process to watch is dropped after this long.
NO_PID_TTL = 12 * 60 * 60
LOCK_NAME = '.lock'


class Failed(Exception):
    """A git or gh call did not work, so no answer can be trusted."""


class Usage(Exception):
    pass


def run(args):
    try:
        done = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Failed(f'{" ".join(args[:3])}: {e}')
    if done.returncode != 0:
        detail = (done.stderr or done.stdout).strip().splitlines()
        raise Failed(f'{" ".join(args[:3])} failed: {detail[-1] if detail else done.returncode}')
    return done.stdout


def git(*args):
    return run(['git', *args])


def claims_dir():
    common = git('rev-parse', '--path-format=absolute', '--git-common-dir').strip()
    return os.path.join(common, 'file-claims')


def current_branch():
    return git('branch', '--show-current').strip()


def repo_path(raw):
    """The repository-relative, slash-separated form of a path given from the current folder."""
    top = os.path.realpath(git('rev-parse', '--show-toplevel').strip())
    full = os.path.realpath(raw)
    rel = os.path.relpath(full, top)
    if rel == '.' or rel == '..' or rel.startswith('..' + os.sep):
        raise Usage(f'{raw} is not inside the repository')
    return rel.replace(os.sep, '/')


def overlaps(a, b):
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except (PermissionError, ValueError, OverflowError):
        return True
    return True


def held(data):
    """True while a claim holds. A record that cannot be read holds, since its holder is
    unknown."""
    if not data:
        return True
    pid = data.get('pid')
    if pid not in (None, ''):
        return pid_alive(pid)
    made = data.get('ts')
    return not isinstance(made, (int, float)) or time.time() - made < NO_PID_TTL


def record_path(directory, path):
    return os.path.join(directory, hashlib.sha1(path.encode()).hexdigest() + '.json')


def read_record(file):
    """The claim in a file, None when it is gone, or {} when it cannot be read."""
    try:
        with open(file) as f:
            data = json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def all_claims(directory):
    try:
        names = sorted(os.listdir(directory))
    except FileNotFoundError:
        return []
    found = []
    for name in names:
        if not name.endswith('.json'):
            continue
        file = os.path.join(directory, name)
        data = read_record(file)
        if data is not None:
            found.append((file, data))
    return found


def unlink_quiet(file):
    try:
        os.unlink(file)
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def locked(directory):
    """Hold the folder's exclusive lock, so reading a claim and changing it is one step."""
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, LOCK_NAME), 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def drop_stale(directory):
    dropped = []
    for file, data in all_claims(directory):
        if not held(data):
            unlink_quiet(file)
            dropped.append(data.get('path', file))
    return dropped


def claim_line(data, path):
    line = f"CLAIM {data.get('session') or '?'} {data.get('branch') or '-'} {path}"
    return f"{line} issue={data['issue']}" if data.get('issue') else line


def claim_conflicts(directory, paths, session):
    """Lines for every live claim by another session that overlaps one of the paths."""
    lines = []
    for _, data in all_claims(directory):
        if not held(data) or (data and session and data.get('session') == session):
            continue
        claimed = data.get('path', '')
        for path in paths:
            if not claimed or overlaps(path, claimed):
                lines.append(claim_line(data, claimed or path))
                break
    return lines


def pull_requests():
    out = run(['gh', 'pr', 'list', '--state', 'open', '--limit', str(PR_LIMIT),
               '--json', 'number,headRefName,files'])
    try:
        prs = json.loads(out)
    except ValueError as e:
        raise Failed(f'gh pr list returned text that is not JSON: {e}')
    for pr in prs:
        names = [f['path'] for f in pr.get('files') or []]
        if len(names) >= GH_FILE_LIMIT:
            names = run(['gh', 'api', '--paginate',
                         f"repos/{{owner}}/{{repo}}/pulls/{pr['number']}/files",
                         '--jq', '.[].filename']).splitlines()
        pr['paths'] = names
    return prs


def pr_conflicts(paths, branch):
    lines = []
    for pr in pull_requests():
        if branch and pr.get('headRefName') == branch:
            continue
        for path in paths:
            hit = next((n for n in pr['paths'] if overlaps(path, n)), None)
            if hit:
                lines.append(f"PR #{pr['number']} {pr.get('headRefName') or '-'} {hit}")
    return lines


def find_conflicts(directory, paths, session, branch):
    return claim_conflicts(directory, paths, session) + pr_conflicts(paths, branch)


def write_record(directory, path, session, pid, branch, issue):
    """Record the claim, replacing this session's own or a stale one. False when another
    session still holds the file. Call it with the folder's lock held."""
    target = record_path(directory, path)
    current = read_record(target)
    if current is not None and current.get('session') != session and held(current):
        return False
    data = {'path': path, 'session': session, 'pid': pid, 'branch': branch, 'issue': issue,
            'ts': int(time.time())}
    fd, tmp = tempfile.mkstemp(dir=directory, prefix='.new-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        os.replace(tmp, target)
    finally:
        unlink_quiet(tmp)
    return True


def need_session(args):
    if not args.session:
        raise Usage('no session id: pass --session or set CLAUDE_CODE_SESSION_ID')


def cmd_check(args):
    directory = claims_dir()
    paths = [repo_path(p) for p in args.paths]
    lines = find_conflicts(directory, paths, args.session, args.branch or current_branch())
    return report(lines)


def cmd_claim(args):
    need_session(args)
    directory = claims_dir()
    paths = [repo_path(p) for p in args.paths]
    for raw in args.paths:
        if os.path.isdir(raw):
            raise Usage(f'{raw} is a folder: claim the files in it')
    branch = args.branch or current_branch()
    # Another pull request is read before the lock, which a slow gh call would hold up.
    lines = pr_conflicts(paths, branch)
    if lines:
        return report(claim_conflicts(directory, paths, args.session) + lines)
    with locked(directory):
        drop_stale(directory)
        lines = claim_conflicts(directory, paths, args.session)
        if lines:
            return report(lines)
        before = {p: read_record(record_path(directory, p)) for p in paths}
        made = []
        for path in paths:
            if write_record(directory, path, args.session, args.pid, branch, args.issue):
                made.append(path)
                continue
            for done in made:
                if before[done] is None:
                    unlink_quiet(record_path(directory, done))
                else:
                    restore(directory, done, before[done])
            return report([claim_line(read_record(record_path(directory, path)) or {}, path)])
    for path in made:
        print(f'claimed {path}')
    return EXIT_OK


def restore(directory, path, data):
    """Put back the record a refused batch had replaced."""
    fd, tmp = tempfile.mkstemp(dir=directory, prefix='.new-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        os.replace(tmp, record_path(directory, path))
    finally:
        unlink_quiet(tmp)


def cmd_release(args):
    need_session(args)
    if args.force and not args.paths:
        raise Usage('--force needs the paths to release')
    directory = claims_dir()
    wanted = {repo_path(p) for p in args.paths}
    with locked(directory):
        for file, data in all_claims(directory):
            claimed = data.get('path')
            if wanted and claimed not in wanted:
                continue
            if not args.force and data.get('session') != args.session:
                continue
            unlink_quiet(file)
            print(f'released {claimed or file}')
    return EXIT_OK


def cmd_prune(args):
    directory = claims_dir()
    with locked(directory):
        for path in drop_stale(directory):
            print(f'pruned {path}')
    return EXIT_OK


def cmd_list(args):
    for _, data in all_claims(claims_dir()):
        state = 'live' if held(data) else 'stale'
        print(f"{state} {data.get('session') or '?'} {data.get('branch') or '-'} "
              f"{data.get('path') or '?'}")
    return EXIT_OK


def default_base():
    """The branch origin's HEAD names, or main when the clone recorded none."""
    try:
        ref = git('symbolic-ref', '--short', 'refs/remotes/origin/HEAD').strip()
    except Failed:
        return 'main'
    return ref.split('/', 1)[1] if ref.startswith('origin/') else 'main'


def cmd_sync(args):
    base = args.base or default_base()
    git('fetch', 'origin', base)
    remote = f'origin/{base}'
    fork = git('merge-base', 'HEAD', remote).strip()
    theirs = set(git('diff', '--name-only', fork, remote).split('\n')) - {''}
    ours = set(git('diff', '--name-only', fork).split('\n')) - {''}
    # --full-name keeps these relative to the repository root like the diffs above, whatever
    # folder the command runs in.
    ours |= set(git('ls-files', '--others', '--exclude-standard', '--full-name',
                    '--', ':/').split('\n')) - {''}
    return report([f'SYNC {path}' for path in sorted(theirs & ours)])


def report(lines):
    for line in lines:
        print(line)
    return EXIT_CONFLICT if lines else EXIT_OK


def first_env(*names):
    return next((os.environ[n] for n in names if os.environ.get(n)), None)


def parser():
    # The subcommands repeat the two flags with no default, so a flag after the command wins
    # and an absent one leaves the value the top level parsed.
    flags = argparse.ArgumentParser(add_help=False)
    flags.add_argument('--session', default=argparse.SUPPRESS)
    flags.add_argument('--pid', default=argparse.SUPPRESS)

    top = argparse.ArgumentParser(description='File claims for concurrent sessions.')
    top.add_argument('--session', default=first_env('CLAUDE_CODE_SESSION_ID', 'PI_SESSION_ID'))
    top.add_argument('--pid', default=first_env('CLAUDE_PID'))
    sub = top.add_subparsers(dest='command', required=True)

    p = sub.add_parser('check', parents=[flags])
    p.add_argument('paths', nargs='+')
    p.add_argument('--branch')
    p.set_defaults(run=cmd_check)

    p = sub.add_parser('claim', parents=[flags])
    p.add_argument('paths', nargs='+')
    p.add_argument('--branch')
    p.add_argument('--issue')
    p.set_defaults(run=cmd_claim)

    p = sub.add_parser('release', parents=[flags])
    p.add_argument('paths', nargs='*')
    p.add_argument('--force', action='store_true')
    p.set_defaults(run=cmd_release)

    sub.add_parser('prune', parents=[flags]).set_defaults(run=cmd_prune)
    sub.add_parser('list', parents=[flags]).set_defaults(run=cmd_list)

    p = sub.add_parser('sync', parents=[flags])
    p.add_argument('base', nargs='?')
    p.set_defaults(run=cmd_sync)
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except Usage as e:
        print(f'claims.py: {e}', file=sys.stderr)
        return EXIT_USAGE
    except Failed as e:
        print(f'claims.py: {e}', file=sys.stderr)
        return EXIT_FAILED


if __name__ == '__main__':
    sys.exit(main())
