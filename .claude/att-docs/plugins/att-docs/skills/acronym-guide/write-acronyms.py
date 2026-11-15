#!/usr/bin/env python3
"""Renders the dictionary page from the dictionary and the pending list.

The dictionary never leaves this side. The reader who needs it is on the work
side, where only the shipped documents arrive, so the dictionary is written out
into one page that ships with them.

    write-acronyms.py --config <file>            write the page
    write-acronyms.py --config <file> --check    exit 1 if the page on disk is
                                                 not what the dictionary renders

The config names the dictionary (terms), the pending list (unknown), the page
(page), the folder its wiki publishes (docsRoot), the files at the top of the
repository a row may cite (rootDocs), and the page's opening text (preamble);
see config.py.

The page is generated in full every time. Editing it by hand is undone by the
next run: the row in the dictionary is what a reader is arguing with.

Exit 0 when the page is written or already current, 1 when --check finds it
stale, 64 when there is no config.
"""

import os
import sys
import urllib.parse

import config

CONFIG, ARGS = config.take(sys.argv[1:], "write-acronyms.py")
ROOT = CONFIG.root
TERMS = CONFIG.path("terms") or ""
UNKNOWN = CONFIG.path("unknown") or ""
TARGET = CONFIG.path("page")
if not TARGET:
    config.fail("write-acronyms.py", "the config names no page", 2)
DOCS_ROOT = CONFIG.value("docsRoot", "docs").rstrip("/") + "/"
ROOT_DOCS = set(CONFIG.value("rootDocs", []))

# The page's opening text: a string, or a list of its lines.
PREAMBLE = CONFIG.value("preamble", "# Acronyms")
if isinstance(PREAMBLE, list):
    PREAMBLE = "\n".join(PREAMBLE)

SCOPED_HEADING = """## Short forms that mean something narrower in one place

These carry a different expansion depending on which document is using them.
The third column says where the narrower reading applies.
"""

PENDING_HEADING = """## Short forms with no expansion on record

These are real short forms whose words no document in here spells out. They are
listed so a reader knows the term is a short form rather than a code, and so
anyone who knows the answer can say so.
"""


def rows():
    """Reads the dictionary into (acronym, expansion, scope, source) tuples."""
    out = []
    with open(TERMS, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            acronym, expansion = parts[0].strip(), parts[1].strip()
            scope = parts[2].strip() if len(parts) > 2 and parts[2].strip() else "*"
            source = parts[3].strip() if len(parts) > 3 else ""
            out.append((acronym, expansion, scope, source))
    return out


def pending():
    """Reads the pending list: the short forms nobody has found the words for."""
    if not os.path.exists(UNKNOWN):
        return []
    with open(UNKNOWN, encoding="utf-8") as handle:
        return sorted(l.strip() for l in handle if l.strip() and not l.startswith("#"))


def cell(text):
    """Escapes the one character that would break out of a table cell."""
    return text.replace("|", r"\|")


# What a row whose fourth column names a person renders as. Who answered is
# provenance for this side, and the reader on the work side is being told
# whether there is a file to open, so the answer they get is that there is not.
NO_SOURCE = "no document in here states it"

STANDARD = "standard technical term"


def source_cell(source):
    """Renders the fourth column. A source under the docs root is a page of
    the same wiki this file is read in, so it is written as a link the reader
    can follow. Anything outside it, a root document included, is text: the
    wiki publishes the docs root alone, and a link out of it opens nothing."""
    if source == STANDARD:
        return STANDARD
    if source in ROOT_DOCS:
        return f"`{cell(source)}`"
    if not source or "/" not in source:
        return NO_SOURCE
    if source.startswith(DOCS_ROOT) and source.endswith(".md"):
        page = source[len(DOCS_ROOT):]
        return f"[{cell(page)}]({urllib.parse.quote(page)})"
    return f"`{cell(source)}`"


def table(header, lines):
    out = ["| " + " | ".join(header) + " |"]
    out.append("| " + " | ".join("---" for _ in header) + " |")
    out.extend(lines)
    return "\n".join(out)


def render():
    general, scoped = [], []
    for acronym, expansion, scope, source in sorted(rows()):
        if scope == "*":
            general.append(
                f"| {cell(acronym)} | {cell(expansion)} | {source_cell(source)} |"
            )
        else:
            scoped.append(
                f"| {cell(acronym)} | {cell(expansion)} | `{cell(scope)}` "
                f"| {source_cell(source)} |"
            )

    parts = [PREAMBLE.rstrip("\n"), table(["Acronym", "Stands for", "Stated in"], general)]
    if scoped:
        parts.append(SCOPED_HEADING.rstrip("\n"))
        parts.append(
            table(["Acronym", "Stands for", "Where it applies", "Stated in"], scoped)
        )
    waiting = pending()
    if waiting:
        parts.append(PENDING_HEADING.rstrip("\n"))
        parts.append(table(["Acronym"], [f"| {cell(w)} |" for w in waiting]))
    return "\n\n".join(parts) + "\n"


def main():
    checking = "--check" in ARGS
    text = render()
    current = None
    if os.path.exists(TARGET):
        with open(TARGET, encoding="utf-8") as handle:
            current = handle.read()

    if checking:
        if current == text:
            sys.exit(0)
        where = os.path.relpath(TARGET, ROOT)
        print(f"{where} does not match the dictionary.")
        print("Run check-acronyms.sh --write and commit the result.")
        sys.exit(1)

    if current == text:
        print(f"{os.path.relpath(TARGET, ROOT)}: already current")
        sys.exit(0)
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"{os.path.relpath(TARGET, ROOT)}: written")


if __name__ == "__main__":
    main()
