#!/usr/bin/env python3
"""Merge multiple lexica JSON files into a single merged lexicon.

Usage: python tools/lexica/merge_lexica.py --dir tools/lexica --out tools/lexica/merged_lexicon.json

Notes: only merges JSON mapping of token->emotion. Does not crawl proprietary sources.
If you want Duden-style data, provide a local CC/PD/your-license file and pass it in.
"""
from pathlib import Path
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    base = Path(args.dir)
    outp = Path(args.out)
    merged = {}
    for p in sorted(base.glob('*.json')):
        try:
            with p.open('r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k, v in data.items():
                    if not k:
                        continue
                    # keep first seen mapping
                    if k in merged:
                        continue
                    merged[k] = v
        except Exception:
            continue
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote merged lexicon: {outp} ({len(merged)} entries)")


if __name__ == '__main__':
    raise SystemExit(main())
