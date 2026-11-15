#!/usr/bin/env python3
"""Resume an explicitly started oversee loop at session and turn boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

HELPER_DIR = Path(__file__).resolve().parent.parent / 'skills' / 'oversee-development'
sys.dont_write_bytecode = True
sys.path.insert(0, str(HELPER_DIR))
import loop  # noqa: E402

HELPER = HELPER_DIR / 'loop.py'
OVERSEE = HELPER_DIR / 'oversee.sh'
MAX_CONTINUATIONS = 8


def ledger_progress(directory, session):
    owners = {}
    relevant = []
    try:
        with (directory / 'ledger.tsv').open(encoding='utf-8') as source:
            for line in source:
                fields = line.rstrip('\n').split('\t')
                if len(fields) < 6:
                    continue
                issue, status, note = fields[1], fields[2], fields[5]
                if status == 'start':
                    owner = re.search(r'(?:^| )session ([^ ]+)', note)
                    owners[issue] = owner.group(1) if owner else None
                if (owners.get(issue) == session
                        and not (status == 'skipped' and note.startswith('not workable at start:'))):
                    relevant.append(line)
    except FileNotFoundError:
        pass
    return hashlib.sha256(''.join(relevant).encode()).hexdigest()


def instruction(session, marker):
    command = f'python3 {shlex.quote(str(HELPER))} --session {shlex.quote(session)}'
    scope = json.dumps({'label': marker.get('label'), 'milestone': marker.get('milestone')},
                       ensure_ascii=False)
    return (f'An active loop belongs to this session (scope {scope}). Resume the '
            f'oversee-development procedure; run bash {shlex.quote(str(OVERSEE))} status '
            f'and next with CLAUDE_CODE_SESSION_ID={shlex.quote(session)}, and recover any '
            'in-flight issue before selecting another. '
            f'When deliberately stopping, run {command} stop "reason" first. '
            f'For any user-requested pause, run {command} pause "reason" first; '
            'resume only when the user is ready.')


def decide(payload):
    event = payload.get('hook_event_name')
    session = payload.get('session_id')
    if payload.get('agent_id') or not loop.valid_session(session):
        return None
    if event == 'SessionStart':
        command = f'python3 {shlex.quote(str(HELPER))} --session {shlex.quote(session)}'
        context = f'This session ID is {session}; for oversee loop commands use `{command}`.'
        directory = None
        try:
            directory = loop.state_dir(payload.get('cwd') or Path.cwd())
            if (directory / 'loops').is_dir():
                with loop.locked(directory, timeout=2):
                    marker = loop.load(directory, session)
                    if marker and marker.get('state') == 'active':
                        context += ' ' + instruction(session, marker)
                    elif marker and marker.get('state') == 'paused':
                        context += f' The loop is paused; use `{command} resume` only when ready.'
                    elif any(
                        other and other.get('state') in ('active', 'paused')
                        for path in (directory / 'loops').glob('*.json')
                        if path.stem != session and loop.valid_session(path.stem)
                        for other in [loop.load(directory, path.stem)]
                    ):
                        context += (f' Other sessions have active or paused loops; use '
                                    f'`{command} status --all` to inspect their markers. '
                                    'Loop markers belong to their original sessions.')
        except TimeoutError:
            context += (f' Loop marker is busy; inspect `{command} status` before '
                        'continuing loop work.')
        except (OSError, ValueError, subprocess.SubprocessError):
            if directory is None:
                return None
            context += (f' Loop marker could not be read; inspect `{command} status` '
                        'before continuing loop work.')
        return {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': context}}
    if event != 'Stop':
        return None
    try:
        directory = loop.state_dir(payload.get('cwd') or Path.cwd())
        if not (directory / 'loops').is_dir():
            return None
        progress = ledger_progress(directory, session)
        with loop.locked(directory, timeout=2):
            marker = loop.load(directory, session)
            if not marker:
                return None
            if marker.get('state') != 'active':
                return None
            previous = marker.get('ledger_progress')
            count = 0 if previous is not None and previous != progress else marker.get('continuations', 0) + 1
            marker.update(continuations=count, ledger_progress=progress)
            if count >= MAX_CONTINUATIONS:
                reason = f'paused on stop attempt {count} without ledger progress'
                marker.update(state='paused', reason=reason)
                loop.save(directory, marker)
                return {'systemMessage': f'Oversee loop {reason}. Inspect the failure and '
                        'resume the loop when ready.'}
            loop.save(directory, marker)
            return {'decision': 'block', 'reason': instruction(session, marker)}
    except TimeoutError:
        return {'systemMessage': 'Oversee loop marker is busy; continuation was not scheduled. '
                'Inspect the loop status before continuing.'}
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config')
    parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        result = decide(payload) if isinstance(payload, dict) else None
        if result:
            print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError):
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
