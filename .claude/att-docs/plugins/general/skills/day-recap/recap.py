#!/usr/bin/env python3
"""End-of-day recap across GitHub repositories. Reads only; never writes anything."""
import argparse
import datetime
import json
import subprocess
import sys

try:
    from zoneinfo import ZoneInfo
    EASTERN = ZoneInfo("America/New_York")
except Exception:  # no time zone database on this machine
    EASTERN = datetime.timezone(datetime.timedelta(hours=-5))

DEFAULT_REVIEW = "Manual Review Needed"
DEFAULT_PROGRESS = "In Progress"
LIMIT = 100  # rows per gh listing; a listing that fills it is reported as cut short
WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen", "twenty"]


class GhError(Exception):
    pass


def run_gh(args):
    """Run gh and return parsed JSON. Raises GhError on a nonzero exit."""
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, check=False)
    except OSError as e:
        raise GhError(str(e))
    if p.returncode != 0:
        raise GhError(p.stderr.strip() or "gh failed")
    try:
        return json.loads(p.stdout or "[]")
    except ValueError as e:
        raise GhError(str(e))


def to_eastern(stamp):
    dt = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return dt.astimezone(EASTERN)


def clock(dt):
    return dt.strftime("%I:%M %p").lstrip("0")


def utc_range(day):
    """A UTC date range that covers the whole Eastern date `day`.

    GitHub reads a bare date as UTC, and the Eastern day runs from 4 or 5 AM UTC on
    `day` to 4 or 5 AM UTC the next day, so the range spans both UTC dates. Rows
    outside the Eastern day are dropped after the fetch."""
    nxt = datetime.date.fromisoformat(day) + datetime.timedelta(days=1)
    return "%s..%s" % (day, nxt.isoformat())


def listing(gh, args, cut, section):
    """Run one gh listing capped at LIMIT and note the section in `cut` if it filled."""
    rows = gh(args + ["--limit", str(LIMIT)])
    if len(rows) >= LIMIT:
        cut.append(section)
    return rows


def collect_repo(repo, day, review_label, progress_label, gh=run_gh):
    """Everything for one repository on the Eastern date `day` (YYYY-MM-DD)."""
    cut = []
    merged = []
    for pr in listing(gh, ["pr", "list", "--repo", repo, "--state", "merged", "--search",
                           "merged:" + utc_range(day),
                           "--json", "number,title,mergedAt"], cut, "merged"):
        when = to_eastern(pr["mergedAt"])
        if when.date().isoformat() == day:
            merged.append({"number": pr["number"], "title": pr["title"],
                           "time": clock(when), "_at": pr["mergedAt"]})
    merged.sort(key=lambda m: m["_at"])
    for m in merged:
        del m["_at"]

    waiting, ready = [], []
    for pr in listing(gh, ["pr", "list", "--repo", repo, "--state", "open",
                           "--label", review_label,
                           "--json", "number,title,labels,mergeable,isDraft"],
                      cut, "waiting_review"):
        names = [l.get("name") for l in pr.get("labels", [])]
        if review_label not in names:
            continue
        item = {"number": pr["number"], "title": pr["title"]}
        waiting.append(item)
        if pr.get("mergeable") == "MERGEABLE" and not pr.get("isDraft"):
            ready.append(item)

    in_progress = [{"number": i["number"], "title": i["title"]} for i in
                   listing(gh, ["issue", "list", "--repo", repo, "--state", "open",
                                "--label", progress_label, "--json", "number,title"],
                           cut, "in_progress")]

    failed = []
    try:
        runs = listing(gh, ["run", "list", "--repo", repo, "--status", "failure",
                            "--created", utc_range(day),
                            "--json", "databaseId,name,createdAt"], cut, "failed_runs")
    except GhError:
        runs = []  # no Actions on this repository
    for r in runs:
        when = to_eastern(r["createdAt"])
        if when.date().isoformat() == day:
            failed.append({"name": r["name"], "time": clock(when)})

    return {"repo": repo, "merged": merged, "waiting_review": waiting,
            "in_progress": in_progress, "failed_runs": failed, "ready_to_merge": ready,
            "cut_short": cut}


def build(repos, day, review_label, progress_label, gh=run_gh):
    return {"date": day, "repos": [collect_repo(r, day, review_label, progress_label, gh)
                                   for r in repos]}


def fmt_text(report):
    day = datetime.date.fromisoformat(report["date"])
    out = ["Recap for %s" % day.strftime("%A, %B %-d")]
    for r in report["repos"]:
        out += ["", r["repo"], ""]
        cut = r.get("cut_short", [])
        more = "  (GitHub listed %d; there may be more)" % LIMIT
        sections = [
            ("Merged today", ["#%d %s (%s)" % (m["number"], m["title"], m["time"])
                              for m in r["merged"]]),
            ("Waiting on review", ["#%d %s" % (p["number"], p["title"])
                                   for p in r["waiting_review"]]),
            ("Issues in progress", ["#%d %s" % (p["number"], p["title"])
                                    for p in r["in_progress"]]),
            ("Failed runs today", ["%s (%s)" % (f["name"], f["time"])
                                   for f in r["failed_runs"]]),
            ("Needs you: ready to merge", ["#%d %s" % (p["number"], p["title"])
                                           for p in r["ready_to_merge"]]),
        ]
        keys = ["merged", "waiting_review", "in_progress", "failed_runs", "waiting_review"]
        for (head, lines), key in zip(sections, keys):
            out.append(head + ":" + (more if key in cut else ""))
            out += ["  " + l for l in lines] if lines else ["  none"]
    return "\n".join(out)


def num(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def cap(s):
    return s[0].upper() + s[1:]


def fmt_spoken(report):
    sentences = []
    for r in report["repos"]:
        name = r["repo"].split("/")[-1]
        n = len(r["merged"])
        if n:
            sentences.append("%s merged in %s." % (
                cap(num(n) + (" pull request" if n == 1 else " pull requests")), name))
        else:
            sentences.append("Nothing merged in %s." % name)
        n = len(r["waiting_review"])
        if n:
            sentences.append("One pull request waits on your review." if n == 1
                             else "%s pull requests wait on your review." % cap(num(n)))
        n = len(r["ready_to_merge"])
        if n:
            sentences.append("One is ready to merge." if n == 1
                             else "%s are ready to merge." % cap(num(n)))
        n = len(r["in_progress"])
        if n:
            sentences.append("One issue is in progress." if n == 1
                             else "%s issues are in progress." % cap(num(n)))
        n = len(r["failed_runs"])
        if n:
            sentences.append("One run failed today." if n == 1
                             else "%s runs failed today." % cap(num(n)))
        if r.get("cut_short"):
            sentences.append("%s has more than the recap could list; check the screen."
                             % name)
    return " ".join(sentences)


def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        print("recap: cannot read config %s: %s" % (path, e), file=sys.stderr)
        sys.exit(64)
    if not isinstance(cfg, dict):
        print("recap: config must be a JSON object", file=sys.stderr)
        sys.exit(64)
    return cfg


def main(argv=None, gh=run_gh):
    ap = argparse.ArgumentParser(description="End-of-day recap across repositories.")
    ap.add_argument("--config", help="extension.json listing repos")
    ap.add_argument("--repo", action="append", default=[], help="owner/name, repeatable")
    ap.add_argument("--date", help="Eastern date YYYY-MM-DD (default: today)")
    ap.add_argument("--format", choices=["text", "spoken", "json"], default="text")
    ap.add_argument("--review-label")
    ap.add_argument("--in-progress-label")
    args = ap.parse_args(argv)

    cfg = load_config(args.config) if args.config else {}
    repos = list(args.repo) or list(cfg.get("repos") or [])
    if not repos:
        print("recap: no repositories; pass --config with repos or --repo owner/name",
              file=sys.stderr)
        return 64
    review = args.review_label or cfg.get("reviewLabel") or DEFAULT_REVIEW
    progress = args.in_progress_label or cfg.get("inProgressLabel") or DEFAULT_PROGRESS
    day = args.date or datetime.datetime.now(EASTERN).date().isoformat()
    try:
        datetime.date.fromisoformat(day)
    except ValueError:
        print("recap: --date must be YYYY-MM-DD", file=sys.stderr)
        return 64
    try:
        report = build(repos, day, review, progress, gh)
    except GhError as e:
        print("recap: %s" % e, file=sys.stderr)
        return 1
    print({"text": fmt_text, "spoken": fmt_spoken,
           "json": lambda r: json.dumps(r, indent=2)}[args.format](report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
