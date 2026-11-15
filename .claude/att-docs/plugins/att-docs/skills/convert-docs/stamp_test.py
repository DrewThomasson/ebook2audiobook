#!/usr/bin/env python3
"""Cases for stamp.clean: what it takes off Pandoc's output."""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("stamp", HERE / "stamp.py")
STAMP = importlib.util.module_from_spec(SPEC)
# Its dataclasses look their module up by name while the module loads.
sys.modules["stamp"] = STAMP
SPEC.loader.exec_module(STAMP)


class BulletGlyphTest(unittest.TestCase):
    def test_a_glyph_a_slide_drew_goes(self):
        self.assertEqual(STAMP.clean("- • First point\n"), "- First point\n")
        self.assertEqual(STAMP.clean("- o Second point\n"), "- Second point\n")

    def test_a_word_opening_with_o_keeps_its_o(self):
        text = "1.  open the To-Do Detail window\n- one row for each child\n- only this\n"
        self.assertEqual(STAMP.clean(text), text)

    def test_a_bare_o_or_one_before_a_tab_goes(self):
        self.assertEqual(STAMP.clean("text\n- o\n- next\n"), "text\n-\n- next\n")
        self.assertEqual(STAMP.clean("- o\tThird point\n"), "- Third point\n")

    def test_of_and_or_keep_their_o(self):
        text = "- of the stage\n- or the case\n"
        self.assertEqual(STAMP.clean(text), text)


if __name__ == "__main__":
    unittest.main()
