#!/usr/bin/env python3
"""Smoke runner: compile example YAML and preprocess chunks to SSML without calling the heavy renderer.

Usage: python tools/run_smoke_preproc.py [path/to/episode.yaml]
"""
from pathlib import Path
import subprocess
import sys
import json

ROOT = Path(__file__).parent.parent
PY = sys.executable

EP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'run' / 'example_episode.yaml'
if not EP.exists():
    print('Example YAML not found:', EP)
    raise SystemExit(2)

meta_out = EP.with_suffix('.meta.json')

print('Compiling:', EP)
res = subprocess.run([PY, str(ROOT / 'tools' / 'yaml_podcast_compiler.py'), str(EP), '--out-meta', str(meta_out), '--auto-annotate'], capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print('Compiler failed:', res.stderr)
    raise SystemExit(res.returncode)

meta = json.loads(meta_out.read_text(encoding='utf-8'))
chunks = meta.get('chunk_files', [])
print('Chunks count:', len(chunks))
failed = 0
for c in chunks:
    p = Path(c)
    ssml_out = p.with_suffix('.ssml')
    ann = p.with_suffix('.annotations.json')
    cmd = [PY, str(ROOT / 'tools' / 'text_to_ssml.py'), str(p), '--out', str(ssml_out), '--lexicon', str(ROOT / 'tools' / 'lexica' / 'emotion_lexicon_de.json')]
    if ann.exists():
        cmd += ['--annotations', str(ann)]
    print('Preprocessing chunk:', p.name)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('Preproc failed for', p, r.stderr)
        failed += 1
    else:
        print('Wrote', ssml_out)

print('Smoke run done. failed preprocess:', failed)
raise SystemExit(0)
