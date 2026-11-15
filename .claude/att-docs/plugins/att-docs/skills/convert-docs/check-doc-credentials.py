#!/usr/bin/env python3
"""Reports Markdown that holds a password written out as a value.

A converted document is copied from its source as it stands, so a setup page
that lists a server login and its password lands with both. The scan reads two
shapes:

  a field     `FTP password: <value>`, `Password - <value>`, a table cell
              after a `Password` cell
  a setting   `pwd=<value>`, `Password=<value>` in a connection string

The first token of the value is what is judged, so a note after a password
does not hide it. A password holds a letter and a digit or a symbol, so a
token that is a plain or hyphenated word (`If the password ...`, `Button`,
`Case-sensitive`), a number (`| Password | 20 |` in a table of field lengths),
or a mask (`********`, a row of bullets) describes the field and passes. So
does a token that names where the secret is held: one in parentheses or angle
brackets, `(held by the noisy alerts support team)` or `<password>`, one that
reads a setting or variable (`AppSettings("x")`, `$PASSWORD`, `${pwd}`,
`%PWD%`), a link or a path (`https://.../reset`, `/opt/conn`), and `n/a` or
`e.g.`.

The report names the file, the line, and the key, never the value, so a hit
does not copy the secret into a job log.

Usage:
  check-doc-credentials.py PATH...

A directory argument is walked for `.md` files. Exits 0 clean, 2 when a file
holds a password value.
"""
from __future__ import annotations

import re
import sys

from doc_paths import markdown_under

KEY = r"(?:password|passwd|passcode|pwd)"

# `FTP password: x`, `- Password - x`, `**Password:** x`. The separator is a
# colon, or a dash with a space on each side so a hyphenated word is not one.
# The value is the one token judged, so a second key later in the line is read
# too.
FIELD = re.compile(
    rf"\b(?P<key>{KEY})\b[*_]*\s*(?::|\s-\s)\s*[*_]*\s*(?P<value>\S*)",
    re.IGNORECASE,
)

# `pwd=x;` in a connection string, or `Password = "x"` in quoted code. The value
# ends at a delimiter or a quote.
SETTING = re.compile(
    rf"\b(?P<key>{KEY})\s*=\s*[\"']?(?P<value>[^;,\s\"'&]+)",
    re.IGNORECASE,
)

# `| Password | x |`, `| FTP password: | x |`: the cell after a cell that is
# only the key and its label.
CELL = re.compile(
    rf"\|\s*[*_]*(?P<key>[\w ]*{KEY})[*_]*\s*:?\s*[*_]*\s*\|\s*(?P<value>[^|]*)\|",
    re.IGNORECASE,
)

# The placeholders that carry a symbol, so the plain-word rule misses them.
PLACEHOLDER_WORDS = {"n/a", "e.g", "i.e"}

# A word, hyphenated or with an apostrophe: `Button`, `Case-sensitive`, `user's`.
WORD = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


def is_placeholder(value: str) -> bool:
    """True when the value is not a secret: a description, or where one is kept."""
    words = value.split()
    if not words:
        return True
    text = words[0].strip("*_`").rstrip(".,;:")
    if not text or text[0] in "(<[{":
        return True
    if text.lower() in PLACEHOLDER_WORDS or WORD.fullmatch(text):
        return True
    # A link or a path says where to go: a reset page, the directory `pwd`
    # printed.
    if "://" in text or text[0] in "/\\~":
        return True
    # A password holds a letter and a digit or symbol. A number is a length or
    # a count, and a run of mask characters holds no letter.
    if not re.search(r"[A-Za-z]", text):
        return True
    # A read of a setting or a variable: a shell variable, a batch variable, a
    # template slot, or a call by name, `AppSettings("x")`, which a setting
    # value cuts off at its quote as `AppSettings(`. A `$` or `(` elsewhere in
    # the token is a symbol in the password.
    return bool(re.match(r"\$|%\w+%$|\{\{|[A-Za-z_][\w.]*\((.*\))?$", text))


def hits(line: str) -> list[str]:
    found = []
    for pattern in (CELL, SETTING, FIELD):
        for match in pattern.finditer(line):
            if not is_placeholder(match.group("value")):
                found.append(match.group("key").strip())
        if found:
            break
    return found


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check-doc-credentials.py PATH...", file=sys.stderr)
        return 1
    reported = 0
    for path in markdown_under(sys.argv[1:]):
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            keys = hits(line)
            if keys:
                reported += 1
                print(f"{path}:{number}: a {keys[0]} value is written out")
    if reported:
        print(f"\n{reported} line(s) hold a password value. Replace each with "
              "where the secret is held, such as (held by the support team), "
              "and have its owner rotate it, since git history keeps it.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
