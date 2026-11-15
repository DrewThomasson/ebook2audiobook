#!/usr/bin/env python3
"""Closes the open pin pull requests in one repository that a newer pin pull request replaces.

usage: close_superseded_pins.py [--dry-run] <owner/repo> <new-tag> <new-pr-number>

A pin pull request is one titled "chore: <verb> the Overmind pin to v<major>.<minor>.<patch>",
as the bump pull requests the post-merge pin step opens are. The new pull request must be open
with <new-tag> in its title, or nothing is closed. Then this closes every other open pin pull
request in the repository that targets an earlier version, with a comment naming the new pull
request, and deletes its branch when the branch is in the same repository. It never touches the
new pull request itself, a pin pull request for the same or a newer version, or a pull request
that is not a pin pull request. With --dry-run it only says what it would close.

It prints one line for each pull request it closed, would close, or failed to close, and
exits 0, or 1 when any close or branch delete failed or the arguments are wrong. gh must be
signed in.
"""
import json
import re
import subprocess
import sys

PIN_TITLE = re.compile(
    r"^chore(?:\([^)]*\))?:\s+\w+\s+(?:the\s+)?Overmind pin to v?(\d+)\.(\d+)\.(\d+)\s*$",
    re.IGNORECASE)
TAG = re.compile(r"v?(\d+)\.(\d+)\.(\d+)")


def version_of(text, pattern):
    """The (major, minor, patch) a pattern finds in text, or None."""
    found = pattern.search(text or "")
    return tuple(int(part) for part in found.groups()) if found else None


def superseded(pulls, new_version, new_number):
    """The pin pull requests in `pulls` that target a version earlier than new_version, other
    than pull request new_number, each as (number, version, branch to delete or "")."""
    older = []
    for pull in pulls:
        if pull.get("number") == new_number:
            continue
        version = version_of(pull.get("title"), PIN_TITLE)
        if version is not None and version < new_version:
            branch = "" if pull.get("isCrossRepository") else pull.get("headRefName") or ""
            older.append((pull["number"], version, branch))
    return sorted(older)


def run_gh(args):
    """(exit code, stdout, stderr) of a gh command."""
    done = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    return done.returncode, done.stdout, done.stderr


def close_superseded(repo, new_tag, new_number, dry_run=False, gh=run_gh):
    """Closes the older pin pull requests in repo; returns (lines to print, number that failed)."""
    new_version = version_of(new_tag, TAG)
    if new_version is None:
        raise ValueError("%r is not a tag like v1.2.3" % new_tag)
    code, out, err = gh(["pr", "list", "-R", repo, "--state", "open", "--limit", "200",
                         "--json", "number,title,headRefName,isCrossRepository"])
    if code != 0:
        raise RuntimeError("could not list pull requests in %s: %s" % (repo, err.strip()))
    pulls = json.loads(out or "[]")
    if not any(p.get("number") == new_number
               and version_of(p.get("title"), PIN_TITLE) == new_version for p in pulls):
        raise RuntimeError("#%d is not an open pin pull request for %s in %s"
                           % (new_number, new_tag, repo))
    lines, failed = [], 0
    for number, version, branch in superseded(pulls, new_version, new_number):
        old = "v%d.%d.%d" % version
        if dry_run:
            lines.append("would close #%d (%s) in %s" % (number, old, repo))
            continue
        comment = "Superseded by #%d, which moves the pin to %s." % (new_number, new_tag)
        code, _, err = gh(["pr", "close", str(number), "-R", repo, "--comment", comment])
        if code != 0:
            failed += 1
            lines.append("could not close #%d in %s: %s" % (number, repo, err.strip()))
            continue
        lines.append("closed #%d (%s) in %s" % (number, old, repo))
        if branch:
            code, _, err = gh(["api", "-X", "DELETE",
                               "repos/%s/git/refs/heads/%s" % (repo, branch)])
            if code != 0 and "Reference does not exist" not in err:
                failed += 1
                lines.append("closed #%d but could not delete branch %s: %s"
                             % (number, branch, err.strip()))
    return lines, failed


def main(argv, out=None, err=None, gh=run_gh):
    out = out or sys.stdout
    err = err or sys.stderr
    args = [a for a in argv[1:] if a != "--dry-run"]
    dry_run = len(args) != len(argv) - 1
    if len(args) != 3 or not re.fullmatch(r"[0-9]+", args[2]) \
            or not re.fullmatch(r"[\w.-]+/[\w.-]+", args[0]):
        print(__doc__.strip().splitlines()[2], file=err)
        return 1
    try:
        lines, failed = close_superseded(args[0], args[1], int(args[2]), dry_run, gh)
    except (ValueError, RuntimeError) as error:
        print(str(error), file=err)
        return 1
    for line in lines:
        print(line, file=out)
    if not lines:
        print("no older pin pull requests in %s" % args[0], file=out)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
