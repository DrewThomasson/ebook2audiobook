#!/usr/bin/env python3
"""Lists the tools and tool arguments that differ between two Baton tool snapshots.

usage: python3 drift.py <committed.json> <fresh.json>

Both files have the shape refresh.sh writes:
{"source": <commit>, "tools": {<name>: [<argument>, ...]}}.
Only the tools are compared; a different source commit with the same tools is no difference,
and the order of tools and arguments does not matter. Standard library only.

Prints one line per difference, at most LIMIT lines and then a count of the rest:

  tool send: added
  tool read_issue: removed
  tool read_issue: argument repo added
  tool read_issue: argument number removed

Exit status: 0 when the tools match, 1 when they differ, 2 when a file cannot be read.
"""
import json
import sys

LIMIT = 50


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    tools = data["tools"]
    if not isinstance(tools, dict) or not all(
        isinstance(args, list) and all(isinstance(a, str) for a in args) for args in tools.values()
    ):
        raise ValueError("tools must map each tool name to a list of argument names")
    return {name: set(args) for name, args in tools.items()}


def compare(committed, fresh):
    """Returns the difference lines for two {tool: set of arguments} maps."""
    lines = []
    for name in sorted(fresh.keys() - committed.keys()):
        lines.append(f"tool {name}: added")
    for name in sorted(committed.keys() - fresh.keys()):
        lines.append(f"tool {name}: removed")
    for name in sorted(committed.keys() & fresh.keys()):
        for arg in sorted(fresh[name] - committed[name]):
            lines.append(f"tool {name}: argument {arg} added")
        for arg in sorted(committed[name] - fresh[name]):
            lines.append(f"tool {name}: argument {arg} removed")
    return lines


def main(argv):
    if len(argv) != 2:
        print(__doc__.split("\n")[2], file=sys.stderr)
        return 2
    try:
        committed, fresh = load(argv[0]), load(argv[1])
    except (OSError, ValueError, KeyError, TypeError) as err:
        print(f"cannot read a snapshot: {err}", file=sys.stderr)
        return 2
    lines = compare(committed, fresh)
    for line in lines[:LIMIT]:
        print(line)
    if len(lines) > LIMIT:
        print(f"and {len(lines) - LIMIT} more")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
