#!/usr/bin/env python3
"""Tests for merge_pin_pr.py, with gh, the clock and sleep stubbed."""
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_pin_pr  # noqa: E402

REPO = "owner/repo"
PIN_FILES = [".claude/att-docs.lock", ".claude/att-docs/plugins/general/skills/implement/SKILL.md"]
SETTLE_POLLS = merge_pin_pr.SETTLE_MINUTES * 60 // merge_pin_pr.POLL_SECONDS
PASSED = {"__typename": "CheckRun", "name": "check", "status": "COMPLETED",
          "conclusion": "SUCCESS"}
FAILED = {"__typename": "CheckRun", "name": "check", "status": "COMPLETED",
          "conclusion": "FAILURE"}
RUNNING = {"__typename": "CheckRun", "name": "check", "status": "IN_PROGRESS",
           "conclusion": ""}


def pull(**changes):
    base = {"state": "OPEN", "isDraft": False, "isCrossRepository": False, "baseRefName": "main",
            "title": "chore: bump Overmind pin to v0.24.3", "headRefOid": "abc",
            "paths": PIN_FILES, "statusCheckRollup": [PASSED], "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN"}
    base.update(changes)
    return base


SHOWN = {"state", "isDraft", "isCrossRepository", "baseRefName", "title", "headRefOid",
         "statusCheckRollup", "mergeable", "mergeStateStatus"}
LOCK_TEXT = "repo=merph518/Overmind\ntag=v0.24.3\ncommit=c1\ntree=t1\n"


def files_out(view):
    """The files endpoint's lines for a view: one JSON array per file, as the --jq gives."""
    rows = view.get("files") or [
        ["removed" if p in view.get("removed", []) else "modified", p, None]
        for p in view["paths"]]
    return "".join(json.dumps(row) + "\n" for row in rows)


class FakeGh:
    """Answers gh calls from a list of pull request views, one per view, the last repeating."""

    def __init__(self, views, merge_code=0, allowed=None, label_code=0, repo_code=0,
                 base_code=0):
        self.views = list(views)
        self.current = None
        self.merge_code = merge_code
        self.label_code = label_code
        self.repo_code = repo_code
        self.base_code = base_code
        self.allowed = allowed or {"mergeCommitAllowed": True, "squashMergeAllowed": True}
        self.calls = []

    def __call__(self, args):
        self.calls.append(args)
        if args[:2] == ["pr", "view"]:
            self.current = self.views.pop(0) if len(self.views) > 1 else self.views[0]
            return 0, json.dumps({k: v for k, v in self.current.items() if k in SHOWN}), ""
        if args[:2] == ["api", "--paginate"]:
            return 0, self.current.get("files_raw") or files_out(self.current), ""
        if args[:2] == ["repo", "view"] and "--jq" in args:
            return self.base_code, "" if self.base_code else "main\n", "no access"
        if args[0] == "api" and "/contents/" in args[1]:
            if args[1].endswith("?ref=main"):
                if self.current.get("first_pin"):
                    return 1, "", "gh: Not Found (HTTP 404)"
                return 0, LOCK_TEXT.replace("v0.24.3", "v0.24.2"), ""
            return (self.current.get("lock_code", 0), self.current.get("lock", LOCK_TEXT),
                    "bad gateway")
        if args[0] == "api" and "/commits/" in args[1]:
            return 0, self.current.get("tag_sha", "c1") + "\n", ""
        if args[0] == "api":
            return self.label_code, "", "" if self.label_code == 0 else "forbidden\n"
        if args[:2] == ["repo", "view"]:
            return self.repo_code, json.dumps(self.allowed), "" if not self.repo_code else "x"
        if args[:2] == ["pr", "merge"]:
            return self.merge_code, "", "" if self.merge_code == 0 else "merge blocked\n"
        return 0, "", ""

    def did(self, *prefix):
        return [c for c in self.calls if c[:len(prefix)] == list(prefix)]

    def labels(self):
        return [c for c in self.did("api") if c[1].endswith("/labels")]


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def run(gh, *args):
    out, err, clock = io.StringIO(), io.StringIO(), Clock()
    code = merge_pin_pr.main(["merge_pin_pr.py", *args], out, err, gh, clock, clock.sleep)
    return code, out.getvalue(), err.getvalue()


class PinOnly(unittest.TestCase):
    def test_lock_and_vendored_files_are_a_pin(self):
        self.assertEqual(merge_pin_pr.not_pin_only(pull()), "")

    def test_a_file_outside_the_pin_is_not(self):
        paths = PIN_FILES + [".claude/skills/implement/extension.json"]
        self.assertIn("outside the pin", merge_pin_pr.not_pin_only(pull(paths=paths)))

    def test_vendored_files_without_the_lock_are_not(self):
        self.assertIn("lock", merge_pin_pr.not_pin_only(pull(paths=PIN_FILES[1:])))

    def test_a_removed_lock_is_not(self):
        self.assertIn("removed", merge_pin_pr.not_pin_only(pull(removed=[PIN_FILES[0]])))

    def test_another_base_branch_is_not(self):
        self.assertIn("targets release",
                      merge_pin_pr.not_pin_only(pull(baseRefName="release"), "main"))

    def test_too_many_files_to_list_is_not(self):
        paths = [PIN_FILES[0]] + [".claude/att-docs/f%d" % i
                                  for i in range(merge_pin_pr.FILES_PAGE)]
        self.assertIn("more than GitHub lists", merge_pin_pr.not_pin_only(pull(paths=paths)))

    def test_a_branch_in_another_repository_is_not(self):
        self.assertIn("another repository",
                      merge_pin_pr.not_pin_only(pull(isCrossRepository=True)))

    def test_other_titles_drafts_and_closed_are_not(self):
        self.assertIn("title", merge_pin_pr.not_pin_only(pull(title="chore: bump eslint")))
        self.assertEqual(merge_pin_pr.not_pin_only(pull(isDraft=True)), "a draft")
        self.assertEqual(merge_pin_pr.not_pin_only(pull(state="MERGED")), "not open")

    def test_title_forms(self):
        for title in ("chore: Move the Overmind pin to v0.24.3",
                      "chore(deps): bump Overmind pin to 0.24.3"):
            self.assertEqual(merge_pin_pr.not_pin_only(pull(title=title)), "", title)


class Merge(unittest.TestCase):
    def test_passing_checks_merge_and_delete_the_branch(self):
        gh = FakeGh([pull()])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertEqual(out.split()[:3], ["merged", "owner/repo#5", "v0.24.3"])
        self.assertEqual(gh.did("pr", "merge"), [["pr", "merge", "5", "-R", REPO, "--merge",
                                                  "--delete-branch", "--match-head-commit",
                                                  "abc"]])
        self.assertEqual(len(gh.did("pr", "view")), 1 + SETTLE_POLLS)
        self.assertEqual(gh.did("pr", "comment"), [])

    def test_squash_when_merge_commits_are_off(self):
        gh = FakeGh([pull()], allowed={"squashMergeAllowed": True})
        run(gh, REPO, "5")
        self.assertIn("--squash", gh.did("pr", "merge")[0])

    def test_a_non_pin_change_is_left_for_review_untouched(self):
        gh = FakeGh([pull(paths=PIN_FILES + ["src/app.js"])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("review"))
        self.assertEqual({c[0] + " " + c[1] for c in gh.calls},
                         {"pr view", "api --paginate", "repo view"})

    def test_a_file_renamed_into_the_vendored_folder_is_seen(self):
        gh = FakeGh([pull(files=[["modified", PIN_FILES[0], None],
                                 ["renamed", ".claude/att-docs/ci.yml",
                                  ".github/workflows/ci.yml"]])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn(".github/workflows/ci.yml", out)

    def test_a_removed_lock_goes_to_review(self):
        code, out, _ = run(FakeGh([pull(removed=[PIN_FILES[0]])]), REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("the lock is removed", out)

    def test_a_lock_renamed_into_the_vendored_folder_goes_to_review(self):
        gh = FakeGh([pull(files=[["renamed", ".claude/att-docs/old.lock", PIN_FILES[0]]])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("removed or renamed", out)

    def test_a_file_name_with_a_newline_cannot_pass_for_the_lock(self):
        # The jq escapes the newline, so the name stays one line and the lock is unchanged.
        gh = FakeGh([pull(files=[["added", ".claude/att-docs/a\n" + PIN_FILES[0], None]])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("the lock is not changed", out)
        # Output split anywhere but between values does not parse, and nothing merges.
        raw = '["added", ".claude/att-docs/a\n.claude/att-docs.lock", null]\n'
        gh = FakeGh([pull(files_raw=raw)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("error"), out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_lock_naming_another_repository_goes_to_review(self):
        gh = FakeGh([pull(lock=LOCK_TEXT.replace("merph518/Overmind", "someone/Overmind"))])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("names someone/Overmind, not merph518/Overmind", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_lock_with_a_repeated_key_goes_to_review(self):
        gh = FakeGh([pull(lock="tag=v0.1.0\n" + LOCK_TEXT)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("repeats a key", out)

    def test_a_lock_key_with_a_space_goes_to_review(self):
        gh = FakeGh([pull(lock="repo =someone/x\n" + LOCK_TEXT)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("a key with a space", out)

    def test_a_first_pin_goes_to_review_without_a_flag(self):
        gh = FakeGh([pull(first_pin=True)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("first pin", out)
        self.assertEqual(gh.labels() + gh.did("pr", "comment") + gh.did("pr", "merge"), [])

    def test_a_lock_that_cannot_be_read_flags(self):
        gh = FakeGh([pull(lock_code=1)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("could not be read: bad gateway", out)
        self.assertEqual(len(gh.labels()), 1)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_lock_pinning_another_tag_goes_to_review(self):
        gh = FakeGh([pull(lock=LOCK_TEXT.replace("v0.24.3", "v0.24.2"))])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("the lock pins v0.24.2, not v0.24.3", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_lock_commit_the_tag_does_not_point_to_goes_to_review(self):
        gh = FakeGh([pull(tag_sha="c2")])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("not the one v0.24.3 points to", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_the_lock_is_read_at_the_head_commit(self):
        gh = FakeGh([pull()])
        run(gh, REPO, "5")
        reads = [c[1] for c in gh.did("api") if "/contents/" in c[1]]
        self.assertEqual(reads, ["repos/owner/repo/contents/.claude/att-docs.lock?ref=abc",
                                 "repos/owner/repo/contents/.claude/att-docs.lock?ref=main"])
        self.assertEqual([c[1] for c in gh.did("api") if "/commits/" in c[1]],
                         ["repos/merph518/Overmind/commits/v0.24.3"])

    def test_a_default_branch_that_cannot_be_read_stops(self):
        gh = FakeGh([pull()], base_code=1)
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("error"), out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_every_changed_file_is_read_past_the_first_hundred(self):
        vendored = [".claude/att-docs/f%03d" % i for i in range(150)]
        gh = FakeGh([pull(paths=[PIN_FILES[0], *vendored, "src/app.js"])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("src/app.js", out)

    def test_a_failing_check_flags_and_does_not_merge(self):
        gh = FakeGh([pull(statusCheckRollup=[PASSED, dict(FAILED, name="deb")])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("a check failed: deb", out)
        self.assertEqual(gh.did("pr", "merge"), [])
        self.assertEqual(len(gh.did("pr", "comment")), 1)
        self.assertEqual(gh.labels(), [["api", "repos/owner/repo/issues/5/labels", "-f",
                                        "labels[]=Manual Review Needed"]])

    def test_a_failing_status_context_flags(self):
        gh = FakeGh([pull(statusCheckRollup=[{"__typename": "StatusContext",
                                              "context": "ci/build", "state": "ERROR"}])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("ci/build", out)

    def test_running_checks_are_waited_for(self):
        gh = FakeGh([pull(statusCheckRollup=[RUNNING]), pull(statusCheckRollup=[RUNNING]),
                     pull()])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("merged"))
        self.assertEqual(len(gh.did("pr", "view")), 1 + SETTLE_POLLS)

    def test_a_new_head_waits_the_settle_time_again(self):
        late = [pull()] * (SETTLE_POLLS - 1)
        gh = FakeGh([*late, pull(headRefOid="def", statusCheckRollup=[]), pull(headRefOid="def")])
        code, _, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertEqual(len(gh.did("pr", "view")), SETTLE_POLLS + SETTLE_POLLS)
        self.assertEqual(gh.did("pr", "merge")[0][-1], "def")

    def test_a_fast_check_passing_does_not_skip_the_settle_time(self):
        gh = FakeGh([pull(), pull(statusCheckRollup=[PASSED, RUNNING]),
                     pull(statusCheckRollup=[PASSED, FAILED])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("a check failed", out)

    def test_checks_still_running_at_the_deadline_flag(self):
        gh = FakeGh([pull(statusCheckRollup=[RUNNING])])
        code, out, _ = run(gh, "--wait-minutes", "6", REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("after 6 minutes, checks still running", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_no_checks_waits_for_them_to_start(self):
        gh = FakeGh([pull(statusCheckRollup=[]), pull(statusCheckRollup=[RUNNING]), pull()])
        code, _, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertEqual(len(gh.did("pr", "view")), 1 + SETTLE_POLLS)

    def test_no_checks_at_all_merges_after_the_settle_time(self):
        gh = FakeGh([pull(statusCheckRollup=[])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("merged"))
        self.assertEqual(len(gh.did("pr", "view")), 1 + SETTLE_POLLS)

    def test_a_change_pushed_while_waiting_goes_to_review(self):
        gh = FakeGh([pull(statusCheckRollup=[RUNNING]), pull(paths=PIN_FILES + ["README.md"])])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 2)
        self.assertIn("README.md", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_conflict_flags(self):
        gh = FakeGh([pull(mergeable="CONFLICTING")])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("conflicts", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_branch_rule_still_blocking_at_the_deadline_flags(self):
        gh = FakeGh([pull(mergeStateStatus="BLOCKED")])
        code, out, _ = run(gh, "--wait-minutes", "10", REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("after 10 minutes, a branch rule blocks the merge", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_branch_rule_that_clears_is_waited_for(self):
        blocked = [pull(mergeStateStatus="BLOCKED")] * (SETTLE_POLLS + 3)
        gh = FakeGh([*blocked, pull()])
        code, _, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)
        self.assertEqual(len(gh.did("pr", "merge")), 1)

    def test_an_unknown_merge_state_is_waited_for(self):
        unknown = [pull(mergeable="UNKNOWN", mergeStateStatus="UNKNOWN")] * (SETTLE_POLLS + 2)
        gh = FakeGh([*unknown, pull()])
        code, _, _ = run(gh, REPO, "5")
        self.assertEqual(code, 0)

    def test_a_conflict_ends_the_wait_at_once(self):
        gh = FakeGh([pull(statusCheckRollup=[RUNNING], mergeable="CONFLICTING",
                          mergeStateStatus="DIRTY")])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("conflicts", out)
        self.assertEqual(len(gh.did("pr", "view")), 1)

    def test_a_dry_run_takes_any_wait(self):
        code, out, _ = run(FakeGh([pull()]), "--dry-run", "--wait-minutes", "0", REPO, "5")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("would-merge"), out)

    def test_a_wait_shorter_than_the_settle_time_is_refused(self):
        gh = FakeGh([pull()])
        code, _, err = run(gh, "--wait-minutes", "4", REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("usage", err)
        self.assertEqual(gh.calls, [])

    def test_a_new_head_near_the_deadline_names_the_settle_time(self):
        gh = FakeGh([*[pull(statusCheckRollup=[RUNNING])] * (SETTLE_POLLS - 2),
                     pull(headRefOid="def")])
        code, out, _ = run(gh, "--wait-minutes", "5", REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("after 5 minutes, the newest commit's checks had not had time", out)

    def test_a_conflict_is_named_over_a_branch_behind(self):
        gh = FakeGh([pull(mergeable="CONFLICTING", mergeStateStatus="BEHIND")])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("conflicts", out)

    def test_merge_methods_that_cannot_be_read_flag(self):
        gh = FakeGh([pull()], repo_code=1)
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("merge methods could not be read", out)
        self.assertEqual(gh.did("pr", "merge"), [])

    def test_a_full_page_of_checks_flags(self):
        gh = FakeGh([pull(statusCheckRollup=[PASSED] * merge_pin_pr.CHECKS_PAGE)])
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("100 or more checks", out)

    def test_a_read_failing_while_waiting_flags(self):
        calls = []

        def gh(args):
            calls.append(args)
            if args[:2] == ["pr", "view"] and len(calls) > 2:
                return 1, "", "rate limited"
            if args[:2] == ["pr", "view"]:
                return 0, json.dumps({k: v for k, v in pull(statusCheckRollup=[RUNNING]).items()
                                      if k in SHOWN}), ""
            if args[:2] == ["api", "--paginate"]:
                return 0, files_out(pull()), ""
            if args[:2] == ["repo", "view"]:
                return 0, "main\n", ""
            return 0, "", ""
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("could not be read while waiting", out)
        self.assertTrue(any(c[:2] == ["pr", "comment"] for c in calls))

    def test_bad_json_while_waiting_flags(self):
        gh = FakeGh([pull(statusCheckRollup=[RUNNING])])

        def broken(args):
            if args[:2] == ["pr", "view"] and gh.did("pr", "view"):
                gh.calls.append(args)
                return 0, "{truncated", ""
            return gh(args)
        code, out, _ = run(broken, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("could not be read while waiting", out)
        self.assertEqual(len(gh.labels()), 1)

    def test_a_refused_merge_flags(self):
        gh = FakeGh([pull()], merge_code=1)
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("merge was refused: merge blocked", out)
        self.assertEqual(len(gh.labels()), 1)

    def test_a_label_that_cannot_be_added_is_reported(self):
        gh = FakeGh([pull(statusCheckRollup=[FAILED])], label_code=1)
        code, out, _ = run(gh, REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("label could not be added: forbidden", out)

    def test_dry_run_writes_nothing_and_does_not_wait(self):
        for view, verdict in ((pull(), "would-merge"),
                              (pull(statusCheckRollup=[FAILED]), "would-flag"),
                              (pull(statusCheckRollup=[RUNNING]), "would-flag")):
            gh = FakeGh([view])
            _, out, _ = run(gh, "--dry-run", REPO, "5")
            self.assertTrue(out.startswith(verdict), out)
            self.assertEqual(gh.did("pr", "merge") + gh.did("pr", "comment") + gh.labels(), [])
            self.assertEqual(len(gh.did("pr", "view")), 1)

    def test_bad_arguments(self):
        for args in ([REPO], [REPO, "x"], ["repo", "5"], ["--wait-minutes", REPO, "5"]):
            code, _, err = run(FakeGh([pull()]), *args)
            self.assertEqual(code, 1, args)
            self.assertIn("usage", err)

    def test_an_unreadable_pull_request(self):
        code, out, err = run(lambda args: (1, "", "not found"), REPO, "5")
        self.assertEqual(code, 1)
        self.assertIn("could not read owner/repo#5", err)
        self.assertTrue(out.startswith("error  owner/repo#5  -  could not read"), out)


if __name__ == "__main__":
    unittest.main()
