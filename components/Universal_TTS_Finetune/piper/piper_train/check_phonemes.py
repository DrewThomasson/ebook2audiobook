#!/usr/bin/env python3
import json
import sys
import unicodedata
from collections import Counter

from .phonemize import DEFAULT_PHONEME_ID_MAP


def main() -> None:
    used_phonemes: "Counter[str]" = Counter()
    missing_phonemes: "Counter[str]" = Counter()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        utt = json.loads(line)
        for phoneme in utt["phonemes"]:
            used_phonemes[phoneme] += 1

            if phoneme not in DEFAULT_PHONEME_ID_MAP:
                missing_phonemes[phoneme] += 1

    if missing_phonemes:
        print("Missing", len(missing_phonemes), "phoneme(s)", file=sys.stderr)

    json.dump(
        {
            "used": {
                phoneme: {
                    "count": count,
                    "hex": f"\\u{hex(ord(phoneme))}",
                    "name": unicodedata.category(phoneme),
                    "category": unicodedata.category(phoneme),
                }
                for phoneme, count in used_phonemes.most_common()
            },
            "missing": {
                phoneme: {
                    "count": count,
                    "hex": f"\\u{hex(ord(phoneme))}",
                    "name": unicodedata.category(phoneme),
                    "category": unicodedata.category(phoneme),
                }
                for phoneme, count in missing_phonemes.most_common()
            },
        },
        sys.stdout,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
