#!/usr/bin/env python3
"""Cases for check-doc-credentials.py: which lines hold a password value."""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "check-doc-credentials.py"
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("check_doc_credentials", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

# Made-up values in the shapes a converted document carries.
SECRET = [
    "- FTP password: Xq7!pass",
    "- FTP password - Xq7pass",
    "- FTP password: Xq7!pass (changed yearly)",
    "**Password:** hunter2",
    "| Password | Xq7!pass |",
    "| FTP password: | Xq7pass |",
    "Server=db;Uid=app;Pwd=Xq7pass;",
    'connect("Password=Xq7pass")',
    "passwd: s3cret",
    "- FTP password: P@ss$word1",
    "Server=db;Pwd=Xq7(pass;",
    "connect with password='Xq7pass'",
    'x.Password = "Xq7pass"',
    "Password - reset by the admin; new password: Xq7pass",
]

CLEAN = [
    "- FTP password: (held by the noisy alerts support team)",
    "- FTP password: <password>",
    "| Password | If the password field is empty, the user sees an error |",
    "| Reset Password | Button |",
    "| Password | Text Field |",
    "| Password | 20 |",
    "Password: Required",
    "Password: Case-sensitive, 8 to 20 characters",
    "Password: 8-20 characters",
    "Password: n/a",
    "Password: e.g. the user's choice",
    "Password: ********",
    "Password: ••••••",
    "x.Password = ConfigurationManager.AppSettings(\"WMS.Password\")",
    "Password: https://example.gov/reset",
    "pwd: /opt/conn/alert",
    "Pwd=$DB_PASSWORD;",
    "Pwd=%PWD%;",
    "password: {{ secret }}",
    "The user enters a password-protected file.",
    "Password",
]


class Hits(unittest.TestCase):
    def test_secret_lines_are_reported(self):
        for line in SECRET:
            with self.subTest(line=line):
                self.assertTrue(CHECK.hits(line))

    def test_clean_lines_pass(self):
        for line in CLEAN:
            with self.subTest(line=line):
                self.assertEqual(CHECK.hits(line), [])


class Report(unittest.TestCase):
    def run_check(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True)

    def test_hit_names_the_line_but_never_the_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = pathlib.Path(tmp, "setup.md")
            page.write_text("# Setup\n\n- FTP password: Xq7!pass\n")
            result = self.run_check(tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("setup.md:3:", result.stdout)
        self.assertNotIn("Xq7!pass", result.stdout + result.stderr)

    def test_clean_tree_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            pathlib.Path(tmp, "a.md").write_text("Password: Required\n")
            self.assertEqual(self.run_check(tmp).returncode, 0)

    def test_missing_path_is_an_error(self):
        result = self.run_check("no/such/folder")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no such file or directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
