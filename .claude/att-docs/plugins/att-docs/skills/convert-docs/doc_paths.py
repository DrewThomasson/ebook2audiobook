"""The Markdown files the convert-docs checks read from their path arguments."""
from __future__ import annotations

import pathlib
import re
import sys


def hyphenated(name: str) -> str:
    """A file name as it is written under docs/, where no name holds a space.

    Each run of spaces, with any hyphens touching it, becomes one hyphen, and a
    hyphen left in front of the extension is dropped, so
    `ACT 4.0 - Activity Entry.docx` is `ACT-4.0-Activity-Entry.docx`. The wiki
    shows a hyphen as a space, so the page title still reads as the document's.
    _shared/doc-names.mjs writes the same rule.
    """
    if not re.search(r"\s", name):
        return name
    joined = re.sub(r"[\s-]*\s[\s-]*", "-", name.strip())
    return re.sub(r"-(\.[A-Za-z0-9]+)$", r"\1", joined)


def markdown_under(paths: list[str]) -> list[pathlib.Path]:
    """Walks each directory for `.md` files and takes each file as given.

    A path that does not exist stops the check, so a mistyped or moved folder
    reads as an error rather than as a clean scan of nothing.
    """
    found: list[pathlib.Path] = []
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            found.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            found.append(path)
        else:
            sys.exit(f"{raw}: no such file or directory")
    return found
