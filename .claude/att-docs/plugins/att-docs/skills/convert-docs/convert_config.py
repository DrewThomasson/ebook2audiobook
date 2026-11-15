#!/usr/bin/env python3
"""Reads the extension file every convert-docs script takes as `--config`.

The file is JSON. A path in it is relative to the git toplevel of the folder the
file sits in, so the scripts find the consuming repository from the file rather
than from where they are installed. The fields:

  todoRoot        where a batch of source documents is dropped
  appsRoot        where the converted Markdown lands
  futureFolder    the folder in a group that holds revisions not carried yet
  words           the word list the shifted text check reads
  collisions      sources downloaded under a longer name than the library's
  sharePointHost  the scheme and host the document library lives on

Run as a script, it prints one field as the file states it, for convert.sh:

  convert_config.py CONFIG FIELD

A missing file, a folder outside a git work tree, or a missing field exits 64.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_USAGE = 64


def fail(prog: str, message: str) -> None:
    print(f"{prog}: {message}", file=sys.stderr)
    sys.exit(EXIT_USAGE)


@dataclass
class Config:
    """One extension file, its repository, and the fields it states."""

    file: Path
    root: Path
    values: dict
    prog: str

    def value(self, field: str) -> str:
        """A field as the file states it."""
        found = self.values.get(field)
        if not isinstance(found, str) or not found:
            fail(self.prog, f"{self.file} names no {field}")
        return found

    def path(self, field: str) -> Path:
        """A path field, resolved against the repository the file sits in."""
        return self.root / self.value(field)


def load(file: str | None, prog: str) -> Config:
    """Reads `file`, or stops the script with exit 64 when it cannot."""
    if not file:
        fail(prog, "--config <extension.json> is required")
    path = Path(file).resolve()
    if not path.is_file():
        fail(prog, f"no config at {file}")
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(prog, f"{file} does not read as JSON: {error}")
    if not isinstance(values, dict):
        fail(prog, f"{file} does not hold a JSON object")
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path.parent, capture_output=True, text=True, check=False,
    )
    if top.returncode != 0 or not top.stdout.strip():
        fail(prog, f"{file} is not inside a git work tree")
    return Config(path, Path(top.stdout.strip()), values, prog)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        fail("convert_config", "usage: convert_config.py CONFIG FIELD")
    print(load(argv[0], "convert-docs").value(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
