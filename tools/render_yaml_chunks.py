#!/usr/bin/env python3
"""Render compiled YAML chunk files through app.py headless mode.

Reads the *_meta.json created by podcast_yaml_compiler.py and executes chunk-by-chunk
headless renders. Optionally merges produced audio files into one final file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import statistics
from pathlib import Path
from typing import Any

from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
from typing import Optional
import librosa
import soundfile as sf
import numpy as np


def _load_meta(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Meta JSON root must be an object")
    return data


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _words_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def _extract_pause_seconds(text: str) -> list[float]:
    values: list[float] = []
    for m in re.finditer(r"\[pause(?::([0-9]+(?:\.[0-9]+)?))?\]", text, flags=re.IGNORECASE):
        if m.group(1):
            try:
                values.append(float(m.group(1)))
            except Exception:
                values.append(1.2)
        else:
            values.append(1.2)
    return values


def _extract_voice_sequence(text: str) -> list[str]:
    seq: list[str] = []
    for m in re.finditer(r"\[voice:(.*?)\]", text, flags=re.IGNORECASE):
        seq.append((m.group(1) or "").strip().lower())
    return [x for x in seq if x]


def _extract_chunk_speakers_from_text(text: str, known_roles: list[str]) -> list[str]:
    roles: list[str] = []
    if not known_roles:
        return roles
    pattern = r"\b(" + "|".join(re.escape(r) for r in known_roles if r) + r")\b"
    for m in re.finditer(pattern, text, flags=re.IGNORECASE):
        roles.append((m.group(1) or "").strip().lower())
    return roles


def _extract_speaker_name_sequence(text: str, speaker_name_to_role: dict[str, str]) -> list[str]:
    sequence: list[str] = []
    if not speaker_name_to_role:
        return sequence
    items = sorted(
        [(name, role) for name, role in speaker_name_to_role.items() if name and role],
        key=lambda x: len(x[0]),
        reverse=True,
    )
    pattern = r"\b(" + "|".join(re.escape(name) for name, _ in items) + r")\b"
    role_map = {name.lower(): role for name, role in items}
    for m in re.finditer(pattern, text, flags=re.IGNORECASE):
        k = (m.group(1) or "").strip().lower()
        role = role_map.get(k)
        if role:
            sequence.append(role)
    return sequence


def _parse_output_audio(stdout: str) -> str | None:
    # app.py typically writes one or more lines like: Completed → C:\...\file.flac
    matches = re.findall(r"Completed\s*→\s*(.+?\.(?:flac|wav|mp3|m4a|m4b|ogg))", stdout)
    if not matches:
        return None
    return matches[-1].strip()


def _render_chunk(
    python_cmd: list[str],
    app_path: str,
    text_file: Path,
    language: str,
    speakers: str,
    voice_map: str,
    style: dict[str, Any],
    chunk_override: dict[str, Any] | None = None,
) -> subprocess.CompletedProcess[str]:
    chunk_cfg = dict(chunk_override or {})
    xtts_speed = chunk_cfg.get("xtts_speed", style.get("xtts_speed", 1.0))
    xtts_temp = chunk_cfg.get("xtts_temperature", style.get("xtts_temperature", 0.78))
    xtts_top_p = chunk_cfg.get("xtts_top_p", style.get("xtts_top_p", 0.92))
    xtts_rep = chunk_cfg.get("xtts_repetition_penalty", style.get("xtts_repetition_penalty", 2.05))
    # Engine-specific params: can be provided in style or per-chunk as dict of key->value
    # Example: {"prosody_rate": "fast", "intonation_model": "podcast_v2", "use_intensity": True}
    engine_params: dict[str, Any] = {}
    if isinstance(style.get("engine_params"), dict):
        engine_params.update(style.get("engine_params", {}))
    if isinstance(chunk_cfg.get("engine_params"), dict):
        engine_params.update(chunk_cfg.get("engine_params", {}))

    cmd = [
        *python_cmd,
        app_path,
        "--headless",
        "--text_file",
        str(text_file),
        "--language",
        language,
        "--script_layer_enabled",
        "--script_speaker_mode",
        str(style.get("script_speaker_mode", "heuristic")),
        "--script_format_mode",
        str(style.get("script_format_mode", "podcast")),
        "--script_multispeaker",
        "--script_multispeaker_speakers",
        str(style.get("script_multispeaker_speakers", 2)),
        "--script_podcast_speakers",
        speakers,
        "--script_podcast_voice_map",
        voice_map,
        "--script_filler_mode",
        str(style.get("script_filler_mode", "off")),
        "--script_emotion_mode",
        str(style.get("script_emotion_mode", "light")),
        "--script_style_preset",
        str(style.get("script_style_preset", "documentary")),
        "--script_paragraph_pause",
        str(style.get("script_paragraph_pause", 0.45)),
        "--script_natural_preset",
        str(style.get("script_natural_preset", "manual")),
        "--speed",
        str(xtts_speed),
        "--temperature",
        str(xtts_temp),
        "--top_p",
        str(xtts_top_p),
        "--repetition_penalty",
        str(xtts_rep),
    ]
    # Map friendly engine_params keys to actual app.py CLI flags (only allow known flags)
    try:
        from lib.conf import cli_options as APP_CLI_OPTIONS
    except Exception:
        APP_CLI_OPTIONS = []

    friendly_map = {
        "prosody_rate": "--speed",
        "speaking_style": "--script_natural_preset",
        "speaking_style_preset": "--script_style_preset",
        "script_style": "--script_style_preset",
        "use_intensity": None,  # no direct mapping
        "intonation_model": None,  # no direct mapping
        "enable_text_splitting": "--enable_text_splitting",
    }

    for k, v in engine_params.items():
        if not k:
            continue
        mapped = friendly_map.get(k, None)
        if mapped is None:
            # skip unknown/non-mapped params
            continue
        if mapped not in APP_CLI_OPTIONS:
            # safety: only pass flags known to app.py
            continue
        # boolean true -> flag only; boolean false -> skip
        if isinstance(v, bool):
            if v:
                cmd.append(mapped)
            continue
        # list -> multiple occurrences
        if isinstance(v, (list, tuple)):
            for item in v:
                cmd.extend([mapped, str(item)])
            continue
        cmd.extend([mapped, str(v)])
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", env=env)


def _master_segment(seg: AudioSegment, target_dbfs: float | None, compress: bool) -> AudioSegment:
    out = seg
    if compress:
        out = compress_dynamic_range(out, threshold=-22.0, ratio=3.0, attack=5, release=100)
    if target_dbfs is not None and out.dBFS != float("-inf"):
        out = out.apply_gain(float(target_dbfs) - out.dBFS)
    return out


def _merge_audio(inputs: list[Path], output: Path, crossfade_ms: int, target_dbfs: float | None, compress: bool) -> None:
    if not inputs:
        raise ValueError("No input files to merge")
    merged: AudioSegment | None = None
    for p in inputs:
        seg = AudioSegment.from_file(str(p))
        seg = _master_segment(seg, target_dbfs=target_dbfs, compress=compress)
        if merged is None:
            merged = seg
            continue
        local_crossfade = max(0, min(int(crossfade_ms), len(merged), len(seg)))
        merged = merged.append(seg, crossfade=local_crossfade)

    if merged is None:
        raise ValueError("No decodable input files to merge")

    # Final loudness trim for consistent audiobook playback.
    if target_dbfs is not None and merged.dBFS != float("-inf"):
        merged = merged.apply_gain(float(target_dbfs) - merged.dBFS)

    output.parent.mkdir(parents=True, exist_ok=True)
    fmt = output.suffix.lower().lstrip(".") or "flac"
    merged.export(str(output), format=fmt)


def _safe_load_audio(path: str) -> Optional[AudioSegment]:
    try:
        return AudioSegment.from_file(path)
    except Exception:
        return None


def _apply_sfx_to_audio(audio_path: Path, sfx_cfg: dict[str, Any]) -> None:
    """Apply sfx_before, sfx_after, background_music to the audio file in-place.

    sfx_cfg fields:
      - sfx_before: {path: str, volume_db: float (optional), fade_in_ms, fade_out_ms}
      - sfx_after: {path: str, volume_db: float (optional), fade_in_ms, fade_out_ms}
      - background_music: {path: str, volume_db: float (optional), loop: bool, fade_in_ms, fade_out_ms}
    """
    if not sfx_cfg:
        return
    if not audio_path.exists():
        return
    try:
        main = AudioSegment.from_file(str(audio_path))
    except Exception:
        return


def _apply_time_stretch(audio_path: Path, factor: float) -> None:
    """Apply pitch-preserving time-stretch to `audio_path` in-place using librosa.
    `factor` > 1.0 speeds up (shorter), < 1.0 slows down (longer).
    """
    if factor is None or factor == 1.0:
        return
    if not audio_path.exists():
        return
    try:
        # Load preserving channels
        y, sr = librosa.load(str(audio_path), sr=None, mono=False)
        # librosa returns shape (n,) for mono, (n_channels, n_samples) for multi
        if y.ndim == 1:
            y_st = librosa.effects.time_stretch(y, rate=float(factor))
        else:
            # apply per channel
            chans = []
            for c in range(y.shape[0]):
                chans.append(librosa.effects.time_stretch(y[c], rate=float(factor)))
            # pad channels to same length if necessary
            maxlen = max(len(ch) for ch in chans)
            chans = [np.pad(ch, (0, maxlen - len(ch)), mode="constant") for ch in chans]
            y_st = np.vstack(chans)
        # write back using soundfile; transpose if multi-channel
        if isinstance(y_st, np.ndarray) and y_st.ndim == 2:
            # shape (n_channels, n_samples) -> transpose to (n_samples, n_channels)
            sf.write(str(audio_path), y_st.T, sr)
        else:
            sf.write(str(audio_path), y_st, sr)
    except Exception:
        return

    # Prepend sfx_before
    before = None
    if isinstance(sfx_cfg.get("sfx_before"), (str,)):
        before = _safe_load_audio(sfx_cfg.get("sfx_before"))
    elif isinstance(sfx_cfg.get("sfx_before"), dict):
        before = _safe_load_audio(sfx_cfg.get("sfx_before").get("path", ""))
    if before:
        vol = None
        if isinstance(sfx_cfg.get("sfx_before"), dict):
            vol = sfx_cfg.get("sfx_before").get("volume_db")
        if isinstance(vol, (int, float)):
            before = before.apply_gain(float(vol))
        fi = sfx_cfg.get("sfx_before", {}).get("fade_in_ms") or 0
        fo = sfx_cfg.get("sfx_before", {}).get("fade_out_ms") or 0
        if fi:
            before = before.fade_in(int(fi))
        if fo:
            before = before.fade_out(int(fo))
        # simple append with small crossfade
        main = before.append(main, crossfade=50)

    # Background music: overlay under main
    bg = None
    if isinstance(sfx_cfg.get("background_music"), (str,)):
        bg = _safe_load_audio(sfx_cfg.get("background_music"))
    elif isinstance(sfx_cfg.get("background_music"), dict):
        bg = _safe_load_audio(sfx_cfg.get("background_music").get("path", ""))
    if bg:
        vol = None
        if isinstance(sfx_cfg.get("background_music"), dict):
            vol = sfx_cfg.get("background_music").get("volume_db")
        if isinstance(vol, (int, float)):
            bg = bg.apply_gain(float(vol))
        # loop or cut to length
        loop = bool(sfx_cfg.get("background_music", {}).get("loop", True))
        if loop and len(bg) < len(main):
            parts = []
            while sum(len(p) for p in parts) < len(main):
                parts.append(bg)
            bg = sum(parts)
        bg = bg[: len(main)]
        # fade
        fi = sfx_cfg.get("background_music", {}).get("fade_in_ms") or 0
        fo = sfx_cfg.get("background_music", {}).get("fade_out_ms") or 0
        if fi:
            bg = bg.fade_in(int(fi))
        if fo:
            bg = bg.fade_out(int(fo))
        try:
            blend = str(sfx_cfg.get("blend_mode", "overlay") or "overlay").lower()
            duck_db = float(sfx_cfg.get("duck_amount_db", 8.0) or 8.0)
            if blend == "overlay":
                # place main over music (music underneath)
                main = bg.overlay(main)
            elif blend == "duck":
                # reduce music while main plays
                reduced_bg = bg.apply_gain(-abs(duck_db))
                main = reduced_bg.overlay(main)
            else:  # replace
                main = bg
        except Exception:
            pass

    # Append sfx_after
    after = None
    if isinstance(sfx_cfg.get("sfx_after"), (str,)):
        after = _safe_load_audio(sfx_cfg.get("sfx_after"))
    elif isinstance(sfx_cfg.get("sfx_after"), dict):
        after = _safe_load_audio(sfx_cfg.get("sfx_after").get("path", ""))
    if after:
        vol = None
        if isinstance(sfx_cfg.get("sfx_after"), dict):
            vol = sfx_cfg.get("sfx_after").get("volume_db")
        if isinstance(vol, (int, float)):
            after = after.apply_gain(float(vol))
        fi = sfx_cfg.get("sfx_after", {}).get("fade_in_ms") or 0
        fo = sfx_cfg.get("sfx_after", {}).get("fade_out_ms") or 0
        if fi:
            after = after.fade_in(int(fi))
        if fo:
            after = after.fade_out(int(fo))
        main = main.append(after, crossfade=50)

    # overwrite original
    fmt = audio_path.suffix.lower().lstrip(".") or "flac"
    try:
        main.export(str(audio_path), format=fmt)
    except Exception:
        try:
            main.export(str(audio_path) + ".flac", format="flac")
        except Exception:
            return


def _time_stretch_with_formant_preserve(audio_path: Path, factor: float) -> None:
    """Conservative, prototype formant-preserving time-stretch.

    Uses a phase-vocoder approach on a mono mix and writes back to the file.
    This is an approximation; for production use a proper vocoder (WORLD / neural vocoder).
    """
    if factor is None or factor == 1.0:
        return
    if not audio_path.exists():
        return
    try:
        import soundfile as sf

        data, sr = sf.read(str(audio_path))
        if data is None:
            return

        # ensure shape: (n_samples, ) or (n_samples, n_channels)
        if data.ndim == 1:
            mono = True
            channels = [data]
        else:
            mono = False
            # convert to list of 1d arrays per channel
            channels = [data[:, i] for i in range(data.shape[1])]

        n_fft = 2048
        hop_length = 512
        processed = []
        for ch in channels:
            if ch is None or len(ch) == 0:
                processed.append(ch)
                continue
            S = librosa.stft(ch.astype(float), n_fft=n_fft, hop_length=hop_length)
            try:
                S_stretched = librosa.phase_vocoder(S, rate=float(factor), hop_length=hop_length)
                # estimate target length
                target_len = None
                if factor != 0:
                    target_len = int(len(ch) / float(factor))
                y_hat = librosa.istft(S_stretched, hop_length=hop_length, length=target_len)
            except Exception:
                # fallback: naive resample-based time stretch
                import numpy as _np
                target_len = int(len(ch) / float(factor)) if factor != 0 else len(ch)
                y_hat = _np.interp(
                    _np.linspace(0, len(ch), target_len, endpoint=False),
                    _np.arange(len(ch)),
                    ch,
                )
            processed.append(y_hat)

        # stack processed channels, ensure same length
        import numpy as _np
        maxlen = max(len(p) for p in processed if p is not None)
        chans = []
        for p in processed:
            if p is None:
                p = _np.zeros(maxlen)
            if len(p) < maxlen:
                p = _np.pad(p, (0, maxlen - len(p)), mode='constant')
            chans.append(p)
        if len(chans) == 1:
            out = chans[0]
        else:
            out = _np.vstack(chans).T

        sf.write(str(audio_path), out, sr)
    except Exception:
        return


def _build_quality_summary(
    rows: list[dict[str, Any]],
    selected_chunks: list[Path],
    style: dict[str, Any],
    speakers: str,
    language: str,
    speakers_meta: dict[str, Any],
) -> dict[str, Any]:
    total = len(rows)
    ok_rows = [r for r in rows if r.get("ok")]
    ok_count = len(ok_rows)
    success_rate = (ok_count / total) if total else 0.0

    durations: list[float] = []
    words: list[int] = []
    wpm_values: list[float] = []
    pause_values: list[float] = []
    voice_sequence: list[str] = []
    role_sequence: list[str] = []
    name_role_sequence: list[str] = []
    known_roles = [r.strip().lower() for r in str(speakers or "").split(",") if r.strip()]
    speaker_name_to_role: dict[str, str] = {}
    if isinstance(speakers_meta, dict):
        for role, cfg in speakers_meta.items():
            if not isinstance(cfg, dict):
                continue
            name = str(cfg.get("name", "")).strip().lower()
            role_key = str(role or "").strip().lower()
            if name and role_key:
                speaker_name_to_role[name] = role_key

    row_by_chunk = {str(r.get("chunk_file", "")): r for r in rows}
    for chunk in selected_chunks:
        key = str(chunk)
        row = row_by_chunk.get(key)
        if not row:
            continue
        txt = _read_text(chunk)
        wc = _words_count(txt)
        words.append(wc)
        pause_values.extend(_extract_pause_seconds(txt))
        voice_sequence.extend(_extract_voice_sequence(txt))
        role_sequence.extend(_extract_chunk_speakers_from_text(txt, known_roles))
        name_role_sequence.extend(_extract_speaker_name_sequence(txt, speaker_name_to_role))

        out_audio = row.get("output_audio")
        if not (row.get("ok") and out_audio):
            continue
        p = Path(str(out_audio))
        if not p.exists():
            continue
        try:
            duration = len(AudioSegment.from_file(str(p))) / 1000.0
            durations.append(duration)
            if duration > 0 and wc > 0:
                wpm_values.append((wc / duration) * 60.0)
        except Exception:
            continue

    voice_switches = 0
    sequence_for_switches = name_role_sequence or role_sequence or voice_sequence
    if sequence_for_switches:
        prev = sequence_for_switches[0]
        for v in sequence_for_switches[1:]:
            if v != prev:
                voice_switches += 1
            prev = v

    fmt_mode = str(style.get("script_format_mode", "narrative")).strip().lower()
    lang = str(language or "").strip().lower()
    if lang == "deu":
        target_wpm_min = 90.0 if fmt_mode == "narrative" else 95.0
        target_wpm_max = 170.0 if fmt_mode == "narrative" else 190.0
    elif lang == "eng":
        target_wpm_min = 120.0 if fmt_mode == "narrative" else 130.0
        target_wpm_max = 195.0 if fmt_mode == "narrative" else 210.0
    else:
        target_wpm_min = 105.0 if fmt_mode == "narrative" else 115.0
        target_wpm_max = 185.0 if fmt_mode == "narrative" else 205.0
    max_failed_chunks = int(style.get("qa_max_failed_chunks", 0))
    default_min_switches = 1 if (fmt_mode == "podcast" and len(speaker_name_to_role) >= 2) else 0
    min_voice_switches = int(style.get("qa_min_voice_switches", default_min_switches))
    min_pause_mean = float(style.get("qa_min_pause_mean", 0.30))
    max_pause_mean = float(style.get("qa_max_pause_mean", 1.40))

    warnings: list[str] = []
    failed_chunks = total - ok_count
    if failed_chunks > max_failed_chunks:
        warnings.append(f"failed_chunks>{max_failed_chunks} ({failed_chunks})")

    wpm_mean = statistics.mean(wpm_values) if wpm_values else 0.0
    if wpm_values and (wpm_mean < target_wpm_min or wpm_mean > target_wpm_max):
        warnings.append(f"wpm_mean_out_of_range ({wpm_mean:.1f} not in [{target_wpm_min:.1f},{target_wpm_max:.1f}])")

    pause_mean = statistics.mean(pause_values) if pause_values else 0.0
    if pause_values and (pause_mean < min_pause_mean or pause_mean > max_pause_mean):
        warnings.append(f"pause_mean_out_of_range ({pause_mean:.2f} not in [{min_pause_mean:.2f},{max_pause_mean:.2f}])")

    if fmt_mode == "podcast" and voice_switches < min_voice_switches:
        warnings.append(f"voice_switches_too_low ({voice_switches} < {min_voice_switches})")

    score = 100.0
    score -= min(40.0, failed_chunks * 20.0)
    if wpm_values:
        if wpm_mean < target_wpm_min:
            score -= min(20.0, (target_wpm_min - wpm_mean) * 0.3)
        elif wpm_mean > target_wpm_max:
            score -= min(20.0, (wpm_mean - target_wpm_max) * 0.3)
    if pause_values:
        if pause_mean < min_pause_mean:
            score -= min(15.0, (min_pause_mean - pause_mean) * 30.0)
        elif pause_mean > max_pause_mean:
            score -= min(15.0, (pause_mean - max_pause_mean) * 20.0)
    if fmt_mode == "podcast" and voice_switches < min_voice_switches:
        score -= min(15.0, (min_voice_switches - voice_switches) * 5.0)
    score = max(0.0, round(score, 2))

    return {
        "gate_passed": len(warnings) == 0,
        "warnings": warnings,
        "score": score,
        "metrics": {
            "total_chunks": total,
            "ok_chunks": ok_count,
            "failed_chunks": failed_chunks,
            "success_rate": round(success_rate, 4),
            "total_duration_sec": round(sum(durations), 2),
            "avg_chunk_duration_sec": round(statistics.mean(durations), 2) if durations else 0.0,
            "median_chunk_duration_sec": round(statistics.median(durations), 2) if durations else 0.0,
            "total_words": int(sum(words)),
            "avg_chunk_words": round(statistics.mean(words), 1) if words else 0.0,
            "wpm_mean": round(wpm_mean, 2) if wpm_values else 0.0,
            "wpm_min": round(min(wpm_values), 2) if wpm_values else 0.0,
            "wpm_max": round(max(wpm_values), 2) if wpm_values else 0.0,
            "pause_count": len(pause_values),
            "pause_mean_sec": round(pause_mean, 3) if pause_values else 0.0,
            "voice_switches": int(voice_switches),
            "voice_tags": int(len(voice_sequence)),
            "role_mentions": int(len(role_sequence)),
            "speaker_name_mentions": int(len(name_role_sequence)),
        },
        "gates": {
            "max_failed_chunks": max_failed_chunks,
            "target_wpm_min": target_wpm_min,
            "target_wpm_max": target_wpm_max,
            "min_pause_mean": min_pause_mean,
            "max_pause_mean": max_pause_mean,
            "min_voice_switches": min_voice_switches,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Render chunk files from YAML compiler meta")
    ap.add_argument("--meta", required=True, help="Path to *_meta.json")
    ap.add_argument("--python", default="py", help="Python executable command")
    ap.add_argument("--python-arg", default="-3.11", help="Optional single python arg")
    ap.add_argument("--app", default="app.py", help="Path to app.py")
    ap.add_argument("--start", type=int, default=1, help="1-based chunk start index")
    ap.add_argument("--max-chunks", type=int, default=0, help="0 = all remaining")
    ap.add_argument("--manifest", default="", help="Output manifest path")
    ap.add_argument("--merge-output", default="", help="Optional merged output audio path")
    ap.add_argument("--crossfade-ms", type=int, default=-1, help="Crossfade during merge (ms). -1 = auto from style")
    ap.add_argument("--preprocess-ssml", action="store_true", help="Preprocess chunk text with tools/text_to_ssml.py into SSML before rendering")
    # SFX / Music mixing CLI defaults (per-chunk overrides in meta.chunk_sfx supported)
    ap.add_argument("--sfx-volume-db", type=float, default=0.0, help="Default SFX gain in dB (applied to sfx_before/after when specified in YAML)")
    ap.add_argument("--music-volume-db", type=float, default=-8.0, help="Default background music gain in dB (relative attenuation)")
    ap.add_argument("--sfx-crossfade-ms", type=int, default=50, help="Default crossfade ms when appending sfx_before/after")
    ap.add_argument("--background-mix-mode", choices=["overlay", "duck", "replace"], default="overlay", help="Mixing mode for background music: overlay|duck|replace")
    ap.add_argument("--duck-amount-db", type=float, default=8.0, help="If background-mix-mode=duck, reduce main audio by this many dB during music")
    ap.add_argument("--target-dbfs", type=float, default=999.0, help="Target loudness in dBFS for mastering. 999 disables.")
    ap.add_argument("--no-compress", action="store_true", help="Disable light dynamic-range compression in mastering")
    args = ap.parse_args()

    meta_path = Path(args.meta)
    meta = _load_meta(meta_path)

    chunk_files = [Path(p) for p in meta.get("chunk_files", [])]
    if not chunk_files:
        raise SystemExit("No chunk_files in meta")

    language = str(meta.get("language", "deu"))
    speakers = str(meta.get("recommended_cli", {}).get("script_podcast_speakers", "host"))
    voice_map = str(meta.get("voice_map_file", "")).strip()
    if not voice_map:
        raise SystemExit("No voice_map_file in meta")
    style = meta.get("style", {}) if isinstance(meta.get("style", {}), dict) else {}
    chunk_overrides_raw = meta.get("chunk_overrides", [])
    chunk_overrides: list[dict[str, Any]] = chunk_overrides_raw if isinstance(chunk_overrides_raw, list) else []
    chunk_sfx_raw = meta.get("chunk_sfx", [])
    chunk_sfx: list[dict[str, Any]] = chunk_sfx_raw if isinstance(chunk_sfx_raw, list) else []

    default_crossfade = int(style.get("crossfade_ms", 80 if str(style.get("script_format_mode", "podcast")) == "podcast" else 120))
    crossfade_ms = default_crossfade if int(args.crossfade_ms) < 0 else max(0, int(args.crossfade_ms))
    default_target = -16.0 if str(style.get("script_format_mode", "podcast")) == "podcast" else -18.0
    target_dbfs = None if float(args.target_dbfs) == 999.0 else float(args.target_dbfs)
    if target_dbfs is None:
        target_dbfs = float(style.get("target_dbfs", default_target))

    start_idx = max(1, int(args.start))
    selected = chunk_files[start_idx - 1 :]
    if int(args.max_chunks) > 0:
        selected = selected[: int(args.max_chunks)]

    py_cmd: list[str] = [args.python]
    if args.python_arg:
        py_cmd.append(args.python_arg)

    rows: list[dict[str, Any]] = []
    out_files: list[Path] = []

    for i, chunk in enumerate(selected, start=start_idx):
        txt = _read_text(chunk)
        if not txt:
            rows.append({"chunk_index": i, "chunk_file": str(chunk), "ok": False, "error": "empty chunk"})
            continue

        # Create a temp file for either plain text or preprocessed SSML
        suffix = ".ssml" if bool(args.preprocess_ssml) else ".txt"
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as tmp:
            tmp_path = Path(tmp.name)
            if not bool(args.preprocess_ssml):
                tmp.write(txt)
            else:
                # We'll generate SSML via tools/text_to_ssml.py into tmp_path
                # Remove the empty temp file so the preprocessor can write a fresh one
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass

        try:
            # If requested, run the SSML preprocessor before calling the renderer
            if bool(args.preprocess_ssml):
                pre_cmd = [*py_cmd, "tools/text_to_ssml.py", str(chunk), "--out", str(tmp_path), "--lexicon", "run/lexicon.json", "--guest-voice"]
                env = os.environ.copy()
                env["PYTHONUTF8"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"
                preproc = subprocess.run(pre_cmd, capture_output=True, text=True, encoding="utf-8", env=env)
                if preproc.returncode != 0:
                    rows.append({
                        "chunk_index": i,
                        "chunk_file": str(chunk),
                        "ok": False,
                        "error": "preprocess_failed",
                        "stderr_tail": "\n".join((preproc.stderr or "").splitlines()[-20:]),
                    })
                    continue

                # Detect if preprocessor requested formant-preserving operations
                need_formant_preserve = False
                try:
                    ssml_text = tmp_path.read_text(encoding='utf-8')
                    if '<!--E2A:formant_preserve=1-->' in ssml_text:
                        need_formant_preserve = True
                except Exception:
                    need_formant_preserve = False

            proc = _render_chunk(
                python_cmd=py_cmd,
                app_path=args.app,
                text_file=tmp_path,
                language=language,
                speakers=speakers,
                voice_map=voice_map,
                style=style,
                chunk_override=chunk_overrides[i - 1] if (i - 1) < len(chunk_overrides) else None,
            )
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

        out = _parse_output_audio(proc.stdout)
        ok = proc.returncode == 0 and out is not None
        row = {
            "chunk_index": i,
            "chunk_file": str(chunk),
            "returncode": proc.returncode,
            "ok": ok,
            "output_audio": out,
        }
        if not ok:
            row["stderr_tail"] = "\n".join((proc.stderr or "").splitlines()[-20:])
            row["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-20:])
        rows.append(row)

        if ok and out:
            # apply post-render modifiers: optional time-stretch (pitch-preserving)
            try:
                chunk_ts = None
                # check per-chunk override first, then style
                chunk_cfg = chunk_overrides[i - 1] if (i - 1) < len(chunk_overrides) else None
                if isinstance(chunk_cfg, dict) and chunk_cfg.get("post_time_stretch"):
                    chunk_ts = float(chunk_cfg.get("post_time_stretch"))
                elif isinstance(style.get("post_time_stretch"), (int, float, str)):
                    chunk_ts = float(style.get("post_time_stretch"))
                if chunk_ts and chunk_ts != 1.0:
                    # prefer formant-preserving variant when marker present
                    if need_formant_preserve:
                        _time_stretch_with_formant_preserve(Path(out), chunk_ts)
                    else:
                        _apply_time_stretch(Path(out), chunk_ts)
            except Exception:
                pass

            # apply sfx if present for this chunk (merge meta config with CLI/style defaults)
            try:
                base_cfg = chunk_sfx[i - 1] if (i - 1) < len(chunk_sfx) else {}
                if not isinstance(base_cfg, dict):
                    base_cfg = {}
                sfx_cfg = dict(base_cfg)
                # ensure structured dict values for sfx and background music
                if isinstance(sfx_cfg.get("sfx_before"), str):
                    sfx_cfg["sfx_before"] = {"path": sfx_cfg.get("sfx_before")}
                if isinstance(sfx_cfg.get("sfx_after"), str):
                    sfx_cfg["sfx_after"] = {"path": sfx_cfg.get("sfx_after")}
                if isinstance(sfx_cfg.get("background_music"), str):
                    sfx_cfg["background_music"] = {"path": sfx_cfg.get("background_music")}

                # apply CLI defaults when not provided
                if "sfx_before" in sfx_cfg and isinstance(sfx_cfg.get("sfx_before"), dict):
                    sfx_cfg["sfx_before"].setdefault("volume_db", args.sfx_volume_db)
                    sfx_cfg["sfx_before"].setdefault("fade_in_ms", 0)
                    sfx_cfg["sfx_before"].setdefault("fade_out_ms", 0)
                if "sfx_after" in sfx_cfg and isinstance(sfx_cfg.get("sfx_after"), dict):
                    sfx_cfg["sfx_after"].setdefault("volume_db", args.sfx_volume_db)
                    sfx_cfg["sfx_after"].setdefault("fade_in_ms", 0)
                    sfx_cfg["sfx_after"].setdefault("fade_out_ms", 0)
                if "background_music" in sfx_cfg and isinstance(sfx_cfg.get("background_music"), dict):
                    sfx_cfg["background_music"].setdefault("volume_db", args.music_volume_db)
                    sfx_cfg["background_music"].setdefault("loop", True)
                    sfx_cfg["background_music"].setdefault("fade_in_ms", 0)
                    sfx_cfg["background_music"].setdefault("fade_out_ms", 0)

                # add mixing policy
                sfx_cfg.setdefault("blend_mode", args.background_mix_mode)
                sfx_cfg.setdefault("duck_amount_db", args.duck_amount_db)
                sfx_cfg.setdefault("crossfade_ms", args.sfx_crossfade_ms)

                if sfx_cfg:
                    _apply_sfx_to_audio(Path(out), sfx_cfg)
            except Exception:
                pass
            out_files.append(Path(out))
            print(f"[ok] chunk {i}: {out}")
        else:
            print(f"[fail] chunk {i}")

    manifest_path = Path(args.manifest) if args.manifest else meta_path.with_name(meta_path.stem + "_render_manifest.json")
    manifest = {
        "meta": str(meta_path),
        "start": start_idx,
        "count": len(selected),
        "rows": rows,
        "quality": _build_quality_summary(
            rows,
            selected,
            style,
            speakers,
            language,
            meta.get("speakers", {}) if isinstance(meta.get("speakers", {}), dict) else {},
        ),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest_path}")

    quality = manifest["quality"]
    print(f"Quality score: {quality.get('score')} / 100")
    print(f"Quality gate: {'PASS' if quality.get('gate_passed') else 'FAIL'}")
    for w in quality.get("warnings", []):
        print(f"[quality-warning] {w}")

    if args.merge_output:
        merge_path = Path(args.merge_output)
        good_files = [p for p in out_files if p.exists()]
        _merge_audio(
            good_files,
            merge_path,
            crossfade_ms=crossfade_ms,
            target_dbfs=target_dbfs,
            compress=not bool(args.no_compress),
        )
        print(f"Merged: {merge_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
