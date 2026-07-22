#!/usr/bin/env python3
"""Convert ebook/text sources into a unified 1-speaker podcast YAML.

Supported input formats:
- .txt, .md
- .epub
- .html, .htm
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_html_file(path: Path) -> str:
    from bs4 import BeautifulSoup

    raw = _read_text_file(path)
    soup = BeautifulSoup(raw, "html.parser")
    return soup.get_text("\n")


def _read_epub_file(path: Path) -> str:
    import ebooklib
    from bs4 import BeautifulSoup
    from ebooklib import epub

    book = epub.read_epub(str(path))
    parts: list[str] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        txt = soup.get_text("\n")
        if txt.strip():
            parts.append(txt)
    return "\n\n".join(parts)


def _clean_text(raw: str) -> str:
    txt = raw.replace("\r\n", "\n").replace("\r", "\n")
    txt = re.sub(r"[\t\f\v]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"[ ]{2,}", " ", txt)
    return txt.strip()


def _to_paragraphs(text: str, max_len: int) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out: list[str] = []
    current = ""
    for p in paras:
        if not p:
            continue
        candidate = p if not current else f"{current} {p}"
        if len(candidate) <= max_len:
            current = candidate
            continue
        if current:
            out.append(current)
            current = ""
        if len(p) <= max_len:
            current = p
            continue
        # Split only if a single paragraph is still too long.
        sentences = re.split(r"(?<=[.!?])\s+", p)
        tmp = ""
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            cand = s if not tmp else f"{tmp} {s}"
            if len(cand) <= max_len:
                tmp = cand
            else:
                if tmp:
                    out.append(tmp)
                tmp = s
        if tmp:
            current = tmp
    if current:
        out.append(current)
    return out


def _load_source(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return _read_text_file(path)
    if ext in {".html", ".htm"}:
        return _read_html_file(path)
    if ext == ".epub":
        return _read_epub_file(path)
    raise ValueError(f"Unsupported input format: {ext}")


def _build_yaml(
    title: str,
    language: str,
    speaker_name: str,
    speaker_voice: str,
    episode_id: str,
    paragraphs: list[str],
) -> dict[str, Any]:
    return {
        "podcast": {
            "title": title,
            "language": language,
            "format": "narrative",
            "speakers": {
                "host": {
                    "name": speaker_name,
                    "voice": speaker_voice,
                }
            },
            "style": {
                "script_natural_preset": "natural_audiobook_de",
                "script_speaker_mode": "heuristic",
                "script_format_mode": "narrative",
                "script_multispeaker_speakers": 1,
                "script_filler_mode": "off",
                "script_emotion_mode": "light",
                "script_style_preset": "documentary",
                "script_paragraph_pause": 0.52,
                "tempo": 0.97,
                "energy": "medium",
                "target_dbfs": -18.0,
                "crossfade_ms": 120,
            },
            "episodes": [
                {
                    "id": episode_id,
                    "segments": [
                        {
                            "type": "chapter",
                            "turns": [
                                {
                                    "speaker": "host",
                                    "text": p,
                                    "tempo": 0.97,
                                    "energy": "medium",
                                    "pause_after": 0.52,
                                }
                                for p in paragraphs
                            ],
                        }
                    ],
                }
            ],
        }
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert ebook/text into a unified 1-speaker podcast YAML")
    ap.add_argument("--input", required=True, help="Path to source file (.txt/.md/.epub/.html)")
    ap.add_argument("--output", required=True, help="Path to output YAML")
    ap.add_argument("--title", default=None, help="Podcast title (default: input stem)")
    ap.add_argument("--language", default="deu", help="ISO-639-3 language code, e.g. deu/eng")
    ap.add_argument("--speaker-name", default="Narrator", help="Single speaker display name")
    ap.add_argument("--speaker-voice", required=True, help="Absolute voice file path")
    ap.add_argument("--episode-id", default="episode_1", help="Episode id")
    ap.add_argument("--max-paragraph-len", type=int, default=700, help="Max chars per paragraph turn")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    voice_path = Path(args.speaker_voice)
    if not voice_path.exists():
        raise SystemExit(f"Speaker voice not found: {voice_path}")

    raw = _load_source(in_path)
    cleaned = _clean_text(raw)
    if not cleaned:
        raise SystemExit("Source is empty after cleaning")

    paragraphs = _to_paragraphs(cleaned, max_len=max(200, int(args.max_paragraph_len)))
    if not paragraphs:
        raise SystemExit("No paragraphs generated")

    title = args.title or in_path.stem
    model = _build_yaml(
        title=title,
        language=str(args.language).strip().lower(),
        speaker_name=str(args.speaker_name).strip(),
        speaker_voice=str(voice_path.as_posix()),
        episode_id=str(args.episode_id).strip(),
        paragraphs=paragraphs,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(model, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote YAML: {out_path}")
    print(f"Turns: {len(paragraphs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
