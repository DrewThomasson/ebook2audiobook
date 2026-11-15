#!/usr/bin/env python3
"""Compare the SharePoint documentation libraries with the converted set under the apps root.

  docwatch.py --config FILE SUBCOMMAND ...

Subcommands:
  payload       print page.js filled with the folder table, the readable formats and
                the provenance index
  compare FILE  classify the report page.js wrote, as JSON
  summary FILE  print a compare result as the plain-text run summary
  issue-body    render the tracking issue body from the todo root and a compare result
  place FILE    move approved downloads into the todo root, dropping re-saved documents,
                and each revision the web app does not carry yet (--future) into its
                Future folder
  link FILE     give each converted file a SharePoint line per source a links scan found
  index         print the provenance index as JSON
  check-config  check that every folder table row names a listed library and a known rule

FILE after --config is the skill's extension.json. A path in it is relative to the git
toplevel of the folder the file sits in. The fields:

  convert         convert-docs' extension.json, which names the todo root, the apps root,
                  the Future folder and the SharePoint host
  libraries       library key -> [web, library title]; the key "" is the default library
  suites          one-character suite code -> suite name, as folder table rows name them
  folders         the folder table
  sources         the table of the folder each repeated source name was converted from
  ignored         the table of library files to pass over
  notFromLibrary  optional pattern for source names that never came from a library

A missing config, or a field it lacks or misstates, exits 64.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote

HERE = Path(__file__).resolve().parent
CONVERT_DOCS = HERE.parent / "convert-docs"
sys.path.insert(0, str(CONVERT_DOCS))
import convert_config  # noqa: E402  the --config reader convert-docs keeps
from doc_paths import hyphenated  # noqa: E402  the docs naming rule convert-docs keeps

PAGE = HERE / "page.js"
CONVERT = CONVERT_DOCS / "convert.sh"
PROG = "docwatch"

# Every value below the line is set by configure() from the --config file.
# ROOT: the repository the config sits in. APPS and TODO: the apps and todo roots, and
# APPS_ROOT and TODO_ROOT: the same as written in convert-docs' config, relative to a
# checkout. FUTURE: the folder under a suite for a revision the web app does not carry
# yet, <apps root>/<SUITE>/<FUTURE>, while the suite folder keeps the version it follows.
# HOST: the scheme and host the libraries live on.
#
# LIBRARIES: the libraries the scan walks, by key: the web (a site or subsite) and the
# library folder under it. The default library, keyed "", has its folders written as they
# sit in it. Another library's folders carry its key and a colon, `Key:Folder`, and
# SharePoint allows no colon in a folder name, so the two can never read as one folder.
# The key and colon alone, `Key:`, is that library's root, for files that sit in no folder.
# SUITES: one-character code -> suite name, and CODES the reverse.
# NOT_FROM_LIBRARY: source names a provenance block carries that came from no library.
ROOT: Path
APPS: Path
TODO: Path
APPS_ROOT: str
TODO_ROOT: str
FUTURE: str
HOST: str
FOLDERS: Path
IGNORED: Path
SOURCES: Path
LIBRARIES: dict[str, tuple[str, str]]
SUITES: dict[str, str]
CODES: dict[str, str]
NOT_FROM_LIBRARY: re.Pattern | None

# "track" follows the converted documents in a folder without reporting its other files;
# "skip" leaves the folder out of the walk.
RULES = ("track", "skip")

# A provenance line names one source file in backticks. A file that only transports the
# content reads "- Source: <origin>, by way of `<file>`", and the file is still the key.
SOURCE_LINE = re.compile(r"^- Source: (?:.*by way of )?`([^`]+)`\s*$")
CONVERTED_LINE = re.compile(r"^- Converted: (\d{4}-\d{2}-\d{2})")
# The same line with the time convert-docs adds, in Zulu time; an older copy holds the date alone.
CONVERTED_STAMP = re.compile(r"^- Converted: (\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)")
# How many lines from the top of a converted file the provenance block is read from.
BLOCK_LINES = 41

# A trailing _MMDDYYYY or _YYYYMMDD date on a file stem, which revisions of one document
# carry. Written once here: it keys the index and is filled into page.js, and it is
# plain enough to mean the same to Python and to JavaScript.
DATE_SUFFIX = (
    r"_(?:(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])(?:19|20)\d\d"
    r"|(?:19|20)\d\d(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))$"
)

# The formats convert.sh reads, taken from its own routing table rather than copied.
TO_MARKDOWN = re.compile(r"^to_markdown\(\)\s*\{$")
CASE_LABEL = re.compile(r"^([a-z0-9]+(?:\|[a-z0-9]+)*)\)$")


def configure(file: str | None) -> None:
    """Set the repository roots, libraries, suites and tables from an extension.json."""
    global ROOT, APPS, TODO, APPS_ROOT, TODO_ROOT, FUTURE, HOST, FOLDERS, IGNORED, SOURCES
    global LIBRARIES, SUITES, CODES, NOT_FROM_LIBRARY
    config = convert_config.load(file, PROG)
    convert = convert_config.load(str(config.path("convert")), PROG)
    ROOT = config.root
    APPS_ROOT, TODO_ROOT = convert.value("appsRoot"), convert.value("todoRoot")
    APPS, TODO = ROOT / APPS_ROOT, ROOT / TODO_ROOT
    FUTURE, HOST = convert.value("futureFolder"), convert.value("sharePointHost")
    FOLDERS, IGNORED = config.path("folders"), config.path("ignored")
    SOURCES = config.path("sources")
    libraries, suites = config.values.get("libraries"), config.values.get("suites")
    if not isinstance(libraries, dict) or not all(
        isinstance(v, list) and len(v) == 2 and all(isinstance(p, str) and p for p in v)
        for v in libraries.values()
    ):
        convert_config.fail(PROG, f"{config.file} libraries is not key -> [web, library]")
    if not isinstance(suites, dict) or not all(
        len(code) == 1 and isinstance(name, str) and name for code, name in suites.items()
    ) or len(set(suites.values())) != len(suites):
        convert_config.fail(PROG, f"{config.file} suites is not one character -> one suite")
    LIBRARIES = {key: (web, library) for key, (web, library) in libraries.items()}
    SUITES = dict(suites)
    CODES = {suite: code for code, suite in SUITES.items()}
    pattern = config.values.get("notFromLibrary")
    try:
        NOT_FROM_LIBRARY = re.compile(pattern) if pattern else None
    except re.error as error:
        convert_config.fail(PROG, f"{config.file} notFromLibrary does not compile: {error}")


def fnv(text: str) -> str:
    """FNV-1a over the lowercased name, the same hash page.js computes."""
    value = 0x811C9DC5
    for ch in text.lower():
        value ^= ord(ch)
        value = (value * 0x01000193) & 0xFFFFFFFF
    return format(value, "08x")


def read_block(md: Path) -> tuple[list[str], str] | None:
    """The source names and Converted date of one converted file, or None."""
    sources: list[str] = []
    with md.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle):
            # The block sits right under the H1, well inside the first lines.
            if number >= BLOCK_LINES:
                break
            if match := SOURCE_LINE.match(line.rstrip("\n")):
                sources.append(match.group(1))
            elif match := CONVERTED_LINE.match(line):
                return (sources, match.group(1)) if sources else None
    return None


def converted_stamp(md: Path) -> str:
    """The Converted value of a converted file: `YYYY-MM-DD HH:MM` (Zulu time), or the date alone."""
    with md.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle):
            if number >= BLOCK_LINES:
                break
            if match := CONVERTED_STAMP.match(line):
                return match.group(1)
    return ""


def is_future(md: Path) -> bool:
    """Whether a converted file sits in its suite's Future folder."""
    parts = md.relative_to(APPS).parts
    return len(parts) > 2 and parts[1] == FUTURE


def build_index(follow: bool = True) -> dict[str, list[dict]]:
    """Map each source file name to every converted file that claims it.

    With `follow`, a name with a copy in a suite's Future folder is followed through that
    copy alone, which is the newest revision converted. The suite folder's copy is the
    version the web app follows, held until the revision migrates, and is never reported
    as changed. Without it, every converted file is listed, for the links and sources.tsv.
    """
    index: dict[str, list[dict]] = {}
    for md in sorted(APPS.rglob("*.md")):
        block = read_block(md)
        if block is None:
            continue
        sources, converted = block
        for name in sources:
            if NOT_FROM_LIBRARY and NOT_FROM_LIBRARY.match(name):
                continue
            index.setdefault(name, []).append({
                "path": md.relative_to(ROOT).as_posix(),
                "suite": md.relative_to(APPS).parts[0],
                "converted": converted,
                "converted_at": converted_stamp(md),
                "future": is_future(md),
            })
    for name, claims in index.items() if follow else ():
        ahead = {c["suite"] for c in claims if c["future"]}
        index[name] = [c for c in claims if c["future"] or c["suite"] not in ahead]
    return index


def todo_folder(suite: str, future: bool) -> str:
    """The todo root folder a download waits in, which convert.sh mirrors under apps."""
    return f"{suite}/{FUTURE}" if future else suite


def read_formats() -> list[str]:
    """The extensions convert.sh turns into Markdown, read out of its own case block.

    One routing table serves both skills: a format convert.sh stops reading stops being
    reported as a new document on the next scan, with no list to keep in step here.
    """
    formats: set[str] = set()
    inside = False
    for line in CONVERT.read_text(encoding="utf-8").splitlines():
        if TO_MARKDOWN.match(line):
            inside = True
            continue
        if inside:
            if line == "}":
                break
            if match := CASE_LABEL.match(line.strip()):
                formats.update(match.group(1).split("|"))
    # A parse that comes back empty or short would hide every new document instead of
    # the handful in formats nothing reads, so it stops the run.
    if "docx" not in formats or "pdf" not in formats:
        sys.exit(f"docwatch: {CONVERT.name} routing table did not parse: {sorted(formats)}")
    return sorted(formats)


def read_tsv(path: Path) -> list[list[str]]:
    """Rows of a checked-in table, comments and blank lines dropped."""
    if not path.exists():
        return []
    return [
        line.split("\t")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def read_folders() -> list[tuple[str, str]]:
    """The folder table as (library-relative prefix, rule), longest prefix first."""
    rows = []
    for row in read_tsv(FOLDERS):
        folder, rule = row[0].strip("/"), row[1]
        if rule not in CODES and rule not in RULES:
            sys.exit(f"{FOLDERS.name}: unknown rule {rule!r} for {folder!r}")
        if folder.rpartition(":")[0] not in LIBRARIES:
            sys.exit(f"{FOLDERS.name}: {folder!r} names no library the config lists")
        rows.append((folder, rule))
    return sorted(rows, key=lambda row: len(row[0]), reverse=True)


def library_path(folder: str, name: str) -> str:
    """The server-relative path of a file in a scan folder, whichever library holds it."""
    key, _, inside = folder.rpartition(":")
    web, library = LIBRARIES[key]
    return f"{web}/{library}/{file_in(inside, name)}"


def file_in(folder: str, name: str) -> str:
    """A file's path under a scan folder, where a library root such as `Key:` takes no slash."""
    return f"{folder}{name}" if folder.endswith(":") or not folder else f"{folder}/{name}"


def stem(name: str) -> str:
    """The file name without its extension, the key a .doc and its .pdf twin share.

    A trailing date is dropped too: a document published under a new dated name at each
    revision (Contract_08252026.yaml) is one document whatever date it carries. The
    payload hands page.js the same pattern.
    """
    return re.sub(DATE_SUFFIX, "", re.sub(r"\.[^.]*$", "", name))


def by_stem(index: dict[str, list[dict]]) -> dict[str, dict]:
    """Group the index by lowercased stem, keeping each converted file once."""
    grouped: dict[str, dict] = {}
    for name, claims in index.items():
        group = grouped.setdefault(stem(name).lower(), {"names": [], "claims": {}})
        group["names"].append(name)
        for claim in claims:
            group["claims"][claim["path"]] = claim
    return grouped


def read_sources(grouped: dict[str, dict]) -> dict[str, dict[str, str]]:
    """The sources table as {lowercased stem: {converted file: library folder it came from}}.

    A row naming a file with no provenance block, or a folder the scan never walks, can
    never match a library file, so either one stops the run rather than going quiet. So
    does a name with a row for one of its converted files and none for another, since the
    file left out would never be compared again.
    """
    folders = read_folders()
    # A suite copy its Future copy shadows is still a converted file a row can name.
    owner = {path: key for key, group in by_stem(build_index(follow=False)).items()
             for path in group["claims"]}
    homes: dict[str, dict[str, str]] = {}
    for row in read_tsv(SOURCES):
        md, folder = f"{APPS_ROOT}/{row[0]}", row[1].strip("/")
        if md not in owner:
            sys.exit(f"{SOURCES.name}: {row[0]!r} is not a converted file"
                     " with a provenance block")
        rule = next((r for prefix, r in folders if under(folder, prefix)), None)
        if rule in (None, "skip"):
            sys.exit(f"{SOURCES.name}: {folder!r} for {row[0]!r} is not a walked folder")
        homes.setdefault(owner[md], {})[md] = folder
    for key, rows in homes.items():
        if left := sorted(set(grouped[key]["claims"]) - set(rows)):
            sys.exit(f"{SOURCES.name}: no row for {', '.join(left)},"
                     " which shares a source name")
    return homes


def under(folder: str, prefix: str) -> bool:
    """Whether a library folder is the prefix or inside it, as page.js reads the tables."""
    return folder == prefix or folder.startswith(prefix if prefix.endswith(":") else f"{prefix}/")


def from_source(folder: str, source: str) -> bool:
    """Whether a library folder holds a sources.tsv row's copy; a root row means its files."""
    return folder == source if source.endswith(":") else under(folder, source)


def packed_index() -> dict:
    """The index as page.js reads it: hashed stems, a suite code, a date position."""
    grouped = by_stem(build_index())
    days = sorted({c["converted"] for g in grouped.values() for c in g["claims"].values()})
    entries = []
    for key, group in sorted(grouped.items()):
        claims = sorted(group["claims"].values(), key=lambda c: c["path"])
        # A document claimed twice is due again once its older conversion is out of date.
        day = min(c["converted"] for c in claims)
        entries.append(f"{fnv(key)}{CODES[claims[0]['suite']]}{days.index(day)}")
    joined = " ".join(entries)
    return {"days": days, "entries": joined, "check": fnv(joined)}


def payload(mode: str, cached: bool, names: tuple[str, ...] = ()) -> str:
    """page.js with the folder table, the readable formats and the hashed index filled in.

    The page keeps the index in its own localStorage, so a cached payload leaves it out
    and the page reports INDEX stale when its copy is from another version.
    """
    packed = packed_index()
    version = hashlib.sha1(json.dumps(packed).encode()).hexdigest()[:12]
    homes = read_sources(by_stem(build_index()))
    sources = [[fnv(key), sorted(set(rows.values()))] for key, rows in homes.items()]
    # Comments and indentation are dropped; the text is sent whole on every run.
    script = "\n".join(
        line.strip() for line in PAGE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("//")
    )
    return (
        script
        .replace("'__MODE__'", json.dumps(mode))
        .replace("'__VERSION__'", json.dumps(version))
        .replace("__LIBRARIES__", json.dumps(
            [[key, web, f"{web}/{library}"] for key, (web, library) in LIBRARIES.items()]
        ))
        .replace("__FOLDERS__", json.dumps(read_folders()))
        .replace("__FORMATS__", json.dumps(read_formats()))
        .replace("__DATE_SUFFIX__", json.dumps(DATE_SUFFIX))
        .replace("__SOURCES__", json.dumps(sorted(sources)))
        .replace("__NAMES__", json.dumps(sorted({fnv(stem(name)) for name in names})))
        .replace("__INDEX__", "null" if cached else json.dumps(packed))
    )


def parse_report(text: str) -> dict[str, list[list[str]]]:
    """The lines between the report markers, grouped by their first field."""
    body = text.split("DOCWATCH-BEGIN", 1)[-1].split("DOCWATCH-END", 1)[0]
    groups: dict[str, list[list[str]]] = {}
    for line in body.split():
        kind, *fields = (unquote(field) for field in line.split("|"))
        groups.setdefault(kind, []).append(fields)
    return groups


def same_name(rows: list[list[str]], homes: dict[str, dict[str, str]]) -> list[dict]:
    """SAMENAME report lines grouped by stem, one entry per name found in several folders.

    The state is `conflict` for different files that sources.tsv does not settle, `copy`
    when every folder holds the same files at the same sizes, and `resolved` when
    sources.tsv names the folder each converted file came from.
    """
    grouped: dict[str, dict] = {}
    for state, folder, name, modified, size in rows:
        key = stem(name).lower()
        entry = grouped.setdefault(key, {"stem": key, "state": state, "files": []})
        if key in homes:
            entry["sources"] = homes[key]
        entry["files"].append(
            {"folder": folder, "name": name, "modified": modified, "size": int(size or 0)}
        )
    order = {"conflict": 0, "copy": 1, "resolved": 2}
    return sorted(grouped.values(), key=lambda e: (order.get(e["state"], 3), e["stem"]))


def compare(text: str) -> dict:
    """Classify the page report against the provenance index."""
    groups = parse_report(text)
    index = build_index()
    grouped = by_stem(index)
    homes = read_sources(grouped)
    by_hash = {fnv(key): key for key in grouped}
    # The ignored table: a file name, then "*" for every version or the Modified time to
    # pass over.
    ignored = {(row[0], row[1] if len(row) > 1 else "*") for row in read_tsv(IGNORED)}
    result: dict = {
        "run": dt.date.today().isoformat(),
        "index": (groups.get("INDEX") or [[]])[0],
        "session": (groups.get("SESSION") or [["missing"]])[0],
        "walked": (groups.get("WALKED") or [["0", "0"]])[0],
        "errors": groups.get("ERROR", []),
        "unmapped": [row[0] for row in groups.get("UNMAPPED", [])],
        "unchanged": int((groups.get("UNCHANGED") or [["0"]])[0][0]),
        "changed": [], "new": [], "ignored": 0,
        # Files under a walked folder in a format no converter reads, counted by format.
        "unreadable": {ext: int(count) for ext, count in groups.get("UNREADABLE", [])},
        "conflicts": {n: [e["path"] for e in c] for n, c in index.items() if len(c) > 1},
        "same_name": same_name(groups.get("SAMENAME", []), homes),
        "not_listed": [],
    }
    for folder, name, modified, size in groups.get("CHANGED", []):
        if (name, "*") in ignored or (name, modified) in ignored:
            result["ignored"] += 1
            continue
        group = grouped.get(stem(name).lower())
        if group is None:
            # A hash collision with an unrelated library file; the stem settles it.
            continue
        # A name sources.tsv places is compared only with the files its rows say it came from.
        placed = homes.get(stem(name).lower(), {})
        stale = [
            c for c in group["claims"].values()
            if modified[:10] > c["converted"]
            and (not placed or from_source(folder, placed[c["path"]]))
        ]
        # Every stale conversion is replaced, so a document claimed by two suites lands in both.
        for claim in sorted(stale, key=lambda c: c["path"]):
            result["changed"].append({
                "suite": claim["suite"], "name": name, "folder": folder,
                "modified": modified, "size": int(size or 0),
                "url": library_path(folder, name),
                "replaces": claim["path"], "converted": claim["converted"],
                "future": claim["future"],
            })
    for folder, name, modified, size, suite in groups.get("NEW", []):
        if (name, "*") in ignored:
            result["ignored"] += 1
            continue
        result["new"].append({
            "suite": suite, "name": name, "folder": folder, "modified": modified,
            "size": int(size or 0), "url": library_path(folder, name), "replaces": None,
            "future": False,
        })
    missing = (groups.get("MISSING") or [[""]])[0][0].split()
    result["not_listed"] = sorted(
        name for h in missing if h in by_hash for name in grouped[by_hash[h]]["names"]
    )
    return result


def modified_minute(modified: str) -> str:
    """A library Modified time (ISO, Zulu time) as `YYYY-MM-DD HH:MM`."""
    return f"{modified[:10]} {modified[11:16]}"


def is_stale(modified: str, converted_at: str) -> bool:
    """Whether a library copy changed after its conversion, to the minute.

    A conversion stamped with a time is compared to the minute, and an edit in the same minute
    counts as stale, since the stamp cannot tell which came first. One stamped with the date
    alone has no time to compare, so a copy modified on that day or later counts as stale.
    """
    if len(converted_at) > 10:
        return modified_minute(modified) >= converted_at
    return modified[:10] >= converted_at


def lookup(text: str, names: list[str]) -> dict:
    """Classify the named documents from a lookup report, to the minute.

    `changed` lists a document whose converted copy is stale and `new` one with no converted
    copy, both in the shape `place` reads. `current` and `not_found` name the rest, `held` a
    name in two folders holding different files that sources.tsv does not settle, `no_suite`
    a new document in a folder that follows documents without naming a suite, and `ignored`
    a document the ignored table passes over. `readable` is false, with the reason in
    `session`, `errors`, or `index`, when the walk did not finish, so an unreachable library
    is never read as documents not found.
    """
    groups = parse_report(text)
    session = (groups.get("SESSION") or [["ok"]])[0][0]
    errors = groups.get("ERROR", [])
    index_state = (groups.get("INDEX") or [[]])[0]
    result: dict = {
        "readable": bool(groups.get("WALKED")) and session == "ok" and not errors
        and not index_state,
        "session": session, "errors": errors, "index": index_state,
        "changed": [], "new": [], "current": [], "not_found": [], "held": [],
        "no_suite": [], "ignored": [],
    }
    if not result["readable"]:
        return result
    ignored = {(row[0], row[1] if len(row) > 1 else "*") for row in read_tsv(IGNORED)}
    rows = groups.get("LOOKUP", [])
    grouped = by_stem(build_index())
    homes = read_sources(grouped)
    for wanted in names:
        key = stem(wanted).lower()
        found = [r for r in rows if stem(r[1]).lower() == key]
        # A revision copy stands in only when no current copy was found.
        found = [r for r in found if len(r) < 6 or r[5] != "side"] or found
        if not found:
            result["not_found"].append(wanted)
            continue
        placed = homes.get(key, {})
        group = grouped.get(key)
        by_folder: dict[str, list[tuple[str, str]]] = {}
        for folder, name, _modified, size, *_rest in found:
            by_folder.setdefault(folder, []).append((name.lower(), size))
        if len(by_folder) > 1 and not placed:
            if len({tuple(sorted(files)) for files in by_folder.values()}) > 1:
                result["held"].append({"name": wanted, "folders": sorted(by_folder)})
                continue
            found = found[:1]
        if any((name, "*") in ignored or (name, modified) in ignored
               for _f, name, modified, *_rest in found):
            result["ignored"].append(wanted)
            continue
        if group is None:
            folder, name, modified, size, rule, *_rest = found[0]
            if rule not in SUITES.values():
                result["no_suite"].append({"name": name, "folder": folder, "rule": rule})
                continue
            result["new"].append({
                "suite": rule, "name": name, "folder": folder, "modified": modified,
                "size": int(size or 0), "url": library_path(folder, name),
                "replaces": None, "future": False,
            })
            continue
        stale = []
        for folder, name, modified, size, *_rest in found:
            for claim in group["claims"].values():
                if placed and not from_source(folder, placed[claim["path"]]):
                    continue
                if is_stale(modified, claim["converted_at"] or claim["converted"]):
                    stale.append({
                        "suite": claim["suite"], "name": name, "folder": folder,
                        "modified": modified, "size": int(size or 0),
                        "url": library_path(folder, name), "replaces": claim["path"],
                        "converted": claim["converted"], "future": claim["future"],
                    })
        if stale:
            result["changed"].extend(stale)
        else:
            result["current"].append(wanted)
    return result


def every_document_changed(text: str) -> str:
    """The links report with each found document turned into a changed one.

    The links scan names every converted document it found in the library. Reading
    those as changed on a far-future Modified time gives `place` the whole converted set
    to download, for a batch that is converted again whatever the library says.
    """
    lines = []
    for line in text.splitlines():
        kind, *fields = line.split("|")
        if kind == "FOUND":
            lines.append("|".join(["CHANGED", *fields, quote("2099-01-01T00:00:00Z"), "0"]))
        elif kind != "NEW":
            lines.append(line)
    return "\n".join(lines) + "\n"


def summary(result: dict) -> str:
    """The run summary a person reads."""
    session = "\t".join(result["session"])
    unreadable = result.get("unreadable", {})
    formats = ", ".join(f"{ext} {count}" for ext, count in sorted(unreadable.items()))
    pairs = result.get("same_name", [])
    states = {s: sum(e["state"] == s for e in pairs) for s in ("conflict", "copy", "resolved")}
    lines = [
        f"Session: {session}",
        f"Walked {result['walked'][0]} folders, {result['walked'][1]} files",
        f"Unchanged: {result['unchanged']}",
        f"Changed: {len(result['changed'])}",
        f"New: {len(result['new'])}",
        f"Passed over through {IGNORED.name}: {result['ignored']}",
        f"Passed over, no converter reads the format: {sum(unreadable.values())}"
        + (f" ({formats})" if formats else ""),
        f"Converted sources not found in the library: {len(result['not_listed'])}",
        f"Sources claimed by two converted files: {len(result['conflicts'])}",
        f"Names found in two or more walked folders: {len(pairs)}"
        f" ({states['conflict']} held back, {states['copy']} copies,"
        f" {states['resolved']} settled by {SOURCES.name})",
        f"Top folders missing from {FOLDERS.name}: {len(result['unmapped'])}",
        f"Errors: {len(result['errors'])}",
    ]
    for kind in ("changed", "new"):
        for item in result[kind]:
            target = item["replaces"] or "new"
            if item.get("future"):
                target += ", not migrated"
            lines.append(
                f"  {kind.upper()} {item['suite']}: {item['name']}"
                f" (modified {item['modified'][:10]}, {item['size']} bytes) -> {target}"
            )
    for entry in pairs:
        label = {"conflict": "HELD", "copy": "COPY"}.get(entry["state"], "SETTLED")
        folders = sorted(set(entry.get("sources", {}).values()))
        source = f", converted from {' and '.join(folders)}" if folders else ""
        lines.append(f"  {label} {entry['stem']}{source}:")
        lines += [
            f"    {file_in(f['folder'], f['name'])}"
            f" (modified {f['modified'][:10]}, {f['size']} bytes)"
            for f in entry["files"]
        ]
    lines += [f"  UNMAPPED {folder}" for folder in result["unmapped"]]
    lines += [f"  ERROR {folder}: {message}" for folder, message in result["errors"]]
    return "\n".join(lines) + "\n"


def in_todo(path: str) -> tuple[str, ...]:
    """The parts of a checkout-relative path under the todo root."""
    return Path(path).relative_to(TODO_ROOT).parts


def todo_files(repo: Path) -> list[str]:
    """Documents waiting in the todo root, outside convert.sh's own _done and _needs_merge."""
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard",
         TODO_ROOT],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return sorted(p for p in out if len(in_todo(p)) > 1 and not in_todo(p)[0][0] == "_")


def commit_day(path: str, repo: Path) -> str | None:
    """The day a file under the todo root was last committed, or None when it is untracked."""
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%cs", "--", path],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return out or None


def issue_body(result: dict | None, repo: Path) -> str:
    """The tracking issue body: every document waiting, one checklist row each.

    `repo` is the checkout whose todo root is listed, so the body can describe the
    download branch before it merges.
    """
    grouped = by_stem(build_index())
    pending = {
        (item["suite"], hyphenated(item["name"])): item
        for item in (result or {}).get("changed", []) + (result or {}).get("new", [])
    }
    # A file waits under its name without spaces, and the converted documents are keyed
    # on the library name, which the library map records at the end of its path.
    library_names = {
        (row[0], row[1]): row[2].rsplit("/", 1)[-1]
        for row in read_tsv(library_paths(repo)) if len(row) > 2
    }
    rows = []
    for path in todo_files(repo):
        parts = in_todo(path)
        suite, name = parts[0], parts[-1]
        future = len(parts) > 2 and parts[1] == FUTURE
        item = pending.pop((suite, name), None)
        modified = item["modified"][:10] if item else "not recorded"
        library_name = (
            item["name"] if item
            else library_names.get((todo_folder(suite, future), name), name)
        )
        group = grouped.get(stem(library_name).lower())
        claims = sorted(group["claims"].values(), key=lambda c: c["path"]) if group else []
        row = f"- [ ] {suite}: `{name}`, modified {modified}"
        if future:
            row += f", **not migrated, converts into `{APPS_ROOT}/{suite}/{FUTURE}/`**"
        if not claims:
            rows.append(f"{row}, **new**")
            continue
        claim = next((c for c in claims if c["suite"] == suite), claims[0])
        row += f", {'replaces' if claim['future'] == future else 'beside'} `{claim['path']}`"
        if claim["suite"] != suite:
            row += f", **move to `{TODO_ROOT}/{claim['suite']}/`**"
        added = commit_day(path, repo)
        if added and claim["converted"] >= added:
            row += f", **converted {claim['converted']}, clear it from `{TODO_ROOT}`**"
        rows.append(row)
    for (suite, name), item in sorted(pending.items()):
        replaces = f"replaces `{item['replaces']}`" if item["replaces"] else "**new**"
        if item.get("future"):
            replaces += f", **not migrated, converts into `{APPS_ROOT}/{suite}/{FUTURE}/`**"
        rows.append(
            f"- [ ] {suite}: `{name}`, modified {item['modified'][:10]}, {replaces},"
            " **pending download**"
        )
    lines = [
        "Documents waiting to be converted with `/convert-docs`. The `doc-watch` skill"
        " rewrites this list on every run, so change the documents rather than this body.",
        "",
        f"Last run: {dt.date.today().isoformat()}",
        "",
        *(rows or ["Nothing is waiting."]),
    ]
    return "\n".join(lines) + "\n"


def stamp_module():
    """The convert-docs stamper beside this skill, so both agree on dates and links."""
    import stamp  # noqa: E402  on the path with convert_config, from CONVERT_DOCS

    return stamp


def link(text: str, apply: bool) -> str:
    """Give every converted file a SharePoint line per source the links scan found.

    The scan reports a FOUND row for each library file a converted file names, in the
    folder the comparison settled on, so a name held as a conflict has no row and its
    file is left as it is. The lines go right under the Source lines and replace any
    SharePoint lines already there.
    """
    stamp = stamp_module()
    index = build_index(follow=False)
    found: dict[str, list[str]] = {}
    for folder, name in parse_report(text).get("FOUND", []):
        found.setdefault(name, []).append(library_path(folder, name))
    changed, unchanged, unfound = [], 0, []
    for md in sorted({c["path"] for claims in index.values() for c in claims}):
        path = ROOT / md
        block = read_block(path)
        names = block[0] if block else []
        links = [
            stamp.sharepoint_line(name, sorted(found[name])[0], HOST)
            for name in names if name in found
        ]
        if not links:
            unfound.append(md)
            continue
        lines = path.read_text(encoding="utf-8").split("\n")
        head = lines[:BLOCK_LINES]
        kept = [line for line in head if not line.startswith("- SharePoint: ")]
        last = max(i for i, line in enumerate(kept) if SOURCE_LINE.match(line))
        new = kept[:last + 1] + links + kept[last + 1:] + lines[BLOCK_LINES:]
        if new == lines:
            unchanged += 1
            continue
        changed.append(md)
        if apply:
            path.write_text("\n".join(new), encoding="utf-8")
    out = [f"linked {len(changed)}, already linked {unchanged}, not found {len(unfound)}"]
    out += [f"NOT FOUND  {md}" for md in unfound]
    return "\n".join(out) + "\n"


def embedded_day(path: Path) -> str | None:
    """The last-saved date a downloaded file carries about itself, where it has one."""
    stamp = stamp_module()

    suffix = path.suffix.lower()
    if suffix in stamp.OPC_SUFFIXES:
        return stamp.opc_properties(path)
    if suffix == ".pdf":
        return stamp.pdf_properties(path)
    return None


def library_paths(repo: Path) -> Path:
    """The library map, library.tsv in the todo root: where each waiting document sits.

    convert.sh reads it by that name to link each converted file to its library document.
    """
    return repo / TODO_ROOT / "library.tsv"


def record_paths(repo: Path, placed: list[dict]) -> None:
    """Add or replace a library.tsv row for each placed document.

    A row stays while its file is still in the todo root, waiting in its suite folder or
    kept in _done after converting, which is as long as convert.sh can read it.
    """
    path = library_paths(repo)
    todo = repo / TODO_ROOT
    rows = {
        (row[0], row[1]): row[2] for row in read_tsv(path)
        if len(row) > 2
        and ((todo / row[0] / row[1]).exists() or (todo / "_done" / row[0] / row[1]).exists())
    }
    for item in placed:
        rows[(todo_folder(item["suite"], item["future"]), hyphenated(item["name"]))] = item["url"]
    lines = [
        "# suite folder, file name, and server-relative library path of each downloaded document",
        *(f"{suite}\t{name}\t{url}" for (suite, name), url in sorted(rows.items())),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def place(result: dict, downloads: Path, apply: bool, repo: Path,
          keep_resaved: bool = False, future: frozenset[str] = frozenset()) -> str:
    """Move downloaded documents into <todo root>/<SUITE>/, dropping re-saves.

    A changed document whose own last-saved date is no later than its conversion was
    re-saved on the site without an edit, so it is dropped and recorded in the ignored
    table against that Modified time; a later edit moves the time and reports it again.
    `repo` is the checkout whose todo root receives the files, which is the download
    branch's worktree rather than the one this script runs from. `keep_resaved` keeps
    those re-saved documents, for a batch that is redownloaded to be converted again.
    A document already followed through its Future copy, or named in `future`, waits in
    <todo root>/<SUITE>/<FUTURE>, so it converts beside the version the web app follows.
    """
    lines = []
    ignored_rows = []
    placed = []
    formats = set(read_formats())
    if unknown := future - {item["name"] for item in result["changed"] + result["new"]}:
        sys.exit(f"place: --future names no changed or new document: {', '.join(sorted(unknown))}")
    for item in result["changed"] + result["new"]:
        item = {**item, "future": item.get("future", False) or item["name"] in future}
        source = downloads / item["name"]
        # No converted name holds a space. library.tsv keeps the library name, which
        # convert.sh hands the stamper for the Source line and the title.
        folder = todo_folder(item["suite"], item["future"])
        target = repo / TODO_ROOT / folder / hyphenated(item["name"])
        # A format convert.sh has no route for, such as a yaml contract, is left in the
        # downloads folder for its copy under the apps root to be replaced by hand.
        if Path(item["name"]).suffix.lower().lstrip(".") not in formats:
            lines.append(f"BY HAND  {item['name']}: no converter reads it, replace "
                         f"{item['replaces'] or f'its {APPS_ROOT} copy'}")
            continue
        if not source.exists() and not target.exists():
            lines.append(f"MISSING  {item['name']} is not in {downloads}")
            continue
        if not source.exists():
            lines.append(f"PLACED   {target.relative_to(repo)} (already there)")
            placed.append(item)
            continue
        day = embedded_day(source) if item["replaces"] and not keep_resaved else None
        if day and day <= item["converted"]:
            lines.append(
                f"DROPPED  {item['name']}: saved {day}, converted {item['converted']}"
            )
            ignored_rows.append(f"{item['name']}\t{item['modified']}\tre-saved, saved {day}")
            if apply:
                source.unlink()
            continue
        lines.append(f"PLACE    {item['name']} -> {target.relative_to(repo)}")
        placed.append(item)
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            # The same download can be due in two suite folders, so copy until the last.
            twins = [
                other for other in result["changed"]
                if other["name"] == item["name"] and other["replaces"] != item["replaces"]
                and not (
                    repo / TODO_ROOT
                    / todo_folder(other["suite"],
                                  other.get("future", False) or other["name"] in future)
                    / hyphenated(other["name"])
                ).exists()
            ]
            if twins:
                target.write_bytes(source.read_bytes())
            else:
                source.replace(target)
    if apply and placed:
        record_paths(repo, placed)
    if apply and ignored_rows:
        with IGNORED.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(ignored_rows) + "\n")
    return "\n".join(lines) + "\n"


def load_json(path: str | None) -> dict | None:
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else None


def check_config() -> str:
    """Read the folder table and the converter's formats as every subcommand would.

    A folder table row naming a library the config does not list, or a rule that is
    neither a listed suite nor `track` or `skip`, stops here with the row named.
    """
    folders = read_folders()
    formats = read_formats()
    return (
        f"config ok: {len(LIBRARIES)} libraries, {len(SUITES)} suites,"
        f" {len(folders)} folder rows, {len(formats)} formats\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", help="the skill's extension.json")
    sub = parser.add_subparsers(dest="command", required=True)
    pay = sub.add_parser("payload")
    pay.add_argument("--mode", choices=("scan", "survey", "links", "lookup"), default="scan")
    pay.add_argument("--name", action="append", default=[],
                     help="a library file name to report, for --mode lookup; repeatable")
    pay.add_argument("--cached", action="store_true", help="leave the index out")
    looker = sub.add_parser("lookup")
    looker.add_argument("report", help="file holding the lookup page report")
    looker.add_argument("--name", action="append", required=True,
                        help="a library file name to classify; repeatable")
    comparer = sub.add_parser("compare")
    comparer.add_argument("report", help="file holding the page report")
    comparer.add_argument("--all", action="store_true",
                          help="read a links report as if every found document had changed")
    sub.add_parser("summary").add_argument("result", help="compare output")
    body = sub.add_parser("issue-body")
    body.add_argument("--result", help="compare output")
    body.add_argument("--repo", help="checkout whose todo root is listed; default the config's")
    placer = sub.add_parser("place")
    placer.add_argument("result", help="compare output")
    placer.add_argument("--downloads", default=str(Path.home() / "Downloads"))
    placer.add_argument("--apply", action="store_true", help="move files; default only lists")
    placer.add_argument("--repo", help="checkout that receives the files; default the config's")
    placer.add_argument("--keep-resaved", action="store_true",
                        help="keep documents whose saved date is no later than their"
                        " conversion")
    placer.add_argument("--future", action="append", default=[], metavar="NAME",
                        help="a library file name whose revision the web app does not"
                        " carry yet")
    linker = sub.add_parser("link")
    linker.add_argument("report", help="file the links scan downloaded")
    linker.add_argument("--apply", action="store_true", help="write; default only counts")
    sub.add_parser("index")
    sub.add_parser("check-config")
    args = parser.parse_args()
    configure(args.config)
    if getattr(args, "repo", None) is None:
        args.repo = str(ROOT)

    if args.command == "payload":
        sys.stdout.write(payload(args.mode, args.cached, tuple(args.name)))
    elif args.command == "lookup":
        text = Path(args.report).read_text(encoding="utf-8")
        json.dump(lookup(text, args.name), sys.stdout, indent=1)
    elif args.command == "compare":
        text = Path(args.report).read_text(encoding="utf-8")
        json.dump(compare(every_document_changed(text) if args.all else text), sys.stdout,
                  indent=1)
    elif args.command == "summary":
        sys.stdout.write(summary(load_json(args.result)))
    elif args.command == "issue-body":
        sys.stdout.write(issue_body(load_json(args.result), Path(args.repo)))
    elif args.command == "place":
        result = load_json(args.result)
        sys.stdout.write(place(result, Path(args.downloads), args.apply, Path(args.repo),
                               args.keep_resaved, frozenset(args.future)))
    elif args.command == "link":
        sys.stdout.write(link(Path(args.report).read_text(encoding="utf-8"), args.apply))
    elif args.command == "check-config":
        sys.stdout.write(check_config())
    else:
        json.dump(build_index(), sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
