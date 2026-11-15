#!/usr/bin/env python3
"""Cases for verify-terms.py: a dictionary row passes only when its cited file
states the expansion beside the acronym.

Run: python3 plugins/att-docs/skills/acronym-guide/verify-terms_test.py
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "verify-terms.py"
os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


class VerifyTerms(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "docs").mkdir()
        (self.root / "extension.json").write_text(json.dumps({"terms": "terms.tsv"}))

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, terms, **docs):
        (self.root / "terms.tsv").write_text(terms, encoding="utf-8")
        for name, text in docs.items():
            (self.root / "docs" / name).write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.root / "extension.json")],
            capture_output=True, text=True, env=ENV, cwd=self.root,
        )

    def test_row_stated_in_parenthesis_passes(self):
        r = self.run_script(
            "ABC\tAlpha Beta Charlie\t*\tdocs/a.md\n",
            **{"a.md": "The Alpha Beta Charlie (ABC) process starts here.\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 row(s) checked against their source, 0 failed.", r.stdout)

    def test_case_ampersand_and_possessive_do_not_count(self):
        r = self.run_script(
            "RD\tResearch & Development\t*\tdocs/a.md\nPS\tParent's Share\t*\tdocs/a.md\n",
            **{"a.md": "| RD | research and development |\n\nPS stands for Parent's Share.\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_expansion_elsewhere_in_file_fails(self):
        filler = "word " * 100
        r = self.run_script(
            "ABC\tAlpha Beta Charlie\t*\tdocs/a.md\n",
            **{"a.md": f"ABC is used here.\n{filler}\nAlpha Beta Charlie is far away.\n"},
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn('ABC: docs/a.md does not state "Alpha Beta Charlie"', r.stdout)
        self.assertIn("1 failed", r.stdout)

    def test_wrong_expansion_fails_among_passing_rows(self):
        r = self.run_script(
            "ABC\tAlpha Beta Charlie\t*\tdocs/a.md\nXYZ\tWrong Words\t*\tdocs/a.md\n",
            **{"a.md": "Alpha Beta Charlie (ABC) and XYZ (Xray Yankee Zulu).\n"},
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn("XYZ:", r.stdout)
        self.assertNotIn("ABC:", r.stdout)
        self.assertIn("2 row(s) checked against their source, 1 failed.", r.stdout)

    def test_expansion_split_across_a_line_passes(self):
        r = self.run_script(
            "ABC\tAlpha Beta Charlie\t*\tdocs/a.md\n",
            **{"a.md": "Alpha Beta\nCharlie (ABC)\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_person_answered_rows_are_listed_not_checked(self):
        r = self.run_script(
            "QQ\tQuiet Question\t*\tasked Pat\n"
            "UU\tUrl Unit\t*\thttps://example.com/glossary\n"
            "SS\tSlash Sentence\t*\tasked Pat and/or Sam\n"
            "NN\tNo Source\n",
            **{"a.md": "nothing\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Rows a person answered for", r.stdout)
        self.assertIn("QQ = Quiet Question (asked Pat)", r.stdout)
        self.assertIn("UU = Url Unit (https://example.com/glossary)", r.stdout)
        self.assertIn("SS = Slash Sentence (asked Pat and/or Sam)", r.stdout)
        self.assertIn("NN = No Source (no source)", r.stdout)
        self.assertIn("0 row(s) checked", r.stdout)

    def test_missing_markdown_source_fails_and_names_the_row(self):
        r = self.run_script(
            "ZZ\tZed Zed\t*\tdocs/missing.md\nAB\tAlpha Beta\t*\tdocs/a.md\n",
            **{"a.md": "AB (Alpha Beta)\n"},
        )
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ZZ: docs/missing.md does not exist", r.stdout)
        self.assertIn("1 row(s) checked against their source, 1 failed.", r.stdout)

    def test_markdown_path_with_spaces_is_still_a_path(self):
        r = self.run_script("ZZ\tZed Zed\t*\tdocs/Missing Doc.md\n")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ZZ: docs/Missing Doc.md does not exist", r.stdout)

    def test_missing_non_markdown_path_fails(self):
        r = self.run_script("ZZ\tZed Zed\t*\tsrc/data/codes.json\n")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ZZ: src/data/codes.json does not exist", r.stdout)

    def test_existing_non_markdown_path_is_answered_not_checked(self):
        r = self.run_script(
            "ZZ\tZed Zed\t*\tdocs/codes.json\n",
            **{"codes.json": "{}\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ZZ = Zed Zed (docs/codes.json)", r.stdout)
        self.assertIn("0 row(s) checked", r.stdout)

    def test_comments_and_blank_lines_are_skipped(self):
        r = self.run_script(
            "# comment\n\n   \nABC\tAlpha Beta Charlie\t*\tdocs/a.md\n",
            **{"a.md": "Alpha Beta Charlie (ABC)\n"},
        )
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 row(s) checked", r.stdout)

    def test_missing_config_exits_64(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.root / "nope.json")],
            capture_output=True, text=True, env=ENV,
        )
        self.assertEqual(r.returncode, 64)
        self.assertIn("does not exist", r.stderr)

    def test_no_arguments_exits_64(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=ENV)
        self.assertEqual(r.returncode, 64)
        self.assertIn("--config", r.stderr)


if __name__ == "__main__":
    unittest.main()
