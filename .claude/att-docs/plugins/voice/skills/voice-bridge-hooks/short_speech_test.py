#!/usr/bin/env python3
"""Checks short_speech.py against blocks built in each test.

usage: python3 short_speech_test.py
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hook_config  # noqa: E402
CONFIG = os.path.join(HERE, 'test-config.json')
hook_config.use(CONFIG)
import short_speech as ss  # noqa: E402


def sentences(count):
    return ' '.join(f'Detail {n} of the run.' for n in range(1, count + 1))


class Brief(unittest.TestCase):
    def test_a_short_block_is_read_whole(self):
        self.assertEqual(ss.brief('Two files changed. Tests pass.'),
                         'Two files changed. Tests pass.')

    def test_the_limit_itself_is_read_whole_and_one_past_it_is_cut(self):
        at_limit = 'A' * (ss.SPOKEN_LIMIT - 1) + '.'
        self.assertEqual(ss.brief(at_limit), at_limit)
        self.assertEqual(ss.brief(at_limit + ' B'),
                         'A' * ss.OPENING_LIMIT + '. ' + ss.ON_SCREEN)

    def test_a_long_block_is_its_opening_sentence_and_a_note(self):
        text = 'The suite passed after one fix. ' + sentences(60)
        self.assertEqual(ss.brief(text), 'The suite passed after one fix. ' + ss.ON_SCREEN)

    def test_a_question_mark_or_exclamation_ends_the_opening_sentence(self):
        for first in ('Did it pass?', 'It passed!'):
            self.assertEqual(ss.brief(f'{first} {sentences(60)}'), f'{first} {ss.ON_SCREEN}')

    def test_a_decimal_or_an_abbreviation_does_not_end_the_sentence(self):
        text = 'Took 7.5 seconds, e.g. a fast run, vs. the old one. ' + sentences(60)
        self.assertEqual(ss.brief(text),
                         'Took 7.5 seconds, e.g. a fast run, vs. the old one. ' + ss.ON_SCREEN)

    def test_a_long_first_sentence_is_cut_at_a_word(self):
        text = ' '.join(['word'] * 400)
        said = ss.brief(text)
        opening = said[:-len(ss.ON_SCREEN) - 1]
        self.assertTrue(opening.endswith('word.'))
        self.assertLessEqual(len(opening), ss.OPENING_LIMIT + 1)
        self.assertTrue(said.endswith(ss.ON_SCREEN))

    def test_a_long_text_with_no_space_is_still_cut(self):
        said = ss.brief('x' * 2000)
        self.assertEqual(said, 'x' * ss.OPENING_LIMIT + '. ' + ss.ON_SCREEN)

    def test_a_list_marker_does_not_end_the_opening_sentence(self):
        text = 'Three things changed: 1. The hook reads it. 2. The docs say so. ' + sentences(60)
        self.assertEqual(ss.brief(text), 'Three things changed: 1. The hook reads it. ' + ss.ON_SCREEN)
        self.assertEqual(ss.brief('1. Fixed the cutter. ' + sentences(60)),
                         '1. Fixed the cutter. ' + ss.ON_SCREEN)

    def test_no_followed_by_a_sentence_is_not_an_abbreviation(self):
        self.assertEqual(ss.brief('No. The test fails. ' + sentences(60)),
                         'No. ' + ss.ON_SCREEN)

    def test_a_list_flattened_to_one_line_is_not_cut_at_a_marker(self):
        # The spoken text of a heading and a list has lost its line breaks.
        self.assertEqual(ss.brief('Summary 1. Fixed the parser. 2. Added tests. ' + sentences(60)),
                         'Summary 1. Fixed the parser. ' + ss.ON_SCREEN)
        said = ss.brief('1. Fixed the parser 2. Added tests 3. Updated the docs. ' + sentences(60))
        self.assertEqual(said, '1. Fixed the parser 2. Added tests 3. Updated the docs. '
                         + ss.ON_SCREEN)

    def test_a_cut_keeps_a_word_that_ends_at_the_limit(self):
        text = 'word ' * 59 + 'xxxxx ' + ' '.join(['more'] * 200)
        self.assertEqual(ss.brief(text), 'word ' * 59 + 'xxxxx. ' + ss.ON_SCREEN)

    def test_a_long_question_is_read_whole(self):
        text = 'Question: Which suite? Options: ' + ', '.join(f'suite {n}' for n in range(200))
        self.assertGreater(len(text), ss.SPOKEN_LIMIT)
        self.assertEqual(ss.brief(text), text)

    def test_text_with_multibyte_characters_is_counted_in_characters(self):
        text = '日' * ss.SPOKEN_LIMIT
        self.assertEqual(ss.brief(text), text)


class ReadyLine(unittest.TestCase):
    def test_one_pull_request(self):
        self.assertEqual(ss.ready_line('PULL REQUEST 214 IS READY FOR YOUR REVIEW\n\n' + sentences(60)),
                         'Pull request 214 is ready for review.')

    def test_the_number_may_carry_a_hash_and_emphasis(self):
        self.assertEqual(ss.ready_line('**Pull request #9** is ready for your review'),
                         'Pull request 9 is ready for review.')

    def test_several_pull_requests_are_listed_once_in_order(self):
        text = ('PULL REQUEST 10 IS READY FOR YOUR REVIEW\n'
                'PULL REQUEST 9 IS READY FOR YOUR REVIEW\n'
                'PULL REQUEST 10 IS READY FOR YOUR REVIEW\n'
                'PULL REQUEST 11 IS READY FOR YOUR REVIEW')
        self.assertEqual(ss.ready_line(text), 'Pull requests 9, 10 and 11 are ready for review.')
        self.assertEqual(ss.ready_line(text.split('\n')[0] + '\n' + text.split('\n')[1]),
                         'Pull requests 9 and 10 are ready for review.')

    def test_a_block_without_the_line_has_none(self):
        self.assertIsNone(ss.ready_line('Done. ' + sentences(60)))


class Command(unittest.TestCase):
    def run_form(self, form, text, config=CONFIG):
        return subprocess.run([sys.executable, os.path.join(HERE, 'short_speech.py'),
                               '--config', config, form], input=text, capture_output=True,
                              text=True, check=False)

    def test_ready_prints_the_line(self):
        done = self.run_form('ready', 'PULL REQUEST 3 IS READY FOR YOUR REVIEW')
        self.assertEqual((done.returncode, done.stdout), (0, 'Pull request 3 is ready for review.\n'))

    def test_ready_exits_1_and_prints_nothing_without_the_line(self):
        done = self.run_form('ready', 'All done.')
        self.assertEqual((done.returncode, done.stdout), (1, ''))

    def test_brief_prints_the_cut_text(self):
        done = self.run_form('brief', 'First. ' + sentences(60))
        self.assertEqual((done.returncode, done.stdout), (0, 'First. ' + ss.ON_SCREEN))

    def test_an_unknown_form_exits_64(self):
        self.assertEqual(self.run_form('other', '').returncode, 64)


if __name__ == '__main__':
    unittest.main()
