#!/usr/bin/env python3
"""Generate a concise quality report from a render manifest.

Reads the manifest produced by tools/render_yaml_chunks.py and prints
summary metrics, gate result, warnings, and optional JSON output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Report render quality from manifest")
    ap.add_argument("--manifest", required=True, help="Path to *_render_manifest*.json")
    ap.add_argument("--output", default="", help="Optional path to write extracted quality JSON")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = _load_json(manifest_path)
    quality = manifest.get("quality")
    if not isinstance(quality, dict):
        raise SystemExit("Manifest has no quality block. Re-run render_yaml_chunks.py with stage-3 code.")

    metrics = quality.get("metrics", {}) if isinstance(quality.get("metrics"), dict) else {}
    gates = quality.get("gates", {}) if isinstance(quality.get("gates"), dict) else {}
    warnings = quality.get("warnings", []) if isinstance(quality.get("warnings"), list) else []

    print(f"Manifest: {manifest_path}")
    print(f"Gate: {'PASS' if quality.get('gate_passed') else 'FAIL'}")
    print(f"Score: {quality.get('score', 0)} / 100")
    print(
        "Chunks: "
        f"{metrics.get('ok_chunks', 0)}/{metrics.get('total_chunks', 0)} ok, "
        f"failed={metrics.get('failed_chunks', 0)}, "
        f"success_rate={metrics.get('success_rate', 0)}"
    )
    print(
        "Timing: "
        f"total={metrics.get('total_duration_sec', 0)}s, "
        f"avg_chunk={metrics.get('avg_chunk_duration_sec', 0)}s"
    )
    print(
        "Speech: "
        f"wpm_mean={metrics.get('wpm_mean', 0)} "
        f"(target {gates.get('target_wpm_min', 0)}-{gates.get('target_wpm_max', 0)}), "
        f"voice_switches={metrics.get('voice_switches', 0)}"
    )
    print(
        "Pauses: "
        f"count={metrics.get('pause_count', 0)}, "
        f"mean={metrics.get('pause_mean_sec', 0)}s "
        f"(target {gates.get('min_pause_mean', 0)}-{gates.get('max_pause_mean', 0)})"
    )

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Quality JSON written: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
