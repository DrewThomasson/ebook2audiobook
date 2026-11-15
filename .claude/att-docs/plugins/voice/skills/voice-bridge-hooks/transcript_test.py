"""Tests for transcript.py: the tool calls a session made and the ledgers they name.

usage: python3 transcript_test.py

The ledger tools are test-config.json's. blocked() reads its ledger through a stand-in
ledger module, written with a config of its own into a scratch git work tree.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hook_config  # noqa: E402
FIXTURE = os.path.join(HERE, 'test-config.json')
hook_config.use(FIXTURE)
import transcript  # noqa: E402

# The stand-in ledger module: one row per line, its fields split on tabs.
LEDGER_MODULE = '''
FIELDS = ('label', 'branch', 'run', 'job', 'state', 'tally', 'title')
STATIC_CHECKS_NAME = 'Checks'


def read_ledger(path):
    with open(path, encoding='utf-8') as f:
        return [dict(zip(FIELDS, line.rstrip('\\n').split('\\t') + [''] * len(FIELDS)))
                for line in f if line.strip()]
'''


def scratch_config(folder):
    """A config in a scratch git work tree whose scriptsDir holds the stand-in module."""
    subprocess.run(['git', 'init', '-q', folder], check=True)
    os.makedirs(os.path.join(folder, 'tools'))
    with open(os.path.join(folder, 'tools', 'fixture_ledger.py'), 'w') as f:
        f.write(LEDGER_MODULE)
    with open(FIXTURE) as f:
        values = dict(json.load(f), scriptsDir='tools')
    path = os.path.join(folder, 'extension.json')
    with open(path, 'w') as f:
        json.dump(values, f)
    return path


def bash(use_id, command):
    block = {'type': 'tool_use', 'id': use_id, 'name': 'Bash', 'input': {'command': command}}
    return {'type': 'assistant', 'message': {'content': [block]}}


def result(use_id, text, error=False):
    block = {'type': 'tool_result', 'tool_use_id': use_id, 'content': text, 'is_error': error}
    return {'type': 'user', 'message': {'content': [block]}}


class ReadSessionTests(unittest.TestCase):
    def test_a_result_is_paired_with_its_call(self):
        entries = [bash('a', 'ls'), result('a', 'out', error=True)]
        calls, by_id = transcript.read_session(entries)
        self.assertEqual([c.command for c in calls], ['ls'])
        self.assertEqual((by_id['a'].result, by_id['a'].error, by_id['a'].answered),
                         ('out', True, True))

    def test_a_tool_result_is_not_a_prompt(self):
        self.assertFalse(transcript.starts_turn(result('a', 'out')))
        typed = {'type': 'user', 'message': {'content': 'hello'}}
        self.assertTrue(transcript.starts_turn(typed))
        event = {'type': 'user', 'message': {'content': '<ci-monitor-event>x'}}
        self.assertTrue(transcript.starts_turn(event))
        local = {'type': 'user', 'message': {'content': '<command-name>/model</command-name>'}}
        self.assertFalse(transcript.starts_turn(local))

    def test_prompt_kind_by_origin_then_tag(self):
        def user(content, **extra):
            return {'type': 'user', 'message': {'content': content}, **extra}

        kind = transcript.prompt_kind
        self.assertEqual(kind(user('hello')), transcript.HUMAN)
        self.assertEqual(kind(user('<ci-monitor-event>x')), transcript.EVENT)
        self.assertEqual(kind(user('x', origin={'kind': 'peer'})), transcript.EVENT)
        self.assertEqual(kind(user('x', origin={'kind': 'human'})), transcript.HUMAN)
        self.assertIsNone(kind(user('Summary', isCompactSummary=True)))
        notice = '<system-reminder> You are operating in a git worktree</system-reminder>'
        self.assertEqual(kind(user(notice)), transcript.EVENT)
        self.assertEqual(kind(user(notice + '\n\nTask (from the session): go')), transcript.HUMAN)
        resumed = '<system-reminder>The app was quit while you were working.</system-reminder>'
        self.assertEqual(kind(user(resumed)), transcript.HUMAN)
        self.assertEqual(kind(user(notice + '<ci-monitor-event>x')), transcript.EVENT)
        self.assertEqual(kind(user('<agent-message from="a1">done')), transcript.EVENT)
        self.assertIsNone(kind(result('a', 'out')))
        joined = {'type': 'attachment', 'attachment': {
            'type': 'queued_command', 'origin': {'kind': 'human'}, 'prompt': 'also'}}
        self.assertEqual(kind(joined), transcript.HUMAN)


class LedgerTests(unittest.TestCase):
    def ledgers(self, command):
        calls, _ = transcript.read_session([bash('a', command)])
        return transcript.ledgers(calls)

    def test_ledger_tool_argument(self):
        self.assertEqual(self.ledgers('tools/ledger.py wait /tmp/l.tsv'), ['/tmp/l.tsv'])
        self.assertEqual(self.ledgers('tools/ledger.py add-checks /tmp/c.tsv 5'),
                         ['/tmp/c.tsv'])

    def test_dispatch_flag_skips_a_quoted_pipe(self):
        command = "tools/dispatch.sh -f grep='A-1|A-2' --ledger /tmp/l.tsv"
        self.assertEqual(self.ledgers(command), ['/tmp/l.tsv'])

    def test_driver_state_directory(self):
        self.assertEqual(self.ledgers('bash watch.sh /tmp/state/'),
                         ['/tmp/state/ledger.tsv'])
        self.assertEqual(self.ledgers('nohup tools/sweep.sh a b /tmp/s > out.log'),
                         ['/tmp/s/ledger.tsv'])

    def test_a_script_the_config_does_not_name_is_no_driver(self):
        self.assertEqual(self.ledgers('bash watch-done.sh /tmp/state/'), [])

    def test_assignment_in_the_command_is_expanded(self):
        self.assertEqual(self.ledgers('L=/tmp/l.tsv; tools/ledger.py check $L'),
                         ['/tmp/l.tsv'])

    def test_blocked_reads_open_rows_and_leaves_the_sessions_own_pull_requests_out(self):
        with tempfile.TemporaryDirectory() as folder:
            work = os.path.join(folder, 'work')
            os.makedirs(work)
            ledger = os.path.join(folder, 'l.tsv')

            def row(run, state='open', branch='', title=''):
                return '\t'.join(['label', branch, run, 'url', state, 'added', title])
            with open(ledger, 'w') as f:
                f.write('\n'.join([
                    row('issue:5180'), row('issue:5170', 'done'),
                    row('pr:5181', branch='feat/holder'),
                    # The session's own: opened by its gh pr create, checked, or its branch.
                    row('pr:5190', branch='feat/opened'), row('pr:5191', branch='feat/checked'),
                    row('1', 'done', 'feat/checked', 'Checks on pull request 5191'),
                    row('pr:5192', branch='feat/was-on')]) + '\n')
            created = bash('c', 'gh pr create --body-file b.md')
            done = {'type': 'user', 'message': {'content': [{
                'type': 'tool_result', 'tool_use_id': 'c',
                'content': 'https://github.com/o/r/pull/5190'}]}}
            # A relative path resolves against the working directory of the call naming it.
            named = dict(bash('a', 'tools/ledger.py wait --all ../l.tsv'), cwd=work)
            path = os.path.join(folder, 't.jsonl')
            with open(path, 'w') as f:
                f.write('\n'.join(json.dumps(r) for r in [
                    named, created, done, {'type': 'user', 'gitBranch': 'feat/was-on'}]))
            config = scratch_config(os.path.join(folder, 'repo'))
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    self.assertEqual(transcript.main(
                        ['transcript.py', '--config', config, 'blocked', path]), 0)
            finally:
                hook_config.use(FIXTURE)
            self.assertEqual(json.loads(out.getvalue()), {
                'ledgers': [ledger], 'issues': [5180],
                'pulls': [5181]})
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(transcript.main(['transcript.py']), 2)

    def test_the_defaults_name_no_ledger_and_block_on_nothing(self):
        hook_config.use(os.path.join(HERE, 'defaults.json'))
        try:
            transcript.built.cache_clear()
            call = transcript.Call(0, 'Bash', {'command': 'ledger.py add-pr /tmp/l.tsv 1'})
            self.assertEqual(list(transcript.call_ledgers(call)), [])
            self.assertEqual(transcript.blocked([]),
                             {'ledgers': [], 'issues': [], 'pulls': []})
        finally:
            hook_config.use(FIXTURE)
            transcript.built.cache_clear()

    def test_a_missing_config_exits_64(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as end:
            transcript.main(['transcript.py', '--config', '/nonexistent.json', 'blocked', 'x'])
        self.assertEqual(end.exception.code, hook_config.EXIT_USAGE)
        hook_config.use(FIXTURE)


if __name__ == '__main__':
    unittest.main()
