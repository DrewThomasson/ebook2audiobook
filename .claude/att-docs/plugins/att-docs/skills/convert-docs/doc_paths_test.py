#!/usr/bin/env python3
"""Cases for doc_paths.py: hyphenated file names and Markdown discovery.

Run: python3 plugins/att-docs/skills/convert-docs/doc_paths_test.py
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import doc_paths  # noqa: E402


class HyphenatedTest(unittest.TestCase):
    def test_spaced_dash_collapses(self):
        self.assertEqual(
            doc_paths.hyphenated("ACT 4.0 - Activity Entry.docx"),
            "ACT-4.0-Activity-Entry.docx")

    def test_name_without_space_is_unchanged(self):
        self.assertEqual(doc_paths.hyphenated("a-b_c.docx"), "a-b_c.docx")

    def test_hyphen_before_extension_dropped(self):
        self.assertEqual(doc_paths.hyphenated("Plan -.docx"), "Plan.docx")

    def test_space_run_becomes_one_hyphen(self):
        self.assertEqual(doc_paths.hyphenated("A   B.md"), "A-B.md")


class MarkdownUnderTest(unittest.TestCase):
    def test_walks_directories_and_takes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "sub").mkdir()
            (root / "a.md").write_text("a")
            (root / "sub" / "b.md").write_text("b")
            (root / "sub" / "c.txt").write_text("c")
            lone = root / "sub" / "c.txt"
            got = doc_paths.markdown_under([str(root), str(lone)])
            self.assertEqual(got, [root / "a.md", root / "sub" / "b.md", lone])

    def test_missing_path_exits_with_message(self):
        with self.assertRaises(SystemExit) as ctx:
            doc_paths.markdown_under(["/nonexistent-dir-xyz"])
        self.assertIn("no such file or directory", str(ctx.exception.code))


if __name__ == "__main__":
    unittest.main()
