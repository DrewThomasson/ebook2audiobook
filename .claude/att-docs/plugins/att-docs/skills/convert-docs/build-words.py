#!/usr/bin/env python3
"""Rebuilds the word list the shifted text check reads.

The list is the vocabulary of the documents already converted, kept to the
words a system dictionary also knows, so that a product name or a column
heading the documents happen to spell does not become a word. The check reads
it to decide whether the decoding of a glyph run says anything in English, so
the words these documents actually use are the ones worth holding.

Usage:
  build-words.py --config FILE [--docs DIR] [--dictionary PATH] [--out PATH]

FILE is the skill's extension.json. --docs defaults to its `appsRoot` and --out
to its `words` field. A missing config exits 64.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import convert_config

DICTIONARIES = [
    "/usr/share/dict/american-english",
    "/usr/share/dict/words",
]


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--config", help="the skill's extension.json")
    parser.add_argument("--docs")
    parser.add_argument("--dictionary")
    parser.add_argument("--out")
    args = parser.parse_args()
    config = convert_config.load(args.config, "build-words")
    args.docs = args.docs or str(config.path("appsRoot"))
    args.out = args.out or str(config.path("words"))

    paths = [args.dictionary] if args.dictionary else DICTIONARIES
    dictionary = next((p for p in paths if pathlib.Path(p).exists()), None)
    if not dictionary:
        print("build-words: no system dictionary to read", file=sys.stderr)
        return 1

    known = {
        line.strip().lower()
        for line in pathlib.Path(dictionary).read_text(
            encoding="utf-8", errors="replace").splitlines()
        if line.strip().isalpha()
    }

    used = set()
    for path in sorted(pathlib.Path(args.docs).rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in re.findall(r"[A-Za-z]{4,}", text):
            low = token.lower()
            if low in known:
                used.add(low)

    pathlib.Path(args.out).write_text(
        "\n".join(sorted(used)) + "\n", encoding="utf-8")
    print(f"{len(used)} words from {dictionary} into {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
