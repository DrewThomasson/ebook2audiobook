#!/usr/bin/env python3
"""Checks ready_line.py against replies and label commands built in each test.

usage: python3 ready_line_test.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402
hook_config.use(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test-config.json'))
import ready_line as rl  # noqa: E402

ENDPOINT = 'gh api -X POST repos/o/r/issues/{}/labels {} "labels[]=Awaiting Final Review"'


def assistant(text):
    return {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': text}]}}


class ReadyNumbers(unittest.TestCase):
    def test_reads_the_line_in_any_case_and_with_emphasis(self):
        for line in ('PULL REQUEST 77 IS READY FOR YOUR REVIEW',
                     'pull request #77 is ready for your review',
                     'PULL REQUEST **77** IS READY FOR YOUR REVIEW'):
            self.assertEqual(rl.ready_numbers({'last_assistant_message': line}, []), ['77'])

    def test_lists_each_number_once_in_ascending_order(self):
        reply = ('PULL REQUEST 9 IS READY FOR YOUR REVIEW\n'
                 'PULL REQUEST 10 IS READY FOR YOUR REVIEW\n'
                 'PULL REQUEST 9 IS READY FOR YOUR REVIEW')
        self.assertEqual(rl.ready_numbers({'last_assistant_message': reply}, []), ['9', '10'])

    def test_reads_assistant_text_after_the_last_tool_call(self):
        entries = [assistant('PULL REQUEST 5 IS READY FOR YOUR REVIEW')]
        self.assertEqual(rl.ready_numbers({}, entries), ['5'])

    def test_a_reply_without_the_line_names_none(self):
        self.assertEqual(rl.ready_numbers({'last_assistant_message': 'Done.'}, []), [])


class LabeledNumbers(unittest.TestCase):
    def test_an_endpoint_call_with_a_field_adds_the_label(self):
        self.assertEqual(rl.labeled_numbers(ENDPOINT.format(12, '-f')), ['12'])

    def test_an_endpoint_call_without_a_field_only_reads(self):
        self.assertIsNone(rl.labeled_numbers('gh api repos/o/r/issues/12/labels'))

    def test_a_delete_takes_the_label_off(self):
        self.assertIsNone(rl.labeled_numbers(ENDPOINT.format(12, '-X DELETE -f')))

    def test_a_pr_edit_adds_the_label(self):
        command = 'gh pr edit 31 --add-label "Awaiting Final Review"'
        self.assertEqual(rl.labeled_numbers(command), ['31'])

    def test_a_remove_label_edit_is_not_an_add(self):
        command = 'gh pr edit 31 --remove-label "Awaiting Final Review"'
        self.assertIsNone(rl.labeled_numbers(command))

    def test_label_added_reads_the_output_of_a_successful_add(self):
        self.assertTrue(rl.LABEL_ADDED.search('https://github.com/o/r/pull/31'))
        self.assertFalse(rl.LABEL_ADDED.search('error: not found'))


if __name__ == '__main__':
    unittest.main()
