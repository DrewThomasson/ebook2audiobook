#!/usr/bin/env python3
"""Try downloading candidate filenames from a given HF repo and report results."""
from huggingface_hub import hf_hub_download
from pathlib import Path
import sys

repo = 'coqui/XTTS-v2'
filenames = [
    'speakers_xtts.pth',
    'config.json',
    'model.pth',
    'vocab.json',
    'ref.wav',
    'config.json.gz'
]
cache = r'C:\Projects\ebook2audiobook\models\tts'
Path(cache).mkdir(parents=True, exist_ok=True)

for fn in filenames:
    try:
        print(f"Trying {fn}...")
        p = hf_hub_download(repo_id=repo, filename=fn, cache_dir=cache)
        print(f" OK: {p}")
    except Exception as e:
        print(f" FAIL: {fn} -> {e}")

print('Done')
