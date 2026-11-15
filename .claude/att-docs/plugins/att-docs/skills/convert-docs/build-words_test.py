#!/usr/bin/env python3
"""Cases for build-words.py: the word list built from converted documents.

Run: python3 plugins/att-docs/skills/convert-docs/build-words_test.py
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")

SCRIPT = pathlib.Path(__file__).resolve().parent / "build-words.py"


class BuildWordsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.config = self.root / "extension.json"
        self.config.write_text(json.dumps(
            {"appsRoot": "apps", "words": "words.txt"}))
        (self.root / "apps" / "sub").mkdir(parents=True)
        self.dictionary = self.root / "dict.txt"
        self.dictionary.write_text("Worker\ncounty\nreport\nnot-alpha\nab\n")

    def run_script(self, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, env=env)

    def test_keeps_only_dictionary_words_used_in_docs(self):
        (self.root / "apps" / "a.md").write_text(
            "The WORKER opens a report. Zorblax too.\n")
        (self.root / "apps" / "sub" / "b.md").write_text("county county\n")
        (self.root / "apps" / "skip.txt").write_text("report extra\n")
        out = self.root / "words.txt"
        r = self.run_script("--config", str(self.config),
                            "--dictionary", str(self.dictionary))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out.read_text(), "county\nreport\nworker\n")
        self.assertIn("3 words", r.stdout)

    def test_explicit_docs_and_out(self):
        other = self.root / "other"
        other.mkdir()
        (other / "c.md").write_text("report\n")
        out = self.root / "custom.txt"
        r = self.run_script("--config", str(self.config), "--docs", str(other),
                            "--out", str(out),
                            "--dictionary", str(self.dictionary))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out.read_text(), "report\n")

    def test_missing_dictionary_exits_1(self):
        r = self.run_script("--config", str(self.config),
                            "--dictionary", str(self.root / "absent"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no system dictionary", r.stderr)
        self.assertFalse((self.root / "words.txt").exists())

    def test_missing_config_exits_64(self):
        r = self.run_script("--dictionary", str(self.dictionary))
        self.assertEqual(r.returncode, 64)
        self.assertIn("--config", r.stderr)


if __name__ == "__main__":
    unittest.main()
