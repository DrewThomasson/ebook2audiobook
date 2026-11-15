#!/usr/bin/env python3
"""Behavioral tests for the loop marker and session hooks."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / 'skills/oversee-development/loop.py'
RUNNER = HERE / 'run.sh'
HOOK = HERE / 'implement_loop.py'


class Loop(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.repo))
        self.env.pop('CLAUDE_CODE_SESSION_ID', None)

    def helper(self, *args, session='one', check=True):
        return subprocess.run(['python3', str(HELPER), '--session', session, *args],
                              cwd=self.repo, env=self.env, capture_output=True, text=True,
                              check=check)

    def hook(self, event='Stop', session='one', **extra):
        payload = dict(hook_event_name=event, session_id=session, cwd=str(self.repo), **extra)
        proc = subprocess.run(['python3', str(HOOK)], cwd=self.repo, env=self.env,
                              input=json.dumps(payload), capture_output=True, text=True, check=True,
                              timeout=5)
        return json.loads(proc.stdout) if proc.stdout else None

    def test_lifecycle_and_isolation(self):
        self.assertIsNone(self.hook())
        self.helper('start', '--milestone', 'first release', 'backend')
        status = self.helper('status').stdout
        self.assertIn('active', status)
        self.assertIn('first release', status)
        self.assertIn('backend', status)
        self.assertEqual(self.hook()['decision'], 'block')
        self.assertIsNone(self.hook(session='two'))
        self.helper('stop', 'waiting for user')
        self.assertIn('waiting for user', self.helper('status').stdout)
        self.assertIsNone(self.hook())
        self.helper('start', 'frontend')
        self.assertEqual(json.loads(self.helper('status').stdout)['label'], 'frontend')
        self.assertEqual(self.hook()['decision'], 'block')

    def test_empty_stop_reason_keeps_the_loop_active(self):
        self.helper('start')
        before = json.loads(self.helper('status').stdout)
        self.assertNotEqual(self.helper('stop', ' ', check=False).returncode, 0)
        self.assertEqual(json.loads(self.helper('status').stdout), before)
        self.assertEqual(self.hook()['decision'], 'block')

    def test_explicit_pause_and_resume(self):
        self.helper('start')
        before = json.loads(self.helper('status').stdout)
        self.assertNotEqual(self.helper('pause', ' ', check=False).returncode, 0)
        self.assertEqual(json.loads(self.helper('status').stdout), before)
        self.helper('pause', 'user needs a break')
        marker = json.loads(self.helper('status').stdout)
        self.assertEqual((marker['state'], marker['reason']), ('paused', 'user needs a break'))
        self.assertIsNone(self.hook())
        self.helper('resume')
        self.assertEqual(self.hook()['decision'], 'block')


    def test_subagents_pass(self):
        self.helper('start')
        self.assertIsNone(self.hook(agent_id='child'))
        self.assertEqual(self.hook()['decision'], 'block')


    def test_start_does_not_replace_active_or_paused_marker(self):
        self.helper('start', 'backend')
        before = json.loads(self.helper('status').stdout)
        self.assertNotEqual(self.helper('start', 'other', check=False).returncode, 0)
        self.assertEqual(json.loads(self.helper('status').stdout), before)
        self.helper('pause', 'requested')
        before = json.loads(self.helper('status').stdout)
        self.assertNotEqual(self.helper('start', 'other', check=False).returncode, 0)
        self.assertEqual(json.loads(self.helper('status').stdout), before)

    def test_session_start_busy_lock_preserves_session_id_and_warns(self):
        self.helper('start')
        lock = self.repo / '.claude/oversee/loops.lock'
        with lock.open('a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            result = self.hook('SessionStart', source='resume')
        context = result['hookSpecificOutput']['additionalContext']
        self.assertIn('--session one', context)
        self.assertIn('busy', context)
        self.assertIn('status', context)

    def test_active_marker_remains_owned_by_its_session(self):
        self.helper('start', 'backend')
        before = json.loads(self.helper('status').stdout)
        self.assertEqual(json.loads(self.helper('status', session='two').stdout)['state'], 'absent')
        self.assertEqual(self.hook()['decision'], 'block')
        self.assertIsNone(self.hook(session='two'))
        self.assertEqual(json.loads(self.helper('status').stdout)['state'], before['state'])

    def test_loop_pauses_after_repeated_continuations_without_progress(self):
        self.helper('start')
        for _ in range(7):
            self.assertEqual(self.hook()['decision'], 'block')
        notice = self.hook()['systemMessage']
        self.assertIn('stop attempt 8 without ledger progress', notice)
        self.assertEqual(json.loads(self.helper('status').stdout)['state'], 'paused')
        self.assertIsNone(self.hook())
        self.helper('resume')
        self.assertEqual(self.hook()['decision'], 'block')

    def test_ledger_progress_resets_continuation_limit(self):
        self.helper('start')
        ledger = self.repo / '.claude/oversee/ledger.tsv'
        ledger.write_text('2026-01-01\t123\tstart\tbranch\t-\tsession one pid \n')
        for _ in range(7):
            self.assertEqual(self.hook()['decision'], 'block')
        oversee = HERE.parent / 'skills/oversee-development/oversee.sh'
        subprocess.run(['bash', str(oversee), 'finish', '123', 'done', '-', 'done'],
                       cwd=self.repo, env=self.env, check=True, capture_output=True)
        for _ in range(8):
            self.assertEqual(self.hook()['decision'], 'block')
        self.assertIn('stop attempt 8', self.hook()['systemMessage'])

    def test_status_commands_and_other_sessions_do_not_mask_stall(self):
        self.helper('start')
        oversee = HERE.parent / 'skills/oversee-development/oversee.sh'
        other = dict(self.env, CLAUDE_CODE_SESSION_ID='other')
        for issue in range(7):
            self.assertEqual(self.hook()['decision'], 'block')
            subprocess.run(['bash', str(oversee), 'status'], cwd=self.repo,
                           env=self.env, check=True, capture_output=True)
            subprocess.run(['bash', str(oversee), 'finish', str(issue), 'done', '-', 'done'],
                           cwd=self.repo, env=other, check=True, capture_output=True)
        self.assertIn('stop attempt 8', self.hook()['systemMessage'])

    def test_unowned_skip_on_previous_issue_does_not_reset_stall(self):
        self.helper('start')
        ledger = self.repo / '.claude/oversee/ledger.tsv'
        ledger.write_text('2026-01-01\t123\tstart\tbranch\t-\tsession one pid 1\n')
        for _ in range(7):
            self.assertEqual(self.hook()['decision'], 'block')
        with ledger.open('a') as out:
            out.write('2026-01-02\t123\tskipped\t-\t-\tnot workable at start: labeled Blocked\n')
        self.assertIn('stop attempt 8', self.hook()['systemMessage'])

    def test_stop_does_not_wait_for_ledger_lock(self):
        self.helper('start')
        lock = self.repo / '.claude/oversee/ledger.tsv.lock'
        with lock.open('a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            self.assertEqual(self.hook()['decision'], 'block')

    def test_busy_marker_lock_reports_failure_before_hook_timeout(self):
        self.helper('start')
        lock = self.repo / '.claude/oversee/loops.lock'
        with lock.open('a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            self.assertIn('busy', self.hook()['systemMessage'])

    def test_same_session_restart_preserves_a_pause(self):
        self.helper('start')
        for _ in range(3):
            self.assertEqual(self.hook()['decision'], 'block')
        self.hook('SessionStart', source='resume')
        self.assertEqual(self.hook()['decision'], 'block')
        self.helper('pause', 'requested')
        context = self.hook('SessionStart', source='resume')['hookSpecificOutput']['additionalContext']
        self.assertIn('paused', context)
        self.assertIsNone(self.hook())
        self.helper('resume')
        self.assertEqual(self.hook()['decision'], 'block')

    def test_non_repository_session_gets_no_loop_context(self):
        payload = {'hook_event_name': 'SessionStart', 'session_id': 'one',
                   'cwd': self.temp.name, 'source': 'startup'}
        proc = subprocess.run(['python3', str(HOOK)], cwd=self.temp.name, env=self.env,
                              input=json.dumps(payload), capture_output=True, text=True, check=True)
        self.assertEqual(proc.stdout, '')

    def test_resume_and_compact_restore_context(self):
        self.helper('start', 'backend')
        for source in ('resume', 'compact'):
            context = self.hook('SessionStart', source=source)['hookSpecificOutput']['additionalContext']
            self.assertIn('backend', context)
            self.assertIn('pause "reason"', context)
            self.assertIn('resume', context.lower())
        self.helper('stop', 'done')
        context = self.hook('SessionStart', source='resume')['hookSpecificOutput']['additionalContext']
        self.assertNotIn('active loop', context.lower())

    def test_session_id_bridge_and_no_automatic_takeover(self):
        context = self.hook('SessionStart', session='two', source='startup')
        self.assertIn('--session two', context['hookSpecificOutput']['additionalContext'])
        self.helper('start', session='one')
        before = json.loads(self.helper('status').stdout)
        context = self.hook('SessionStart', session='two', source='startup')
        self.assertNotIn('initialUserMessage', context)
        text = context['hookSpecificOutput']['additionalContext']
        self.assertIn('status --all', text)
        self.assertNotIn('adopt', text.lower())
        self.assertEqual(json.loads(self.helper('status').stdout), before)
        self.assertEqual(json.loads(self.helper('status', session='two').stdout)['state'], 'absent')
        self.assertIsNone(self.hook(session='two'))
        self.assertEqual(self.hook(session='one')['decision'], 'block')

    def test_paused_marker_is_not_transferred_to_another_session(self):
        self.helper('start', 'backend')
        self.helper('pause', 'requested')
        before = json.loads(self.helper('status').stdout)
        self.hook('SessionStart', session='two', source='resume')
        self.assertEqual(json.loads(self.helper('status').stdout), before)
        self.assertEqual(json.loads(self.helper('status', session='two').stdout)['state'], 'absent')
        self.assertIsNone(self.hook(session='two'))
        self.helper('resume')
        self.assertEqual(self.hook()['decision'], 'block')

    def test_worktree_shares_the_main_checkout_marker(self):
        subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                        'commit', '--allow-empty', '-qm', 'initial'], cwd=self.repo, check=True)
        worktree = Path(self.temp.name) / 'worktree'
        subprocess.run(['git', 'worktree', 'add', '-qb', 'other', str(worktree)],
                       cwd=self.repo, check=True)
        self.helper('start')
        result = subprocess.run(['python3', str(HELPER), '--session', 'one', 'status'],
                                cwd=worktree, env=self.env, capture_output=True, text=True, check=True)
        self.assertIn('active', result.stdout)

    def test_invalid_session_cannot_escape_state_directory(self):
        self.assertNotEqual(self.helper('start', session='../outside', check=False).returncode, 0)
        self.assertIsNone(self.hook(session='../outside'))

    def test_runner_opt_out(self):
        self.helper('start')
        config = self.repo / '.claude/skills/repo-hooks/extension.json'
        config.parent.mkdir(parents=True)
        config.write_text('{"implementLoop": false}')
        result = subprocess.run(['bash', str(RUNNER), '--default-on', 'implementLoop', 'implement_loop.py'],
                                cwd=self.repo, env=self.env, input=json.dumps({
                                    'hook_event_name': 'Stop', 'session_id': 'one'}),
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
