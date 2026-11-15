import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recap  # noqa: E402

PRS_MERGED = [
    # 11:30 PM Eastern on Oct 28 (03:30 UTC Oct 29): not Oct 29
    {"number": 1, "title": "Late yesterday", "mergedAt": "2026-10-29T03:30:00Z"},
    # 12:10 AM Eastern Oct 29 (04:10 UTC)
    {"number": 2, "title": "Just after midnight", "mergedAt": "2026-10-29T04:10:00Z"},
    {"number": 3, "title": "Afternoon", "mergedAt": "2026-10-29T19:30:00Z"},
    # 8:15 PM Eastern Oct 29 (00:15 UTC Oct 30): still Oct 29
    {"number": 4, "title": "Evening", "mergedAt": "2026-10-30T00:15:00Z"},
    # 12:30 AM Eastern Oct 30 (04:30 UTC): tomorrow
    {"number": 5, "title": "Tomorrow", "mergedAt": "2026-10-30T04:30:00Z"},
]
OPEN = [
    {"number": 10, "title": "Ready", "labels": [{"name": "Manual Review Needed"}],
     "mergeable": "MERGEABLE", "isDraft": False},
    {"number": 11, "title": "Conflicted", "labels": [{"name": "Manual Review Needed"}],
     "mergeable": "CONFLICTING", "isDraft": False},
    {"number": 12, "title": "No label", "labels": [], "mergeable": "MERGEABLE",
     "isDraft": False},
]


def fake_gh(actions=True):
    def gh(args):
        if args[:2] == ["pr", "list"] and "merged" in args:
            return PRS_MERGED
        if args[:2] == ["pr", "list"]:
            return OPEN
        if args[:2] == ["issue", "list"]:
            return [{"number": 20, "title": "Working"}]
        if args[:2] == ["run", "list"]:
            if not actions:
                raise recap.GhError("Actions disabled")
            return [{"databaseId": 1, "name": "ci", "createdAt": "2026-10-29T15:00:00Z"},
                    {"databaseId": 2, "name": "old", "createdAt": "2026-10-29T02:00:00Z"}]
        raise AssertionError(args)
    return gh


def run_main(argv, gh=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = recap.main(argv, gh or fake_gh())
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class RecapTest(unittest.TestCase):
    def report(self, **kw):
        return recap.build(["o/Repo"], "2026-10-29", recap.DEFAULT_REVIEW,
                           recap.DEFAULT_PROGRESS, fake_gh(**kw))

    def test_merged_filters_eastern_date(self):
        r = self.report()["repos"][0]
        self.assertEqual([m["number"] for m in r["merged"]], [2, 3, 4])
        self.assertEqual(r["merged"][1]["time"], "3:30 PM")

    def test_open_sections(self):
        r = self.report()["repos"][0]
        self.assertEqual([p["number"] for p in r["waiting_review"]], [10, 11])
        self.assertEqual([p["number"] for p in r["ready_to_merge"]], [10])
        self.assertEqual(len(r["in_progress"]), 1)
        self.assertEqual([f["name"] for f in r["failed_runs"]], ["ci"])
        self.assertEqual(r["failed_runs"][0]["time"], "11:00 AM")

    def test_no_actions(self):
        r = self.report(actions=False)["repos"][0]
        self.assertEqual(r["failed_runs"], [])

    def test_text(self):
        code, out, _ = run_main(["--repo", "o/Repo", "--date", "2026-10-29"])
        self.assertEqual(code, 0)
        self.assertIn("Merged today:", out)
        self.assertIn("#3 Afternoon (3:30 PM)", out)
        self.assertIn("Needs you: ready to merge:", out)

    def test_json(self):
        code, out, _ = run_main(["--repo", "o/Repo", "--date", "2026-10-29",
                                 "--format", "json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["repos"][0]["repo"], "o/Repo")

    def test_spoken(self):
        code, out, _ = run_main(["--repo", "o/Repo", "--date", "2026-10-29",
                                 "--format", "spoken"])
        self.assertEqual(code, 0)
        self.assertIn("Three pull requests merged in Repo.", out)
        self.assertIn("Two pull requests wait on your review.", out)
        self.assertIn("One is ready to merge.", out)
        self.assertNotIn("more than", out)
        self.assertFalse(re.search(r"\d", out), out)

    def test_queries_cover_whole_eastern_day(self):
        calls = []

        def gh(args):
            calls.append(args)
            return fake_gh()(args)
        recap.build(["o/Repo"], "2026-10-29", "Review", "Doing", gh)
        merged = next(c for c in calls if "merged" in c)
        self.assertIn("merged:2026-10-29..2026-10-30", merged)
        runs = next(c for c in calls if c[:2] == ["run", "list"])
        self.assertEqual(runs[runs.index("--created") + 1], "2026-10-29..2026-10-30")
        open_prs = next(c for c in calls if c[:2] == ["pr", "list"] and "open" in c)
        self.assertEqual(open_prs[open_prs.index("--label") + 1], "Review")
        issues = next(c for c in calls if c[:2] == ["issue", "list"])
        self.assertEqual(issues[issues.index("--label") + 1], "Doing")
        for c in calls:
            self.assertEqual(c[c.index("--limit") + 1], str(recap.LIMIT))

    def test_cap_is_reported(self):
        many = [{"number": n, "title": "Issue %d" % n} for n in range(recap.LIMIT)]

        def gh(args):
            if args[:2] == ["issue", "list"]:
                return many
            return fake_gh()(args)
        code, out, _ = run_main(["--repo", "o/Repo", "--date", "2026-10-29"], gh)
        self.assertEqual(code, 0)
        self.assertIn("Issues in progress:  (GitHub listed 100; there may be more)", out)
        self.assertNotIn("Merged today:  (", out)
        code, out, _ = run_main(["--repo", "o/Repo", "--date", "2026-10-29",
                                 "--format", "spoken"], gh)
        self.assertIn("Repo has more than the recap could list", out)
        self.assertIn("100 issues are in progress.", out)

    def test_config(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "extension.json")
            with open(p, "w") as f:
                json.dump({"repos": ["o/A", "o/B"]}, f)
            code, out, _ = run_main(["--config", p, "--format", "spoken",
                                     "--date", "2026-10-29"])
        self.assertEqual(code, 0)
        self.assertIn("in A", out)
        self.assertIn("in B", out)

    def test_missing_config_exits_64(self):
        code, _, err = run_main(["--config", "/nonexistent/extension.json"])
        self.assertEqual(code, 64)
        self.assertIn("config", err)

    def test_no_repos_exits_64(self):
        self.assertEqual(run_main([])[0], 64)


if __name__ == "__main__":
    unittest.main()
