#!/usr/bin/env python3
"""Detects the acronyms a Markdown file uses and checks the dictionary has a
definition for every one of them.

Two modes, both taking repository-relative paths:

    acronyms.py --config <file> list  <file>...   print what each file uses,
                                                  and what has no definition yet
    acronyms.py --config <file> check <file>...   report the acronyms no
                                                  definition covers

A single - in place of the files reads the paths from stdin, one per line,
which keeps a long list off the command line. The config names the
dictionary (terms), the ignore list (ignore), the pending list (unknown), and
the records whose Author: line is a user ID (authorLineFiles); see config.py.

Exit codes: 0 clean, 2 an acronym has no definition, 64 no config. Nothing
here invents an expansion: an acronym absent from the dictionary stops the
run and names the file and line it appeared on. Files are read and never
written.
"""

import fnmatch
import os
import re
import sys

import config

CONFIG, ARGS = config.take(sys.argv[1:], "acronyms.py")
TERMS = CONFIG.path("terms") or ""
IGNORE = CONFIG.path("ignore") or ""
UNKNOWN = CONFIG.path("unknown") or ""
TERMS_NAME = os.path.basename(TERMS) or "terms"

# An expansion says what the letters stand for. A sentence explaining the thing
# belongs in the document that uses it, not in a dictionary row.
MAX_EXPANSION = 80

# A word standing alone in ordinary prose, not part of a longer identifier. The
# lookarounds are what keep CAPS_RESOURCE, MR-TOX-021, and camelCase out: an
# underscore or a hyphen on either side means the reader is looking at a column
# name or a coverage matrix id rather than an acronym. A dot counts too, which
# is what CW.ATT and .NET are, but only where it touches the word on both
# sides: a dot that ends a sentence leaves the word before it in reach.
CANDIDATE = re.compile(
    r"(?<![A-Za-z0-9_\-.])"
    r"([A-Z][A-Z0-9]*[A-Z0-9])(s?)"
    r"(?![A-Za-z0-9_\-])(?!\.[A-Za-z0-9])"
)

ROMAN = {"II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII"}

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
TABLE_ROW = re.compile(r"^\s*\|")
AUTHOR_LINE = re.compile(r"^Author: ")
AUTHOR_LINE_FILES = CONFIG.value("authorLineFiles")
AUTHOR_RECORD = re.compile(AUTHOR_LINE_FILES) if AUTHOR_LINE_FILES else None
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)*?\1", re.S)
URL = re.compile(r"(?:https?://|www\.)\S+")
PATH = re.compile(r"\S*/\S*")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def load_terms():
    """Reads the dictionary into {acronym: [(scope, expansion), ...]}."""
    terms = {}
    if not os.path.exists(TERMS):
        return terms
    with open(TERMS, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                sys.exit(f"{TERMS_NAME}: not enough columns: {line}")
            acronym, expansion = parts[0].strip(), parts[1].strip()
            scope = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "*"
            if len(f"{acronym} {expansion}") > MAX_EXPANSION:
                sys.exit(f"{TERMS_NAME}: {acronym} is expanded past {MAX_EXPANSION} characters")
            terms.setdefault(acronym, []).append((scope, expansion))
    return terms


def load_ignore():
    """Reads the words that look like acronyms and are not: SQL keywords, the
    all-caps words ordinary prose uses, and the one-offs a document brings."""
    words = set()
    if not os.path.exists(IGNORE):
        return words
    with open(IGNORE, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if line:
                words.add(line)
    return words


def load_unknown():
    """Reads the pending list: the acronyms nobody has found an expansion for."""
    if not os.path.exists(UNKNOWN):
        return set()
    with open(UNKNOWN, encoding="utf-8") as handle:
        return {l.strip() for l in handle if l.strip() and not l.startswith("#")}


def expansion_for(terms, acronym, path):
    """Picks the definition that covers this path. The longest matching scope
    wins, so an acronym can mean one thing under one application's folder and
    something else everywhere else."""
    rows = terms.get(acronym)
    if not rows:
        return None
    matches = [(scope, text) for scope, text in rows if fnmatch.fnmatch(path, scope)]
    if not matches:
        return None
    width = max(len(scope) for scope, _ in matches)
    best = {text for scope, text in matches if len(scope) == width}
    if len(best) > 1:
        sys.exit(f"{TERMS_NAME}: {acronym} has two definitions of equal reach for {path}")
    return best.pop()


def strip_fences(lines):
    """Blanks fenced blocks, keeping the line count so a hit still indexes the
    file. A fence closes on a run of at least as many markers as opened it."""
    out = []
    marker = None
    for line in lines:
        found = FENCE.match(line)
        if marker is None:
            if found:
                marker = found.group(1)
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if found and found.group(1)[0] == marker[0] and len(found.group(1)) >= len(marker):
                marker = None
    return out


def scrub(text):
    """Cuts the spans that hold identifiers rather than prose."""
    text = HTML_COMMENT.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = URL.sub(" ", text)
    return PATH.sub(" ", text)


def detect(path, terms, ignore):
    """Returns {acronym: first line number} for one file."""
    with open(path, encoding="utf-8") as handle:
        body = handle.read().split("\n")
    body = strip_fences(body)
    # A table row holds values read out of the application: facility names,
    # street addresses, county names, status codes. They arrive in capitals and
    # none of them is an acronym the reader needs expanded.
    body = ["" if TABLE_ROW.match(line) else line for line in body]
    # A record's Author: line can hold a user ID, which some accounts spell in
    # capitals, such as NY0602.
    if AUTHOR_RECORD and AUTHOR_RECORD.search(str(path).replace("\\", "/")):
        body = ["" if AUTHOR_LINE.match(line) else line for line in body]
    # Inline spans and comments both wrap across lines, so the scrub runs over
    # the whole body at once and the line numbers come from the blanked copy.
    scrubbed = scrub("\n".join(body)).split("\n")
    found = {}
    for number, line in enumerate(scrubbed, start=1):
        for match in CANDIDATE.finditer(line):
            word = match.group(1)
            if word in ROMAN:
                continue
            # A definition outranks the ignore list, so a word that is both
            # ordinary English and an acronym here is reported once the
            # dictionary says what it stands for.
            if word in ignore and expansion_for(terms, word, path) is None:
                continue
            found.setdefault(word, number)
    return found


def main():
    if len(ARGS) < 2 or ARGS[0] not in {"list", "check"}:
        sys.exit(__doc__)
    mode, paths = ARGS[0], ARGS[1:]
    if paths == ["-"]:
        # Read as bytes so the decode is UTF-8 whatever the console code page,
        # and drop the CR a Windows shell leaves on each line.
        lines = sys.stdin.buffer.read().decode("utf-8").split("\n")
        paths = [line.rstrip("\r") for line in lines if line.strip()]
    terms, ignore, pending = load_terms(), load_ignore(), load_unknown()
    undefined = 0
    waiting = set()

    for path in paths:
        found = detect(path, terms, ignore)
        missing = {w: n for w, n in found.items() if expansion_for(terms, w, path) is None}
        if mode == "list":
            for word in sorted(found):
                mark = ""
                if word in missing:
                    mark = " PENDING" if word in pending else " UNKNOWN"
                print(f"{path}:{found[word]}: {word}{mark}")
            continue
        for word in sorted(missing):
            # A word on the pending list is a real acronym nobody has found the
            # words for. It is reported and does not fail the run, so a document
            # using one still lands while the question stays visible.
            if word in pending:
                waiting.add(word)
                continue
            print(f"{path}:{missing[word]}: UNKNOWN: {word}")
            undefined += 1

    if waiting:
        print(f"pending, no expansion found yet: {', '.join(sorted(waiting))}")

    sys.exit(2 if undefined else 0)


if __name__ == "__main__":
    main()
