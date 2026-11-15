#!/usr/bin/env python3
"""Checks background_pending.py against transcripts built in each test.

usage: python3 background_pending_test.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import background_pending as bp  # noqa: E402

T0 = '2026-10-19T13:00:00.000Z'
T0_MS = 1792414800000
MINUTE = 60_000


def result(fields, at=T0, **extra):
    """A tool result row carrying the structured result the harness records."""
    return {'type': 'user', 'timestamp': at, 'toolUseResult': fields, **extra,
            'message': {'role': 'user', 'content': [{'type': 'tool_result', 'content': 'x'}]}}


def notice(ident, status='completed'):
    return f'<task-notification>\n<task-id>{ident}</task-id>\n<status>{status}</status>\n'


def delivered(ident, status='completed'):
    return {'type': 'user', 'timestamp': T0,
            'message': {'role': 'user', 'content': notice(ident, status)}}


def queued(ident, operation):
    return {'type': 'queue-operation', 'operation': operation, 'content': notice(ident)}


def task_status(ident, status):
    return {'type': 'attachment', 'attachment': {'type': 'task_status', 'taskId': ident,
                                                 'taskType': 'local_bash', 'status': status}}


def row_at(when):
    """A plain prompt row written at when, an ISO timestamp."""
    return {'type': 'user', 'timestamp': when, 'message': {'content': 'next'}}


def task_stop(ident):
    return result({'message': f'Successfully stopped task: {ident} (sleep 60)',
                   'task_id': ident, 'task_type': 'local_bash', 'command': 'sleep 60'})


class Pending(unittest.TestCase):
    def check(self, rows, expected, now=T0_MS + MINUTE, **kw):
        self.assertEqual(bp.pending(rows, now, **kw), expected)

    def test_bash_in_background_until_notified(self):
        start = result({'backgroundTaskId': 'b1', 'stdout': ''})
        self.check([start], ['b1'])
        self.check([start, delivered('b1')], [])

    def test_every_final_status_ends_the_work(self):
        for status in sorted(bp.FINAL):
            self.check([result({'backgroundTaskId': 'b1'}), delivered('b1', status)], [])

    def test_task_stop_ends_the_work(self):
        self.check([result({'backgroundTaskId': 'b1'}), task_stop('b1')], [])

    def test_task_status_row_reports_the_status(self):
        start = result({'backgroundTaskId': 'b1'})
        self.check([start, task_status('b1', 'running')], ['b1'])
        self.check([start, task_status('b1', 'completed')], [])

    def test_async_agent_and_workflow(self):
        agent = result({'status': 'async_launched', 'agentId': 'a1', 'isAsync': True})
        flow = result({'status': 'async_launched', 'taskId': 'w1', 'runId': 'r'})
        self.check([agent, flow], ['a1', 'w1'])
        self.check([agent, flow, delivered('w1')], ['a1'])

    def test_skill_forked_into_the_background(self):
        forked = result({'status': 'forked', 'background': True, 'agentId': 'a1'})
        self.check([forked], ['a1'])
        self.check([result({'status': 'forked', 'agentId': 'a1'})], [])

    def test_resumed_agent_is_pending_again(self):
        rows = [result({'status': 'async_launched', 'agentId': 'a1'}), delivered('a1'),
                result({'message': 'Resuming agent a1', 'resumedAgentId': 'a1'})]
        self.check(rows[:2], [])
        self.check(rows, ['a1'])

    def test_notice_queued_before_a_resume_leaves_the_resumed_run(self):
        late = '2026-10-19T13:00:05.000Z'
        text = notice('a1')
        rows = [result({'status': 'async_launched', 'agentId': 'a1'}),
                {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': text},
                result({'resumedAgentId': 'a1'}, at=late),
                {'type': 'attachment', 'timestamp': T0,
                 'attachment': {'type': 'queued_command', 'prompt': text}},
                {'type': 'queue-operation', 'operation': 'remove', 'timestamp': late,
                 'content': text}]
        self.check(rows, ['a1'])
        self.check(rows[:3] + rows[4:] + rows[3:4], ['a1'])
        self.check(rows[:2] + rows[3:], [])
        self.check(rows + [delivered('a1')], [])

    def test_work_that_finished_before_its_launch_row(self):
        late = '2026-10-19T13:00:00.003Z'
        text = notice('b1')
        rows = [{'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': text},
                result({'backgroundTaskId': 'b1'}, at=late),
                {'type': 'attachment', 'timestamp': T0,
                 'attachment': {'type': 'queued_command', 'prompt': text}},
                {'type': 'queue-operation', 'operation': 'remove', 'timestamp': late,
                 'content': text}]
        self.check(rows, [])

    def test_quoted_notices_name_no_task(self):
        restarted = ('<task-notification><task-id>a9</task-id><summary>Background agent '
                     '"x" was restarted after the previous session ended</summary>')
        quote = '<agent-message from="a2">report quoting ' + restarted + notice('b1')
        rows = [result({'backgroundTaskId': 'b1'}),
                {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': quote},
                {'type': 'user', 'timestamp': T0, 'message': {'content': quote}}]
        self.check(rows, ['b1'])

    def test_agent_restarted_after_a_restart(self):
        late = '2026-10-19T13:30:00.000Z'
        text = ('<task-notification>\n<task-id>a1</task-id>\n<summary>Background agent '
                '"x" was restarted after the previous session ended</summary>\n')
        rows = [result({'status': 'async_launched', 'agentId': 'a1'}),
                {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': late,
                 'content': text}]
        started = T0_MS + 20 * MINUTE
        self.check(rows, ['a1'], now=T0_MS + 40 * MINUTE, started_ms=started)
        rows.append({'type': 'user', 'timestamp': late, 'message': {'content': text}})
        self.check(rows, ['a1'], now=T0_MS + 40 * MINUTE, started_ms=started)
        rows.append(delivered('a1'))
        self.check(rows, [], now=T0_MS + 40 * MINUTE, started_ms=started)

    def test_foreground_agent_is_not_pending(self):
        self.check([result({'status': 'completed', 'agentId': 'a1'})], [])

    def test_monitor_until_its_timeout(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': False})
        self.check([start], ['m1'], now=T0_MS + 4 * MINUTE)
        self.check([start], [], now=T0_MS + 6 * MINUTE)

    def test_persistent_monitor_has_no_timeout(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': True})
        self.check([start], ['m1'], now=T0_MS + 600 * MINUTE)
        self.check([start, task_stop('m1')], [], now=T0_MS + 600 * MINUTE)

    def test_latest_wakeup_counts(self):
        early = result({'scheduledFor': T0_MS + 10 * MINUTE})
        late = result({'scheduledFor': T0_MS + 30 * MINUTE})
        self.check([early], [bp.WAKEUP], now=T0_MS + 5 * MINUTE)
        self.check([early], [], now=T0_MS + 11 * MINUTE)
        self.check([early, late], [bp.WAKEUP], now=T0_MS + 11 * MINUTE)

    def test_queued_notice_still_wakes_the_session(self):
        start = result({'backgroundTaskId': 'b1'})
        self.check([start, queued('b1', 'enqueue')], ['b1'])
        self.check([start, queued('b1', 'enqueue'), queued('b1', 'remove')], [])

    def test_notice_delivered_as_queued_command(self):
        command = {'type': 'attachment',
                   'attachment': {'type': 'queued_command', 'prompt': notice('b1')}}
        self.check([result({'backgroundTaskId': 'b1'}), command], [])

    def test_quoted_notice_in_a_tool_result_does_not_end_the_work(self):
        quote = result({'stdout': notice('b1')})
        quote['message']['content'][0]['content'] = notice('b1')
        self.check([result({'backgroundTaskId': 'b1'}), quote], ['b1'])

    def test_assistant_row_naming_a_launch_is_not_one(self):
        said = {'type': 'assistant', 'toolUseResult': {'backgroundTaskId': 'b1'}}
        self.check([said], [])

    def test_queued_monitor_event_wakes_past_the_deadline(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': False})
        event = {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': notice('m1', 'running')}
        self.check([start, event], ['m1'], now=T0_MS + 6 * MINUTE)

    def test_second_queued_event_waits_for_its_own_delivery(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': False})
        first, second = notice('m1', 'running') + 'one', notice('m1', 'running') + 'two'
        rows = [start] + [{'type': 'queue-operation', 'operation': op, 'timestamp': T0,
                           'content': text}
                          for op, text in (('enqueue', first), ('enqueue', second),
                                           ('remove', first))]
        self.check(rows, ['m1'], now=T0_MS + 6 * MINUTE)
        delivered_second = {'type': 'user', 'message': {'content': second}}
        self.check(rows + [delivered_second], [], now=T0_MS + 6 * MINUTE)

    def test_final_notice_clears_only_its_own_queued_notices(self):
        both = notice('a1', 'running') + notice('b1', 'running')
        rows = [{'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': both}, delivered('a1', 'completed')]
        self.check(rows, ['b1'])

    def test_task_status_does_not_deliver_a_queued_notice(self):
        rows = [result({'backgroundTaskId': 'b1'}), queued('b1', 'enqueue'),
                task_status('b1', 'completed')]
        self.check(rows, ['b1'])

    def test_monitor_event_keeps_its_deadline(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': False})
        event = delivered('m1', 'running')
        self.check([start, event], ['m1'], now=T0_MS + 4 * MINUTE)
        self.check([start, event], [], now=T0_MS + 6 * MINUTE)

    def test_work_from_before_a_restart_is_gone(self):
        rows = [result({'status': 'async_launched', 'taskId': 'w1'}),
                result({'backgroundTaskId': 'b1'}, at='2026-10-19T13:30:00.000Z')]
        self.check(rows, ['b1'], now=T0_MS + 40 * MINUTE, started_ms=T0_MS + 20 * MINUTE)
        self.check(rows, ['w1', 'b1'], now=T0_MS + 40 * MINUTE, started_ms=None)

    def test_queued_notice_from_before_a_restart_is_gone(self):
        enqueue = dict(queued('b1', 'enqueue'), timestamp=T0)
        rows = [result({'backgroundTaskId': 'b1'}), enqueue, row_at('2026-10-19T13:05:00Z')]
        self.check(rows, ['b1'], started_ms=T0_MS - MINUTE)
        self.check(rows, [], started_ms=T0_MS + 2 * MINUTE)

    def test_launch_just_before_the_start_survives_a_clock_step(self):
        rows = [result({'backgroundTaskId': 'b1'}), row_at('2026-10-19T13:05:00Z')]
        self.check(rows, ['b1'], started_ms=T0_MS + bp.CLOCK_SLACK_MS / 2)
        self.check(rows, [], started_ms=T0_MS + 2 * bp.CLOCK_SLACK_MS)

    def test_identical_queued_notices_each_wait_for_a_delivery(self):
        start = result({'taskId': 'm1', 'timeoutMs': 5 * MINUTE, 'persistent': False})
        event = {'type': 'queue-operation', 'operation': 'enqueue', 'timestamp': T0,
                 'content': notice('m1', 'running')}
        command = {'type': 'attachment',
                   'attachment': {'type': 'queued_command', 'prompt': notice('m1', 'running')}}
        removed = dict(event, operation='remove')
        late = T0_MS + 6 * MINUTE
        self.check([start, event, event, command, removed], ['m1'], now=late)
        self.check([start, event, event, command, removed, delivered('m1', 'running')], [],
                   now=late)

    def test_launch_without_a_timestamp_counts_as_before_the_start(self):
        rows = [result({'backgroundTaskId': 'b1'}, at=None), row_at(T0)]
        self.check(rows, [], started_ms=T0_MS - MINUTE)
        self.check(rows, ['b1'], started_ms=None)

    def test_start_after_the_latest_row_is_not_the_session(self):
        rows = [result({'backgroundTaskId': 'b1'})]
        self.check(rows, ['b1'], started_ms=T0_MS + MINUTE)


class Main(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.path = os.path.join(self.dir, 'session.jsonl')

    def run_on(self, rows, *pid):
        with open(self.path, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in rows) + '\nnot json\n')
        with contextlib.redirect_stdout(io.StringIO()):
            return bp.main(['background_pending.py', self.path, *pid])

    def test_exit_codes(self):
        self.assertEqual(self.run_on([result({'scheduledFor': 2 * T0_MS})]), 0)
        self.assertEqual(self.run_on([]), 1)
        self.assertEqual(bp.main(['background_pending.py', '/nonexistent']), 1)

    def test_subagent_launches_are_left_out(self):
        rows = [result({'scheduledFor': 2 * T0_MS}, isSidechain=True)]
        self.assertEqual(self.run_on(rows), 1)

    @unittest.skipUnless(os.path.isdir('/proc'), 'process start times come from /proc')
    def test_session_pid_drops_work_from_before_it_started(self):
        now = datetime.now(timezone.utc).isoformat()
        rows = [result({'scheduledFor': 2 * T0_MS}, at='2000-01-01T00:00:00Z'), row_at(now)]
        self.assertEqual(self.run_on(rows, str(os.getpid())), 1)
        self.assertEqual(self.run_on(rows, '999999999'), 0)
        for bad in ('not-a-pid', '\u00b2'):
            self.assertEqual(self.run_on(rows, bad), 2)

    def run_at_stop(self, rows, stop_at):
        with mock.patch.dict(os.environ, {'STOP_AT': str(stop_at)}):
            return self.run_on(rows)

    def test_delivery_since_the_stop_is_a_turn_after_it(self):
        start = result({'backgroundTaskId': 'b1'})
        reply = {'type': 'assistant', 'timestamp': T0, 'message': {'content': 'Done.'}}
        stop = T0_MS + 2000
        later = '2026-10-19T13:00:02.010Z'
        thinking = {'type': 'assistant', 'timestamp': '2026-10-19T13:00:03.000Z',
                    'message': {'content': [{'type': 'thinking', 'thinking': 'x'}]}}
        delivery = {**delivered('b1'), 'timestamp': later}
        self.assertEqual(self.run_at_stop([start, reply, delivery], stop), 0)
        self.assertEqual(self.run_at_stop([start, reply, delivery, thinking], stop), 0)
        self.assertEqual(self.run_on([start, reply, delivery]), 1)
        command = {'type': 'attachment', 'timestamp': later,
                   'attachment': {'type': 'queued_command', 'prompt': notice('zz')}}
        self.assertEqual(bp.unanswered([reply, command], stop), [])
        lone = {**queued('zz', 'remove'), 'timestamp': later}
        self.assertEqual(self.run_at_stop([reply, lone], stop), 1)
        self.assertEqual(self.run_at_stop([start, reply, task_status('b1', 'completed')], stop), 1)

    def test_the_event_that_started_the_stopping_turn_is_left_out(self):
        # The stop came 1.5 seconds after the event and its reply row is not written yet.
        self.assertEqual(bp.unanswered([delivered('b1')], T0_MS + 1500 - bp.STOP_SLACK_MS), [])
        self.assertEqual(bp.unanswered([delivered('b1')], T0_MS), ['b1'])

    def test_any_event_since_the_stop_counts(self):
        event = {'type': 'user', 'timestamp': T0,
                 'message': {'role': 'user', 'content': '<ci-monitor-event>checks failed'}}
        monitor = result({'taskId': 'm1', 'timeoutMs': MINUTE})
        self.assertEqual(bp.unanswered([monitor, delivered('m1', 'running')], T0_MS), ['m1'])
        self.assertEqual(bp.unanswered([event], T0_MS), ['ci-monitor-event'])
        self.assertEqual(bp.unanswered([row_at(T0)], T0_MS), [])
        hinted = {**event, 'message': {'role': 'user', 'content':
                  '<system-reminder>x</system-reminder>\n<ci-monitor-event>checks failed'}}
        self.assertEqual(bp.unanswered([hinted], T0_MS), ['ci-monitor-event'])

    def test_started_ms_reads_proc(self):
        proc = os.path.join(self.dir, 'proc')
        os.makedirs(os.path.join(proc, '42'))
        fields = ['S', '1'] + ['0'] * 17 + [str(50 * 100)]
        with open(os.path.join(proc, '42', 'stat'), 'w') as f:
            f.write('42 (name with) spaces) ' + ' '.join(fields))
        with open(os.path.join(proc, 'stat'), 'w') as f:
            f.write('cpu 1 2\nbtime 1000\n')
        self.assertEqual(bp.started_ms(42, proc, ticks=100), 1050 * 1000)
        self.assertIsNone(bp.started_ms(43, proc, ticks=100))

    def test_started_ms_without_proc(self):
        self.assertIsNone(bp.started_ms(1, os.path.join(self.dir, 'none'), ticks=100))

    def call(self, ident, name, given):
        return {'type': 'assistant', 'timestamp': T0, 'message': {'content': [
            {'type': 'tool_use', 'id': ident, 'name': name, 'input': given}]}}

    def launched_by(self, call_id, fields):
        row = result(fields)
        row['message']['content'][0]['tool_use_id'] = call_id
        return row

    def test_describe_names_each_kind_of_work(self):
        rows = [
            self.call('t1', 'Agent', {'description': 'Opus review of PR 5'}),
            self.launched_by('t1', {'status': 'async_launched', 'agentId': 'a1'}),
            self.call('t2', 'Bash', {'command': 'gh run watch 41064131838', 'description': 'watch'}),
            self.launched_by('t2', {'backgroundTaskId': 'b1'}),
            self.call('t3', 'Bash', {'command': 'sleep 600 &&\n echo done'}),
            self.launched_by('t3', {'backgroundTaskId': 'b2'}),
            self.call('t4', 'Monitor', {'command': 'tail -f log', 'description': 'log'}),
            self.launched_by('t4', {'taskId': 'm1', 'persistent': True}),
            self.call('t5', 'ScheduleWakeup', {'reason': 'check'}),
            self.launched_by('t5', {'scheduledFor': 2 * T0_MS}),
        ]
        ids = bp.pending(rows, now_ms=T0_MS)
        self.assertEqual(bp.describe(rows, ids), [
            ('a1', 'agent', 'Opus review of PR 5'),
            ('b1', 'run', 'watch'),
            ('b2', 'bash', 'sleep 600 && echo done'),
            ('m1', 'monitor', 'log'),
            ('wakeup', 'wakeup', ''),
        ])

    def test_describe_clips_long_text_and_survives_a_missing_call(self):
        rows = [self.call('t1', 'Agent', {'description': 'x' * 200}),
                self.launched_by('t1', {'status': 'async_launched', 'agentId': 'a1'}),
                result({'backgroundTaskId': 'b9'})]
        (first, second) = bp.describe(rows, ['a1', 'b9'])
        self.assertEqual(len(first[2]), bp.WHAT_LIMIT)
        self.assertEqual(second, ('b9', 'work', ''))

    def test_describe_flag_prints_tab_separated_rows(self):
        rows = [self.call('t1', 'Agent', {'description': 'review'}),
                self.launched_by('t1', {'status': 'async_launched', 'agentId': 'a1'})]
        with open(self.path, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in rows) + '\n')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = bp.main(['background_pending.py', '--describe', self.path])
        self.assertEqual((code, out.getvalue()), (0, 'a1\tagent\treview\n'))
        with contextlib.redirect_stdout(out):
            self.assertEqual(bp.main(['background_pending.py', self.path, '--describe']), 0)


if __name__ == '__main__':
    unittest.main()
