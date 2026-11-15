#!/usr/bin/env python3
"""Cases for convert_config.py: reading the extension file and its fields.

Run: python3 plugins/att-docs/skills/convert-docs/convert_config_test.py
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import convert_config  # noqa: E402


def run_load(file, prog="t"):
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            return convert_config.load(file, prog), None, err.getvalue()
        except SystemExit as exit_:
            return None, exit_.code, err.getvalue()


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name).resolve()

    def repo(self, values):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "ext").mkdir()
        file = self.root / "ext" / "extension.json"
        file.write_text(json.dumps(values))
        return file

    def test_path_resolves_against_git_toplevel(self):
        file = self.repo({"appsRoot": "docs/apps", "sharePointHost": "https://h"})
        config, code, _ = run_load(str(file))
        self.assertIsNone(code)
        self.assertEqual(config.path("appsRoot"), self.root / "docs/apps")
        self.assertEqual(config.value("sharePointHost"), "https://h")

    def test_missing_field_exits_64(self):
        file = self.repo({"appsRoot": "x"})
        config, _, _ = run_load(str(file))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as c:
            config.value("words")
        self.assertEqual(c.exception.code, 64)
        self.assertIn("names no words", err.getvalue())

    def test_no_file_argument_exits_64(self):
        _, code, err = run_load(None)
        self.assertEqual(code, 64)
        self.assertIn("--config", err)

    def test_missing_file_exits_64(self):
        _, code, err = run_load(str(self.root / "none.json"))
        self.assertEqual(code, 64)
        self.assertIn("no config at", err)

    def test_invalid_json_exits_64(self):
        file = self.repo({})
        file.write_text("{nope")
        _, code, err = run_load(str(file))
        self.assertEqual(code, 64)
        self.assertIn("JSON", err)

    def test_non_object_exits_64(self):
        file = self.repo({})
        file.write_text("[1]")
        _, code, err = run_load(str(file))
        self.assertEqual(code, 64)
        self.assertIn("JSON object", err)

    def test_outside_git_work_tree_exits_64(self):
        # Ceiling stops git from finding a repository above the scratch dir.
        old = os.environ.get("GIT_CEILING_DIRECTORIES")
        os.environ["GIT_CEILING_DIRECTORIES"] = str(self.root.parent)
        self.addCleanup(
            lambda: os.environ.pop("GIT_CEILING_DIRECTORIES")
            if old is None else os.environ.__setitem__(
                "GIT_CEILING_DIRECTORIES", old))
        file = self.root / "extension.json"
        file.write_text("{}")
        _, code, err = run_load(str(file))
        self.assertEqual(code, 64)
        self.assertIn("git work tree", err)

    def test_script_prints_field(self):
        file = self.repo({"words": "docs/words.txt"})
        script = HERE / "convert_config.py"
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        ok = subprocess.run([sys.executable, str(script), str(file), "words"],
                            capture_output=True, text=True, env=env)
        self.assertEqual((ok.returncode, ok.stdout), (0, "docs/words.txt\n"))
        bad = subprocess.run([sys.executable, str(script), str(file), "nope"],
                             capture_output=True, text=True, env=env)
        self.assertEqual(bad.returncode, 64)


if __name__ == "__main__":
    unittest.main()
