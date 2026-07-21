#!/usr/bin/env python3
"""Compile a single-file podcast YAML into a meta.json + chunk files consumable by render_yaml_chunks.py

Usage:
  py -3.11 tools/yaml_podcast_compiler.py run/podcast_single_file_example.yaml --out-meta run/my_episode_meta.json

YAML schema (simple):

title: string
episode_id: string
language: deu|eng
voice_map_file: optional path
style: { ... }
speakers: { role: {name:..., voice:...} }
segments:
  - id: intro
    text: |
      Plain text or markdown for TTS
    xtts_speed: 1.05
    xtts_temperature: 0.8
    pre_ssml: false

The script writes chunk text files: run/<episode>_chunk1.txt ... and a meta JSON with keys used by render_yaml_chunks.py
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

try:
    import yaml
except Exception:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    raise


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile single-file podcast YAML to meta.json + chunks")
    ap.add_argument("input", help="Input YAML file")
    ap.add_argument("--out-meta", help="Output meta.json path", required=True)
    ap.add_argument("--out-dir", help="Directory for chunk files (default: same dir as out-meta)")
    ap.add_argument("--auto-annotate", action="store_true", help="Run simple heuristic emotion annotator and emit per-chunk annotations JSON")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"Input not found: {inp}", file=sys.stderr)
        return 2

    with inp.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    title = str(doc.get("title", "episode"))
    episode_id = str(doc.get("episode_id", Path(inp).stem))
    language = str(doc.get("language", "deu"))
    style = doc.get("style", {}) or {}
    speakers = doc.get("speakers", {}) or {}
    voice_map_file = doc.get("voice_map_file", "")

    segments = doc.get("segments", []) or []
    if not isinstance(segments, list) or not segments:
        print("No segments found in YAML", file=sys.stderr)
        return 3

    out_meta = Path(args.out_meta)
    out_dir = Path(args.out_dir) if args.out_dir else out_meta.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    chunk_files: list[str] = []
    chunk_overrides: list[dict] = []
    chunk_sfx: list[dict] = []

    # Full text aggregation
    full_text_parts: list[str] = []

    for i, seg in enumerate(segments, start=1):
        seg_id = seg.get("id", f"chunk{i}")
        text = seg.get("text", "") or ""
        ssml = seg.get("ssml", "") or ""
        pre_ssml = bool(seg.get("pre_ssml", False))
        # choose output filename: .txt for plain text, .ssml if pre_ssml true or ssml provided
        if pre_ssml or ssml:
            fname = f"{episode_id}_chunk{i}.ssml"
            out_path = out_dir / fname
            if ssml:
                out_path.write_text(ssml, encoding="utf-8")
            else:
                # wrap plain text in minimal SSML
                out_path.write_text(f"<speak>{text}</speak>", encoding="utf-8")
        else:
            fname = f"{episode_id}_chunk{i}.txt"
            out_path = out_dir / fname
            out_path.write_text(str(text), encoding="utf-8")

        chunk_files.append(str(out_path))

        # collect overrides (including SFX/music hints)
        override: dict = {}
        for k in ("xtts_speed", "xtts_temperature", "xtts_top_p", "xtts_repetition_penalty", "voice"):
            if k in seg:
                override[k] = seg[k]
        # SFX / music integration fields
        for k in ("sfx_before", "sfx_after", "background_music", "sfx_volume", "music_volume", "sfx_crossfade_ms", "blend_mode"):
            if k in seg:
                override[k] = seg[k]
        chunk_overrides.append(override)

        # collect sfx info (optional fields: sfx_before, sfx_after, background_music)
        sfx_info: dict = {}
        for s in ("sfx_before", "sfx_after", "background_music"):
            if s in seg:
                sfx_info[s] = seg[s]
        chunk_sfx.append(sfx_info)

        # optional: auto-annotate simple emotion/focus hints per-segment
        # We'll generate a lightweight annotations list per chunk if requested
        # (populated later when --auto-annotate is passed)
        

        # append to full text
        if text:
            full_text_parts.append(text)
        elif ssml:
            # strip tags naive
            import re

            plain = re.sub(r"<[^>]+>", "", ssml)
            full_text_parts.append(plain)

    full_text_file = out_dir / f"{episode_id}_full.txt"
    full_text_file.write_text("\n\n".join(full_text_parts), encoding="utf-8")

    meta = {
        "input": str(inp),
        "episode_id": episode_id,
        "language": language,
        "speakers": speakers,
        "style": style,
        "full_text_file": str(full_text_file),
        "chunk_files": chunk_files,
        "voice_map_file": voice_map_file or "",
        "chunk_overrides": chunk_overrides,
        "chunk_sfx": chunk_sfx,
        "chunk_annotations": [],
        "recommended_cli": {
            "script_podcast_speakers": doc.get("recommended_cli", {}).get("script_podcast_speakers", "host"),
            "script_podcast_voice_map": doc.get("recommended_cli", {}).get("script_podcast_voice_map", ""),
            "chunk_limit": doc.get("recommended_cli", {}).get("chunk_limit", 900),
        },
    }

    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote meta: {out_meta}")
    # If requested, run a simple auto-annotator for each chunk and attach to meta
    if args.auto_annotate:
        try:
            from pathlib import Path as _P

            def _simple_annotate(text: str) -> list[dict]:
                import re

                # Load optional external lexicon to enrich the built-in list
                lex = {
                    'glücklich': 'joy',
                    'freude': 'joy',
                    'traurig': 'sad',
                    'weinen': 'sad',
                    'wütend': 'anger',
                    'zorn': 'anger',
                    'furcht': 'fear',
                    'ängstlich': 'fear',
                    'überrascht': 'surprise',
                    'schock': 'surprise',
                    'liebe': 'joy',
                    'schrecklich': 'sad',
                    'furchtbar': 'anger',
                    'entzückt': 'joy',
                    'begeistert': 'joy',
                    'enttäuscht': 'sad',
                    'bestürzt': 'sad',
                    'empört': 'anger',
                    'verärgert': 'anger',
                    'besorgt': 'fear',
                    'panik': 'fear',
                    'schockiert': 'surprise',
                    'überwältigt': 'surprise',
                    'zufrieden': 'joy',
                    'erschüttert': 'sad',
                }
                # allow a local lexicon override/extension at tools/lexica/emotion_lexicon_de.json
                try:
                    base = Path(__file__).parent / 'lexica'
                    lex_de = base / 'emotion_lexicon_de.json'
                    lex_en = base / 'emotion_lexicon_en.json'
                    if lex_de.exists():
                        with lex_de.open('r', encoding='utf-8') as lf:
                            data = json.load(lf)
                        if isinstance(data, dict):
                            lex.update({k: v for k, v in data.items() if isinstance(v, str)})
                    if lex_en.exists():
                        with lex_en.open('r', encoding='utf-8') as lf:
                            data2 = json.load(lf)
                        if isinstance(data2, dict):
                            lex.update({k: v for k, v in data2.items() if isinstance(v, str)})
                except Exception:
                    pass
                intensifiers = {
                    'sehr': 1.3,
                    'extrem': 1.5,
                    'etwas': 0.8,
                    'ein wenig': 0.7,
                }
                anns: list[dict] = []
                if not text:
                    return anns
                low = text.lower()
                # word-level hits
                for w, emo in lex.items():
                    if re.search(r'\b' + re.escape(w) + r'\b', low):
                        # base intensity
                        intensity = 0.9
                        # check for nearby intensifiers
                        for it, mul in intensifiers.items():
                            if it in low:
                                intensity = min(1.0, intensity * mul)
                        anns.append({"text": w, "emotion": emo, "intensity": round(float(intensity), 2)})
                # punctuation signals: exclamation mark -> boost
                if '!' in text:
                    anns.append({"text": text.strip()[:80], "emotion": "anger", "intensity": 0.7})
                # ellipsis -> add pause hint
                if '...' in text or '…' in text:
                    anns.append({"text": text.strip()[:80], "overrides": {"pause_ms": 300}})
                # if no word-level annotation, add neutral / focus of sentence
                if not anns:
                    # small heuristic: short sentences with exclamation/question -> mark as focus
                    words = re.findall(r"\b\w+\b", text)
                    if len(words) < 8 and any(c in text for c in ('!', '?')):
                        anns.append({"text": text.strip()[:80], "emotion": "surprise", "intensity": 0.6})
                return anns

            # iterate chunks and write annotation files
            for idx, cf in enumerate(meta.get('chunk_files', [])):
                p = _P(cf)
                txt = ''
                try:
                    txt = p.read_text(encoding='utf-8')
                except Exception:
                    txt = ''
                ann_list = _simple_annotate(txt)
                ann_path = out_dir / (p.stem + '.annotations.json')
                try:
                    ann_path.write_text(json.dumps(ann_list, ensure_ascii=False, indent=2), encoding='utf-8')
                except Exception:
                    pass
                meta['chunk_annotations'].append(str(ann_path))
                # If we have a plain text chunk and text_to_ssml exists, produce a .ssml variant
                try:
                    if p.suffix.lower() == '.txt':
                        tssml = out_dir / (p.stem + '.ssml')
                        tssml_cmd = [sys.executable, str(Path(__file__).parent / 'text_to_ssml.py'), str(p), '--out', str(tssml), '--annotations', str(ann_path)]
                        # include lexicon if present in same dir
                        lex = out_dir / 'lexicon.json'
                        if lex.exists():
                            tssml_cmd.extend(['--lexicon', str(lex)])
                        try:
                            import subprocess as _sub

                            _sub.run(tssml_cmd, check=False)
                            # if created, replace chunk file entry with .ssml
                            if tssml.exists():
                                meta['chunk_files'][idx] = str(tssml)
                        except Exception:
                            pass
                except Exception:
                    pass
            # update meta.json with annotation paths
            out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Wrote annotations for {len(meta['chunk_annotations'])} chunks")
        except Exception as e:
            print(f"Auto-annotate failed: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
