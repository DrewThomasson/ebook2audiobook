#!/usr/bin/env python3
"""Compile a YAML podcast script into renderable text chunks + voice-map JSON.

This tool keeps speaker roles as metadata and emits natural, attributed dialog
sentences for TTS pipelines.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install with: pip install PyYAML"
    ) from exc


ROLE_SANITIZE = re.compile(r"[^a-z0-9_]+")


@dataclass
class Speaker:
    role: str
    name: str
    voice: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _energy_to_value(value: Any, default: float = 0.55) -> float:
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 1.0:
            raw = raw / 100.0
        return _clamp(raw, 0.10, 0.95)
    s = str(value or "").strip().lower()
    if s in ("low", "calm", "soft"):
        return 0.35
    if s in ("high", "energetic", "strong"):
        return 0.80
    if s in ("medium", "mid", "normal"):
        return 0.55
    return _clamp(default, 0.10, 0.95)


def _normalize_natural_preset(style: dict[str, Any]) -> None:
    key = str(style.get("script_natural_preset", "manual") or "manual").strip().lower()
    if key == "natural_audiobook":
        style["script_natural_preset"] = "natural_audiobook_de"
    elif key == "natural_podcast":
        style["script_natural_preset"] = "podcast_conversational_de"


def _sanitize_role(role: str) -> str:
    cleaned = ROLE_SANITIZE.sub("", role.strip().lower().replace("-", "_").replace(" ", "_"))
    if not cleaned:
        raise ValueError("Speaker role cannot be empty after sanitization")
    return cleaned


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be an object")
    return data


def _validate(data: dict[str, Any]) -> tuple[dict[str, Speaker], list[dict[str, Any]], dict[str, Any]]:
    podcast = data.get("podcast")
    if not isinstance(podcast, dict):
        raise ValueError("Missing podcast object")

    speakers_raw = podcast.get("speakers")
    if not isinstance(speakers_raw, dict) or not speakers_raw:
        raise ValueError("podcast.speakers must be a non-empty object")

    speakers: dict[str, Speaker] = {}
    for role_raw, cfg in speakers_raw.items():
        if not isinstance(cfg, dict):
            raise ValueError(f"Speaker '{role_raw}' must be an object")
        role = _sanitize_role(str(role_raw))
        name = str(cfg.get("name", "")).strip()
        voice = str(cfg.get("voice", "")).strip()
        if not name:
            raise ValueError(f"Speaker '{role}' is missing name")
        if not voice:
            raise ValueError(f"Speaker '{role}' is missing voice")
        speakers[role] = Speaker(role=role, name=name, voice=voice)

    if "host" not in speakers:
        raise ValueError("podcast.speakers must include host")

    episodes = podcast.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        raise ValueError("podcast.episodes must be a non-empty list")

    style = podcast.get("style") if isinstance(podcast.get("style"), dict) else {}
    return speakers, episodes, style


def _verb_for_turn(text: str, is_host: bool) -> str:
    s = text.strip()
    if s.endswith("?"):
        return "fragte"
    if is_host:
        return "sagte"
    return "antwortete"


def _render_turn(speaker: Speaker, text: str, is_host: bool) -> str:
    txt = text.strip()
    if not txt:
        return ""
    verb = _verb_for_turn(txt, is_host)
    return f'"{txt}", {verb} {speaker.name}.'


def _auto_pause_seconds(text: str, role: str, style: dict[str, Any]) -> float:
    s = (text or "").strip()
    base = _to_float(style.get("script_paragraph_pause", 0.40), 0.40)
    if s.endswith("?"):
        base -= 0.10
    elif s.endswith("!"):
        base -= 0.08
    elif s.endswith(":"):
        base += 0.10
    elif s.endswith("."):
        base += 0.04
    if role == "host":
        base += 0.03
    return _clamp(base, 0.20, 1.60)


def _resolve_turn_controls(turn: dict[str, Any], rendered_text: str, role: str, style: dict[str, Any]) -> tuple[float, float, float]:
    default_tempo = _clamp(_to_float(style.get("tempo", style.get("default_tempo", 1.0)), 1.0), 0.85, 1.15)
    default_energy = _energy_to_value(style.get("energy", style.get("default_energy", 0.55)), 0.55)
    tempo = _clamp(_to_float(turn.get("tempo", default_tempo), default_tempo), 0.85, 1.15)
    energy = _energy_to_value(turn.get("energy", default_energy), default_energy)

    raw_pause = turn.get("pause_after", None)
    if raw_pause is None:
        pause_after = _auto_pause_seconds(rendered_text, role, style)
    else:
        pause_after = _clamp(_to_float(raw_pause, 0.0), 0.0, 3.0)
    return tempo, energy, pause_after


def _compile_episode_paragraphs(episode: dict[str, Any], speakers: dict[str, Speaker], style: dict[str, Any]) -> list[dict[str, Any]]:
    segments = episode.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError(f"Episode '{episode.get('id', '<unknown>')}' needs non-empty segments")

    paragraphs: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, dict):
            raise ValueError("Each segment must be an object")
        turns = seg.get("turns")
        if not isinstance(turns, list) or not turns:
            raise ValueError("Each segment must have non-empty turns")

        lines: list[str] = []
        tempo_vals: list[float] = []
        energy_vals: list[float] = []
        for turn in turns:
            if not isinstance(turn, dict):
                raise ValueError("Each turn must be an object")
            role = _sanitize_role(str(turn.get("speaker", "")))
            text = str(turn.get("text", "")).strip()
            if role not in speakers:
                raise ValueError(f"Unknown speaker role in turn: {role}")
            rendered = _render_turn(speakers[role], text, is_host=(role == "host"))
            if rendered:
                tempo, energy, pause_after = _resolve_turn_controls(turn, rendered, role, style)
                if pause_after > 0:
                    rendered = f"{rendered} [pause:{pause_after:.2f}]"
                lines.append(rendered)
                tempo_vals.append(tempo)
                energy_vals.append(energy)

        if lines:
            paragraphs.append(
                {
                    "text": " ".join(lines).strip(),
                    "tempo": sum(tempo_vals) / len(tempo_vals) if tempo_vals else 1.0,
                    "energy": sum(energy_vals) / len(energy_vals) if energy_vals else 0.55,
                }
            )

    return paragraphs


def _chunk_paragraphs(paragraphs: list[dict[str, Any]], max_chars: int, style: dict[str, Any]) -> tuple[list[str], list[dict[str, float]]]:
    chunks: list[str] = []
    overrides: list[dict[str, float]] = []
    current = ""
    current_tempo: list[float] = []
    current_energy: list[float] = []

    def _override_from_values(tempo_vals: list[float], energy_vals: list[float]) -> dict[str, float]:
        avg_tempo = sum(tempo_vals) / len(tempo_vals) if tempo_vals else _to_float(style.get("tempo", 1.0), 1.0)
        avg_energy = sum(energy_vals) / len(energy_vals) if energy_vals else _energy_to_value(style.get("energy", 0.55), 0.55)
        base_temp = _to_float(style.get("xtts_temperature", 0.78), 0.78)
        base_top_p = _to_float(style.get("xtts_top_p", 0.92), 0.92)
        base_rep = _to_float(style.get("xtts_repetition_penalty", 2.05), 2.05)
        return {
            "xtts_speed": round(_clamp(avg_tempo, 0.85, 1.15), 3),
            "xtts_temperature": round(_clamp(base_temp + (avg_energy - 0.55) * 0.18, 0.55, 1.05), 3),
            "xtts_top_p": round(_clamp(base_top_p + (avg_energy - 0.55) * 0.10, 0.82, 0.98), 3),
            "xtts_repetition_penalty": round(_clamp(base_rep - (avg_energy - 0.55) * 0.40, 1.60, 2.50), 3),
        }

    def _flush() -> None:
        nonlocal current, current_tempo, current_energy
        if current:
            chunks.append(current)
            overrides.append(_override_from_values(current_tempo, current_energy))
            current = ""
            current_tempo = []
            current_energy = []

    for para in paragraphs:
        p = str(para.get("text", "")).strip()
        if not p:
            continue
        p_tempo = _clamp(_to_float(para.get("tempo", 1.0), 1.0), 0.85, 1.15)
        p_energy = _energy_to_value(para.get("energy", 0.55), 0.55)
        candidate = p if not current else f"{current}\n\n{p}"
        if len(candidate) <= max_chars:
            current = candidate
            current_tempo.append(p_tempo)
            current_energy.append(p_energy)
            continue

        _flush()

        if len(p) <= max_chars:
            current = p
            current_tempo = [p_tempo]
            current_energy = [p_energy]
            continue

        sentences = re.split(r"(?<=[.!?])\s+", p)
        tmp = ""
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            c2 = sent if not tmp else f"{tmp} {sent}"
            if len(c2) <= max_chars:
                tmp = c2
            else:
                if tmp:
                    chunks.append(tmp)
                    overrides.append(_override_from_values([p_tempo], [p_energy]))
                tmp = sent
        if tmp:
            current = tmp
            current_tempo = [p_tempo]
            current_energy = [p_energy]

    _flush()
    return chunks, overrides


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile YAML podcast script to plain text chunks + voice map")
    ap.add_argument("--input", required=True, help="Path to podcast YAML file")
    ap.add_argument("--out-dir", default="run", help="Output directory")
    ap.add_argument("--prefix", default="podcast_compiled", help="Output filename prefix")
    ap.add_argument("--episode-id", default=None, help="Episode ID to compile; default first episode")
    ap.add_argument("--max-chars", type=int, default=900, help="Max chars per chunk for --text mode")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = _load_yaml(in_path)
    speakers, episodes, style = _validate(data)
    _normalize_natural_preset(style)

    selected = None
    if args.episode_id:
        for ep in episodes:
            if str(ep.get("id", "")).strip() == args.episode_id:
                selected = ep
                break
        if selected is None:
            raise SystemExit(f"Episode id not found: {args.episode_id}")
    else:
        selected = episodes[0]

    paragraphs = _compile_episode_paragraphs(selected, speakers, style)
    compiled = "\n\n".join(p["text"] for p in paragraphs if p.get("text"))

    full_path = out_dir / f"{args.prefix}_full.txt"
    full_path.write_text(compiled, encoding="utf-8")

    chunks, chunk_overrides = _chunk_paragraphs(paragraphs, max_chars=max(200, int(args.max_chars)), style=style)
    chunk_paths: list[Path] = []
    for i, chunk in enumerate(chunks, start=1):
        p = out_dir / f"{args.prefix}_chunk{i}.txt"
        p.write_text(chunk, encoding="utf-8")
        chunk_paths.append(p)

    voice_map = {role: s.voice for role, s in speakers.items()}
    voice_map_path = out_dir / f"{args.prefix}_voice_map.json"
    voice_map_path.write_text(json.dumps(voice_map, ensure_ascii=False, indent=2), encoding="utf-8")

    meta = {
        "input": str(in_path),
        "episode_id": selected.get("id"),
        "language": data.get("podcast", {}).get("language", "deu"),
        "speakers": {k: {"name": v.name, "voice": v.voice} for k, v in speakers.items()},
        "style": style,
        "chunk_overrides": chunk_overrides,
        "full_text_file": str(full_path),
        "chunk_files": [str(p) for p in chunk_paths],
        "voice_map_file": str(voice_map_path),
        "recommended_cli": {
            "script_podcast_speakers": ",".join(speakers.keys()),
            "script_podcast_voice_map": str(voice_map_path),
            "chunk_limit": args.max_chars,
        },
    }
    meta_path = out_dir / f"{args.prefix}_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Compiled full text: {full_path}")
    print(f"Chunk files: {len(chunk_paths)}")
    print(f"Voice map: {voice_map_path}")
    print(f"Meta: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
