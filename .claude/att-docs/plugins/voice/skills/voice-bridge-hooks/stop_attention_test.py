#!/usr/bin/env python3
"""Checks stop_attention.py against transcripts built in each test.

usage: python3 stop_attention_test.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402
hook_config.use(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test-config.json'))
import stop_attention as sa  # noqa: E402

LABEL = ('gh api -X POST repos/o/r/issues/12/labels '
         '-f "labels[]=Awaiting Final Review"')


def started(kind, text='go'):
    """A row that starts a turn, from the user or from an automated event."""
    return {'type': 'user', 'origin': {'kind': kind}, 'message': {'role': 'user', 'content': text}}


def prompt(text):
    """A prompt row the app writes without an origin."""
    return {'type': 'user', 'message': {'role': 'user', 'content': text}}


def joined(kind, text='also this'):
    """A message delivered during a turn."""
    return {'type': 'attachment',
            'attachment': {'type': 'queued_command', 'origin': {'kind': kind}, 'prompt': text}}


def tool_result(ident='t0', error=False, out='ok'):
    return {'type': 'user', 'message': {'role': 'user', 'content': [
        {'type': 'tool_result', 'tool_use_id': ident, 'content': out, 'is_error': error}]}}



def tool_use(name, ident='t0', **fields):
    return {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': ident, 'name': name, 'input': fields}]}}


def wrap_up(**fields):
    return tool_use(sa.WRAP_UP, recap='done', **fields)


class StatusCommands(unittest.TestCase):
    def test_the_statuses_a_turn_set_come_back_in_order_without_a_failed_one(self):
        rows = [
            tool_use('Bash', 'a', command='python3 x/session_title.py status "needs you"'),
            tool_use('Bash', 'b', command="cd y && python3 session_title.py status 'stuck' && ls"),
            tool_result('b', error=True),
            tool_use('Bash', 'c', command='python3 session_title.py status "waiting on Data"'),
            tool_use('Bash', 'd', command='python3 session_title.py work "x"'),
            tool_use('Read', 'e', command='session_title.py status "idle"'),
        ]
        self.assertEqual(sa.status_commands(rows), ['needs you', 'waiting on Data'])
        self.assertEqual(sa.status_commands([]), [])


class Announcement(unittest.TestCase):
    def check(self, rows, expected, reply='Done.'):
        payload = {'last_assistant_message': reply}
        self.assertEqual(sa.announcement(payload, rows), expected)

    def test_user_turn_without_a_question_is_finished(self):
        self.check([started('human'), tool_result()], 'finished')

    def test_notification_turn_without_a_question_is_quiet(self):
        self.check([started('human'), tool_result(), started('task-notification'),
                    tool_result()], None)

    def test_peer_report_turn_is_quiet(self):
        self.check([started('peer')], None)

    def test_monitor_event_without_an_origin_is_quiet(self):
        self.check([started('human'), prompt('<ci-monitor-event>"Auto-fix" reports')], None)

    def test_local_command_does_not_start_a_turn(self):
        self.check([started('task-notification'), prompt('<command-name>/model</command-name>')],
                   None)

    def test_prompt_without_an_origin_is_the_user(self):
        self.check([prompt('fix the lint')], 'finished')

    def test_user_message_during_an_event_turn_counts(self):
        self.check([started('task-notification'), joined('human')], 'finished')

    def test_peer_message_during_an_event_turn_stays_quiet(self):
        self.check([started('task-notification'), joined('peer')], None)

    def test_wrap_up_question_waits(self):
        self.check([started('task-notification'), wrap_up(ask='Merge it?')],
                   'is waiting for you')

    def test_wrap_up_without_a_question_does_not_wait(self):
        self.check([started('task-notification'), wrap_up()], None)

    def test_wrap_up_from_an_earlier_turn_does_not_count(self):
        self.check([started('human'), wrap_up(ask='Merge it?'), started('task-notification')],
                   None)

    def test_reply_ending_in_a_question_waits(self):
        self.check([started('task-notification')], 'is waiting for you',
                   reply='The run is red.\n\nShould I rerun the **two failed tests?**\n')

    def test_question_mark_earlier_in_the_reply_does_not_wait(self):
        self.check([started('task-notification')], None,
                   reply='Why did it fail? The lease timed out.\n\nRerun is green.')

    def test_label_added_in_the_turn_is_quiet(self):
        self.check([started('human'), tool_use('Bash', 'l1', command=LABEL),
                    tool_result('l1', out='Awaiting Final Review')], None, reply='Labeled.')

    def test_refused_label_still_speaks(self):
        self.check([started('human'), tool_use('Bash', 'l1', command=LABEL),
                    tool_result('l1', error=True)], 'finished')

    def test_label_named_in_a_search_still_speaks(self):
        self.check([started('human'),
                    tool_use('Bash', 'g1', command='grep -rn "Awaiting Final Review" docs'),
                    tool_result('g1')], 'finished')


    def test_label_add_that_printed_nothing_still_speaks(self):
        self.check([started('human'), tool_use('Bash', 'l1', command=LABEL + ' || true'),
                    tool_result('l1', out='')], 'finished')

    def test_answered_question_in_the_turn_is_finished(self):
        self.check([started('human'), tool_use('AskUserQuestion', 'q1'), tool_result('q1')],
                   'finished')

    def test_compact_summary_does_not_start_a_turn(self):
        summary = {'type': 'user', 'isCompactSummary': True,
                   'message': {'role': 'user', 'content': 'Summary: ...'}}
        self.check([started('task-notification'), tool_use('Bash', 'l1', command=LABEL),
                    tool_result('l1', out='Awaiting Final Review'), summary], None)


    def test_label_named_only_in_standard_error_still_speaks(self):
        failed = tool_result('l1', out='failed to add label Awaiting Final Review\ndone')
        failed['toolUseResult'] = {'stdout': 'done', 'stderr': 'failed: Awaiting Final Review'}
        self.check([started('human'), tool_use('Bash', 'l1', command=LABEL + '; echo done'),
                    failed], 'finished')


    def test_injected_notice_during_an_event_turn_stays_quiet(self):
        notice = {'type': 'attachment', 'attachment': {
            'type': 'queued_command',
            'prompt': '<system-reminder> You are in a git worktree</system-reminder>'}}
        self.check([started('task-notification'), notice], None)

    def test_interrupt_marker_does_not_start_a_turn(self):
        self.check([started('task-notification'), prompt('[Request interrupted by user]')], None)


if __name__ == '__main__':
    unittest.main()
