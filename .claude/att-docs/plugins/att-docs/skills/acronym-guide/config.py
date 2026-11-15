#!/usr/bin/env python3
"""Reads the --config file the scripts beside this one take.

The config is a JSON object. A path in it is relative to the git toplevel of
the config file's folder. The keys the scripts read:

    terms            the dictionary: acronym, expansion, scope, source
    ignore           the words that look like acronyms and are not
    unknown          the real short forms nobody has found the words for
    page             the rendered dictionary page
    docsRoot         the folder the rendered page's wiki publishes
    rootDocs         files at the top of the repository a row may cite
    covered          the pattern a changed path matches to be checked
    skipPaths        the pattern for paths read rather than written
    authorLineFiles  the pattern for records whose Author: line is a user ID
    preamble         the rendered page's opening text, a string or its lines
    guide            the page a failing run points the reader at
    mainBranch       the branch the changed files are measured from

    config.py --config <file> get <key>...   print each value on its own line,
                                             an array joined with |

Exit 64 when the config is missing, 2 when it does not read.
"""

import json
import os
import subprocess
import sys


class Config:
    def __init__(self, path, root, data):
        self.file = path
        self.root = root
        self.data = data

    def value(self, key, default=""):
        value = self.data.get(key, default)
        if value is None:
            return default
        return value

    def path(self, key):
        """The absolute path a key names, or None when the config leaves it out."""
        value = self.data.get(key)
        return os.path.join(self.root, value) if value else None


def fail(name, message, code):
    print(f"{name}: {message}", file=sys.stderr)
    sys.exit(code)


def take(argv, name):
    """Takes --config <file> off the front of argv. Returns the config and the
    arguments after it."""
    if len(argv) < 2 or argv[0] != "--config":
        fail(name, "--config <file> is required", 64)
    path, rest = os.path.abspath(argv[1]), argv[2:]
    if not os.path.isfile(path):
        fail(name, f"the config {argv[1]} does not exist", 64)
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=os.path.dirname(path), capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        fail(name, f"the config {argv[1]} is not inside a git work tree", 2)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        fail(name, f"the config {argv[1]} does not read: {error}", 2)
    if not isinstance(data, dict):
        fail(name, f"the config {argv[1]} is not a JSON object", 2)
    return Config(path, root, data), rest


def main():
    config, rest = take(sys.argv[1:], "config.py")
    if not rest or rest[0] != "get":
        sys.exit(__doc__)
    for key in rest[1:]:
        value = config.value(key)
        if isinstance(value, list):
            value = "|".join(str(item) for item in value)
        print(value)


if __name__ == "__main__":
    main()
