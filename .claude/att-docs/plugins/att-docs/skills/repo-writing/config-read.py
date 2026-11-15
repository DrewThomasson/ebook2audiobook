#!/usr/bin/env python3
"""Prints values from a JSON config, each followed by a NUL byte.

usage: config-read.py <config> <key.path>[=default] ...

A string prints as it is, a missing value as its default or an empty string, an
array of strings joined with |, and an array of objects as one line per object,
the object's path and except values separated by a tab.
"""
import json
import sys


def lookup(data, dotted):
    for key in dotted.split("."):
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data


def render(value):
    if value is None:
        return ""
    if isinstance(value, list):
        if value and isinstance(value[0], dict):
            return "\n".join(f"{v.get('path', '')}\t{v.get('except') or ''}" for v in value)
        return "|".join(str(v) for v in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def main():
    if len(sys.argv) < 2:
        print("usage: config-read.py <config> <key.path>[=default] ...", file=sys.stderr)
        return 64
    try:
        with open(sys.argv[1], encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return 2
    if not isinstance(data, dict):
        return 2
    out = []
    for spec in sys.argv[2:]:
        dotted, _, default = spec.partition("=")
        value = lookup(data, dotted)
        out.append(default if value is None else render(value))
    sys.stdout.write("".join(text + "\0" for text in out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
