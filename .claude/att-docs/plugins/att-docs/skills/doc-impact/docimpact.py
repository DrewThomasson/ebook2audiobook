#!/usr/bin/env python3
"""Find what a change to the converted documents means for the test plans.

usage: docimpact.py --config <extension.json> [--state FILE] <subcommand> ...

Subcommands:
  index               print every converted document with the plans, manual test cases,
                      and specs that depend on it, as JSON
  unresolved          print the plan citations that name no converted document
  changes             print the converted documents changed in a range, with their rule
                      changes split into sections and their dependents, as JSON
  rules FILE MAP      print the business rule sets a changes run reaches, with the rule IDs
                      whose anchors sit in the changed text, as JSON. MAP is the rule
                      store's document map
  drift FILE          print the issues a drift result files, one per uploaded document
                      folder that differs from the master, and the rules still waiting in
                      staging or promoted out of it, as JSON
  record FILE         mark the documents a changes run covered, so no later run repeats them
  state               print where the reviews stand

A range is one of:
  --pr N              an open pull request, against the point it branched from main
  --since-watermark   the main ref since the last reviewed commit
  --base REV [--head REV]

The config names the roots, the ID patterns, the main ref, and the issue text; its paths
are relative to the git toplevel of the config file's folder, which is the repository read.
Everything is read from git at the reviewed revision, never from the working tree, so the
result is the same from any checkout, however stale.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent

# The convert-docs helpers sit beside this skill's folder.
sys.path.insert(0, str(HERE.parent / "convert-docs"))
from pages import MARKER as PAGE_MARKER  # noqa: E402  the line convert-docs marks a page with
from doc_paths import hyphenated  # noqa: E402  the file naming rule convert-docs keeps

# The record lives outside the repository: the scheduled scan runs in a checkout it may not
# commit to, and a review has to be able to mark what it covered from there.
STATE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))

PROVENANCE = "**Document provenance**"
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TABLE_RULE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
SPACE = re.compile(r"\s+")
DASHES = re.compile(r"[-\u2013\u2014_]+")

# Set from the config by configure(). Each is described where configure() sets it.
REPO: Path | None = None
DOCS_ROOT = TESTS_ROOT = PLAN_MARKER = NOTES_NAME = SPEC_SUFFIX = FUTURE = ""
DOCS_DEPTH = TESTS_DEPTH = 0
MAIN = REMOTE = MAIN_BRANCH = PR_REF = STATE_NAME = NUMBER_WORD = ""
LEGACY: re.Pattern | None = None
CITED = LINK_FILE = SPEC_PATH = RULE_ID = TC_ID = REQUIREMENT = re.compile("")
WINDOW: re.Pattern | None = None
DRIFT: dict = {}


def configure(config: dict, root: Path | None) -> None:
    """Set the repository's values: the roots, the ID patterns, the main ref, and the issue
    text. `root` is the repository git reads; a caller that never reads git may pass None."""
    global REPO, DOCS_ROOT, TESTS_ROOT, PLAN_MARKER, NOTES_NAME, SPEC_SUFFIX, FUTURE
    global DOCS_DEPTH, TESTS_DEPTH, MAIN, REMOTE, MAIN_BRANCH, PR_REF, STATE_NAME
    global NUMBER_WORD, LEGACY, CITED, LINK_FILE, SPEC_PATH, RULE_ID, TC_ID, REQUIREMENT
    global WINDOW, DRIFT
    REPO = root
    # Converted documents sit one folder per suite under the docs root, and a suite's plans
    # and specs under the tests root's folder of the same suite.
    DOCS_ROOT = config["docsRoot"].strip("/")
    TESTS_ROOT = config["testsRoot"].strip("/")
    DOCS_DEPTH = DOCS_ROOT.count("/") + 1
    TESTS_DEPTH = TESTS_ROOT.count("/") + 1
    # A plan is a Markdown file whose path holds the marker; the notes file beside the
    # documents is no source.
    PLAN_MARKER = config["planMarker"]
    NOTES_NAME = config["notesName"]
    SPEC_SUFFIX = config["specSuffix"]
    # The folder under a suite that holds the revisions the app does not carry yet. The
    # suite folder keeps the version the app follows.
    FUTURE = config["futureFolder"]
    MAIN = config["mainRef"]
    REMOTE, MAIN_BRANCH = MAIN.split("/", 1)
    PR_REF = config["prRef"]
    STATE_NAME = config["stateName"]
    # A plan names a numbered document by its number alone only where it speaks of this.
    NUMBER_WORD = config["numberMentionWord"].lower()
    legacy = "|".join(re.escape(r.strip("/")) for r in config["legacyRoots"])
    LEGACY = re.compile(rf"(?:{legacy})/([^/]+)/") if legacy else None
    cited = "|".join(filter(None, [legacy, re.escape(DOCS_ROOT)]))
    # A cited path can wrap onto the next line inside its backticks, and an older layout
    # sometimes cites the source file itself rather than its converted Markdown.
    CITED = re.compile(rf"`((?:{cited})/[^`]+?\.(?:md|docx?|docm))`", re.I)
    # A plan that links the document on a file share names it in the link's parameter.
    LINK_FILE = re.compile(rf"[?&]{re.escape(config['linkFileParam'])}=([^&\s)`]+)")
    SPEC_PATH = re.compile(rf"`({re.escape(TESTS_ROOT)}/[^`]+?{re.escape(SPEC_SUFFIX)})`")
    RULE_ID = re.compile(config["ruleId"])
    TC_ID = re.compile(config["manualId"])
    # A requirement number a rule's anchor may open with.
    REQUIREMENT = re.compile(config["requirementId"])
    # A screen or window code. A plan can inherit a window's rules and name the window
    # rather than citing its design document.
    WINDOW = re.compile(config["windowId"]) if config.get("windowId") else None
    # The rule tool's name and the drift issue's title, marker, and fix commands.
    DRIFT = config["drift"]


def load_config(path: str | Path) -> None:
    """Read the config file and point git at the toplevel of the config's folder."""
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding="utf-8"))
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path.parent,
                          check=True, capture_output=True, text=True).stdout.strip()
    configure(config, Path(root))


def doc_suite(path: str) -> str:
    """The suite folder a converted document sits in."""
    return path.split("/")[DOCS_DEPTH]


def plan_suite(path: str) -> str:
    """The suite folder a plan sits in."""
    return path.split("/")[TESTS_DEPTH]


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), *args], input=data, check=True,
                          capture_output=True).stdout


def decode(raw: bytes) -> str:
    """A few plans were saved in a Windows code page. A curly quote read as a replacement
    character costs nothing here, where a decode error would stop the review."""
    return raw.decode("utf-8", "replace")


def show(rev: str, path: str) -> str | None:
    """The file at a revision, or None when it does not exist there."""
    try:
        return decode(git("show", f"{rev}:{path}"))
    except subprocess.CalledProcessError:
        return None


def blob(rev: str, path: str) -> str | None:
    try:
        return decode(git("rev-parse", f"{rev}:{path}")).strip()
    except subprocess.CalledProcessError:
        return None


def rev_parse(rev: str) -> str:
    return decode(git("rev-parse", rev)).strip()


# ---------------------------------------------------------------------------------------
# The rule diff


def is_converted(text: str | None) -> bool:
    """A converted document carries a provenance block right under its title."""
    return bool(text) and PROVENANCE in "\n".join(text.splitlines()[:12])


def strip_provenance(lines: list[str]) -> list[str]:
    """Drop the provenance block: the Converted date and the Revised rung change on every
    reconversion without the document saying anything new."""
    out: list[str] = []
    # before: not reached yet; opening: blank lines under the marker; items: its list.
    # The first blank line after the list ends the block, so a body that opens with a
    # list of its own keeps it.
    phase = "before"
    for line in lines:
        if phase == "before" and line.strip() == PROVENANCE:
            phase = "opening"
            continue
        if phase == "opening" and not line.strip():
            continue
        if phase in ("opening", "items") and line.lstrip().startswith("- "):
            phase = "items"
            continue
        if phase in ("opening", "items"):
            phase = "after"
            if not line.strip():
                continue
        out.append(line)
    return out


def squash(text: str) -> str:
    return SPACE.sub(" ", text).strip()


def table_row(line: str) -> str:
    cells = [squash(cell) for cell in line.strip().strip("|").split("|")]
    return "| " + " | ".join(cells) + " |"


def units(text: str) -> list[tuple[str, str]]:
    """Split a document into (section, unit) pairs.

    A unit is a heading, a table row, a list item, or a paragraph, with its whitespace
    collapsed, so a paragraph the PDF route wrapped at a different column compares equal.
    The section is the nearest heading above the unit."""
    out: list[tuple[str, str]] = []
    section = ""
    para: list[str] = []

    def flush() -> None:
        if para:
            out.append((section, squash(" ".join(para))))
            para.clear()

    for raw in strip_provenance(text.splitlines()):
        line = raw.rstrip()
        # A page marker says where the original's page turned, which moves whenever
        # the original is laid out again, and is nothing the document says.
        if PAGE_MARKER.match(line):
            continue
        bare = line.lstrip("> ").rstrip() if line.lstrip().startswith(">") else line
        if not bare.strip():
            flush()
            continue
        if match := HEADING.match(bare):
            flush()
            section = squash(match.group(2)).strip("*").strip()
            out.append((section, "#" * len(match.group(1)) + " " + section))
        elif bare.lstrip().startswith("|"):
            flush()
            if not TABLE_RULE.match(bare.strip()):
                out.append((section, table_row(bare)))
        elif LIST_ITEM.match(bare):
            flush()
            para.append(bare.strip())
        else:
            para.append(bare.strip())
    flush()
    return out


def rule_changes(old: str | None, new: str | None) -> dict:
    """The units a change removed and added, grouped into hunks by section. A new or
    removed document is reviewed whole, so it carries no hunks."""
    if old is None or new is None:
        return {"kind": "added" if old is None else "removed", "hunks": []}
    a = units(old)
    b = units(new)
    # The PDF route decides from layout alone whether a short line is a heading, so the
    # same line can come back as a heading in one conversion and a paragraph in the next.
    ka = [unit.lstrip("#").strip() for _, unit in a]
    kb = [unit.lstrip("#").strip() for _, unit in b]
    if ka == kb:
        return {"kind": "unchanged", "hunks": []}
    if SPACE.sub("", "".join(ka)) == SPACE.sub("", "".join(kb)):
        return {"kind": "layout", "hunks": []}
    matcher = difflib.SequenceMatcher(None, ka, kb, autojunk=False)
    hunks = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        removed = [u for _, u in a[i1:i2]]
        added = [u for _, u in b[j1:j2]]
        # A section heading on the new side names where the change landed.
        if added:
            section = b[j1][0]
        else:
            section = a[i1][0] if i1 < len(a) else ""
        # Every section the hunk runs through, for a change that crosses a heading.
        spans = list(dict.fromkeys(s for s, _ in a[i1:i2] + b[j1:j2])) or [section]
        hunks.append({"section": section, "sections": spans, "removed": removed,
                      "added": added})
    return {"kind": "content", "hunks": hunks}


# ---------------------------------------------------------------------------------------
# One revision's documents and plans


class Snapshot:
    """The converted documents, test plans, and spec paths of one revision."""

    def __init__(self, texts: dict[str, str], paths: set[str]):
        self.texts = texts
        self.paths = paths
        self._windows: dict[str, set[str]] = {}
        self._cases: dict[str, set[str]] = {}

    # A batch can change hundreds of documents, and each one asks every file the same
    # two questions, so each file is read for them once.
    def windows(self, path: str) -> set[str]:
        if path not in self._windows:
            self._windows[path] = windows_in(self.texts[path])
        return self._windows[path]

    def cases(self, path: str) -> set[str]:
        if path not in self._cases:
            self._cases[path] = set(TC_ID.findall(self.texts[path]))
        return self._cases[path]

    @classmethod
    def at(cls, rev: str) -> Snapshot:
        listing = decode(git("ls-tree", "-r", "-z", "--format=%(objectname) %(path)",
                             rev, "--", DOCS_ROOT, TESTS_ROOT))
        paths: set[str] = set()
        wanted: list[tuple[str, str]] = []
        for entry in filter(None, listing.split("\0")):
            oid, path = entry.split(" ", 1)
            paths.add(path)
            if cls.readable(path):
                wanted.append((oid, path))
        batch = git("cat-file", "--batch", data="".join(f"{o}\n" for o, _ in wanted).encode())
        texts: dict[str, str] = {}
        pos = 0
        for _, path in wanted:
            header_end = batch.index(b"\n", pos)
            size = int(batch[pos:header_end].split()[2])
            start = header_end + 1
            texts[path] = decode(batch[start:start + size])
            pos = start + size + 1
        return cls(texts, paths)

    @classmethod
    def of_directory(cls, root: Path) -> Snapshot:
        paths = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        texts = {p: decode((root / p).read_bytes()) for p in paths if cls.readable(p)}
        return cls(texts, paths)

    @staticmethod
    def readable(path: str) -> bool:
        return path.endswith(".md") and (path.startswith(f"{DOCS_ROOT}/")
                                         or PLAN_MARKER in path)

    def plans(self, suite: str | None = None) -> list[str]:
        prefix = f"{TESTS_ROOT}/{suite}/" if suite else f"{TESTS_ROOT}/"
        return sorted(p for p in self.texts if p.startswith(prefix) and PLAN_MARKER in p)

    def app_docs(self) -> list[str]:
        return sorted(p for p in self.texts if p.startswith(f"{DOCS_ROOT}/"))

    def specs_beside(self, plan: str) -> list[str]:
        folder = plan.rsplit("/", 1)[0] + "/"
        return sorted(p for p in self.paths if p.startswith(folder)
                      and p.endswith(SPEC_SUFFIX) and "/" not in p[len(folder):])


def name_key(name: str) -> str:
    """A document name reduced to what survives the ways plans misquote it: case, runs of
    spaces, the hyphens a file name writes them as, and the source extension the older
    layout kept in the file name."""
    stem = re.sub(r"\.(md|docx?|docm|pdf|xlsx?|pptx?)$", "", name.strip(), flags=re.I)
    # A revision history copy is an older save of the same document.
    stem = re.sub(r"_Rev(ision)?\s*\d+(\.\d+)*$", "", stem, flags=re.I)
    return hyphenated(squash(stem)).lower()


def converted_docs(snap: Snapshot) -> dict[str, str]:
    """Every converted document under the docs root, keyed by name_key, to its repo path.

    A name held by two suite folders keys to both, joined by a tab, so a citation that
    cannot say which one it meant stays visibly ambiguous."""
    docs: dict[str, str] = {}
    for path in snap.app_docs():
        if not is_converted(snap.texts[path]):
            continue
        key = name_key(path.split("/")[-1])
        docs[key] = f"{docs[key]}\t{path}" if key in docs else path
    return docs


def all_paths(docs: dict[str, str]) -> set[str]:
    return {path for paths in docs.values() for path in paths.split("\t")}


def is_future(path: str) -> bool:
    """Whether a converted document sits in its suite's Future folder."""
    parts = path.split("/")
    return len(parts) > DOCS_DEPTH + 2 and parts[DOCS_DEPTH + 1] == FUTURE


def current_of(path: str, docs: dict[str, str]) -> str | None:
    """The suite folder's copy of a Future document, the version the app follows."""
    current = path.replace(f"/{FUTURE}/", "/", 1)
    held = docs.get(name_key(current.split("/")[-1]), "").split("\t")
    return current if is_future(path) and current in held else None


def resolve(cited: str, suite: str, docs: dict[str, str]) -> list[str]:
    """The converted documents a cited path or name means. A citation of an older
    `<legacy root>/<app>/...` layout, or a bare name, is matched on its last segment, and a
    name held by two suites goes to the one the citation or the citing plan belongs to. A
    name with a Future copy means the suite folder's copy, which the app follows."""
    last = cited.rstrip("/").split("/")[-1]
    hit = docs.get(name_key(last))
    if not hit:
        return []
    paths = hit.split("\t")
    paths = [p for p in paths if not is_future(p)] or paths
    if len(paths) > 1:
        legacy = LEGACY.match(cited) if LEGACY else None
        want = (legacy.group(1) if legacy else suite).upper()
        preferred = [p for p in paths if doc_suite(p).upper() == want]
        paths = preferred or paths
    return paths


def closest(cited: str, docs: dict[str, str]) -> str | None:
    """The nearest converted name to one that resolved to nothing, offered as a hint for
    whoever fixes the citation and never used as a match."""
    key = name_key(cited.rstrip("/").split("/")[-1])
    near = difflib.get_close_matches(key, list(docs), n=1, cutoff=0.75)
    return docs[near[0]].split("\t")[0] if near else None


def plan_citations(snap: Snapshot, plan: str, docs: dict[str, str]) -> dict:
    """The documents one plan cites, the specs it names, and the citations that resolve to
    nothing, with the nearest converted name for each."""
    text = snap.texts[plan]
    suite = plan_suite(plan)
    sources = all_paths(docs)
    cited: set[str] = set()
    unresolved = []

    def take(target: str) -> None:
        found = resolve(target, suite, docs)
        if found:
            cited.update(found)
        else:
            unresolved.append({"cited": target, "closest": closest(target, docs)})

    for match in CITED.finditer(text):
        target = re.sub(r"\s*\n\s*", " ", match.group(1))
        target = re.sub(r"\.(docx?|docm)$", ".md", target, flags=re.I)
        if target.startswith(f"{DOCS_ROOT}/") and target in snap.paths:
            # A note beside the documents, such as the suite's notes file, is not a source.
            if target in sources:
                cited.add(target)
            continue
        take(target)
    for match in LINK_FILE.finditer(text):
        take(unquote(match.group(1)).replace("+", " "))
    if not cited and not unresolved:
        unresolved.append({"cited": "(no document citation)", "closest": None})
    specs = sorted({m.group(1) for m in SPEC_PATH.finditer(text) if m.group(1) in snap.paths})
    return {"docs": sorted(cited), "specs": specs or snap.specs_beside(plan),
            "unresolved": unresolved}


def title_form(text: str) -> str:
    """Text reduced so a title quoted in prose matches the file name: no dashes, no zero
    padding, no case, one space between words. `PD 08 – Portal Request ...` and
    `8 - Portal Request ...` read the same."""
    text = DASHES.sub(" ", text.lower())
    text = re.sub(r"\b0+(\d)", r"\1", text)
    return " " + squash(re.sub(r"[`*#|]", " ", text)) + " "


def title_mentions(snap: Snapshot, docs: dict[str, str],
                   cited: dict[str, set[str]]) -> dict[str, list[str]]:
    """Plans that name a document of their own suite by its title rather than by a path.

    Only titles of four words or more count, so a one-word document name such as Security
    cannot match ordinary prose."""
    by_suite: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(all_paths(docs)):
        title = title_form(path.split("/")[-1][:-3])
        if len(title.split()) >= 4:
            by_suite.setdefault(doc_suite(path), []).append((title, path))
    found: dict[str, list[str]] = {}
    for plan in snap.plans():
        text = title_form(snap.texts[plan])
        for title, path in by_suite.get(plan_suite(plan), []):
            if title in text and path not in cited.get(plan, set()):
                found.setdefault(path, []).append(plan)
    return found


def rule_sources(snap: Snapshot, docs: dict[str, str]) -> dict[str, set[str]]:
    """The business rules each converted document is the source of.

    A business-rule table names each rule's source file in a Document column, which is
    how a change to that document reaches the rule and every manual case that cites it."""
    rules: dict[str, set[str]] = {}
    for md in snap.app_docs():
        text = snap.texts[md]
        if not RULE_ID.search(text):
            continue
        column = None
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                column = None
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            named = [i for i, cell in enumerate(cells)
                     if re.fullmatch(r"(source )?document", cell.strip("*").lower())]
            if named and not RULE_ID.search(line):
                column = named[0]
                continue
            ids = RULE_ID.findall(line)
            if column is None or column >= len(cells) or not ids:
                continue
            source = re.sub(r"\s*\(\d+\)(?=\.\w+$|$)", "", cells[column])
            for path in resolve(source, doc_suite(md), docs):
                rules.setdefault(path, set()).update(ids)
    return rules


def build_index(snap: Snapshot) -> dict:
    """Every converted document with the plans that depend on it, the rules each one is
    the source of, and every citation that resolved to nothing."""
    docs = converted_docs(snap)
    dependents: dict[str, list[dict]] = {}
    unresolved = []
    cited: dict[str, set[str]] = {}
    specs: dict[str, list[str]] = {}
    for plan in snap.plans():
        found = plan_citations(snap, plan, docs)
        cited[plan] = set(found["docs"])
        specs[plan] = found["specs"]
        for doc in found["docs"]:
            dependents.setdefault(doc, []).append(
                {"kind": "plan", "file": plan, "specs": found["specs"]})
        for miss in found["unresolved"]:
            unresolved.append({"file": plan, **miss})
    for doc, plans in title_mentions(snap, docs, cited).items():
        for plan in plans:
            dependents.setdefault(doc, []).append(
                {"kind": "title", "file": plan, "specs": specs[plan]})
    rules = {doc: sorted(ids) for doc, ids in rule_sources(snap, docs).items()}
    return {"docs": docs, "dependents": dependents, "rules": rules, "unresolved": unresolved,
            "specs": specs}


def citing_gone(index: dict, gone: str) -> list[dict]:
    """The plans that still cite a document the range renamed or removed. The index is
    built at the head of the range, where that name no longer exists, so those citations
    sit among the unresolved ones rather than under any document."""
    want = name_key(gone.split("/")[-1])
    plans = sorted({miss["file"] for miss in index["unresolved"]
                    if name_key(miss["cited"].rstrip("/").split("/")[-1]) == want})
    return [{"kind": "plan", "file": plan, "specs": index["specs"].get(plan, [])}
            for plan in plans]


# ---------------------------------------------------------------------------------------
# What a changed document reaches beyond the plans that cite it


def cases_citing(snap: Snapshot, ids: set[str]) -> list[dict]:
    """The manual test case rows under the docs root and the plans that cite any of these
    rules, with the manual test case ids each one names."""
    if not ids:
        return []
    found = []
    files = [(md, "manual") for md in snap.app_docs()]
    files += [(plan, "plan-rule") for plan in snap.plans()]
    for path, kind in files:
        text = snap.texts[path]
        if not RULE_ID.search(text):
            continue
        rules: set[str] = set()
        cases: set[str] = set()
        for line in text.splitlines():
            hit = ids & set(RULE_ID.findall(line))
            if hit:
                rules |= hit
                cases |= set(TC_ID.findall(line))
        if rules and (kind == "plan-rule" or cases):
            found.append({"kind": kind, "file": path, "rules": sorted(rules),
                          "cases": sorted(cases)})
    return found


def window_mentions(snap: Snapshot, codes: set[str]) -> list[dict]:
    """The plans, automation notes, and manual test packs that name any of the windows a
    change touched. A manual pack can carry rule ids that hold a window's code."""
    if not codes:
        return []
    files = snap.plans()
    files += [p for p in snap.app_docs()
              if p.endswith(f"/{NOTES_NAME}") or snap.cases(p)]
    found = []
    for path in files:
        named = codes & snap.windows(path)
        if named:
            found.append({"kind": "window", "file": path, "windows": sorted(named),
                          "cases": sorted(snap.cases(path))})
    return found


def windows_in(text: str) -> set[str]:
    """The window codes a text names, none when the config has no window pattern."""
    return set(WINDOW.findall(text)) if WINDOW else set()


def touched_windows(doc: dict, text: str | None) -> set[str]:
    """The window names in a change's hunks, or in the whole text of a new document, plus
    the window the document itself is named for, which every change to it touches."""
    own = windows_in(doc["path"].split("/")[-1])
    if doc["kind"] == "added":
        return own | windows_in(text or "")
    return own | {code for hunk in doc["hunks"] for unit in hunk["removed"] + hunk["added"]
                  for code in windows_in(unit)}


def unnumbered(name: str) -> str:
    """A document's title without its leading number, in title_form."""
    return re.sub(r"^ \d+ ", " ", title_form(re.sub(r"\.md$", "", name)))


def predecessor(path: str, docs: dict[str, str]) -> str | None:
    """The converted document a new one replaces under a new number: same suite, same
    title once the leading number is dropped. A template renumbered when it is reissued
    (`293 Notice` coming back as `446 Notice`) is covered by the plans that covered the old
    number. A new Future document replaces its suite folder's copy, and only a Future
    document can replace by way of the Future folder."""
    if current := current_of(path, docs):
        return current
    name = path.split("/")[-1]
    if not re.match(r"\d", name):
        return None
    want = unnumbered(name)
    suite = doc_suite(path)
    for other in sorted(all_paths(docs)):
        other_name = other.split("/")[-1]
        if (other != path and doc_suite(other) == suite
                and (is_future(path) or not is_future(other))
                and re.match(r"\d", other_name) and unnumbered(other_name) == want):
            return other
    return None


def number_mentions(snap: Snapshot, earlier: str) -> list[dict]:
    """Plans of the same suite that name a numbered document by its number alone, such
    as "letters 294/295". A line counts when it holds the number and the plan holds the
    config's number mention word somewhere, so an ID or a count that happens to share the
    digits in a plan about something else does not."""
    number = re.match(r"(\d+)", earlier.split("/")[-1])
    if not number:
        return []
    pattern = re.compile(rf"(?<![\w-]){number.group(1)}(?![\w-])")
    found = []
    for plan in snap.plans(doc_suite(earlier)):
        text = snap.texts[plan]
        if NUMBER_WORD not in text.lower():
            continue
        lines = [n for n, line in enumerate(text.splitlines(), 1) if pattern.search(line)]
        if lines:
            found.append({"kind": "number", "file": plan, "number": number.group(1),
                          "lines": lines})
    return found


# ---------------------------------------------------------------------------------------
# The business rules a changed document is the source of

# A top-level numbered rule: a line at the left margin opening with `66.`. A nested list
# restarts at 1, so an indented number is never an anchor.
NUMBERED = re.compile(r"^(\d+)\.\s+(.*)$")
PAGE = re.compile(r"[,.]\s*Page\b.*$", re.I)
# Anchors that name a kind of text rather than where it is: `Bullet Item`, `Page 4, Bullet
# 2`, `Unanchored Text`. Any other bare anchor, `Screen Print` or `Navigation`, is a heading.
GENERIC = re.compile(r"(?:Bullet|Page|Rule|Requirement|Text|Unanchored|Paragraph|Item)\b",
                     re.I)


def numbered_rules(text: str) -> list[tuple[int, str]]:
    """The document's top-level numbered rules, each with every indented line under it."""
    out: list[tuple[int, list[str]]] = []
    inside = False
    for line in strip_provenance(text.splitlines()):
        # A page marker sits between blocks without ending the rule it falls inside.
        if PAGE_MARKER.match(line):
            continue
        if match := NUMBERED.match(line):
            out.append((int(match.group(1)), [match.group(2)]))
            inside = True
        elif inside and re.match(r"\s{2,}\S", line):
            out[-1][1].append(line.strip())
        elif line.strip():
            # A paragraph at the margin ends the rule above it.
            inside = False
    return [(number, squash(" ".join(body))) for number, body in out]


def changed_numbers(old: str, new: str) -> tuple[set[int], bool]:
    """The rule numbers whose text a change touched, added, or removed, and whether either
    side gives one number to two rules because its numbering restarts per section."""
    sides = [numbered_rules(old), numbered_rules(new)]
    restarts = any(len({n for n, _ in side}) < len(side) for side in sides)
    before: dict[int, list[str]] = {}
    after: dict[int, list[str]] = {}
    for number, body in sides[0]:
        before.setdefault(number, []).append(body)
    for number, body in sides[1]:
        after.setdefault(number, []).append(body)
    return {n for n in before.keys() | after.keys() if before.get(n) != after.get(n)}, restarts


def anchor_of(rule: dict) -> tuple[str, str | int] | None:
    """What a rule is placed by: its numbered rule, its requirement number, or the section it
    names or sits under. The anchor is the parenthetical a description opens with, such as
    `Rule 6.e, Page 3` or `Requirement # REQ-5.2.3.1, Page 4`. A bullet or unanchored text
    places the rule by the heading it sits under, when the store holds one."""
    head = PAGE.sub("", rule.get("anchor") or "").strip()
    # `Section 42.iv` is numbered rule 42, written the way some workbooks write it.
    if match := re.match(r"Section\s+(\d+)\b", head, re.I):
        return "number", int(match.group(1))
    if match := re.match(r'Section\s*-?\s*"?([^"]+)"?', head, re.I):
        return "section", match.group(1).strip()
    # `Business Rules` alone is the heading of that name, not a rule number.
    if match := re.match(r"(?:Requirement\s*#?|(?:Business\s+)?Rules?)\s+(?=\S)(.*)",
                         head, re.I):
        head = match.group(1).strip()
    if match := REQUIREMENT.match(head):
        return "requirement", match.group(0).rstrip(",.")
    if match := re.match(r"(\d+)\b", head):
        return "number", int(match.group(1))
    if head and not GENERIC.match(head):
        return "section", head
    section = (str(rule.get("section") or "")).strip()
    # Rules loaded from the rule tool name a page there, which a converted document does
    # not have.
    if section and not section.isdigit():
        return "section", section
    return None


def anchor_key(text: str) -> str:
    """Text in title_form with punctuation dropped, a dot kept only inside a number, so
    `(REQ-5.2.3.1).` and `Brief Description of Process:` compare by their words."""
    text = re.sub(r"[^\w.]+", " ", title_form(text))
    return " " + squash(re.sub(r"\.+(?=\s|$)", " ", text)) + " "


def anchored_rules(rules: list[dict], old: str, new: str, hunks: list[dict]) -> dict:
    """The rules whose anchors sit in what a change touched."""
    numbers, restarts = changed_numbers(old, new)
    # A heading carries a number, a colon, or a qualifier the anchor leaves off:
    # `Screen Print (if applicable): Sort Notes` is the `Screen Print` section.
    sections = [re.sub(r"^ [\d.]+ ", " ", anchor_key(section)) for hunk in hunks
                for section in hunk.get("sections", [hunk["section"]])]
    changed = [anchor_key(unit) for hunk in hunks for unit in hunk["removed"] + hunk["added"]]
    found = []
    for rule in rules:
        anchor = anchor_of(rule)
        if anchor is None:
            continue
        kind, value = anchor
        if kind == "number":
            hit = value in numbers
        elif kind == "requirement":
            hit = any(anchor_key(str(value)) in unit for unit in changed)
        else:
            hit = any(section.startswith(anchor_key(str(value))) for section in sections)
        if hit:
            found.append({"rule_id": rule["rule_id"], "anchor": f"{kind} {value}"})
    return {"changed": found, "restarts": restarts}


def rule_refresh(result: dict, rule_map: dict, read=show) -> list[dict]:
    """One item per changed document the business rule map holds, naming the prefix, the
    rule count, and the rules whose anchors the change touched. A document the map does
    not hold has no rules to refresh: its first extraction is a choice, not a review item."""
    mapped = {entry["doc"]: entry for entry in rule_map["documents"]}
    items = []
    for doc in result["documents"]:
        entry = next((mapped[p] for p in (doc["path"], doc.get("old_path"),
                                          doc.get("predecessor"), doc.get("current"))
                      if p in mapped), None)
        if entry is None:
            continue
        moved = entry["doc"] != doc["path"]
        if doc["kind"] in ("unchanged", "layout") and not moved:
            continue
        item = {"doc": doc["path"], "map_doc": entry["doc"], "key": doc["key"],
                "prefix": entry["prefix"], "rules": len(entry["rules"]), "kind": doc["kind"],
                "changed": [], "restarts": False, "future": doc.get("future", False)}
        if doc["kind"] == "removed":
            # Every rule the removed document was the source of is up for retiring.
            item["changed"] = [{"rule_id": r["rule_id"], "anchor": "document removed"}
                               for r in entry["rules"]]
        elif doc["kind"] == "content":
            if doc.get("predecessor") and entry["doc"] == doc["predecessor"]:
                old = read(result["head"], doc["predecessor"])
            else:
                old = read(result["base"], doc.get("old_path") or doc["path"])
            new = read(result["head"], doc["path"])
            item.update(anchored_rules(entry["rules"], old or "", new or "", doc["hunks"]))
        items.append(item)
    return items


# ---------------------------------------------------------------------------------------
# Drift: the business rule folders uploaded to the rule tool against the master


DRIFT_KINDS = ("missing", "changed", "moved", "extra", "attachments", "other_attachments")


def drift_fingerprint(report: dict) -> str:
    """The first 12 of a SHA-256 over what differs, so a run that finds the same drift as
    an earlier one finds its marker and adds nothing."""
    body = json.dumps({"folder": report["drift"]["folder"],
                       **{k: report["drift"][k] for k in DRIFT_KINDS}}, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def cell(value) -> str:
    """A value as one Markdown table cell."""
    text = "" if value is None else str(value)
    return SPACE.sub(" ", text).replace("|", "\\|").strip() or "(empty)"


def drift_title(report: dict) -> str:
    return DRIFT["title"].format(prefix=report["prefix"], title=report["title"])


def drift_body(report: dict, suite: dict, today: str, fingerprint: str) -> str:
    """The issue section for one document folder's drift: every differing rule and field
    with both values, the attachment hashes, which way the fix probably goes, and the
    marker a later run searches for."""
    drift = report["drift"]
    folder = report["folder"]
    tool = DRIFT["tool"]
    where = ("in staging" if folder["in_staging"] else
             f"promoted out of staging on {folder['promoted_on']}"
             if folder["in_staging"] is False else "staging folder not known")
    lines = [f"### {tool} drift found {today}", "",
             f"Document: `{report['doc']}`, prefix {report['prefix']}, "
             f"{report['rules']} active rules, {tool} document folder {folder['id']} "
             f"({where}).", ""]
    if drift["folder"]:
        lines += [f"Document folder: {drift['folder']}.", ""]
    if drift["changed"]:
        lines += ["Fields that differ:", "", f"| Rule | Requirement | Field | {tool} | Master |",
                  "|---|---|---|---|---|"]
        for rule in drift["changed"]:
            for f in rule["fields"]:
                lines.append(f"| {rule['rule_id']} | {rule['alm_req_id']} | "
                             f"{f['column']} (`{f['field']}`) | {cell(f['alm'])} | "
                             f"{cell(f['master'])} |")
        lines.append("")
    if drift["missing"]:
        lines += [f"Missing from {tool}:", ""]
        lines += [f"- {m['rule_id']}" + (f" (requirement {m['alm_req_id']})"
                                         if m["alm_req_id"] else "") + f": {m['reason']}"
                  for m in drift["missing"]]
        lines.append("")
    if drift["moved"]:
        lines += ["Moved to another folder under staging:", ""]
        lines += [f"- {m['rule_id']} (requirement {m['alm_req_id']}): recorded in folder "
                  f"{m['from']}, now in folder {m['to']}" for m in drift["moved"]]
        lines.append("")
    if drift["extra"]:
        lines += ["In the document's folders with no active rule to account for it:", ""]
        lines += [f"- requirement {e['id']} \"{e['name']}\" in folder {e['folder']}"
                  for e in drift["extra"]]
        lines.append("")
    if drift["attachments"]:
        lines += ["Attachments:", "", f"| File | State | {tool} SHA-256 | Master SHA-256 |",
                  "|---|---|---|---|"]
        lines += [f"| {a['file']} | {a['state']} | {a['alm_sha'] or 'none'} | "
                  f"{a['master_sha']} |" for a in drift["attachments"]]
        lines.append("")
    if drift["other_attachments"]:
        lines += ["Other attachments on the document folder: "
                  + ", ".join(f"`{name}`" for name in drift["other_attachments"]), ""]

    resend = DRIFT["resend" if report["staging_id"] else "resendUnstaged"].format(
        folder=suite["folder"], staging_id=report["staging_id"])
    update = DRIFT["update"].format(doc=report["doc"])
    fixes = []
    if drift["changed"]:
        fixes.append(f"Changed fields: when the {tool} text is an edit a reviewer meant, take "
                     f"it into the master with {update}; "
                     f"otherwise resend from the master with {resend}.")
    if drift["missing"] or drift["attachments"] or drift["folder"]:
        fixes.append(f"Missing rules, attachments, or folder: resend from the master with "
                     f"{resend}.")
    if drift["moved"] or drift["extra"] or drift["other_attachments"]:
        fixes.append("Moved rules and requirements or attachments no rule accounts for: a "
                     f"person sorts these out in {tool}; the upload leaves them where they "
                     "are.")
    lines += ["Which way the fix probably goes:", ""] + [f"- {fix}" for fix in fixes]
    lines += ["", f"This review writes nothing to {tool} or the master's rule text.", "",
              DRIFT["marker"].format(doc=report["doc"], prefix=report["prefix"],
                                     fingerprint=fingerprint)]
    return "\n".join(lines)


def drift_review(result: dict) -> dict:
    """Reads a drift result into the issues to file, one per document folder that
    differs from the master, and the staging lists the report carries: the rules still
    waiting in staging by upload day, and what was promoted out of it this run."""
    items, waiting, promoted, folders = [], [], [], []
    clean = 0
    for suite in result["suites"]:
        for report in suite["docs"]:
            if report["clean"]:
                clean += 1
            else:
                fingerprint = drift_fingerprint(report)
                items.append({"doc": report["doc"], "prefix": report["prefix"],
                              "title": drift_title(report), "fingerprint": fingerprint,
                              "body": drift_body(report, suite, result["today"], fingerprint)})
            days = [{"uploaded_on": w["uploaded_on"], "count": len(w["rules"]),
                     "rules": w["rules"]} for w in report["waiting"]]
            if days:
                waiting.append({"doc": report["doc"], "prefix": report["prefix"],
                                "folder": report["folder"]["id"],
                                "count": sum(d["count"] for d in days), "by_day": days})
            promoted += [{"doc": report["doc"], **p} for p in report["promoted"]]
            if report["folder"]["newly_promoted"]:
                folders.append({"doc": report["doc"], "folder": report["folder"]["id"],
                                "promoted_on": report["folder"]["promoted_on"]})
    return {"today": result["today"], "recorded": result["recorded"], "clean": clean,
            "notes": result.get("notes", []), "items": items, "waiting": waiting,
            "promoted": promoted, "folders_promoted": folders}


# ---------------------------------------------------------------------------------------
# Ranges and the reviewed record


def load_state(path: Path) -> dict:
    """The last reviewed main commit, and every (document, blob) a review covered."""
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.setdefault("watermark", None)
    state.setdefault("reviewed", {})
    return state


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def pr_range(number: int) -> tuple[str, str]:
    """An open pull request's head, and the main commit it branched from."""
    git("fetch", "-q", REMOTE, PR_REF.format(number=number))
    head = rev_parse("FETCH_HEAD")
    git("fetch", "-q", REMOTE, MAIN_BRANCH)
    return decode(git("merge-base", MAIN, head)).strip(), head


def changed_docs(base: str, head: str) -> list[dict]:
    """The converted documents a range added, changed, renamed, or removed.

    Rename detection pairs a document moved to a new name with its old text, so a move
    with no edit reads as unchanged rather than as a removal and a new document."""
    fields = decode(git("diff", "--name-status", "-M", "-z", base, head, "--",
                        DOCS_ROOT)).split("\0")
    docs = []
    i = 0
    while i < len(fields) and fields[i]:
        status = fields[i]
        if status[0] in "RC":
            old_path, path = fields[i + 1], fields[i + 2]
            i += 3
        else:
            old_path = path = fields[i + 1]
            i += 2
        if not path.endswith(".md"):
            continue
        old = None if status[0] == "A" else show(base, old_path)
        new = None if status[0] == "D" else show(head, path)
        if not (is_converted(old) or is_converted(new)):
            continue
        new_blob = blob(head, path) if new is not None else None
        docs.append({
            "status": status[0],
            "path": path,
            "old_path": old_path if old_path != path else None,
            "blob": new_blob,
            # What the record and the issue marker name: the blob a review read, or for a
            # removal the blob that was removed, so a removal is covered once as well.
            "key": new_blob or f"removed-{blob(base, old_path)}",
            **rule_changes(old if is_converted(old) else None,
                           new if is_converted(new) else None),
        })
    return docs


def review_range(args: argparse.Namespace, state: dict) -> tuple[str, str]:
    if args.pr:
        return pr_range(args.pr)
    if args.base:
        return rev_parse(args.base), rev_parse(args.head or MAIN)
    git("fetch", "-q", REMOTE, MAIN_BRANCH)
    head = rev_parse(MAIN)
    return state["watermark"] or head, head


def dependents_of(doc: dict, snap: Snapshot, index: dict) -> list[dict]:
    deps = list(index["dependents"].get(doc["path"], []))
    if doc["old_path"]:
        deps += citing_gone(index, doc["old_path"])
    if doc["status"] == "D":
        deps += citing_gone(index, doc["path"])
    if doc["predecessor"]:
        deps += index["dependents"].get(doc["predecessor"], [])
        deps += number_mentions(snap, doc["predecessor"])
    elif doc.get("current"):
        # Plans cite the suite folder's copy, so a Future revision reaches its dependents.
        deps += index["dependents"].get(doc["current"], [])
    listed = {dep["file"] for dep in deps}
    text = snap.texts.get(doc["path"])
    deps += [w for w in window_mentions(snap, touched_windows(doc, text))
             if w["file"] not in listed]
    # The rules this document is the source of, and any rule a changed unit quotes.
    ids = set(index["rules"].get(doc["path"], []))
    ids |= {rule for hunk in doc["hunks"] for unit in hunk["removed"] + hunk["added"]
            for rule in RULE_ID.findall(unit)}
    deps += [c for c in cases_citing(snap, ids) if c["file"] != doc["path"]]
    return deps


def changes(args: argparse.Namespace, state: dict) -> dict:
    """The changed converted documents in a range, each with its dependents, leaving out
    the ones an earlier review already covered at the same blob."""
    base, head = review_range(args, state)
    out = {"base": base, "head": head, "pr": args.pr, "first_run": False,
           "reviewed_before": [], "documents": [], "unresolved": []}
    if not args.pr and not args.base and state["watermark"] is None:
        # A first run has nothing to compare against and would otherwise review all of
        # history; it starts the record at the current main instead.
        out["first_run"] = True
        return out
    snap = Snapshot.at(head)
    index = build_index(snap)
    out["unresolved"] = index["unresolved"]
    for doc in changed_docs(base, head):
        if doc["key"] in state["reviewed"].get(doc["path"], []):
            out["reviewed_before"].append(doc["path"])
            continue
        found = predecessor(doc["path"], index["docs"]) if doc["status"] == "A" else None
        doc["predecessor"] = found
        doc["future"] = is_future(doc["path"])
        # A removed Future copy is a promotion, which the suite copy's own change covers.
        doc["current"] = (current_of(doc["path"], index["docs"])
                          if doc["status"] != "D" else None)
        if found:
            # Reviewed as a revision of the document it replaces.
            doc.update(rule_changes(snap.texts.get(found), snap.texts.get(doc["path"])))
        out["documents"].append({**doc, "dependents": dependents_of(doc, snap, index)})
    return out


def record(result: dict, state: dict) -> dict:
    """Mark every document a review covered. A review of main also moves the watermark; a
    pull request review leaves it, because its commits have not reached main yet."""
    for doc in result["documents"]:
        seen = state["reviewed"].setdefault(doc["path"], [])
        if doc["key"] not in seen:
            seen.append(doc["key"])
    if not result["pr"]:
        state["watermark"] = result["head"]
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", help="the extension.json naming the repository's values")
    parser.add_argument("--state", help="the reviewed record")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("index", "unresolved"):
        sub.add_parser(name).add_argument("--rev", help="revision to read, the main ref "
                                          "by default")
    sub.add_parser("state")
    change = sub.add_parser("changes")
    group = change.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr", type=int)
    group.add_argument("--since-watermark", action="store_true")
    group.add_argument("--base")
    change.add_argument("--head")
    rules = sub.add_parser("rules")
    rules.add_argument("result", help="the changes output under review")
    rules.add_argument("map", help="the rule store's document map")
    sub.add_parser("drift").add_argument("result", help="the drift result")
    sub.add_parser("record").add_argument("result", help="the changes output reviewed")
    args = parser.parse_args()
    if not args.config:
        parser.error("--config <extension.json> is required")
    if not Path(args.config).is_file():
        parser.error(f"--config {args.config}: no such file")
    load_config(args.config)
    state_path = Path(args.state or STATE / STATE_NAME / "state.json")
    state = load_state(state_path)

    if args.command == "index":
        json.dump(build_index(Snapshot.at(args.rev or MAIN))["dependents"], sys.stdout,
                  indent=1)
    elif args.command == "unresolved":
        for miss in build_index(Snapshot.at(args.rev or MAIN))["unresolved"]:
            hint = f"  (closest: {miss['closest']})" if miss["closest"] else ""
            print(f"{miss['file']}: {miss['cited']}{hint}")
    elif args.command == "state":
        reviewed = sum(len(blobs) for blobs in state["reviewed"].values())
        print(f"watermark: {state['watermark'] or 'none, the next run starts the record'}")
        print(f"reviewed: {reviewed} blob(s) across {len(state['reviewed'])} document(s)")
    elif args.command == "changes":
        json.dump(changes(args, state), sys.stdout, indent=1)
    elif args.command == "rules":
        result = json.loads(Path(args.result).read_text(encoding="utf-8"))
        rule_map = json.loads(Path(args.map).read_text(encoding="utf-8"))
        json.dump(rule_refresh(result, rule_map), sys.stdout, indent=1)
    elif args.command == "drift":
        result = json.loads(Path(args.result).read_text(encoding="utf-8"))
        json.dump(drift_review(result), sys.stdout, indent=1)
    else:
        result = json.loads(Path(args.result).read_text(encoding="utf-8"))
        save_state(state_path, record(result, state))
        print(f"recorded {len(result['documents'])} document(s)"
              + ("" if result["pr"] else f", watermark {result['head'][:9]}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
