#!/usr/bin/env python3
import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np

from .norm_audio import make_silence_detector, trim_silence

_DIR = Path(__file__).parent

# Removed from the speaking rate calculation
_PUNCTUATION = re.compile(".。,，?¿？؟!！;；:：-—")


class ExcludeReason(str, Enum):
    MISSING = "file_missing"
    EMPTY = "file_empty"
    LOW = "rate_low"
    HIGH = "rate_high"


@dataclass
class Utterance:
    id: str
    text: str
    duration_sec: float
    speaker: str
    exclude_reason: Optional[ExcludeReason] = None
    rate: float = 0.0

    def __post_init__(self):
        if self.duration_sec > 0:
            # Don't include punctuation is speaking rate calculation since we
            # remove silence.
            text_nopunct = _PUNCTUATION.sub("", self.text)
            self.rate = len(text_nopunct) / self.duration_sec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-json", help="Path to write information about excluded utterances"
    )
    parser.add_argument(
        "--dataset-dir", default=Path.cwd(), help="Path to dataset directory"
    )
    parser.add_argument("--scale-lower", type=float, default=2.0)
    parser.add_argument("--scale-upper", type=float, default=2.0)
    args = parser.parse_args()

    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe not found (is ffmpeg installed?)")

    dataset_dir = Path(args.dataset_dir)
    wav_dir = dataset_dir / "wav"
    if not wav_dir.is_dir():
        wav_dir = dataset_dir / "wavs"

    reader = csv.reader(sys.stdin, delimiter="|")

    text_and_audio = []
    for row in reader:
        filename, text = row[0], row[-1]
        speaker = row[1] if len(row) > 2 else "default"

        # Try file name relative to metadata
        wav_path = dataset_dir / filename

        if not wav_path.exists():
            # Try with .wav
            wav_path = dataset_dir / f"{filename}.wav"

        if not wav_path.exists():
            # Try wav/ or wavs/
            wav_path = wav_dir / filename

        if not wav_path.exists():
            # Try with .wav
            wav_path = wav_dir / f"{filename}.wav"

        text_and_audio.append((filename, text, wav_path, speaker))

    writer = csv.writer(sys.stdout, delimiter="|")

    # speaker -> [rate]
    utts_by_speaker = defaultdict(list)
    process_utterance = ProcessUtterance()
    with ThreadPoolExecutor() as executor:
        for utt in executor.map(lambda args: process_utterance(*args), text_and_audio):
            utts_by_speaker[utt.speaker].append(utt)

    is_multispeaker = len(utts_by_speaker) > 1
    writer = csv.writer(sys.stdout, delimiter="|")

    speaker_details = {}
    for speaker, utts in utts_by_speaker.items():
        rates = [utt.rate for utt in utts]
        if rates:
            # Exclude rates well outside the 25%/75% quantiles
            rate_qs = statistics.quantiles(rates, n=4)
            q1 = rate_qs[0]  # 25%
            q3 = rate_qs[-1]  # 75%
            iqr = q3 - q1
            lower = q1 - (args.scale_lower * iqr)
            upper = q3 + (args.scale_upper * iqr)
            speaker_details[speaker] = {
                "min": min(rates),
                "max": max(rates),
                "quanties": rate_qs,
                "lower": lower,
                "upper": upper,
            }

            for utt in utts:
                if utt.rate < lower:
                    utt.exclude_reason = ExcludeReason.LOW
                elif utt.rate > upper:
                    utt.exclude_reason = ExcludeReason.HIGH
                else:
                    if is_multispeaker:
                        writer.writerow((utt.id, utt.speaker, utt.text))
                    else:
                        writer.writerow((utt.id, utt.text))

    if args.write_json:
        speaker_excluded = {
            speaker: [
                asdict(utt)
                for utt in utts_by_speaker[speaker]
                if utt.exclude_reason is not None
            ]
            for speaker in speaker_details
        }

        with open(args.write_json, "w", encoding="utf-8") as json_file:
            json.dump(
                {
                    speaker: {
                        "details": speaker_details[speaker],
                        "num_utterances": len(utts_by_speaker[speaker]),
                        "num_excluded": len(speaker_excluded[speaker]),
                        "excluded": speaker_excluded[speaker],
                    }
                    for speaker in speaker_details
                },
                json_file,
                indent=4,
                ensure_ascii=False,
            )


class ProcessUtterance:
    def __init__(self):
        self.thread_data = threading.local()

    def __call__(
        self, utt_id: str, text: str, wav_path: Path, speaker: str
    ) -> Utterance:
        if not wav_path.exists():
            return Utterance(
                utt_id,
                text,
                0.0,
                speaker,
                exclude_reason=ExcludeReason.MISSING,
            )

        if wav_path.stat().st_size == 0:
            return Utterance(
                utt_id,
                text,
                0.0,
                speaker,
                exclude_reason=ExcludeReason.EMPTY,
            )

        return Utterance(utt_id, text, self.get_duration(wav_path), speaker)

    def get_duration(self, audio_path: Path) -> float:
        """Uses ffmpeg to get audio duration."""
        if not hasattr(self.thread_data, "detector"):
            self.thread_data.detector = make_silence_detector()

        vad_sample_rate = 16000
        audio_16khz_bytes = subprocess.check_output(
            [
                "ffmpeg",
                "-i",
                str(audio_path),
                "-f",
                "s16le",
                "-acodec",
                "pcm_s16le",
                "-ac",
                "1",
                "-ar",
                str(vad_sample_rate),
                "pipe:",
            ],
            stderr=subprocess.DEVNULL,
        )

        # Normalize
        audio_16khz = np.frombuffer(audio_16khz_bytes, dtype=np.int16).astype(
            np.float32
        )
        audio_16khz /= np.abs(np.max(audio_16khz))

        # Get speaking duration
        offset_sec, duration_sec = trim_silence(
            audio_16khz,
            self.thread_data.detector,
            threshold=0.8,
            samples_per_chunk=480,
            sample_rate=vad_sample_rate,
            keep_chunks_before=2,
            keep_chunks_after=2,
        )

        if duration_sec is None:
            # Speech goes to end of audio
            if len(audio_16khz) > 0:
                duration_sec = (len(audio_16khz) / 16000.0) - offset_sec
            else:
                duration_sec = 0.0

        return duration_sec


if __name__ == "__main__":
    main()
