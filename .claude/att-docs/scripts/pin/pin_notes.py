#!/usr/bin/env python3
"""Writes the body of a pull request that moves a consumer's Overmind pin.

usage: python3 pin_notes.py --changelog <file> --from <vX.Y.Z> --to <vX.Y.Z> --repo <owner/name>

The body names both versions, lists the changelog entries after the pinned version up to
the target (newest first), and adds a note when the minor or major version moved, because
below 1.0 a minor bump marks a change to the extension contract. A version none of whose
entries can be shown gets no heading, and a line says where the changelog starts when the
pinned version is older than its first section and that section's compare link does not
name the pinned version as the one just before it.

The pull requests are read outside this repository, by people who have no access to its
tracker, its builds, its releases or its assistants. So the body links nothing here, the
trailing issue and commit references are dropped from the entries, and an entry that still
names one of those things is left out whole, with a count of the omitted entries so the
list does not pass for complete. The check is a list of words, so it errs toward leaving
an entry out. A changelog that is empty, or has no section for the target version, is an
error: it never reads as "no entries".
"""
import argparse
import re
import sys

TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
HEADING = re.compile(r"^## \[?(\d+)\.(\d+)\.(\d+)(?:\]\(([^)]*)\)|\])?(?:\s+\(([^)]*)\))?\s*$")
# The tag a section's compare link starts from, which is the release just before it.
COMPARE_BASE = re.compile(r"/compare/(v\d+\.\d+\.\d+)\.\.\.")
# What the readers cannot follow, matched after the trailing references are removed: a
# number left in the text, a link into the repository or its host, a tracker or build
# word, and an assistant by name.
PROHIBITED = re.compile(
    r"#\d+|https?://|github|\bissues?\b|\bpull requests?\b|\bPRs?\b|\bCI\b|\bworkflows?\b"
    r"|\brunners?\b|\bself-hosted\b|release-please"
    r"|overmind|claude|anthropic|\bassistants?\b|\bagents?\b|\bAI\b|\bLLMs?\b|copilot|codex"
    r"|gemini|opus|sonnet|haiku|\bsessions?\b|🤖",
    re.IGNORECASE,
)
ENTRY_START = re.compile(r"^[*-] ")
REFERENCES = [
    re.compile(r"\s*\(\[#\d+\]\([^)]*\)\)"),
    re.compile(r"\s*\(\[[0-9a-f]{7,40}\]\([^)]*\)\)"),
    re.compile(r"\s*\(#\d+\)"),
]


def parse_tag(tag):
    m = TAG.match(tag)
    if not m:
        sys.exit(f"pin_notes: '{tag}' is not a tag of the form vMAJOR.MINOR.PATCH")
    return tuple(int(n) for n in m.groups())


def sections(text):
    """Yields (version tuple, date, lines, link) for each release section, in file order.
    The link is the heading's compare link, or None when the heading has none."""
    current = None
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            if current:
                yield current
            current = (tuple(int(n) for n in m.groups()[:3]), m.group(5), [], m.group(4))
        elif current is not None:
            current[2].append(line)
    if current:
        yield current


def clean(line):
    for pattern in REFERENCES:
        line = pattern.sub("", line)
    if line.startswith("### "):
        line = "#" + line
    return line.rstrip()


def blocks(lines):
    """Splits a section into headings, blank lines and entries. An entry is a bullet with
    the indented lines under it; any other text line is its own entry."""
    out = []
    for line in lines:
        if not line.strip():
            out.append(("blank", [line]))
        elif line.startswith("#"):
            out.append(("heading", [line]))
        elif ENTRY_START.match(line) or not out or out[-1][0] != "entry" or not line[0].isspace():
            out.append(("entry", [line]))
        else:
            out[-1][1].append(line)
    return out


def render(version, date, lines, repo_name):
    """Returns (text, omitted): the section without the entries that name something the
    readers cannot follow, and how many entries that left out. The text is None when no
    entry is left, so the version shows no heading."""
    title = "v%d.%d.%d" % version + (f" ({date})" if date else "")
    kept = []
    omitted = 0
    for kind, chunk in blocks(lines):
        chunk = [clean(l) for l in chunk]
        text = "\n".join(chunk)
        if kind == "entry" and (PROHIBITED.search(text) or repo_name.search(text)):
            omitted += 1
        else:
            kept.append((kind, chunk))
    if not any(kind == "entry" for kind, _ in kept):
        return None, omitted
    # A heading with no entry under it, before the next heading or the end, is dropped.
    out = [f"### {title}"]
    for i, (kind, chunk) in enumerate(kept):
        if kind == "heading":
            rest = kept[i + 1:]
            nxt = next((k for k, _ in rest if k != "blank"), None)
            if nxt != "entry":
                continue
        out += chunk
    while out and not out[-1]:
        out.pop()
    # Runs of blank lines left by the dropped references and entries collapse to one.
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)), omitted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changelog", required=True)
    ap.add_argument("--from", dest="old", required=True)
    ap.add_argument("--to", dest="new", required=True)
    ap.add_argument("--repo", required=True)
    args = ap.parse_args()

    old, new = parse_tag(args.old), parse_tag(args.new)
    with open(args.changelog, encoding="utf-8") as f:
        text = f.read()

    found = list(sections(text))
    if not found:
        sys.exit(f"pin_notes: {args.changelog} has no release sections; refusing to say there are no entries")
    if not any(s[0] == new for s in found):
        sys.exit(f"pin_notes: {args.changelog} has no section for {args.new}; refusing to say there are no entries")
    picked = [s for s in found if old < s[0] <= new]
    picked.sort(key=lambda s: s[0], reverse=True)

    shown = []
    omitted = 0
    if picked:
        # The repository's own name is also something the readers cannot resolve.
        repo_name = re.compile(re.escape(args.repo.split("/")[-1]), re.IGNORECASE)
        rendered = [render(version, date, lines, repo_name) for version, date, lines, _ in picked]
        shown = [t for t, _ in rendered if t]
        omitted = sum(n for _, n in rendered)

    out = [
        f"Moves the Overmind pin from {args.old} to {args.new}.",
        "",
    ]
    if new[:2] > old[:2]:
        where = "the entries below" if shown else "the new version"
        out += [
            f"The extension contract changed between {args.old} and {args.new}, because the "
            f"minor version moved. Check this repository's extension against {where} "
            "before merging.",
            "",
        ]
    out += [f"## Changes since {args.old}", ""]
    if shown:
        out.append("\n\n".join(shown))
    elif not omitted:
        out.append(f"No changelog entries since {args.old}.")
    if omitted:
        if shown:
            noun = "entry is" if omitted == 1 else "entries are"
            out += ["", f"{omitted} changelog {noun} left out of this list because the text cannot be shown here."]
        else:
            noun = "entry cannot" if omitted == 1 else "entries cannot"
            out.append(f"{omitted} changelog {noun} be shown here, so none are listed.")
    # The earliest section's compare link names the release just before it. When that is
    # the pinned version, the changelog covers everything since the pin.
    earliest = min(found, key=lambda s: s[0])
    base = COMPARE_BASE.search(earliest[3] or "")
    if old < earliest[0] and not (base and base.group(1) == args.old):
        out += ["", "The changelog starts at v%d.%d.%d; it cannot show anything older." % earliest[0]]
    print("\n".join(out).rstrip())


if __name__ == "__main__":
    main()
