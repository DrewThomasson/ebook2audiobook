#!/usr/bin/env python3
"""Manage per-session oversee loop markers in the shared checkout."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone

SESSION = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}\Z')


def valid_session(value):
    return isinstance(value, str) and SESSION.fullmatch(value) is not None


def state_dir(cwd):
    result = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            cwd=cwd, capture_output=True, text=True, check=True)
    return Path(result.stdout.strip()).parent / '.claude' / 'oversee'


@contextmanager
def locked(directory, timeout=None):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'loops.lock').open('a') as lock:
        if timeout is None:
            fcntl.flock(lock, fcntl.LOCK_EX)
        else:
            deadline = time.monotonic() + timeout
            while True:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('loop marker lock is busy')
                    time.sleep(0.05)
        yield


def marker_path(directory, session):
    if not valid_session(session):
        raise ValueError('a valid session ID is required (pass --session)')
    return directory / 'loops' / (session + '.json')


def load(directory, session):
    path = marker_path(directory, session)
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) and value.get('session') == session else None
    except (FileNotFoundError, json.JSONDecodeError, UnicodeError):
        return None


def save(directory, marker):
    path = marker_path(directory, marker['session'])
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.loop-')
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump(marker, out, ensure_ascii=False)
            out.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', default=os.environ.get('CLAUDE_CODE_SESSION_ID'))
    commands = parser.add_subparsers(dest='command', required=True)
    start = commands.add_parser('start')
    start.add_argument('--milestone')
    start.add_argument('label', nargs='?')
    stop = commands.add_parser('stop')
    stop.add_argument('reason')
    pause = commands.add_parser('pause')
    pause.add_argument('reason')
    commands.add_parser('resume')
    status = commands.add_parser('status')
    status.add_argument('--all', action='store_true')
    args = parser.parse_args()
    if not valid_session(args.session):
        parser.error('a valid session ID is required (pass --session)')
    try:
        directory = state_dir(Path.cwd())
        with locked(directory):
            marker = load(directory, args.session)
            if args.command == 'status' and args.all:
                paths = sorted((directory / 'loops').glob('*.json'))
                markers = [load(directory, path.stem) for path in paths if valid_session(path.stem)]
                print(json.dumps([item for item in markers if item is not None], ensure_ascii=False))
                return 0
            if args.command == 'start':
                if marker and marker.get('state') in ('active', 'paused'):
                    raise ValueError('this session already has an active or paused loop')
                marker = dict(session=args.session, state='active', started=now(),
                              label=args.label, milestone=args.milestone, reason='')
            elif args.command == 'status':
                print(json.dumps(marker or {'session': args.session, 'state': 'absent'}, ensure_ascii=False))
                return 0
            elif not marker:
                raise ValueError('this session has no loop')
            elif args.command == 'stop':
                if not args.reason.strip():
                    raise ValueError('stop requires a reason')
                marker.update(state='stopped', reason=args.reason)
            elif args.command == 'pause':
                if not args.reason.strip():
                    raise ValueError('pause requires a reason')
                if marker.get('state') != 'active':
                    raise ValueError('only an active loop can be paused')
                marker.update(state='paused', reason=args.reason)
            elif args.command == 'resume':
                if marker.get('state') != 'paused':
                    raise ValueError('only a paused loop can be resumed; start a new loop otherwise')
                marker.update(state='active', reason='', continuations=0)
                marker.pop('ledger_progress', None)
            save(directory, marker)
            print(json.dumps(marker, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'loop.py: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
