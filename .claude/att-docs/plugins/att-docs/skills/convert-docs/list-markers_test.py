#!/usr/bin/env python3
"""Cases for list-markers.lua: the labels Word draws on letter and roman lists."""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
FILTERS = [HERE / "drop-images.lua", HERE / "flatten-tables.lua", HERE / "list-markers.lua"]

# The Word file builders the list-numbers cases already use.
SPEC = importlib.util.spec_from_file_location("list_numbers_test", HERE / "list-numbers_test.py")
WORD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORD)


def convert(source: pathlib.Path, reader: str) -> list[str]:
    """The lines convert.sh's Pandoc call writes, blank lines dropped."""
    command = ["pandoc", "-f", reader, "-t", "gfm-raw_html-raw_attribute",
               "--columns=100", "--wrap=auto"]
    command += [f"--lua-filter={path}" for path in FILTERS] + [str(source)]
    out = subprocess.run(command, capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line.strip()]


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
class MarkerTest(unittest.TestCase):
    def setUp(self):
        self.work = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.work)

    def markdown(self, text: str) -> list[str]:
        source = self.work / "in.md"
        source.write_text(text, encoding="utf-8")
        return convert(source, "markdown")

    def word(self, body, definitions) -> list[str]:
        source, target = self.work / "in.docx", self.work / "out.docx"
        WORD.docx(source, body, definitions)
        self.assertEqual(WORD.LIST.main(["list-numbers.py", str(source), str(target)]), 0)
        return convert(target, "docx")

    def test_a_word_letter_list_under_a_numbered_item_keeps_its_letters(self):
        definitions = [
            WORD.abstract(1, WORD.level(0, left=720),
                          WORD.level(1, fmt="lowerLetter", text="%2.", left=1440)),
            WORD.num(1, 1),
        ]
        body = [WORD.para("The grid holds these columns:", 1, 0),
                WORD.para("Select check box", 1, 1), WORD.para("Resource Name", 1, 1),
                WORD.para("The grid is sorted.", 1, 0)]
        self.assertEqual(self.word(body, definitions), [
            "1.  The grid holds these columns:", r"    a\. Select check box",
            r"    b\. Resource Name", "2.  The grid is sorted.",
        ])

    def test_a_word_roman_list_keeps_its_numerals(self):
        definitions = [
            WORD.abstract(1, WORD.level(0, left=720)),
            WORD.abstract(2, WORD.level(0, fmt="lowerRoman", text="%1.", left=1620)),
            WORD.num(1, 1), WORD.num(2, 2),
        ]
        body = [WORD.para("one", 1), WORD.para("sub one", 2), WORD.para("sub two", 2),
                WORD.para("two", 1)]
        self.assertEqual(self.word(body, definitions), [
            "1.  one", r"    i\. sub one", r"    ii\. sub two", "2.  two",
        ])

    def test_upper_case_and_delimiters_follow_the_list(self):
        # The writer escapes punctuation that could open Markdown syntax.
        self.assertEqual(self.markdown("A) first\nB) second\n\n(iv) fourth\n(v) fifth\n"), [
            r"A\) first", r"B\) second", r"\(iv\) fourth", r"\(v\) fifth",
        ])

    def test_a_letter_list_starting_late_runs_past_z(self):
        self.assertEqual(self.markdown("c. third\nd. fourth\n")[0], r"c\. third")
        definitions = [
            WORD.abstract(1, WORD.level(0, fmt="lowerLetter", text="%1.", left=720, start=26)),
            WORD.num(1, 1),
        ]
        body = [WORD.para("last", 1), WORD.para("next", 1)]
        # The writer escapes `z.`, which could open a list, and leaves `aa.`.
        self.assertEqual(self.word(body, definitions), [r"z\. last", "aa. next"])

    def test_the_rest_of_an_item_follows_its_label_in_order(self):
        text = "1.  rule\n\n    a.  item\n\n        more about it\n\n        i.  deeper\n\n    b.  next\n"
        self.assertEqual(self.markdown(text), [
            "1.  rule", r"    a\. item", "    more about it", r"    i\. deeper",
            r"    b\. next",
        ])

    def test_a_digit_list_is_left_as_a_list(self):
        self.assertEqual(self.markdown("1. one\n2. two\n\n    1. sub\n"), [
            "1.  one", "2.  two", "    1.  sub",
        ])

    def test_a_letter_list_in_a_table_cell_stays_text(self):
        text = "+------+------+\n| Name | Rule |\n+======+======+\n| x    | a. y |\n|      | b. z |\n+------+------+\n"
        lines = self.markdown(text)
        self.assertEqual(lines[-1], "| x    | y; z |")


if __name__ == "__main__":
    unittest.main()
