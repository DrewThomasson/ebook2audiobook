#!/usr/bin/env python3
"""Cases for check-list-numbers.py: which converted list numbers disagree with the source."""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "check-list-numbers.py"
SPEC = importlib.util.spec_from_file_location("check_list_numbers", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

# A text export the way LibreOffice writes one: labels drawn, sub-items indented.
EXPORT = """Case Summary

    1. The window will display the case name and the case number.

    2. The grid lists every stage of the case in date order.
        i. The Stage column holds the stage name.
        ii. The Status column holds the stage status.

    3. The user can launch Person Detail from any row.

    1.3 Assumptions for the summary window as written today

    4. (SIR 101) When the user has selected the allegation of neglect, first case
    5. ~~Struck~~ text in the source.
    6. (SIR 101) When the user has selected the allegation of neglect, second case
"""


def numbers(markdown):
    differ, found, missing = CHECK.compare(markdown, EXPORT)
    return [(number, label) for _, number, label, _ in differ], found, missing


class CompareTest(unittest.TestCase):
    def test_numbers_that_follow_the_source_agree(self):
        markdown = (
            "1.  The window will display the case name and the case number.\n\n"
            "2.  The grid lists every stage of the case in date order.\n\n"
            "    1.  The Stage column holds the stage name.\n\n"
            "3.  The user can launch Person Detail from any row.\n"
        )
        self.assertEqual(numbers(markdown), ([], 3, 0))

    def test_a_restarted_list_differs(self):
        markdown = (
            "1.  The window will display the case name and the case number.\n\n"
            "&nbsp;\n\n"
            "1.  The grid lists every stage of the case in date order.\n\n"
            "2.  The user can launch Person Detail from any row.\n"
        )
        self.assertEqual(numbers(markdown)[0], [(1, "2"), (2, "3")])

    def test_a_sub_item_at_the_margin_is_read_by_its_label(self):
        agree = "2.  The Status column holds the stage status.\n"
        self.assertEqual(numbers(agree), ([], 1, 0))
        differ = "5.  The Status column holds the stage status.\n"
        self.assertEqual(numbers(differ)[0], [(5, "ii")])

    def test_a_level_number_is_read_by_its_last_part(self):
        self.assertEqual(numbers("3.  **Assumptions for the summary window as written today**\n"),
                         ([], 1, 0))

    def test_an_escaped_number_is_read(self):
        markdown = "3\\. The user can launch Person Detail from any row.\n"
        self.assertEqual(numbers(markdown), ([], 1, 0))

    def test_items_opening_alike_are_matched_in_order(self):
        markdown = (
            "4.  (SIR 101) When the user has selected the allegation of neglect, first case\n\n"
            "5.  ~~Struck~~ text in the source.\n\n"
            "6.  (SIR 101) When the user has selected the allegation of neglect, second case\n"
        )
        self.assertEqual(numbers(markdown), ([], 3, 0))

    def test_an_item_the_source_does_not_hold_is_counted_not_failed(self):
        markdown = "7.  A sentence the conversion wrote differently.\n"
        self.assertEqual(numbers(markdown), ([], 0, 1))

    def test_an_earlier_item_opening_alike_does_not_excuse_a_restart(self):
        export = ("    1. The Save pushbutton will be enabled when the page loads.\n"
                  "    2. The Cancel pushbutton closes the window without saving.\n"
                  "    3. The Save pushbutton will be enabled when the page loads.\n")
        markdown = ("1.  The Save pushbutton will be enabled when the page loads.\n\n"
                    "2.  The Cancel pushbutton closes the window without saving.\n\n"
                    "1.  The Save pushbutton will be enabled when the page loads.\n")
        differ, found, _ = CHECK.compare(markdown, export)
        self.assertEqual([(n, label) for _, n, label, _ in differ], [(1, "3")])
        self.assertEqual(found, 3)

    def test_an_item_with_no_labelled_copy_ahead_is_not_found(self):
        # Item 3's copy in the export carries no label, as a table cell's would.
        export = (
            "    1. (Build 4 2026) When the user has selected the allegation, the window opens.\n"
            "    2. The Cancel pushbutton closes the window without saving.\n"
            "(Build 4 2026) When the user has selected the allegation, a tab opens.\n"
            "    4. The Cancel pushbutton closes the window without saving.\n"
        )
        markdown = (
            "2.  The Cancel pushbutton closes the window without saving.\n\n"
            "3.  (Build 4 2026) When the user has selected the allegation, a tab opens.\n\n"
            "4.  The Cancel pushbutton closes the window without saving.\n"
        )
        self.assertEqual(CHECK.compare(markdown, export), ([], 2, 1))

    def test_an_earlier_item_opening_alike_with_the_same_number_is_found(self):
        export = ("    1. The Save pushbutton will be enabled when the page loads.\n"
                  "    2. The Cancel pushbutton closes the window without saving.\n")
        markdown = ("2.  The Cancel pushbutton closes the window without saving.\n\n"
                    "1.  The Save pushbutton will be enabled when the page loads.\n")
        self.assertEqual(CHECK.compare(markdown, export), ([], 2, 0))

    def test_a_later_copy_with_the_number_does_not_hide_a_shifted_list(self):
        # The second list repeats the first item's opening under number 2; the
        # first list, numbered one high throughout, still differs on every item.
        export = ("    1. The window will display the case name and number.\n"
                  "    2. The Cancel pushbutton closes the window without saving.\n"
                  "    1. Zeta item text here for list two.\n"
                  "    2. The window will display the case name and number.\n"
                  "    3. Last item text in list two goes here.\n")
        markdown = ("2.  The window will display the case name and number.\n\n"
                    "3.  The Cancel pushbutton closes the window without saving.\n\n"
                    "4.  Zeta item text here for list two.\n")
        differ, found, missing = CHECK.compare(markdown, export)
        self.assertEqual([(n, label) for _, n, label, _ in differ],
                         [(2, "1"), (3, "2"), (4, "1")])
        self.assertEqual((found, missing), (3, 0))

    def test_an_unpaired_opening_far_ahead_does_not_reopen_earlier_items(self):
        # The first item pairs with the second "Intro" copy, leaving the first
        # one unpaired; item 3's own copy still carries no label.
        export = (
            "    1. Intro text that repeats later in the document.\n"
            "    1. Some other heading list item text.\n"
            "    2. Intro text that repeats later in the document.\n"
            "    1. (Build 4 2026) When the user has selected the allegation, the window opens.\n"
            "    2. The Cancel pushbutton closes the window without saving.\n"
            "(Build 4 2026) When the user has selected the allegation, a tab opens.\n"
            "    4. The Cancel pushbutton closes the window without saving.\n"
        )
        markdown = (
            "2.  Intro text that repeats later in the document.\n\n"
            "2.  The Cancel pushbutton closes the window without saving.\n\n"
            "3.  (Build 4 2026) When the user has selected the allegation, a tab opens.\n\n"
            "4.  The Cancel pushbutton closes the window without saving.\n"
        )
        self.assertEqual(CHECK.compare(markdown, export), ([], 3, 1))

    def test_an_item_whose_first_line_is_short_pairs_with_its_longer_copy(self):
        export = ("    1. The window shows the value from https://example.org/very/long/path/"
                  "to/page and more.\n"
                  "    2. Second item text that is long enough here.\n")
        markdown = ("5.  The window shows the value from\n"
                    "    <https://example.org/very/long/path/to/page> and more.\n\n"
                    "6.  Second item text that is long enough here.\n")
        differ, found, missing = CHECK.compare(markdown, export)
        self.assertEqual([(n, label) for _, n, label, _ in differ], [(5, "1"), (6, "2")])
        self.assertEqual((found, missing), (2, 0))

    def test_short_items_and_fenced_code_are_skipped(self):
        markdown = ("1.  Yes\n\n```\n"
                    "9.  The window will display the case name and the case number.\n```\n")
        self.assertEqual(numbers(markdown), ([], 0, 0))


class LabelTest(unittest.TestCase):
    def test_label_values(self):
        self.assertEqual(CHECK.label_values("12"), {12})
        self.assertEqual(CHECK.label_values("c"), {3, 100})
        self.assertEqual(CHECK.label_values("iv"), {4})
        self.assertEqual(CHECK.label_values("aa"), {27})
        self.assertEqual(CHECK.label_values("2.10"), {10})


class MainTest(unittest.TestCase):
    def setUp(self):
        self.work = pathlib.Path(tempfile.mkdtemp())
        (self.work / "source.txt").write_text(EXPORT, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.work)

    def run_check(self, markdown):
        page = self.work / "page.md"
        page.write_text(markdown, encoding="utf-8")
        return CHECK.main(["check-list-numbers.py", str(page), str(self.work / "source.txt")])

    def test_exit_codes(self):
        self.assertEqual(self.run_check("3.  The user can launch Person Detail from any row.\n"), 0)
        self.assertEqual(self.run_check("1.  The user can launch Person Detail from any row.\n"), 2)
        self.assertEqual(CHECK.main(["check-list-numbers.py", str(self.work / "page.md"),
                                     str(self.work / "missing.txt")]), 1)
        self.assertEqual(CHECK.main(["check-list-numbers.py"]), 64)


if __name__ == "__main__":
    unittest.main()
