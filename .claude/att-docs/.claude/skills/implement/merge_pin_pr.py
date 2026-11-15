#!/usr/bin/env python3
"""Merges a pin pull request in one repository once its checks pass, with no review.

usage: merge_pin_pr.py [--dry-run] [--wait-minutes <n, at least 5>] <owner/repo> <pr-number>

A pin pull request is an open, non-draft pull request from a branch in the same repository
into its default branch, titled "chore: <verb> the Overmind pin to v<major>.<minor>.<patch>",
whose every changed file, and every file a rename moved from, is the lock,
.claude/att-docs.lock, or a vendored file under .claude/att-docs/, and which changes the
lock without removing or renaming it. At the commit it merges, the lock must name the same
repository as the lock on the default branch, the title's tag, and the commit that tag
points to there, with no key repeated. Every
changed file is read, up to the FILES_PAGE that GitHub lists. Any other pull
request, one with any other file in its diff, or one with FILES_PAGE files or more, is left
for review: nothing is written and the exit code is 2.

For a pin pull request it waits up to --wait-minutes (60 by default, at least
SETTLE_MINUTES) for its checks. A
commit is given SETTLE_MINUTES from when it is first seen at the head for its checks to
start, so a pull request just opened or just pushed to is not merged ahead of them, and a
new head starts that time again. A branch rule that blocks the merge, or GitHub still
working out whether it merges, is waited on too, since a required check can register late.
When every check has passed, or none has started by then, it merges that commit only, with the repository's allowed method, a merge commit first,
then squash, then rebase, and deletes the branch.

A failing check, a wait still unfinished at the deadline (checks running, a branch rule
blocking it, or a merge state GitHub has not worked out), a conflict, a branch behind its
base that a rule requires up to date, CHECKS_PAGE checks or more, a pull request that cannot
be read while waiting, or a merge that is refused leaves the pull request open: it gets a comment saying why and the label Manual
Review Needed, so it shows as waiting on the owner, and the exit code is 1. With --dry-run
it judges the pull request as it stands, without waiting, and only says what it would do.

It prints one line, "<verdict>  <owner/repo>#<n>  <tag>  <reason>", with the verdict merged,
would-merge, flagged, would-flag, review, or error when the pull request could not be read
at the start, and exits 0 when it merged or would merge. gh must be signed in.
"""
import json
import re
import subprocess
import sys
import time

PIN_TITLE = re.compile(
    r"^chore(?:\([^)]*\))?:\s+\w+\s+(?:the\s+)?Overmind pin to (v?\d+\.\d+\.\d+)\s*$",
    re.IGNORECASE)
LOCK = ".claude/att-docs.lock"
VENDORED = ".claude/att-docs/"
REVIEW_LABEL = "Manual Review Needed"
FAILED = {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR",
          "STALE"}
PENDING = {"PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
# gh reads the first 100 checks of a pull request; a full page may hide more.
CHECKS_PAGE = 100
# GitHub lists at most 3000 changed files of a pull request.
FILES_PAGE = 3000
BLOCKS = {"DIRTY": "it conflicts with the base branch",
          "BEHIND": "it is behind the base branch, which a branch rule requires it not to be"}
POLL_SECONDS = 30
SETTLE_MINUTES = 5


def run_gh(args):
    """(exit code, stdout, stderr) of a gh command."""
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return 127, "", "gh is not installed"
    return done.returncode, done.stdout, done.stderr


def not_pin_only(pull, base=""):
    """Why the pull request is not a pin-only change, or "" when it is one. base is the
    repository's default branch, which the pull request must target when it is given."""
    if pull.get("state") != "OPEN":
        return "not open"
    if pull.get("isDraft"):
        return "a draft"
    if pull.get("isCrossRepository"):
        return "its branch is in another repository"
    if base and pull.get("baseRefName") != base:
        return "it targets %s, not %s" % (pull.get("baseRefName"), base)
    if not PIN_TITLE.match(pull.get("title") or ""):
        return "title is not a pin bump"
    paths = pull.get("paths") or []
    if len(paths) >= FILES_PAGE:
        return "it has %d or more changed files, more than GitHub lists" % FILES_PAGE
    if LOCK not in paths:
        return "the lock is not changed"
    if LOCK in (pull.get("removed") or []):
        return "the lock is removed or renamed"
    other = [p for p in paths if p != LOCK and not p.startswith(VENDORED)]
    if other:
        return "changes files outside the pin: %s" % ", ".join(sorted(other)[:5])
    return ""


def check_state(rollup):
    """("pass" | "fail" | "pending", names of the failing or pending checks) for a
    statusCheckRollup: a check run by status and conclusion, a status context by state."""
    failing, pending = [], []
    for check in rollup or []:
        name = check.get("name") or check.get("context") or "check"
        if check.get("__typename") == "StatusContext" or "state" in check:
            state = (check.get("state") or "").upper()
            if state in FAILED:
                failing.append(name)
            elif state in PENDING or not state:
                pending.append(name)
            continue
        if (check.get("status") or "").upper() != "COMPLETED":
            pending.append(name)
        elif (check.get("conclusion") or "").upper() in FAILED:
            failing.append(name)
    if failing:
        return "fail", failing
    if pending:
        return "pending", pending
    return "pass", []


def view(repo, number, gh):
    """The pull request, with "paths" holding every changed file and every file a rename
    moved from, and "removed" the files it deletes or renames away, read page by page. Each
    file comes as one JSON line, so no file name can pass for another."""
    code, out, err = gh(["pr", "view", str(number), "-R", repo, "--json",
                         "state,isDraft,isCrossRepository,baseRefName,title,headRefOid,"
                         "statusCheckRollup,mergeable,mergeStateStatus"])
    if code != 0:
        raise RuntimeError("could not read %s#%d: %s" % (repo, number, err.strip()))
    pull = json.loads(out)
    code, out, err = gh(["api", "--paginate", "repos/%s/pulls/%d/files" % (repo, number),
                         "--jq", ".[] | [.status, .filename, .previous_filename] | tojson"])
    if code != 0:
        raise RuntimeError("could not list the files of %s#%d: %s"
                           % (repo, number, err.strip()))
    try:
        files = [json.loads(line) for line in out.split("\n") if line.strip()]
    except ValueError as error:
        raise RuntimeError("could not read the files of %s#%d: %s" % (repo, number, error))
    pull["paths"] = [name for _, name, _ in files] + [old for _, _, old in files if old]
    pull["removed"] = ([name for status, name, _ in files if status == "removed"]
                       + [old for _, _, old in files if old])
    return pull


def default_branch(repo, gh):
    """The repository's default branch, or raises RuntimeError when it cannot be read."""
    code, out, err = gh(["repo", "view", repo, "--json", "defaultBranchRef",
                         "--jq", ".defaultBranchRef.name"])
    if code != 0 or not out.strip():
        raise RuntimeError("could not read the default branch of %s: %s" % (repo, err.strip()))
    return out.strip()


def read_lock(repo, ref, gh):
    """The lock at ref as {key: value}, None when ref has no lock, or raises RuntimeError
    when it cannot be read, and ValueError when a key repeats or holds a space, since a
    reader that trims keys or takes the first would see another pin."""
    code, out, err = gh(["api", "repos/%s/contents/%s?ref=%s" % (repo, LOCK, ref),
                         "-H", "Accept: application/vnd.github.raw"])
    if code != 0 and "404" in err:
        return None
    if code != 0:
        raise RuntimeError("the lock at %s could not be read: %s" % (ref, err.strip()))
    pairs = [line.split("=", 1) for line in out.splitlines() if "=" in line]
    lock = dict(pairs)
    if len(lock) != len(pairs) or any(re.search(r"\s", key) for key in lock):
        raise ValueError("the lock at %s repeats a key or has a key with a space" % ref)
    return lock


def lock_mismatch(repo, head, base, tag, gh):
    """(reason to flag or "", reason to leave for review or "") for the lock at commit head:
    it must name the same repository as the lock on base, the tag, and the commit the tag
    points to there. A read that fails is flagged; a lock that differs goes to review."""
    try:
        lock = read_lock(repo, head, gh)
        was = read_lock(repo, base, gh)
    except RuntimeError as error:
        return str(error), ""
    except ValueError as error:
        return "", str(error)
    if lock is None:
        return "the lock at %s could not be found" % head, ""
    if was is None:
        return "", "the default branch has no lock, so this is a first pin"
    if lock.get("tag", "").lstrip("v") != tag.lstrip("v"):
        return "", "the lock pins %s, not %s" % (lock.get("tag") or "no tag", tag)
    if not lock.get("repo") or lock.get("repo") != was.get("repo"):
        return "", "the lock names %s, not %s as before" % (lock.get("repo") or "no repository",
                                                           was.get("repo") or "nothing")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", lock["repo"]):
        return "", "the lock names no repository"
    code, out, err = gh(["api", "repos/%s/commits/%s" % (lock["repo"], lock["tag"]),
                         "--jq", ".sha"])
    if code != 0:
        return "the tag %s could not be read in %s: %s" % (lock["tag"], lock["repo"],
                                                          err.strip()), ""
    if out.strip() != lock.get("commit"):
        return "", "the lock's commit is not the one %s points to" % lock["tag"]
    return "", ""


def merge_method(repo, gh):
    """The merge flag for the repository's first allowed method, a merge commit first, or
    raises RuntimeError when the methods cannot be read."""
    code, out, err = gh(["repo", "view", repo, "--json",
                         "mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed"])
    if code != 0:
        raise RuntimeError("its merge methods could not be read: %s" % err.strip())
    allowed = json.loads(out or "{}")
    for key, method in (("mergeCommitAllowed", "--merge"), ("squashMergeAllowed", "--squash"),
                        ("rebaseMergeAllowed", "--rebase")):
        if allowed.get(key):
            return method
    return "--merge"


def flag(repo, number, reason, gh):
    """Leaves the pull request open for the owner with a comment and the review label, and
    returns the reason, with any write that failed added to it."""
    failed = []
    code, _, err = gh(["pr", "comment", str(number), "-R", repo, "--body",
                       "Not merged automatically: %s. This pin pull request waits for review."
                       % reason])
    if code != 0:
        failed.append("the comment could not be added: %s" % err.strip())
    code, _, err = gh(["api", "repos/%s/issues/%d/labels" % (repo, number),
                       "-f", "labels[]=%s" % REVIEW_LABEL])
    if code != 0:
        failed.append("the %s label could not be added: %s" % (REVIEW_LABEL, err.strip()))
    return "; ".join([reason, *failed])


def wait_for_checks(repo, number, pull, base, wait_minutes, gh, clock, sleep, settle=True):
    """Polls until the head's checks pass and GitHub lets it merge, a check fails, or the
    deadline passes. Returns (pull, reason to flag or "", reason to leave for review or "")."""
    deadline = clock() + wait_minutes * 60
    head, seen = pull.get("headRefOid"), clock()
    while True:
        if pull.get("headRefOid") != head:
            head, seen = pull.get("headRefOid"), clock()
        rollup = pull.get("statusCheckRollup") or []
        state, names = check_state(rollup)
        if state == "fail":
            return pull, "a check failed: %s" % ", ".join(names), ""
        if pull.get("mergeable") == "CONFLICTING":
            return pull, BLOCKS["DIRTY"], ""
        if pull.get("mergeStateStatus") in BLOCKS:
            return pull, BLOCKS[pull["mergeStateStatus"]], ""
        if state == "pending":
            waiting = "checks still running: %s" % ", ".join(names)
        elif settle and clock() - seen < SETTLE_MINUTES * 60:
            waiting = ("the newest commit's checks had not had time to start" if rollup
                       else "no checks have started")
        elif pull.get("mergeable") == "UNKNOWN" or pull.get("mergeStateStatus") == "UNKNOWN":
            waiting = "GitHub has not worked out whether it merges"
        elif pull.get("mergeStateStatus") == "BLOCKED":
            waiting = "a branch rule blocks the merge, such as a required review or check"
        else:
            return pull, "", ""
        if clock() >= deadline:
            return pull, ("after %d minutes, %s" % (wait_minutes, waiting) if wait_minutes
                          else "not yet: %s" % waiting), ""
        sleep(POLL_SECONDS)
        try:
            pull = view(repo, number, gh)
        except (RuntimeError, ValueError) as error:
            return pull, "it could not be read while waiting: %s" % error, ""
        review = not_pin_only(pull, base)
        if review:
            return pull, "", review


def merge_pin(repo, number, dry_run=False, wait_minutes=60, gh=run_gh, clock=time.monotonic,
              sleep=time.sleep):
    """Returns (verdict, tag, reason) after merging, flagging or skipping the pull request."""
    pull = view(repo, number, gh)
    title = PIN_TITLE.match(pull.get("title") or "")
    tag = title.group(1) if title else "-"
    base = default_branch(repo, gh)
    review = not_pin_only(pull, base)
    if review:
        return "review", tag, review
    # A dry run judges the pull request as it stands.
    pull, reason, review = wait_for_checks(repo, number, pull, base,
                                           0 if dry_run else wait_minutes, gh, clock, sleep,
                                           settle=not dry_run)
    if review:
        return "review", tag, review
    if not reason and len(pull.get("statusCheckRollup") or []) >= CHECKS_PAGE:
        reason = "it has %d or more checks, more than one read can check" % CHECKS_PAGE
    if reason:
        if dry_run:
            return "would-flag", tag, reason
        return "flagged", tag, flag(repo, number, reason, gh)
    reason, review = lock_mismatch(repo, pull.get("headRefOid") or "", base, tag, gh)
    if review:
        return "review", tag, review
    if reason:
        if dry_run:
            return "would-flag", tag, reason
        return "flagged", tag, flag(repo, number, reason, gh)
    if dry_run:
        return "would-merge", tag, "checks pass"
    try:
        method = merge_method(repo, gh)
    except (RuntimeError, ValueError) as error:
        return "flagged", tag, flag(repo, number, str(error), gh)
    code, _, err = gh(["pr", "merge", str(number), "-R", repo, method,
                       "--delete-branch", "--match-head-commit", pull.get("headRefOid") or ""])
    if code != 0:
        reason = "the merge was refused: %s" % (err.strip().splitlines() or ["no reason"])[-1]
        return "flagged", tag, flag(repo, number, reason, gh)
    return "merged", tag, "checks pass"


def main(argv, out=None, err=None, gh=run_gh, clock=time.monotonic, sleep=time.sleep):
    out = out or sys.stdout
    err = err or sys.stderr
    args = list(argv[1:])
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    wait = 60
    if "--wait-minutes" in args:
        at = args.index("--wait-minutes")
        value = args[at + 1] if at + 1 < len(args) else ""
        if not re.fullmatch(r"[0-9]+", value) or (int(value) < SETTLE_MINUTES and not dry_run):
            print(__doc__.strip().splitlines()[2], file=err)
            return 1
        wait = int(value)
        del args[at:at + 2]
    if len(args) != 2 or not re.fullmatch(r"[0-9]+", args[1]) \
            or not re.fullmatch(r"[\w.-]+/[\w.-]+", args[0]):
        print(__doc__.strip().splitlines()[2], file=err)
        return 1
    repo, number = args[0], int(args[1])
    try:
        verdict, tag, reason = merge_pin(repo, number, dry_run, wait, gh, clock, sleep)
    except (RuntimeError, ValueError) as error:
        print("error  %s#%d  -  %s" % (repo, number, error), file=out)
        print(str(error), file=err)
        return 1
    print("%s  %s#%d  %s  %s" % (verdict, repo, number, tag, reason), file=out)
    return {"merged": 0, "would-merge": 0, "review": 2}.get(verdict, 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
