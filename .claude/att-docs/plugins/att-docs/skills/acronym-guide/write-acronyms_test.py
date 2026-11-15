#!/usr/bin/env python3
"""Cases for write-acronyms.py: the dictionary page renders whole from the
dictionary and the pending list, and --check reports a page that is behind.

Run: python3 plugins/att-docs/skills/acronym-guide/write-acronyms_test.py
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "write-acronyms.py"
os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

TERMS = (
    "# comment\n"
    "ZED\tZed Expansion\t*\tdocs/guide/Zed Notes.md\n"
    "ABC\tAlpha | Beta\t*\tdocs/a.md\n"
    "QQ\tQuiet Question\t*\tasked Pat\n"
    "RT\tRoot Thing\t*\tREADME.md\n"
    "STD\tStandard Thing\t*\tstandard technical term\n"
    "SRC\tCode Thing\t*\tsrc/app.cs\n"
    "NAR\tNarrow Reading\tdocs/x/*\tdocs/a.md\n"
)


class WriteAcronyms(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.page = self.root / "docs" / "Acronyms.md"
        self.write_config({})
        (self.root / "terms.tsv").write_text(TERMS, encoding="utf-8")
        (self.root / "unknown.txt").write_text("# c\nPEND\nAAA\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def write_config(self, extra):
        data = {
            "terms": "terms.tsv", "unknown": "unknown.txt",
            "page": "docs/Acronyms.md", "docsRoot": "docs",
            "rootDocs": ["README.md"], "preamble": ["# Acronyms", "", "Intro."],
        }
        data.update(extra)
        (self.root / "extension.json").write_text(json.dumps(data))

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.root / "extension.json"), *args],
            capture_output=True, text=True, env=ENV, cwd=self.root,
        )

    def test_writes_page_with_all_three_tables(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "docs/Acronyms.md: written")
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Acronyms\n\nIntro.\n\n| Acronym | Stands for | Stated in |"))
        self.assertTrue(text.endswith("\n"))
        lines = text.splitlines()
        # Sorted by acronym; pipes escaped; sources rendered by kind.
        start = lines.index("| Acronym | Stands for | Stated in |") + 2
        general = lines[start:lines.index("", start)]
        self.assertEqual([l.split(" | ")[0] for l in general],
                         ["| ABC", "| QQ", "| RT", "| SRC", "| STD", "| ZED"])
        self.assertIn(r"| ABC | Alpha \| Beta | [a.md](a.md) |", lines)
        self.assertIn("| QQ | Quiet Question | no document in here states it |", lines)
        self.assertIn("| RT | Root Thing | `README.md` |", lines)
        self.assertIn("| SRC | Code Thing | `src/app.cs` |", lines)
        self.assertIn("| STD | Standard Thing | standard technical term |", lines)
        self.assertIn("| ZED | Zed Expansion | [guide/Zed Notes.md](guide/Zed%20Notes.md) |", lines)
        self.assertIn("## Short forms that mean something narrower in one place", text)
        self.assertIn("| NAR | Narrow Reading | `docs/x/*` | [a.md](a.md) |", lines)
        self.assertIn("## Short forms with no expansion on record", text)
        pending = lines[lines.index("| Acronym |") + 2:]
        self.assertEqual(pending, ["| AAA |", "| PEND |"])

    def test_omits_scoped_and_pending_sections_when_empty(self):
        (self.root / "terms.tsv").write_text("ABC\tAlpha\t*\tdocs/a.md\n", encoding="utf-8")
        (self.root / "unknown.txt").unlink()
        self.assertEqual(self.run_script().returncode, 0)
        text = self.page.read_text(encoding="utf-8")
        self.assertNotIn("narrower", text)
        self.assertNotIn("no expansion on record", text)

    def test_second_run_is_already_current(self):
        self.run_script()
        before = self.page.read_text(encoding="utf-8")
        r = self.run_script()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "docs/Acronyms.md: already current")
        self.assertEqual(self.page.read_text(encoding="utf-8"), before)

    def test_check_passes_on_current_page_and_fails_on_missing_or_edited(self):
        r = self.run_script("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("docs/Acronyms.md does not match the dictionary.", r.stdout)
        self.assertFalse(self.page.exists())
        self.run_script()
        self.assertEqual(self.run_script("--check").returncode, 0)
        self.page.write_text(self.page.read_text(encoding="utf-8") + "hand edit\n", encoding="utf-8")
        self.assertEqual(self.run_script("--check").returncode, 1)

    def test_write_undoes_a_hand_edit(self):
        self.run_script()
        good = self.page.read_text(encoding="utf-8")
        self.page.write_text("hand edit\n", encoding="utf-8")
        self.run_script()
        self.assertEqual(self.page.read_text(encoding="utf-8"), good)

    def test_check_goes_stale_when_a_row_is_added(self):
        self.run_script()
        with open(self.root / "terms.tsv", "a", encoding="utf-8") as handle:
            handle.write("NEW\tNew Word\t*\tdocs/a.md\n")
        self.assertEqual(self.run_script("--check").returncode, 1)

    def test_page_in_new_folder_is_created(self):
        self.write_config({"page": "out/deep/Acronyms.md"})
        self.assertEqual(self.run_script().returncode, 0)
        self.assertTrue((self.root / "out/deep/Acronyms.md").is_file())

    def test_config_without_page_exits_2(self):
        data = json.loads((self.root / "extension.json").read_text())
        del data["page"]
        (self.root / "extension.json").write_text(json.dumps(data))
        r = self.run_script()
        self.assertEqual(r.returncode, 2)
        self.assertIn("names no page", r.stderr)

    def test_missing_config_exits_64(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(self.root / "nope.json")],
            capture_output=True, text=True, env=ENV,
        )
        self.assertEqual(r.returncode, 64)
        self.assertIn("does not exist", r.stderr)


if __name__ == "__main__":
    unittest.main()
