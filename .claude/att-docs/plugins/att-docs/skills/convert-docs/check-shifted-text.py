#!/usr/bin/env python3
"""Reports Markdown that holds PDF glyph codes rather than the text they draw.

A PDF whose body text is set in a non-embedded font with a `Custom` encoding
and no ToUnicode map has nothing to map a glyph back to a character with.
`pdftotext` emits the glyph codes, which sit a fixed distance below the
characters they draw, and the conversion writes them into the Markdown. Every
other output invariant passes: the word count is healthy, the provenance block
is there, and the text carries no banned tag and no em dash.

The codes for the letters land between `$` and `]`, so the shifted text holds
no lowercase letter however long the run, and the space encodes to a control
character that is dropped. That second part is what makes the shape readable:
a whole phrase arrives as one unbroken token, so a token in that range whose
decoding segments into English words is shifted text and nothing else.

Usage:
  check-shifted-text.py --config FILE [--all] [--shift N] PATH...

FILE is the skill's extension.json, whose `words` field names the word list.
A directory argument is walked for `.md` files. Exits 0 clean, 2 when a file
holds shifted text, 64 without a config.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import convert_config
from doc_paths import markdown_under

# The offset between a glyph code and the character it draws. It is a property
# of the font rather than a constant, so it is an option; 29 is what a
# letterhead template uses and is the only value seen so far.
DEFAULT_SHIFT = 29

# The shortest run worth decoding, and the longest word the segmenter will try.
MIN_WORD = 4
MAX_WORD = 20

# The words the dictionary is too short to hold. A phrase arrives with its
# spaces gone, so the segmentation only reaches the end of one if it can spend
# these on the way: `youmayrequestahearing` is two dictionary words and five of
# these. They are kept apart from the dictionary because a three letter word
# matches often enough to carry a gibberish run on its own.
SHORT_WORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "but", "by", "can",
    "do", "for", "from", "had", "has", "have", "he", "her", "him", "his",
    "how", "if", "in", "is", "it", "its", "may", "must", "no", "nor", "not",
    "of", "on", "one", "or", "our", "out", "own", "per", "see", "she", "so",
    "the", "their", "them", "they", "this", "to", "two", "up", "us", "was",
    "we", "were", "who", "why", "will", "with", "you", "your",
}

# A token this long or shorter is only believed when the whole of it decodes to
# one word. Longer than this, the decoding has to segment into several. Four
# and five letter accidents are common in these documents: `FREE` decodes to
# `cobb` and `5817` to `RUNT`, and neither is a defect.
SHORT_TOKEN = 6

# The share of a long token's characters the segmentation has to account for.
COVERAGE = 0.8

# How many runs a file's report shows. A letter set in such a font carries one
# per line, and the first few say as much as all of them.
EXAMPLES = 5

# What a code arrives as when the font falls back to the standard encoding
# rather than carrying none at all. Code 39 draws the typographic quote there,
# and it stands for a capital D, which starts enough of a letter's words that
# leaving it out costs the whole run: `Dear`, `Division`, `During`.
FROM_STANDARD = {"’": "'", "‘": "`"}


def load_words(words: pathlib.Path) -> set[str]:
    return {
        line.strip().lower()
        for line in words.read_text(encoding="utf-8").splitlines()
        if len(line.strip()) >= MIN_WORD
    }


def emitted(shift: int) -> set[int]:
    """The code points a shifted encoding can produce for a letter."""
    return {ord(c) - shift for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"} | {
        ord(c) - shift for c in "abcdefghijklmnopqrstuvwxyz"
    }


def segment(low: str, words: set[str]) -> tuple[int, list[str]]:
    """Covers as much of `low` as the words can, and names the dictionary ones.

    The count that comes back is of dictionary words alone, because the short
    words are common enough that a run of them proves nothing.
    """
    best: list[tuple[int, list[str]]] = [(0, [])] * (len(low) + 1)
    for end in range(1, len(low) + 1):
        best[end] = best[end - 1]
        for start in range(max(0, end - MAX_WORD), end):
            piece = low[start:end]
            if len(piece) >= MIN_WORD:
                if piece not in words:
                    continue
                found = [piece]
            elif piece in SHORT_WORDS:
                found = []
            else:
                continue
            covered, chosen = best[start]
            if covered + len(piece) > best[end][0]:
                best[end] = (covered + len(piece), chosen + found)
    return best[len(low)]


def reads_as_english(decoded: str, words: set[str]) -> list[str] | None:
    """The words the decoding holds, or None when it holds none worth having."""
    low = decoded.lower()
    if len(low) <= SHORT_TOKEN:
        # A word the font drew keeps its own case, so a short one decodes to
        # lowercase, capitalised, or all capitals. `macK` is the decoding of
        # `PDF.` and is not a word in any case.
        if not (decoded.islower() or decoded.isupper() or decoded.istitle()):
            return None
        return [low] if low in words else None
    covered, chosen = segment(low, words)
    if covered / len(low) < COVERAGE:
        return None
    # A phrase reaches this point as several words. One long word on its own is
    # believed only when the decoding accounts for every character of it, which
    # is how a `Sincerely` standing alone arrives.
    if len(chosen) >= 2 or (chosen and covered == len(low)):
        return chosen
    return None


def scan(path: pathlib.Path, words: set[str], shift: int) -> dict:
    """Groups a file's hits into the strong ones and the short, weak ones."""
    codes = emitted(shift)
    strong: list[tuple[int, str, str]] = []
    weak: list[tuple[int, str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    # The space encodes to a control character, which is usually dropped and
    # leaves the phrase in one piece. Where it survives instead, it is a word
    # boundary, and it has to read as one rather than as part of a token.
    text = "".join(
        " " if ord(c) < 32 and c not in "\t\n" else c for c in text
    )
    for number, line in enumerate(text.splitlines(), start=1):
        for raw in line.split():
            token = "".join(FROM_STANDARD.get(c, c) for c in raw)
            if len(token) < MIN_WORD:
                continue
            if not all(ord(c) in codes for c in token):
                continue
            decoded = "".join(chr(ord(c) + shift) for c in token)
            if not decoded.isalpha():
                continue
            if reads_as_english(decoded, words) is None:
                continue
            hit = (number, raw, decoded)
            (weak if len(token) <= SHORT_TOKEN else strong).append(hit)
    return {"strong": strong, "weak": weak}


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--config", help="the skill's extension.json")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--shift", type=int, default=DEFAULT_SHIFT)
    # A short token on its own is the one shape that produces false reports, so
    # it is held back unless the file also holds a run long enough to be certain
    # about. This prints those held-back hits for a reader chasing one down.
    parser.add_argument("--all", action="store_true")
    # The conversion scans a file it has not named yet, so it says what to call
    # it in the report.
    parser.add_argument("--label")
    args = parser.parse_args()

    config = convert_config.load(args.config, "check-shifted-text")
    words = load_words(config.path("words"))
    reported = 0
    for path in markdown_under(args.paths):
        hits = scan(path, words, args.shift)
        show = hits["strong"] or (args.all and hits["weak"])
        if not show:
            continue
        if hits["strong"]:
            reported += 1
        print(f"{args.label or path}: text in a font the conversion "
              "could not map")
        found = sorted(hits["strong"] + hits["weak"])
        for number, token, decoded in found[:EXAMPLES]:
            print(f"  line {number}: {token}  reads as  {decoded}")
        if len(found) > EXAMPLES:
            print(f"  and {len(found) - EXAMPLES} more run(s)")
    if reported:
        # The tally is for a sweep of a tree. A conversion scanning the one
        # document it just produced has already said which one it was.
        if not args.label:
            print(f"\n{reported} file(s) hold shifted text")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
