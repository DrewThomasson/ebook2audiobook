#!/usr/bin/env python3
"""Reads every row of the dictionary and checks the file in its fourth column
actually states that expansion for that acronym.

    verify-terms.py --config <file>

The config names the dictionary (terms); a source path in a row is relative
to the config's git toplevel. See config.py.

A row passes when the cited file carries the acronym and the expansion close
enough together to be one statement: a glossary heading, a table row, or the
parenthesis a document opens the first time it uses the short form. Capitals,
punctuation, "and" against "&", and a possessive apostrophe do not count
against it, and the words may sit up to two words apart, which covers a
document breaking the phrase across a line.

The expansion appearing somewhere else in the file is not enough. A file can
say "Adoptive Parent" about one code and use a different code two pages later,
and a dictionary built on that reads as sourced when it is not.

A row whose fourth column looks like a path (it ends in .md, or holds a slash
and no whitespace) fails when that file is missing, so a deleted or renamed
document cannot leave its rows citing nothing. A row whose fourth column is
prose, a URL, or a file this check cannot read (a JSON dump) is listed
separately. Those are the rows a person answered for, and they are read
rather than checked.

Exit 0 when every path-sourced row checks out, 1 otherwise, 64 when there is
no config.
"""

import os
import re
import sys

import config

CONFIG, ARGS = config.take(sys.argv[1:], "verify-terms.py")
TERMS = CONFIG.path("terms") or ""
ROOT = CONFIG.root

# How far apart the acronym and its expansion may sit and still be one
# statement. A table row carrying a code, a name, and two more columns is the
# widest real case.
WINDOW = 120


def normalise(text):
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def states(haystack, acronym, expansion):
    words = normalise(expansion).split()
    if not words:
        return False
    phrase = r"(?:\W+\w+){0,2}\W+".join(re.escape(word) for word in words)
    short = re.escape(normalise(acronym))
    near = rf"\b{short}\b.{{0,{WINDOW}}}?{phrase}|{phrase}.{{0,{WINDOW}}}?\b{short}\b"
    return re.search(near, haystack) is not None


def looks_like_path(source):
    if source.endswith(".md"):
        return True
    return "/" in source and "://" not in source and not any(c.isspace() for c in source)


def main():
    failures = 0
    answered = []
    checked = 0
    for raw in open(TERMS, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        acronym, expansion = parts[0].strip(), parts[1].strip()
        source = parts[3].strip() if len(parts) > 3 else ""
        path = os.path.join(ROOT, source)
        if looks_like_path(source) and not os.path.exists(path):
            print(f"{acronym}: {source} does not exist")
            failures += 1
            continue
        if not source.endswith(".md"):
            answered.append(f"{acronym} = {expansion} ({source or 'no source'})")
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            haystack = normalise(handle.read())
        checked += 1
        if not states(haystack, acronym, expansion):
            print(f'{acronym}: {source} does not state "{expansion}" for it')
            failures += 1

    if answered:
        print()
        print("Rows a person answered for, which no file in here can confirm:")
        for row in answered:
            print(f"  {row}")

    print()
    print(f"{checked} row(s) checked against their source, {failures} failed.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
