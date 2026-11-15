#!/usr/bin/env python3
"""Checks that the skills name only bridge tools and tool arguments that exist.

usage: python3 skill_tools.py [--snapshot <file>] [--root <folder>]

Baton, the voice bridge, offers the voice chat a list of tools, and the skills tell a
session how to use them. A skill that names a tool that was renamed or an argument that
was dropped misleads every session that reads it, and a skill that never mentions a new
argument leaves the voice chat unaware of it. This check reads the tool list from
bridge-tools.json, written by refresh.sh from Baton's own definitions, and compares it
with the Markdown files in SCANNED. Standard library only.

What counts as a mention is a Markdown code span, outside a fenced block, that may wrap
onto the next line of its paragraph:

  `read_pull_request`        the tool, named
  `read_pull_request(repo)`  the tool and the arguments the skill says it takes, in call
                             form; a list is comma separated, and `tool()` names none

An argument is tied to its tool only in call form, because a bare `repo` is as often a
setting or a field of something else as an argument.

Errors (exit 1):
  - a call form whose arguments the tool does not take
  - a call form or a snake_case name that is no tool and is not in NOT_TOOLS
  - a Markdown file outside SCANNED that names a bridge tool by a snake_case name or a
    call form, so the file is either added to SCANNED or its text is not about the bridge
  - a snapshot that is missing or malformed

Warnings (the exit status stays 0): an argument of a tool the skills cover, meaning at
least one call form names it, that no call form names.

A tool whose name is one plain word (`send`, `follow`, `summary`) is checked only in call
form, because the same word in a code span is as often code as the tool. A renamed
one-word tool goes unnoticed for the same reason.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEFAULT_SNAPSHOT = os.path.join(HERE, "bridge-tools.json")

# The files that tell a session how to use the bridge, relative to the root.
SCANNED = [
    "README.md",
    "plugins/voice/skills/voice-bridge-hooks/SKILL.md",
    "plugins/voice/skills/voice-request/SKILL.md",
]
# Snake_case names these files use that are not bridge tools: hook scripts, fields of the
# hooks' own state files, a tool of the coding assistant, and a call in an extension module.
NOT_TOOLS = {
    "voice_bridge_reply",
    "session_title",
    "player_pid",
    "hook_pid",
    "noise_w",
    "ast_edit",
    "read_ledger",
}
# Folders no Markdown is read from. A worktree under .claude/worktrees is another branch.
SKIP_DIRS = {"node_modules", ".git", "__pycache__"}
SKIPPED_FILES = {"CHANGELOG.md"}

# A code span opens and closes with a run of the same number of backticks.
SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
CALL = re.compile(r"^([a-z][a-z0-9_]*)\(([^()]*)\)$")
SNAKE = re.compile(r"^[a-z]+(?:_[a-z]+)+$")
ARGUMENT = re.compile(r"^[a-z][A-Za-z0-9_]*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
BLOCK_START = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s|^\s*\||^#")
QUOTE = re.compile(r"^(?:>\s?)+")


class Problems:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append(f"ERROR  {where}: {message}")

    def warn(self, where, message):
        self.warnings.append(f"WARN   {where}: {message}")


def load_snapshot(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise SystemExit(f"ERROR  {path}: cannot read the tool list ({e}); run refresh.sh")
    tools = data.get("tools") if isinstance(data, dict) else None
    if not isinstance(tools, dict) or not tools or not all(
        isinstance(args, list) and all(isinstance(a, str) for a in args)
        for args in tools.values()
    ):
        raise SystemExit(f"ERROR  {path}: expected a non-empty \"tools\" object of argument lists")
    return {name: set(args) for name, args in tools.items()}


def blocks(path):
    """Yields each run of (line number, text) lines outside a fenced block that a code span
    can wrap across. A blank line, a list item, a table row or a fence ends a run, and a
    heading is a run of its own, so a stray backtick never pairs with one in the next item."""
    fence = None  # the marker of the fence that is open
    run = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            marker = FENCE.match(line)
            marker = marker.group(1) if marker else None
            if fence:
                # Only a line of the same character, at least as long, closes the fence.
                if marker and marker[0] == fence[0] and len(marker) >= len(fence) \
                        and not line.strip().strip(fence[0]):
                    fence = None
                continue
            opens = marker and not (marker[0] == "`" and "`" in line.strip()[len(marker):])
            if opens or not line.strip() or BLOCK_START.match(line):
                if run:
                    yield run
                run = []
            if opens:
                fence = marker
            elif line.strip():
                run.append((number, QUOTE.sub("", line.strip())))
                if line.startswith("#"):
                    yield run
                    run = []
    if run:
        yield run


def mentions(path):
    """Yields (line number, span text) for each code span outside a fenced block, with the
    line the span starts on."""
    for run in blocks(path):
        text = ""
        starts = []  # where each line's text begins in text
        for number, line in run:
            starts.append((len(text), number))
            text += line + " "
        for span in SPAN.finditer(text):
            number = [n for offset, n in starts if offset <= span.start()][-1]
            yield number, re.sub(r"\s+", " ", span.group(2)).strip()


def markdown_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not (rel == ".claude" and d == "worktrees")
        ]
        for name in filenames:
            if name.endswith(".md") and name not in SKIPPED_FILES:
                yield os.path.relpath(os.path.join(dirpath, name), root)


def check_scanned(root, tools, problems):
    """Returns the arguments each tool's call forms name."""
    named = {}
    for rel in SCANNED:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            problems.error(rel, "is listed in SCANNED but does not exist")
            continue
        for number, text in mentions(path):
            where = f"{rel}:{number}"
            call = CALL.match(text)
            if call:
                head, raw = call.groups()
                arguments = [a.strip() for a in raw.split(",")] if raw.strip() else []
                if head in tools:
                    seen = named.setdefault(head, set())
                    for argument in arguments:
                        if not ARGUMENT.match(argument):
                            problems.error(where, f"`{text}`: {argument!r} is not an argument name")
                        elif argument not in tools[head]:
                            problems.error(
                                where, f"`{text}`: {head} takes no argument {argument}"
                                f" (it takes {', '.join(sorted(tools[head])) or 'none'})")
                        else:
                            seen.add(argument)
                elif "_" in head and head not in NOT_TOOLS:
                    problems.error(where, f"`{text}`: {head} is not a bridge tool")
            elif SNAKE.match(text) and text not in tools and text not in NOT_TOOLS:
                problems.error(where, f"`{text}` is not a bridge tool")
    return named


def check_unscanned(root, tools, problems):
    scanned = {os.path.normpath(p) for p in SCANNED}
    for rel in sorted(markdown_files(root)):
        if os.path.normpath(rel) in scanned:
            continue
        for number, text in mentions(os.path.join(root, rel)):
            call = CALL.match(text)
            head = call.group(1) if call else text
            if head in tools and (call or "_" in head):
                problems.error(
                    f"{rel}:{number}",
                    f"`{text}` names the bridge tool {head}, but the file is not in SCANNED;"
                    " add it there so its tool and argument names are checked")


def check_coverage(tools, named, problems):
    for name in sorted(named):
        missing = sorted(tools[name] - named[name])
        if missing:
            problems.warn(
                name, f"the bridge takes {', '.join(missing)}, which no skill names;"
                f" write each as a call form such as `{name}({missing[0]})`"
                " where a skill says what it does")


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--root", default=REPO)
    args = parser.parse_args(argv)

    tools = load_snapshot(args.snapshot)
    problems = Problems()
    named = check_scanned(args.root, tools, problems)
    check_unscanned(args.root, tools, problems)
    check_coverage(tools, named, problems)

    for line in problems.errors + problems.warnings:
        print(line)
    print(f"{len(problems.errors)} errors, {len(problems.warnings)} warnings")
    return 1 if problems.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
