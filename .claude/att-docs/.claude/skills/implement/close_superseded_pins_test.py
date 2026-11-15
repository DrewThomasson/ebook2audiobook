#!/usr/bin/env python3
"""Checks close_superseded_pins.py against a fake gh.

usage: python3 close_superseded_pins_test.py
"""
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import close_superseded_pins as cp  # noqa: E402

PULLS = [
    {"number": 10, "title": "chore: Move the Overmind pin to v0.24.0", "headRefName": "chore/a"},
    {"number": 11, "title": "chore: move the Overmind pin to v0.24.1", "headRefName": "chore/b"},
    {"number": 12, "title": "chore: Move the Overmind pin to v0.24.2", "headRefName": "chore/c"},
    {"number": 13, "title": "chore: Move the Overmind pin to v0.25.0", "headRefName": "chore/d"},
    {"number": 14, "title": "docs: explain how the pin works", "headRefName": "docs/pin"},
    {"number": 15, "title": "chore(deps): bump lodash from 4.17.20 to 4.17.21",
     "headRefName": "dependabot/x"},
    {"number": 16, "title": "feat: add pin to v0.1.0 of another tool", "headRefName": "feat/p"},
    {"number": 17, "title": 'Revert "chore: Move the Overmind pin to v0.24.0"',
     "headRefName": "revert/r"},
    {"number": 18, "title": "chore: Move the Overmind pin to v0.24.0-rc1", "headRefName": "chore/rc"},
]


class FakeGh:
    def __init__(self, pulls=PULLS, fail=(), fail_delete=()):
        self.pulls = pulls
        self.fail = set(fail)
        self.fail_delete = set(fail_delete)
        self.calls = []

    def __call__(self, args):
        self.calls.append(args)
        if args[:2] == ["pr", "list"]:
            return 0, json.dumps(self.pulls), ""
        if args[:2] == ["pr", "close"]:
            if int(args[2]) in self.fail:
                return 1, "", "cannot close"
            return 0, "", ""
        if args[:3] == ["api", "-X", "DELETE"]:
            if args[3].split("heads/", 1)[1] in self.fail_delete:
                return 1, "", "Branch is protected"
            return 0, "", ""
        raise AssertionError(args)

    def closed(self):
        return [int(c[2]) for c in self.calls if c[:2] == ["pr", "close"]]

    def deleted(self):
        return [c[3].split("heads/", 1)[1] for c in self.calls if c[:3] == ["api", "-X", "DELETE"]]


class Superseded(unittest.TestCase):
    def test_only_pin_pull_requests_for_an_earlier_version_are_picked(self):
        found = cp.superseded(PULLS, (0, 24, 2), 99)
        self.assertEqual([n for n, _, _ in found], [10, 11])
        self.assertEqual(found[0], (10, (0, 24, 0), "chore/a"))

    def test_the_new_pull_request_itself_is_never_picked(self):
        self.assertEqual(cp.superseded(PULLS, (0, 25, 0), 11),
                         [(10, (0, 24, 0), "chore/a"), (12, (0, 24, 2), "chore/c")])

    def test_versions_compare_as_numbers_not_text(self):
        pulls = [{"number": 1, "title": "chore: Move the Overmind pin to v0.9.0"},
                 {"number": 2, "title": "chore: Move the Overmind pin to v0.10.0"}]
        self.assertEqual([n for n, _, _ in cp.superseded(pulls, (0, 10, 0), 9)], [1])


class Closing(unittest.TestCase):
    def test_a_stale_older_pin_pr_is_closed_with_a_comment_and_its_branch_deleted(self):
        gh = FakeGh()
        lines, failed = cp.close_superseded("o/r", "v0.24.2", 12, gh=gh)
        self.assertEqual(failed, 0)
        self.assertEqual(gh.closed(), [10, 11])
        close = next(c for c in gh.calls if c[:3] == ["pr", "close", "10"])
        self.assertIn("Superseded by #12", close[close.index("--comment") + 1])
        self.assertIn("v0.24.2", close[close.index("--comment") + 1])
        self.assertEqual(gh.deleted(), ["chore/a", "chore/b"])
        self.assertEqual(lines, ["closed #10 (v0.24.0) in o/r", "closed #11 (v0.24.1) in o/r"])

    def test_a_pin_pr_for_the_same_or_a_newer_version_is_left_open(self):
        gh = FakeGh()
        cp.close_superseded("o/r", "v0.24.1", 11, gh=gh)
        self.assertEqual(gh.closed(), [10])
        self.assertNotIn(12, gh.closed())
        self.assertNotIn(13, gh.closed())

    def test_a_pull_request_that_is_not_a_pin_pr_is_left_open(self):
        new = {"number": 99, "title": "chore: Move the Overmind pin to v9.0.0", "headRefName": "n"}
        gh = FakeGh(pulls=PULLS + [new])
        cp.close_superseded("o/r", "v9.0.0", 99, gh=gh)
        self.assertEqual(gh.closed(), [10, 11, 12, 13])
        for other in (14, 15, 16, 17, 18, 99):
            self.assertNotIn(other, gh.closed())

    def test_a_new_pull_request_that_is_not_an_open_pin_for_the_tag_closes_nothing(self):
        for number, tag in ((99, "v0.24.2"), (12, "v0.25.0"), (14, "v0.24.2")):
            gh = FakeGh()
            with self.assertRaises(RuntimeError):
                cp.close_superseded("o/r", tag, number, gh=gh)
            self.assertEqual(gh.closed(), [])

    def test_a_failed_branch_delete_is_reported_after_the_close(self):
        gh = FakeGh(fail_delete=["chore/a"])
        lines, failed = cp.close_superseded("o/r", "v0.24.2", 12, gh=gh)
        self.assertEqual(failed, 1)
        self.assertEqual(gh.closed(), [10, 11])
        self.assertEqual(lines[0], "closed #10 (v0.24.0) in o/r")
        self.assertEqual(lines[1], "closed #10 but could not delete branch chore/a: "
                                   "Branch is protected")

    def test_a_branch_in_a_fork_is_not_deleted(self):
        pulls = [dict(p, isCrossRepository=p["number"] == 10) for p in PULLS]
        gh = FakeGh(pulls=pulls)
        cp.close_superseded("o/r", "v0.24.2", 12, gh=gh)
        self.assertEqual(gh.closed(), [10, 11])
        self.assertEqual(gh.deleted(), ["chore/b"])

    def test_dry_run_closes_nothing(self):
        gh = FakeGh()
        lines, failed = cp.close_superseded("o/r", "v0.24.2", 12, dry_run=True, gh=gh)
        self.assertEqual(gh.closed(), [])
        self.assertEqual(lines[0], "would close #10 (v0.24.0) in o/r")

    def test_a_failed_close_is_reported_and_the_others_still_go_ahead(self):
        gh = FakeGh(fail=[10])
        lines, failed = cp.close_superseded("o/r", "v0.24.2", 12, gh=gh)
        self.assertEqual(failed, 1)
        self.assertEqual(gh.closed(), [10, 11])
        self.assertEqual(lines[0], "could not close #10 in o/r: cannot close")
        self.assertEqual(gh.deleted(), ["chore/b"])

    def test_a_bad_tag_or_a_failed_list_raises(self):
        with self.assertRaises(ValueError):
            cp.close_superseded("o/r", "latest", 1, gh=FakeGh())
        with self.assertRaises(RuntimeError):
            cp.close_superseded("o/r", "v1.0.0", 1, gh=lambda args: (1, "", "no access"))


class Main(unittest.TestCase):
    def run_main(self, *args, gh=None):
        out, err = io.StringIO(), io.StringIO()
        code = cp.main(["close_superseded_pins.py", *args], out=out, err=err, gh=gh or FakeGh())
        return code, out.getvalue(), err.getvalue()

    def test_exit_codes_and_output(self):
        code, out, _ = self.run_main("o/r", "v0.24.2", "12")
        self.assertEqual((code, out.count("closed #")), (0, 2))
        code, out, _ = self.run_main("--dry-run", "o/r", "v0.24.2", "12")
        self.assertEqual((code, out.count("would close")), (0, 2))
        code, out, _ = self.run_main("o/r", "v0.24.0", "10")
        self.assertEqual((code, out.strip()), (0, "no older pin pull requests in o/r"))
        self.assertEqual(self.run_main("o/r", "v0.24.2", "99")[0], 1)
        self.assertEqual(self.run_main("o/r", "v0.24.2", "12", gh=FakeGh(fail=[10]))[0], 1)
        self.assertEqual(self.run_main("o/r", "v0.24.2")[0], 1)
        self.assertEqual(self.run_main("o/r", "v0.24.2", "x")[0], 1)
        self.assertEqual(self.run_main("not a repo", "v0.24.2", "1")[0], 1)
        self.assertEqual(self.run_main("o/r", "main", "1")[0], 1)


if __name__ == "__main__":
    unittest.main()
