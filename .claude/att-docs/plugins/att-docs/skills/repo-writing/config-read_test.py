#!/usr/bin/env python3
"""Cases for config-read.py: how each kind of config value prints, the defaults,
and the exit codes for a missing, malformed, or non-object config.

Run: python3 plugins/att-docs/skills/repo-writing/config-read_test.py
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent / "config-read.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


class ConfigReadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = pathlib.Path(self.tmp.name) / "config.json"

    def run_reader(self, *args, text=None):
        if text is not None:
            self.path.write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, env=ENV,
        )

    def values(self, data, *keys):
        done = self.run_reader(str(self.path), *keys, text=json.dumps(data))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(done.stdout == "" or done.stdout.endswith("\0"))
        return done.stdout.split("\0")[:-1]

    def test_string_and_nested_key(self):
        self.assertEqual(self.values({"a": "x", "b": {"c": "y"}}, "a", "b.c"), ["x", "y"])

    def test_array_of_strings_joins_with_pipe(self):
        self.assertEqual(self.values({"p": ["one", "two", "3"]}, "p"), ["one|two|3"])

    def test_array_of_objects_one_tab_line_each(self):
        data = {"e": [{"path": "docs/", "except": "keep"}, {"path": "x/"}]}
        self.assertEqual(self.values(data, "e"), ["docs/\tkeep\nx/\t"])

    def test_bool_prints_lowercase(self):
        self.assertEqual(self.values({"t": True, "f": False}, "t", "f"), ["true", "false"])

    def test_missing_value_uses_default_or_empty(self):
        out = self.values({"a": "x"}, "nope=main", "nope", "a.deep=d", "a")
        self.assertEqual(out, ["main", "", "d", "x"])

    def test_present_value_ignores_default(self):
        self.assertEqual(self.values({"a": "x"}, "a=zzz"), ["x"])

    def test_no_arguments_prints_usage_and_exits_64(self):
        done = self.run_reader()
        self.assertEqual(done.returncode, 64)
        self.assertIn("usage", done.stderr)

    def test_missing_file_exits_2(self):
        done = self.run_reader(str(self.path) + ".absent", "a")
        self.assertEqual(done.returncode, 2)
        self.assertEqual(done.stdout, "")

    def test_invalid_json_exits_2(self):
        self.assertEqual(self.run_reader(str(self.path), "a", text="{not json").returncode, 2)

    def test_non_object_json_exits_2(self):
        self.assertEqual(self.run_reader(str(self.path), "a", text='["a"]').returncode, 2)


if __name__ == "__main__":
    unittest.main()
