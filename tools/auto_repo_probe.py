#!/usr/bin/env python3
"""Probe repository to find likely HF repo IDs for engines lacking repo in conf_models.

Strategy:
 - Load default_engine_settings from lib.conf_models.
 - For any engine without a repo, search workspace for HF-like repo strings and tokens near engine name.
 - Build candidate repo list and attempt to download configured filenames.
 - Report successes and failures.
"""
from pathlib import Path
import re
import sys
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from lib.conf_models import default_engine_settings, TTS_ENGINES
from lib.conf import tts_dir

import itertools

# gather candidate repo ids from code by regex
repo_pattern = re.compile(r"(?:huggingface.co/|repo_id=\s*['\"])([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)")

candidates = set()
for p in Path('.').rglob('*.py'):
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        continue
    for m in repo_pattern.findall(s):
        candidates.add(m)

print('Found candidate repo ids in code:')
for c in sorted(candidates):
    print(' -', c)

# engines to probe
to_probe = []
for engine, cfg in default_engine_settings.items():
    repo = cfg.get('repo')
    files = cfg.get('files', []) or []
    if not repo and files:
        to_probe.append((engine, files))

print('\nEngines to probe (no repo configured but files declared):')
for engine, files in to_probe:
    print(f' - {engine}: files={files}')

# heuristic candidate mapping: if candidate contains engine name or common names
engine_candidates = {}
for engine, files in to_probe:
    name = engine.lower()
    cand = [c for c in candidates if name in c.lower()]
    # add some common guesses
    if engine.lower() == 'piper':
        cand += ['v2piper/piper', 'ndeep/piper', 'coqui/piper']
    if engine.lower() == 'vits':
        cand += ['tonyliu/vits', 'ljw/vits', 'espnet/vits']
    if engine.lower() == 'fairseq':
        cand += ['facebookresearch/fairseq', 'fairseq/fairseq']
    # dedupe
    engine_candidates[engine] = list(dict.fromkeys(cand))

for engine, cands in engine_candidates.items():
    print(f'\nCandidates for {engine}:')
    if cands:
        for c in cands:
            print(' -', c)
    else:
        print(' - none found')

# attempt downloads for candidates
try:
    from huggingface_hub import hf_hub_download
except Exception as e:
    print('\nhuggingface_hub not available; install with pip install huggingface-hub')
    raise SystemExit(1)

for engine, files in to_probe:
    print(f'\nProbing {engine}...')
    cands = engine_candidates.get(engine, [])
    if not cands:
        print(' No candidates to try')
        continue
    for repo in cands:
        print(' Trying repo:', repo)
        for fn in files:
            try:
                p = hf_hub_download(repo_id=repo, filename=fn, cache_dir=tts_dir)
                print(f'  OK {fn} -> {p}')
            except Exception as e:
                print(f'  FAIL {fn} from {repo}: {e}')

print('\nProbe complete.')
