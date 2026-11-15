#!/usr/bin/env python3
"""Cases for drift.py, which lists the tools and arguments that differ between the committed
Baton tool snapshot and a freshly built one. Each case writes two small snapshots into a
scratch folder and runs the script on them.

usage: python3 scripts/bridge-tools/drift_test.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "drift.py")

TOOLS = {
    "send": ["session", "text"],
    "read_issue": ["number", "repo"],
    "summary": [],
}


class DriftTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def snapshot(self, name, tools, source="abc"):
        path = os.path.join(self.dir.name, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"source": source, "tools": tools}, f)
        return path

    def run_script(self, committed, fresh):
        return subprocess.run([sys.executable, "-I", SCRIPT, committed, fresh],
                              capture_output=True, text=True)

    def compare(self, fresh_tools, committed_tools=None, **kwargs):
        base = TOOLS if committed_tools is None else committed_tools
        committed = self.snapshot("committed.json", base)
        fresh = self.snapshot("fresh.json", fresh_tools, **kwargs)
        return self.run_script(committed, fresh)

    def test_the_same_tools_print_nothing(self):
        r = self.compare(TOOLS)
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_a_different_source_with_the_same_tools_is_no_difference(self):
        r = self.compare(TOOLS, source="def")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_order_of_tools_and_arguments_does_not_matter(self):
        r = self.compare({"summary": [], "send": ["text", "session"],
                          "read_issue": ["repo", "number"]})
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_an_added_tool_is_named(self):
        r = self.compare({**TOOLS, "follow": ["session"]})
        self.assertEqual((r.returncode, r.stdout), (1, "tool follow: added\n"))

    def test_a_removed_tool_is_named(self):
        r = self.compare({"send": TOOLS["send"], "summary": []})
        self.assertEqual((r.returncode, r.stdout), (1, "tool read_issue: removed\n"))

    def test_added_and_removed_arguments_are_named_with_their_tool(self):
        r = self.compare({**TOOLS, "send": ["anyway", "text"],
                          "read_issue": ["number", "repo", "state"]})
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.splitlines(), [
            "tool read_issue: argument state added",
            "tool send: argument anyway added",
            "tool send: argument session removed",
        ])

    def test_a_tool_that_gains_its_first_argument_is_reported(self):
        r = self.compare({**TOOLS, "summary": ["session"]})
        self.assertEqual((r.returncode, r.stdout), (1, "tool summary: argument session added\n"))

    def test_an_empty_fresh_list_reports_every_tool_removed(self):
        r = self.compare({})
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.splitlines(),
                         ["tool read_issue: removed", "tool send: removed",
                          "tool summary: removed"])

    def test_a_long_difference_is_cut_with_a_count(self):
        many = {f"tool_{i:03d}": [] for i in range(60)}
        r = self.compare(many, committed_tools={})
        lines = r.stdout.splitlines()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(lines), 51)
        self.assertEqual(lines[0], "tool tool_000: added")
        self.assertEqual(lines[-1], "and 10 more")

    def test_a_missing_file_is_exit_2(self):
        fresh = self.snapshot("fresh.json", TOOLS)
        r = self.run_script(os.path.join(self.dir.name, "none.json"), fresh)
        self.assertEqual(r.returncode, 2)
        self.assertIn("cannot read a snapshot", r.stderr)

    def test_malformed_snapshots_are_exit_2(self):
        good = self.snapshot("good.json", TOOLS)
        bad_text = os.path.join(self.dir.name, "bad.json")
        with open(bad_text, "w", encoding="utf-8") as f:
            f.write("{ not json")
        no_tools = os.path.join(self.dir.name, "no-tools.json")
        with open(no_tools, "w", encoding="utf-8") as f:
            json.dump({"source": "abc"}, f)
        bad_shape = self.snapshot("bad-shape.json", {"send": "text"})
        for bad in (bad_text, no_tools, bad_shape):
            for pair in ((good, bad), (bad, good)):
                r = self.run_script(*pair)
                self.assertEqual(r.returncode, 2, (pair, r.stdout, r.stderr))
                self.assertEqual(r.stdout, "")


if __name__ == "__main__":
    unittest.main()
