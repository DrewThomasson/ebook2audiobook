#!/usr/bin/env python3
"""Audit repository for assets that must be present for offline runs.

Checks:
 - presence of audio files under `voices/`
 - presence of engine files under `models/tts` (per `lib/conf_models.default_engine_settings`)
 - lists files referenced by hf_hub_download and from_pretrained locations

Outputs missing items and suggested hf_hub_download commands.
"""
from pathlib import Path
import json
import os
import re
import sys

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from lib.conf import tts_dir, voices_dir
from lib.conf_models import default_engine_settings, TTS_ENGINES


def find_files_recursive(base: Path, name: str) -> list:
    return [p for p in base.rglob(name) if p.is_file()]


def check_voices():
    vdir = Path(voices_dir)
    wavs = list(vdir.rglob('*.wav'))
    if wavs:
        print(f"Voices: OK ({len(wavs)} .wav files found under {vdir})")
        return True
    else:
        print(f"Voices: MISSING — no .wav files found under {vdir}")
        print("Suggestion: run the device installer or place a voices archive extracted into that folder.")
        return False


def check_tts_engine_files():
    print("\nChecking TTS engine required files under tts_dir:")
    missing = []
    tdir = Path(tts_dir)
    for engine, cfg in default_engine_settings.items():
        files = cfg.get('files', []) or []
        repo = cfg.get('repo')
        if not files:
            continue
        engine_missing = []
        for fn in files:
            found = False
            # search for filename anywhere under tts_dir
            for p in tdir.rglob(fn):
                if p.is_file():
                    found = True
                    break
            if not found:
                engine_missing.append(fn)
        if engine_missing:
            print(f" - {engine}: missing {engine_missing} (repo:{repo})")
            missing.append((engine, repo, engine_missing))
        else:
            print(f" - {engine}: OK")
    return missing


def scan_code_references():
    print("\nScanning code for HF / from_pretrained usage (files and model names):")
    refs = []
    repo_root = Path('.')
    for p in repo_root.rglob('*.py'):
        try:
            s = p.read_text(encoding='utf-8')
        except Exception:
            continue
        if 'hf_hub_download' in s or 'from_pretrained' in s:
            lines = []
            for i, line in enumerate(s.splitlines(), start=1):
                if 'hf_hub_download' in line or 'from_pretrained' in line:
                    lines.append((i, line.strip()))
            if lines:
                refs.append((str(p), lines))
    for f, lines in refs:
        print(f" - {f}")
        for ln, text in lines:
            print(f"    L{ln}: {text}")
    return refs


def recommend_downloads(missing):
    print('\nRecommendations to pre-download missing assets:')
    for engine, repo, files in missing:
        print(f"\nEngine: {engine} repo: {repo}")
        for fn in files:
            print(f" - Python: from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='{repo}', filename='{fn}', cache_dir=r'{tts_dir}')")
            print(f" - Or place the file under {tts_dir} (recursive).")


def attempt_auto_download(missing):
    try:
        from huggingface_hub import hf_hub_download
    except Exception as e:
        print('\nAuto-download requested but huggingface_hub is not available:')
        print(' - Install it with: pip install huggingface-hub')
        print(f' - Import error: {e}')
        return False

    print('\nAttempting automatic downloads for entries with a known repo...')
    success = True
    for engine, repo, files in missing:
        if not repo or repo in ('None', 'None'):
            print(f" - Skipping {engine}: no repo configured (cannot auto-download)")
            success = False
            continue
        for fn in files:
            try:
                print(f"Downloading {fn} from {repo} -> {tts_dir}...")
                p = hf_hub_download(repo_id=repo, filename=fn, cache_dir=tts_dir)
                print(f" -> downloaded: {p}")
            except Exception as e:
                print(f"Failed to download {fn} from {repo}: {e}")
                success = False
    return success


def main():
    print('Offline audit starting...')
    ok_voice = check_voices()
    missing = check_tts_engine_files()
    refs = scan_code_references()

    recommend_downloads(missing)

    # support --auto-download
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto-download', action='store_true', help='Attempt to automatically download missing assets from HF for known repos')
    args, _ = parser.parse_known_args()
    if args.auto_download:
        ok_dl = attempt_auto_download(missing)
        if ok_dl:
            print('\nAuto-download completed (check above for details).')
        else:
            print('\nAuto-download attempted; some items failed or were skipped.')
    print('\nAudit complete.')
    if not ok_voice or missing:
        print('\nStatus: NOT READY for fully offline rendering. See recommendations above.')
        raise SystemExit(2)
    else:
        print('\nStatus: looks good for offline rendering of core TTS engines (files present).')
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
