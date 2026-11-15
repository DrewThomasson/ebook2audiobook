#!/usr/bin/env python3
"""Static checks for the repository. Standard library only.

Checks: plugin and marketplace JSON, SKILL.md frontmatter, relative Markdown links,
and syntax of every .py, .mjs/.js and .sh file. shellcheck runs on .sh files when it
is installed; its output is advisory and never fails the run.
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"node_modules", ".git", "__pycache__"}
errors = []


def error(path, message):
    errors.append(f"{os.path.relpath(path, ROOT)}: {message}")


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        # Other worktrees live under .claude/worktrees and are checked on their own.
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS
            and not (rel == ".claude" and d == "worktrees")
        ]
        for name in filenames:
            yield os.path.join(dirpath, name)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        error(path, f"not valid JSON ({e})")
        return None


def check_json(files):
    for path in files:
        base = os.path.basename(path)
        parent = os.path.basename(os.path.dirname(path))
        if base == "plugin.json" and parent == ".claude-plugin":
            load_json(path)
        elif base == "marketplace.json" and parent == ".claude-plugin":
            data = load_json(path)
            if not isinstance(data, dict):
                continue
            for plugin in data.get("plugins", []):
                source = plugin.get("source") if isinstance(plugin, dict) else None
                if not isinstance(source, str):
                    error(path, f"plugin {plugin!r} has no string source")
                    continue
                if not os.path.exists(os.path.join(ROOT, source)):
                    error(path, f"source {source} does not exist")


def check_skills(files):
    prefixes = ("plugins" + os.sep, os.path.join(".claude", "skills") + os.sep)
    for path in files:
        if os.path.basename(path) != "SKILL.md":
            continue
        if not os.path.relpath(path, ROOT).startswith(prefixes):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = re.match(r"---\r?\n(.*?)\r?\n---\s*(\r?\n|$)", text, re.S)
        if not m:
            error(path, "no frontmatter")
            continue
        fields = {}
        current = None
        for line in m.group(1).splitlines():
            km = re.match(r"([A-Za-z_-]+):\s*(.*)$", line)
            if km:
                current = km.group(1)
                fields[current] = km.group(2).strip()
            elif current and line.strip():
                fields[current] += " " + line.strip()
        for key in ("name", "description"):
            value = fields.get(key, "").strip().strip("|>-").strip()
            if not value:
                error(path, f"frontmatter {key} is missing or empty")


LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def check_links(files):
    for path in files:
        if not path.endswith(".md"):
            continue
        in_fence = None
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                fm = re.match(r"\s*(```+|~~~+)", line)
                if fm:
                    marker = fm.group(1)[0]
                    if in_fence is None:
                        in_fence = marker
                    elif in_fence == marker:
                        in_fence = None
                    continue
                if in_fence:
                    continue
                line = re.sub(r"`[^`]*`", "", line)
                for m in LINK.finditer(line):
                    target = m.group(1)
                    if re.match(r"([a-zA-Z][a-zA-Z0-9+.-]*:|#)", target):
                        continue
                    target = target.split("#", 1)[0]
                    if not target:
                        continue
                    resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
                    if not os.path.exists(resolved):
                        error(path, f"line {n}: link {target} does not resolve")


def run(cmd, path):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        error(path, f"{' '.join(cmd[:2])} failed: {(r.stderr or r.stdout).strip()}")


def check_syntax(files):
    for path in files:
        if path.endswith(".py"):
            with open(path, "rb") as f:
                try:
                    compile(f.read(), path, "exec")
                except (SyntaxError, ValueError) as e:
                    error(path, f"py_compile failed: {e}")
        elif path.endswith((".mjs", ".js")):
            run(["node", "--check", path], path)
        elif path.endswith(".sh"):
            run(["bash", "-n", path], path)


def shellcheck(files):
    exe = shutil.which("shellcheck")
    scripts = [p for p in files if p.endswith(".sh")]
    if not exe:
        print("shellcheck not installed; skipped (advisory)")
        return
    r = subprocess.run([exe, "-x", *scripts], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print("shellcheck (advisory, never fails the run):")
    print(out if out else "  no findings")


def main():
    files = list(walk())
    check_json(files)
    check_skills(files)
    check_links(files)
    check_syntax(files)
    shellcheck(files)
    for e in errors:
        print(f"ERROR  {e}")
    print(f"{len(errors)} problem(s) found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
