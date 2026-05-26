from __future__ import annotations

# Patch pkgutil.ImpImporter and importlib.machinery.FileFinder.find_module for Python 3.12 compatibility with older pkg_resources / setuptools
import pkgutil
import importlib.machinery

if not hasattr(pkgutil, "ImpImporter"):
    class DummyImpImporter:
        pass
    pkgutil.ImpImporter = DummyImpImporter

if not hasattr(importlib.machinery.FileFinder, "find_module"):
    def find_module_shim(self, fullname, path=None):
        spec = self.find_spec(fullname, path)
        return spec.loader if spec is not None else None
    importlib.machinery.FileFinder.find_module = find_module_shim

# Patch PyTorch 2.6+ to default to weights_only=False in torch.load for compatibility with older checkpoints
try:
    import torch
    if hasattr(torch, "load"):
        original_load = torch.load
        def patched_load(*args, **kwargs):
            if "weights_only" not in kwargs:
                kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
except ImportError:
    pass

import csv
import json
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
import warnings
from dataclasses import asdict
import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
_MAIN_MODELS_DIR = _PROJECT_ROOT.parent.parent / "models"
if _MAIN_MODELS_DIR.exists() and _MAIN_MODELS_DIR.is_dir():
    _MODELS_DIR = _MAIN_MODELS_DIR
else:
    _MODELS_DIR = _PROJECT_ROOT / "models"
    _MODELS_DIR.mkdir(exist_ok=True)

os.environ["HF_HOME"] = str(_MODELS_DIR)
os.environ["TTS_HOME"] = str(_MODELS_DIR)
os.environ["TORCH_HOME"] = str(_MODELS_DIR)

_CURRENT_PROCESS: subprocess.Popen | None = None

def register_active_process(proc: subprocess.Popen | None):
    global _CURRENT_PROCESS
    _CURRENT_PROCESS = proc

def pause_training() -> str:
    global _CURRENT_PROCESS
    if not _CURRENT_PROCESS or _CURRENT_PROCESS.poll() is not None:
        return "No training process is currently active."
    try:
        import signal
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(_CURRENT_PROCESS.pid), signal.SIGSTOP)
        else:
            _CURRENT_PROCESS.send_signal(signal.SIGSTOP)
        return "Training process paused successfully."
    except Exception as e:
        return f"Error pausing training: {e}"

def resume_training() -> str:
    global _CURRENT_PROCESS
    if not _CURRENT_PROCESS or _CURRENT_PROCESS.poll() is not None:
        return "No training process is currently active."
    try:
        import signal
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(_CURRENT_PROCESS.pid), signal.SIGCONT)
        else:
            _CURRENT_PROCESS.send_signal(signal.SIGCONT)
        return "Training process resumed successfully."
    except Exception as e:
        return f"Error resuming training: {e}"

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

from typing import Any, Callable, Sequence

import soundfile as sf
import torch
import torchaudio
from faster_whisper import WhisperModel
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.manage import ModelManager

from utils.model_registry import MODEL_SPECS, get_model_spec, list_model_choices
from utils.tokenizer import multilingual_cleaners

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_EVAL_PERCENTAGE = 0.15
DEFAULT_MIN_SEGMENT_SECONDS = 0.5
DEFAULT_MAX_SEGMENT_SECONDS = 12.0
DEFAULT_SEGMENT_BUFFER_SECONDS = 0.2
DEFAULT_SHUFFLE_SEED = 0
ERROR_LOG_TAIL_CHARS = 4000
PUNCTUATION_ENDINGS = (".", "!", "?", "。", "！", "？")
MODEL_CACHE: dict[str, Any] = {}

ProgressCallback = Callable[[str], None] | None


def _notify(progress: ProgressCallback, message: str) -> None:
    print(message)
    if progress:
        progress(message)


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _safe_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return safe or "sample"


def _coerce_path(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("path", "name"):
            candidate = value.get(key)
            if candidate:
                return str(candidate)
        return None
    candidate = getattr(value, "name", None)
    if candidate:
        return str(candidate)
    candidate = getattr(value, "path", None)
    if candidate:
        return str(candidate)
    return None


def _resolve_user_path(
    value: str | Path,
    *,
    must_exist: bool = False,
    expect_directory: bool | None = None,
) -> Path:
    raw_value = str(value).strip()
    if "\x00" in raw_value:
        raise ValueError("Path values cannot contain null bytes.")
    if not re.fullmatch(r"[\w\s./:\\-]+", raw_value):
        raise ValueError(f"Unsupported characters in path: {raw_value!r}")
    raw_path = Path(raw_value)
    if ".." in raw_path.parts:
        raise ValueError("Parent directory traversal is not allowed in path inputs.")
    candidate = raw_path.expanduser()
    try:
        resolved = candidate.resolve(strict=must_exist)
    except FileNotFoundError:
        raise
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path not found: {resolved}")
    if expect_directory is True and resolved.exists() and not resolved.is_dir():
        raise NotADirectoryError(f"Expected a directory path but received: {resolved}")
    if expect_directory is False and resolved.exists() and not resolved.is_file():
        raise FileNotFoundError(f"Expected a file path but received: {resolved}")
    return resolved


def resolve_audio_files(audio_files: Sequence[Any] | None = None, audio_dir: str | None = None) -> list[str]:
    resolved: list[str] = []
    if audio_dir:
        directory = _resolve_user_path(audio_dir, must_exist=True, expect_directory=True)
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
                resolved.append(str(path))
    for item in audio_files or []:
        candidate = _coerce_path(item)
        if not candidate:
            continue
        path = _resolve_user_path(candidate, must_exist=True, expect_directory=False)
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            resolved.append(str(path))
    deduplicated = []
    seen: set[str] = set()
    for item in resolved:
        if item not in seen:
            seen.add(item)
            deduplicated.append(item)
    return deduplicated


def _load_waveform(audio_path: Path, sample_rate: int = DEFAULT_SAMPLE_RATE) -> tuple[torch.Tensor, int]:
    try:
        waveform, source_rate = torchaudio.load(str(audio_path))
    except (ImportError, RuntimeError):
        data, source_rate = sf.read(str(audio_path), always_2d=False)
        waveform = torch.tensor(data, dtype=torch.float32)
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.transpose(0, 1)
    if waveform.size(0) > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if source_rate != sample_rate:
        waveform = torchaudio.functional.resample(waveform, source_rate, sample_rate)
        source_rate = sample_rate
    return waveform, source_rate


def _save_waveform(destination: Path, waveform: torch.Tensor, sample_rate: int) -> None:
    tensor = waveform.detach().cpu()
    try:
        torchaudio.save(str(destination), tensor, sample_rate)
        return
    except (ImportError, RuntimeError):
        pass
    array = tensor.squeeze(0).numpy()
    sf.write(str(destination), array, sample_rate)


def _load_transcript_map(transcript_file: str | None) -> dict[str, str]:
    if not transcript_file:
        return {}
    path = _resolve_user_path(transcript_file, must_exist=True, expect_directory=False)
    suffix = path.suffix.lower()
    mapping: dict[str, str] = {}
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            iterable = payload.items()
        elif isinstance(payload, list):
            iterable = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                audio_key = item.get("audio") or item.get("audio_file") or item.get("path") or item.get("file")
                text_value = item.get("text") or item.get("transcript") or item.get("sentence")
                if audio_key and text_value:
                    iterable.append((audio_key, text_value))
        else:
            raise ValueError("Unsupported JSON transcript format.")
        for key, value in iterable:
            if value:
                mapping[str(key)] = str(value).strip()
    else:
        delimiter = "|"
        if suffix == ".tsv":
            delimiter = "\t"
        elif suffix == ".csv":
            delimiter = ","
        with path.open("r", encoding="utf-8", newline="") as handle:
            sample = handle.read(2048)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t|")
                delimiter = dialect.delimiter
            except csv.Error:
                pass
            reader = csv.reader(handle, delimiter=delimiter)
            rows = list(reader)
        if not rows:
            return {}
        header = [cell.strip().lower() for cell in rows[0]]
        data_rows = rows[1:] if {"text", "transcript", "sentence"}.intersection(header) else rows
        if data_rows is rows:
            header = []
        audio_index = 0
        text_index = 1 if len(rows[0]) > 1 else 0
        if header:
            for idx, cell in enumerate(header):
                if cell in {"audio", "audio_file", "file", "path", "filename"}:
                    audio_index = idx
                if cell in {"text", "transcript", "sentence", "utterance"}:
                    text_index = idx
        for row in data_rows:
            if not row:
                continue
            if len(row) <= max(audio_index, text_index):
                continue
            audio_key = row[audio_index].strip()
            text_value = row[text_index].strip()
            if audio_key and text_value:
                mapping[audio_key] = text_value
    normalized: dict[str, str] = {}
    for key, value in mapping.items():
        path_key = Path(key)
        normalized[str(path_key)] = value
        normalized[path_key.name] = value
        normalized[path_key.stem] = value
    return normalized


def _lookup_transcript(audio_path: Path, transcript_map: dict[str, str]) -> str | None:
    keys = (str(audio_path), audio_path.name, audio_path.stem)
    for key in keys:
        if key in transcript_map:
            return transcript_map[key]
    return None


def _clean_text(text: str, language: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return ""
    try:
        cleaned = multilingual_cleaners(text, language)
        cleaned = re.sub(r"\s+", " ", cleaned or "").strip()
        return cleaned or text
    except Exception:
        return text


def _extract_transcribed_words(segments: Sequence[Any]) -> list[Any]:
    words: list[Any] = []
    for segment in segments:
        words.extend(getattr(segment, "words", None) or [])
    return words


def _write_metadata_files(
    entries: list[dict[str, Any]],
    dataset_dir: Path,
    eval_percentage: float,
    shuffle_seed: int,
) -> dict[str, str]:
    metadata_path = dataset_dir / "metadata.csv"
    shuffled_path = dataset_dir / "metadata_shuf.csv"
    train_path = dataset_dir / "metadata_train.csv"
    val_path = dataset_dir / "metadata_val.csv"

    rows = [f"{item['id']}|{item['text']}|{item['original_text']}" for item in entries]
    metadata_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")

    shuffled_entries = list(entries)
    random.Random(shuffle_seed).shuffle(shuffled_entries)
    shuffled_rows = [f"{item['id']}|{item['text']}|{item['original_text']}" for item in shuffled_entries]
    shuffled_path.write_text("\n".join(shuffled_rows) + ("\n" if shuffled_rows else ""), encoding="utf-8")

    if len(shuffled_entries) <= 1:
        train_entries = shuffled_entries
        val_entries: list[dict[str, Any]] = []
    else:
        val_count = max(1, int(round(len(shuffled_entries) * eval_percentage)))
        val_count = min(val_count, len(shuffled_entries) - 1)
        train_entries = shuffled_entries[:-val_count]
        val_entries = shuffled_entries[-val_count:]

    train_rows = [f"{item['id']}|{item['text']}|{item['original_text']}" for item in train_entries]
    val_rows = [f"{item['id']}|{item['text']}|{item['original_text']}" for item in val_entries]
    train_path.write_text("\n".join(train_rows) + ("\n" if train_rows else ""), encoding="utf-8")
    val_path.write_text("\n".join(val_rows) + ("\n" if val_rows else ""), encoding="utf-8")

    return {
        "metadata": str(metadata_path),
        "metadata_shuf": str(shuffled_path),
        "metadata_train": str(train_path),
        "metadata_val": str(val_path),
    }


def _extract_speaker_embeddings_pyannote(entries: list[dict[str, Any]], progress: ProgressCallback = None) -> np.ndarray:
    """Extracts speaker embeddings using pyannote's wespeaker-voxceleb-resnet34-LM model."""
    from pyannote.audio import Model, Inference
    import torch
    import numpy as np

    _notify(progress, "Loading pyannote/wespeaker-voxceleb-resnet34-LM speaker model...")
    model = Model.from_pretrained('pyannote/wespeaker-voxceleb-resnet34-LM')
    if torch.cuda.is_available():
        model = model.cuda()
    elif torch.backends.mps.is_available():
        try:
            model = model.to("mps")
        except Exception:
            pass

    inference = Inference(model, window="whole")
    
    embeddings = []
    for i, entry in enumerate(entries):
        if i % 10 == 0:
            _notify(progress, f"Extracting voice blueprints: {i}/{len(entries)}")
        emb = inference(entry["audio_path"])
        embeddings.append(emb)
        
    return np.array(embeddings)


def prepare_dataset(
    *,
    output_root: str,
    audio_files: Sequence[Any] | None = None,
    audio_dir: str | None = None,
    transcript_file: str | None = None,
    language: str = "en",
    whisper_model_name: str = "small",
    eval_percentage: float = DEFAULT_EVAL_PERCENTAGE,
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED,
    min_segment_seconds: float = DEFAULT_MIN_SEGMENT_SECONDS,
    max_segment_seconds: float = DEFAULT_MAX_SEGMENT_SECONDS,
    segment_buffer_seconds: float = DEFAULT_SEGMENT_BUFFER_SECONDS,
    diarize_speakers: bool = False,
    expected_speakers: int = 0,
    diarize_threshold: float = 0.3,
    dataset_name: str = "LJSpeech-1.1",
    progress: ProgressCallback = None,
) -> dict[str, Any]:
    output_root_path = _resolve_user_path(output_root, expect_directory=True)
    dataset_name = dataset_name or "LJSpeech-1.1"
    dataset_dir = output_root_path / "dataset" / dataset_name
    wavs_dir = dataset_dir / "wavs"

    resolved_audio_files = resolve_audio_files(audio_files, audio_dir)
    if not resolved_audio_files:
        raise ValueError("No audio files found. Provide files directly or point to a folder that contains audio.")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    wavs_dir.mkdir(parents=True, exist_ok=True)

    # Check if transcript_file is a VTT file
    is_vtt = False
    vtt_path = None
    if transcript_file:
        vtt_path = _resolve_user_path(transcript_file, must_exist=True, expect_directory=False)
        if vtt_path.suffix.lower() == ".vtt":
            is_vtt = True

    transcript_map = {} if is_vtt else _load_transcript_map(transcript_file)
    use_whisper = not transcript_map and not is_vtt
    asr_model: WhisperModel | None = None
    if use_whisper:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "float32"
        _notify(progress, f"Loading Whisper model '{whisper_model_name}' on {device}...")
        asr_model = WhisperModel(whisper_model_name, device=device, compute_type=compute_type, download_root=str(_MODELS_DIR))

    entries: list[dict[str, Any]] = []
    total_seconds = 0.0
    longest_entry: dict[str, Any] | None = None

    for index, audio_file in enumerate(resolved_audio_files, start=1):
        audio_path = Path(audio_file).expanduser().resolve()
        _notify(progress, f"Processing {index}/{len(resolved_audio_files)}: {audio_path.name}")
        waveform, sample_rate = _load_waveform(audio_path)
        total_duration = waveform.shape[-1] / sample_rate
        total_seconds += total_duration
        base_name = _safe_name(audio_path.stem)

        if is_vtt:
            _notify(progress, f"Slicing audio with VTT transcript file: {vtt_path.name}...")
            vtt_content = vtt_path.read_text(encoding="utf-8", errors="ignore")
            pattern = r"((?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s+-->\s+((?:\d{2}:)?\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\Z|\n\d|\n\[)"
            matches = re.findall(pattern, vtt_content, re.DOTALL)
            
            for clip_index, (start_str, end_str, text_val) in enumerate(matches):
                def to_secs(t_str):
                    parts = t_str.split(":")
                    if len(parts) == 3:
                        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                    elif len(parts) == 2:
                        return float(parts[0]) * 60 + float(parts[1])
                    return float(parts[0])
                
                sentence_start = max(to_secs(start_str) - segment_buffer_seconds, 0.0)
                clip_end = min(to_secs(end_str) + segment_buffer_seconds, total_duration)
                duration_seconds = clip_end - sentence_start
                sentence_text = re.sub(r"\s+", " ", text_val).strip()
                cleaned = _clean_text(sentence_text, language)
                
                if cleaned and duration_seconds >= min_segment_seconds:
                    sample_id = f"{base_name}_{clip_index:08d}"
                    destination = wavs_dir / f"{sample_id}.wav"
                    start_frame = max(0, int(sentence_start * sample_rate))
                    end_frame = min(waveform.shape[-1], int(clip_end * sample_rate))
                    clip = waveform[:, start_frame:end_frame]
                    if clip.shape[-1] >= int(min_segment_seconds * sample_rate):
                        _save_waveform(destination, clip, sample_rate)
                        entry = {
                            "id": sample_id,
                            "text": cleaned,
                            "original_text": sentence_text,
                            "audio_path": str(destination),
                            "duration_seconds": duration_seconds,
                        }
                        entries.append(entry)
                        if longest_entry is None or duration_seconds > longest_entry["duration_seconds"]:
                            longest_entry = entry
            continue

        if transcript_map:
            transcript = _lookup_transcript(audio_path, transcript_map)
            if not transcript:
                raise ValueError(f"Missing transcript for {audio_path.name}")
            cleaned = _clean_text(transcript, language)
            sample_id = base_name
            destination = wavs_dir / f"{sample_id}.wav"
            suffix = 1
            while destination.exists():
                sample_id = f"{base_name}_{suffix:02d}"
                destination = wavs_dir / f"{sample_id}.wav"
                suffix += 1
            _save_waveform(destination, waveform, sample_rate)
            entry = {
                "id": sample_id,
                "text": cleaned,
                "original_text": transcript.strip(),
                "audio_path": str(destination),
                "duration_seconds": total_duration,
            }
            entries.append(entry)
            if longest_entry is None or entry["duration_seconds"] > longest_entry["duration_seconds"]:
                longest_entry = entry
            continue

        assert asr_model is not None
        segments, _ = asr_model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True,
            word_timestamps=True,
        )
        words = _extract_transcribed_words(segments)
        if not words:
            _notify(progress, f"Warning: Whisper did not return timestamped words for {audio_path.name}. Skipping this file.")
            continue

        clip_index = 0
        sentence_words: list[Any] = []
        sentence_start: float | None = None
        for word_index, word in enumerate(words):
            if sentence_start is None:
                sentence_start = max(float(word.start) - segment_buffer_seconds, 0.0)
            sentence_words.append(word)
            current_duration = float(word.end) - sentence_start
            at_end = word_index == len(words) - 1
            text_fragment = "".join(item.word for item in sentence_words).strip()
            ends_sentence = text_fragment.endswith(PUNCTUATION_ENDINGS)
            should_flush = at_end or ends_sentence or current_duration >= max_segment_seconds
            if not should_flush:
                continue

            clip_end = min(float(word.end) + segment_buffer_seconds, total_duration)
            sentence_text = re.sub(r"\s+", " ", "".join(item.word for item in sentence_words)).strip()
            cleaned = _clean_text(sentence_text, language)
            duration_seconds = clip_end - sentence_start
            if cleaned and duration_seconds >= min_segment_seconds:
                sample_id = f"{base_name}_{clip_index:08d}"
                destination = wavs_dir / f"{sample_id}.wav"
                start_frame = max(0, int(sentence_start * sample_rate))
                end_frame = min(waveform.shape[-1], int(clip_end * sample_rate))
                clip = waveform[:, start_frame:end_frame]
                if clip.shape[-1] >= int(min_segment_seconds * sample_rate):
                    _save_waveform(destination, clip, sample_rate)
                    entry = {
                        "id": sample_id,
                        "text": cleaned,
                        "original_text": sentence_text,
                        "audio_path": str(destination),
                        "duration_seconds": duration_seconds,
                    }
                    entries.append(entry)
                    if longest_entry is None or duration_seconds > longest_entry["duration_seconds"]:
                        longest_entry = entry
                    clip_index += 1
            sentence_words = []
            sentence_start = None

    if not entries:
        raise ValueError("No usable training samples were created from the provided audio.")

    if diarize_speakers and len(entries) > 1:
        _notify(progress, "Starting speaker diarization clustering...")
        try:
            embeddings_array = _extract_speaker_embeddings_pyannote(entries, progress)
            dist_matrix = pdist(embeddings_array, metric='cosine')
            # Use 'average' linkage which is more robust to outliers than 'complete' linkage
            Z = linkage(dist_matrix, method='average')
            if expected_speakers > 0:
                labels = fcluster(Z, expected_speakers, criterion='maxclust')
            else:
                labels = fcluster(Z, t=diarize_threshold, criterion='distance')
            
            from collections import defaultdict
            clusters = defaultdict(list)
            for label, entry in zip(labels, entries):
                clusters[label].append(entry)
                
            sorted_clusters = sorted(clusters.values(), key=lambda c: sum(e["duration_seconds"] for e in c), reverse=True)
            _notify(progress, f"Found {len(sorted_clusters)} distinct speakers.")
            
            # Create sub-datasets
            primary_dataset_info = None
            all_speakers = []
            for idx, cluster_entries in enumerate(sorted_clusters, start=1):
                speaker_dataset_dir = output_root_path / "dataset" / f"{dataset_name}_Speaker_{idx}"
                speaker_wavs_dir = speaker_dataset_dir / "wavs"
                if speaker_dataset_dir.exists():
                    shutil.rmtree(speaker_dataset_dir)
                speaker_wavs_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy wavs
                for entry in cluster_entries:
                    new_wav_path = speaker_wavs_dir / Path(entry["audio_path"]).name
                    shutil.copy2(entry["audio_path"], new_wav_path)
                    entry["audio_path"] = str(new_wav_path)
                
                speaker_metadata = _write_metadata_files(cluster_entries, speaker_dataset_dir, eval_percentage, shuffle_seed)
                (speaker_dataset_dir / "lang.txt").write_text(f"{language}\n", encoding="utf-8")
                
                speaker_longest = max(cluster_entries, key=lambda e: e["duration_seconds"])
                speaker_info = {
                    "dataset_dir": str(speaker_dataset_dir),
                    "wavs_dir": str(speaker_wavs_dir),
                    "language": language,
                    "sample_rate": DEFAULT_SAMPLE_RATE,
                    "input_audio_count": len(resolved_audio_files),
                    "created_sample_count": len(cluster_entries),
                    "total_audio_seconds": round(sum(e["duration_seconds"] for e in cluster_entries), 2),
                    "reference_wav": speaker_longest["audio_path"],
                    **speaker_metadata,
                }
                info_path = speaker_dataset_dir / "dataset_info.json"
                info_path.write_text(json.dumps(_json_ready(speaker_info), indent=2), encoding="utf-8")
                speaker_info["dataset_info"] = str(info_path)
                
                all_speakers.append(speaker_info)
                if idx == 1:
                    primary_dataset_info = speaker_info
            
            # We preserve the original mixed dataset so that it can be re-diarized later
            # shutil.rmtree(dataset_dir)
            
            primary_dataset_info["all_speakers"] = all_speakers
            _notify(progress, f"Diarization complete! Found {len(all_speakers)} speaker(s). Returning Speaker 1 dataset ({primary_dataset_info['total_audio_seconds']} seconds).")
            return primary_dataset_info

        except Exception as e:
            _notify(progress, f"Diarization failed: {e}. Falling back to mixed dataset.")
            traceback.print_exc()

    # Fallback / Non-diarized path
    metadata_files = _write_metadata_files(entries, dataset_dir, eval_percentage, shuffle_seed)
    (dataset_dir / "lang.txt").write_text(f"{language}\n", encoding="utf-8")

    dataset_info = {
        "dataset_dir": str(dataset_dir),
        "wavs_dir": str(wavs_dir),
        "language": language,
        "sample_rate": DEFAULT_SAMPLE_RATE,
        "input_audio_count": len(resolved_audio_files),
        "created_sample_count": len(entries),
        "total_audio_seconds": round(total_seconds, 2),
        "reference_wav": longest_entry["audio_path"] if longest_entry else "",
        **metadata_files,
    }
    info_path = dataset_dir / "dataset_info.json"
    info_path.write_text(json.dumps(_json_ready(dataset_info), indent=2), encoding="utf-8")
    dataset_info["dataset_info"] = str(info_path)
    _notify(progress, f"Dataset creation complete! Created {dataset_info['created_sample_count']} samples.")
    return dataset_info


def re_diarize_dataset(
    *,
    dataset_dir: str,
    expected_speakers: int = 0,
    diarize_threshold: float = 0.35,
    eval_percentage: float = DEFAULT_EVAL_PERCENTAGE,
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED,
    progress: ProgressCallback = None,
) -> dict[str, Any]:
    dataset_path = Path(dataset_dir).expanduser().resolve()
    if not dataset_path.exists() or not dataset_path.is_dir():
        raise ValueError(f"Dataset directory not found: {dataset_path}")
        
    wavs_dir = dataset_path / "wavs"
    if not wavs_dir.exists() or not wavs_dir.is_dir():
        raise ValueError(f"Wavs directory not found inside dataset: {wavs_dir}")
        
    metadata_path = dataset_path / "metadata.csv"
    if not metadata_path.exists():
        raise ValueError(f"metadata.csv not found in dataset: {metadata_path}")
        
    # Read language from lang.txt if available
    language = "en"
    lang_file = dataset_path / "lang.txt"
    if lang_file.exists():
        language = lang_file.read_text(encoding="utf-8").strip()
        
    # Parse metadata.csv
    entries = []
    with metadata_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 2:
                sample_id = parts[0]
                text = parts[1]
                original_text = parts[2] if len(parts) > 2 else text
                audio_path = wavs_dir / f"{sample_id}.wav"
                if audio_path.exists():
                    import soundfile as sf
                    info = sf.info(str(audio_path))
                    duration_seconds = info.duration
                    entries.append({
                        "id": sample_id,
                        "text": text,
                        "original_text": original_text,
                        "audio_path": str(audio_path),
                        "duration_seconds": duration_seconds,
                    })
                    
    if not entries:
        raise ValueError("No valid audio clips found in metadata.csv")
        
    _notify(progress, f"Loaded {len(entries)} clips from metadata.csv. Starting diarization clustering...")
    
    embeddings_array = _extract_speaker_embeddings_pyannote(entries, progress)
    dist_matrix = pdist(embeddings_array, metric='cosine')
    Z = linkage(dist_matrix, method='average')
    if expected_speakers > 0:
        labels = fcluster(Z, expected_speakers, criterion='maxclust')
    else:
        labels = fcluster(Z, t=diarize_threshold, criterion='distance')
        
    from collections import defaultdict
    clusters = defaultdict(list)
    for label, entry in zip(labels, entries):
        clusters[label].append(entry)
        
    sorted_clusters = sorted(clusters.values(), key=lambda c: sum(e["duration_seconds"] for e in c), reverse=True)
    _notify(progress, f"Found {len(sorted_clusters)} distinct speakers.")
    
    # Determine base name of dataset by stripping _Speaker_X
    base_name = dataset_path.name
    base_name = re.sub(r"_Speaker_\d+$", "", base_name)
    
    # Create sub-datasets
    primary_dataset_info = None
    all_speakers = []
    for idx, cluster_entries in enumerate(sorted_clusters, start=1):
        speaker_dataset_dir = dataset_path.parent / f"{base_name}_Speaker_{idx}"
        speaker_wavs_dir = speaker_dataset_dir / "wavs"
        if speaker_dataset_dir.exists():
            shutil.rmtree(speaker_dataset_dir)
        speaker_wavs_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy wavs
        for entry in cluster_entries:
            new_wav_path = speaker_wavs_dir / Path(entry["audio_path"]).name
            shutil.copy2(entry["audio_path"], new_wav_path)
            entry["audio_path"] = str(new_wav_path)
            
        speaker_metadata = _write_metadata_files(cluster_entries, speaker_dataset_dir, eval_percentage, shuffle_seed)
        (speaker_dataset_dir / "lang.txt").write_text(f"{language}\n", encoding="utf-8")
        
        speaker_longest = max(cluster_entries, key=lambda e: e["duration_seconds"])
        speaker_info = {
            "dataset_dir": str(speaker_dataset_dir),
            "wavs_dir": str(speaker_wavs_dir),
            "language": language,
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "input_audio_count": 1,
            "created_sample_count": len(cluster_entries),
            "total_audio_seconds": round(sum(e["duration_seconds"] for e in cluster_entries), 2),
            "reference_wav": speaker_longest["audio_path"],
            **speaker_metadata,
        }
        info_path = speaker_dataset_dir / "dataset_info.json"
        info_path.write_text(json.dumps(_json_ready(speaker_info), indent=2), encoding="utf-8")
        speaker_info["dataset_info"] = str(info_path)
        
        all_speakers.append(speaker_info)
        if idx == 1:
            primary_dataset_info = speaker_info
            
    primary_dataset_info["all_speakers"] = all_speakers
    _notify(progress, f"Re-diarization complete! Found {len(all_speakers)} speaker(s). Returning Speaker 1 dataset ({primary_dataset_info['total_audio_seconds']} seconds).")
    return primary_dataset_info



def _replace_literal(source: str, old: str, new: str) -> str:
    return source.replace(old, new) if old in source else source


def _replace_keyword_value(source: str, keyword: str, value: str) -> str:
    patterns = [
        rf"(?P<prefix>\b{re.escape(keyword)}\s*=\s*)(?P<value>[^,\n\)]+)",
        rf"(?P<prefix>^{re.escape(keyword)}\s*=\s*)(?P<value>.+)$",
    ]
    flags = [re.MULTILINE, re.MULTILINE]
    for pattern, flag in zip(patterns, flags):
        source, count = re.subn(pattern, rf"\g<prefix>{value}", source, count=1, flags=flag)
        if count:
            break
    return source


def _apply_source_overrides(source: str, overrides: dict[str, Any]) -> tuple[str, list[str]]:
    unused: list[str] = []
    for key, value in overrides.items():
        rendered = repr(value) if isinstance(value, str) else json.dumps(value)
        updated = _replace_keyword_value(source, key, rendered)
        if updated == source:
            unused.append(key)
        source = updated
    return source, unused


def _prepare_workspace(spec_key: str, dataset_dir: Path, training_root: Path) -> tuple[Path, Path]:
    spec = get_model_spec(spec_key)
    workspace_root = training_root / "workspace"
    recipe_target_dir = workspace_root / "recipes" / "ljspeech" / spec.recipe_dir
    dataset_target_dir = workspace_root / "recipes" / "ljspeech" / "LJSpeech-1.1"
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
    recipe_target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(spec.recipe_path, recipe_target_dir)
    shutil.copytree(dataset_dir, dataset_target_dir)
    return workspace_root, recipe_target_dir / spec.train_script


def _download_restore_path(spec_key: str, use_pretrained: bool, restore_path: str | None, progress: ProgressCallback) -> str | None:
    spec = get_model_spec(spec_key)
    if restore_path:
        return str(_resolve_user_path(restore_path, must_exist=True, expect_directory=False))
    if spec.family == "xtts":
        _notify(progress, f"{spec.label} already downloads its official base checkpoint inside the recipe.")
        return None
    if not use_pretrained or not spec.official_model_id:
        return None
    _notify(progress, f"Downloading base checkpoint for {spec.label}...")
    model_path, _, _ = ModelManager(progress_bar=True).download_model(spec.official_model_id)
    return model_path


def _resolve_xtts_base_model(spec_key: str) -> dict[str, str] | str:
    """
    Finds the 4 base model files for XTTS (v1 or v2) in the models directory.
    If all 4 files are found, returns a dict with keys:
      - 'dvae_checkpoint'
      - 'mel_norm_file'
      - 'tokenizer_file'
      - 'xtts_checkpoint'
    pointing to their absolute paths.
    
    If not found, returns the path of a shared folder to download them to.
    """
    version_str = "v2.0" if spec_key == "xtts_v2" else "v1.1"
    folder_name = f"XTTS_{version_str}_original_model_files"
    
    # Determine the shared download path
    if (_MODELS_DIR / "tts").is_dir():
        shared_dir = _MODELS_DIR / "tts" / folder_name
    else:
        shared_dir = _MODELS_DIR / folder_name
        
    # List of candidate directories to search for existing files
    candidates = []
    
    # Check if the shared directory already has them
    candidates.append(shared_dir)
    
    # Check HuggingFace cache style folders under both models/ and models/tts/
    hf_repo_name = "models--coqui--XTTS-v2" if spec_key == "xtts_v2" else "models--coqui--XTTS-v1"
    for base in [_MODELS_DIR, _MODELS_DIR / "tts", _PROJECT_ROOT / "models"]:
        hf_dir = base / hf_repo_name / "snapshots"
        if hf_dir.is_dir():
            try:
                for sub in hf_dir.iterdir():
                    if sub.is_dir():
                        candidates.append(sub)
            except Exception:
                pass
                
    # Check simple folder candidates
    for base in [_MODELS_DIR, _MODELS_DIR / "tts", _PROJECT_ROOT / "models"]:
        candidates.append(base / folder_name)
        
    # Search candidates for the 4 required files
    for cand in candidates:
        if not cand.is_dir():
            continue
        dvae = cand / "dvae.pth"
        mel = cand / "mel_stats.pth"
        vocab = cand / "vocab.json"
        model = cand / "model.pth"
        if dvae.is_file() and mel.is_file() and vocab.is_file() and model.is_file():
            return {
                "dvae_checkpoint": str(dvae.resolve()),
                "mel_norm_file": str(mel.resolve()),
                "tokenizer_file": str(vocab.resolve()),
                "xtts_checkpoint": str(model.resolve())
            }
            
    # If not found, make sure the shared download directory exists and return it
    shared_dir.mkdir(parents=True, exist_ok=True)
    return str(shared_dir.resolve())


def _patch_recipe_script(
    script_path: Path,
    *,
    spec_key: str,
    dataset_dir: Path,
    language: str,
    epochs: int,
    batch_size: int,
    grad_accum: int,
    max_audio_seconds: int,
    restore_path: str | None,
    extra_overrides: dict[str, Any],
    reference_wav: str,
) -> list[str]:
    source = script_path.read_text(encoding="utf-8")
    dataset_str = str(dataset_dir)
    wavs_str = str(dataset_dir / "wavs")

    source = _replace_literal(source, 'path=os.path.join(output_path, "../LJSpeech-1.1/")', f'path=r"{dataset_str}"')
    source = _replace_literal(source, 'path="/raid/datasets/LJSpeech-1.1_24khz/"', f'path=r"{dataset_str}"')
    source = _replace_literal(
        source,
        'meta_file_train="/raid/datasets/LJSpeech-1.1_24khz/metadata.csv"',
        f'meta_file_train=r"{dataset_str}/metadata.csv"',
    )
    source = _replace_literal(source, 'data_path = ""', f'data_path = r"{dataset_str}"')
    source = _replace_literal(
        source,
        'data_path=os.path.join(output_path, "../LJSpeech-1.1/wavs/")',
        f'data_path=r"{wavs_str}"',
    )
    source = _replace_literal(source, 'python TTS/bin/compute_attention_masks.py', 'python -m TTS.bin.compute_attention_masks')
    if not torch.cuda.is_available():
        source = source.replace('--use_cuda"', '"')
        source = source.replace('--use_cuda\'"', '\'"')

    source = _replace_keyword_value(source, "batch_size", str(batch_size))
    source = _replace_keyword_value(source, "eval_batch_size", str(batch_size))
    source = _replace_keyword_value(source, "epochs", str(epochs))
    source = _replace_keyword_value(source, "BATCH_SIZE", str(batch_size))
    source = _replace_keyword_value(source, "GRAD_ACUMM_STEPS", str(grad_accum))
    source = _replace_keyword_value(source, "max_wav_length", str(int(max_audio_seconds * DEFAULT_SAMPLE_RATE)))
    source = _replace_keyword_value(source, "num_loader_workers", "0")
    source = _replace_keyword_value(source, "num_eval_loader_workers", "0")
    source = _replace_keyword_value(source, "mixed_precision", "False")

    spec = get_model_spec(spec_key)
    # Patch for multilingual/scratch training on single-language models
    if not spec.supports_language and language != "en":
        for q in ['"', "'"]:
            source = source.replace(f'text_cleaner={q}english_cleaners{q}', f'text_cleaner={q}multilingual_cleaners{q}')
            source = source.replace(f'text_cleaner={q}phoneme_cleaners{q}', f'text_cleaner={q}multilingual_cleaners{q}')
            source = source.replace(f'phoneme_language={q}en-us{q}', f'phoneme_language={q}{language}{q}')

    if spec_key.startswith("xtts_"):
        source = _replace_keyword_value(source, "language", repr(language))
        speaker_value = f'SPEAKER_REFERENCE = [r"{reference_wav}"]'
        source = re.sub(r"SPEAKER_REFERENCE\s*=\s*\[[^\]]*\]", speaker_value, source, count=1, flags=re.DOTALL)
        if restore_path:
            source = _replace_keyword_value(source, "XTTS_CHECKPOINT", repr(restore_path))
            
        # Resolve base model files to avoid duplicate downloads and grab from ebook2audiobook/models
        resolved = _resolve_xtts_base_model(spec_key)
        if isinstance(resolved, dict):
            # We found the files in the cache or some candidate folder, point directly to them
            source = _replace_literal(source, 'DVAE_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(DVAE_CHECKPOINT_LINK))', f'DVAE_CHECKPOINT = r"{resolved["dvae_checkpoint"]}"')
            source = _replace_literal(source, 'DVAE_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, DVAE_CHECKPOINT_LINK.split("/")[-1])', f'DVAE_CHECKPOINT = r"{resolved["dvae_checkpoint"]}"')
            
            source = _replace_literal(source, 'MEL_NORM_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(MEL_NORM_LINK))', f'MEL_NORM_FILE = r"{resolved["mel_norm_file"]}"')
            source = _replace_literal(source, 'MEL_NORM_FILE = os.path.join(CHECKPOINTS_OUT_PATH, MEL_NORM_LINK.split("/")[-1])', f'MEL_NORM_FILE = r"{resolved["mel_norm_file"]}"')
            
            source = _replace_literal(source, 'TOKENIZER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(TOKENIZER_FILE_LINK))', f'TOKENIZER_FILE = r"{resolved["tokenizer_file"]}"')
            source = _replace_literal(source, 'TOKENIZER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, TOKENIZER_FILE_LINK.split("/")[-1])', f'TOKENIZER_FILE = r"{resolved["tokenizer_file"]}"')
            
            source = _replace_literal(source, 'XTTS_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CHECKPOINT_LINK))', f'XTTS_CHECKPOINT = r"{resolved["xtts_checkpoint"]}"')
            source = _replace_literal(source, 'XTTS_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, XTTS_CHECKPOINT_LINK.split("/")[-1])', f'XTTS_CHECKPOINT = r"{resolved["xtts_checkpoint"]}"')
        else:
            # We didn't find the files, point CHECKPOINTS_OUT_PATH to the shared directory so they download there and can be reused next time
            source = _replace_literal(source, 'CHECKPOINTS_OUT_PATH = os.path.join(OUT_PATH, "XTTS_v2.0_original_model_files/")', f'CHECKPOINTS_OUT_PATH = r"{resolved}"')
            source = _replace_literal(source, 'CHECKPOINTS_OUT_PATH = os.path.join(OUT_PATH, "XTTS_v1.1_original_model_files/")', f'CHECKPOINTS_OUT_PATH = r"{resolved}"')
    elif restore_path:
        if "restore_path=None" in source:
            source = source.replace("restore_path=None", f"restore_path=r\"{restore_path}\"", 1)
        else:
            source = source.replace("TrainerArgs()", f"TrainerArgs(restore_path=r\"{restore_path}\")", 1)

    source, unused = _apply_source_overrides(source, extra_overrides)
    script_path.write_text(source, encoding="utf-8")
    return unused


def _latest_matching_file(root: Path, patterns: Sequence[str]) -> Path | None:
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(root.rglob(pattern))
    candidates = [path for path in candidates if path.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _pick_reference_wav(dataset_dir: Path, dataset_info: dict[str, Any]) -> str:
    reference_wav = dataset_info.get("reference_wav")
    if reference_wav and Path(reference_wav).exists():
        return reference_wav
    wavs_dir = dataset_dir / "wavs"
    candidates = sorted(wavs_dir.glob("*.wav"))
    if not candidates:
        return ""
    return str(max(candidates, key=lambda path: sf.info(str(path)).duration))


def _tail_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[-max_chars:]


def _optimize_xtts_checkpoint(source_path: Path, destination_path: Path) -> None:
    try:
        checkpoint = torch.load(str(source_path), map_location=torch.device("cpu"), weights_only=True)
    except TypeError:
        warnings.warn(
            "Falling back to torch.load without weights_only=True. Do not load untrusted checkpoints.",
            RuntimeWarning,
        )
        checkpoint = torch.load(str(source_path), map_location=torch.device("cpu"))
    checkpoint.pop("optimizer", None)
    model_state = checkpoint.get("model", {})
    for key in list(model_state):
        if "dvae" in key:
            del model_state[key]
    torch.save(checkpoint, str(destination_path))


def _finalize_training_artifacts(
    *,
    spec_key: str,
    training_root: Path,
    dataset_dir: Path,
    reference_wav: str,
) -> dict[str, Any]:
    spec = get_model_spec(spec_key)
    ready_dir = training_root / "ready"
    ready_dir.mkdir(parents=True, exist_ok=True)

    workspace_root = training_root / "workspace"
    checkpoint = _latest_matching_file(workspace_root, ["best_model.pth", "*.pth"])
    if checkpoint is None:
        raise FileNotFoundError(f"No checkpoint file was produced for {spec.label}.")

    ignored_suffixes = {"vocab.json", "speakers_xtts.pth", "mel_stats.pth", "dvae.pth"}
    if checkpoint.name in ignored_suffixes:
        raise FileNotFoundError(f"A trainable checkpoint for {spec.label} was not found.")

    config_path = checkpoint.parent / "config.json"
    if not config_path.exists():
        config_path = _latest_matching_file(workspace_root, ["config.json"])
    if config_path is None:
        raise FileNotFoundError(f"config.json was not found for {spec.label}.")

    ready_checkpoint = ready_dir / "model.pth"
    if spec.family == "xtts":
        _optimize_xtts_checkpoint(checkpoint, ready_checkpoint)
    else:
        shutil.copy2(checkpoint, ready_checkpoint)

    ready_config = ready_dir / "config.json"
    shutil.copy2(config_path, ready_config)

    artifacts: dict[str, Any] = {
        "model_key": spec.key,
        "model_label": spec.label,
        "family": spec.family,
        "training_root": str(training_root),
        "dataset_dir": str(dataset_dir),
        "checkpoint": str(ready_checkpoint),
        "config": str(ready_config),
        "reference_wav": reference_wav,
        "default_vocoder_id": spec.default_vocoder_id,
    }

    if reference_wav and Path(reference_wav).exists():
        ready_reference = ready_dir / "reference.wav"
        shutil.copy2(reference_wav, ready_reference)
        artifacts["reference_wav"] = str(ready_reference)

    if spec.family == "xtts":
        vocab = _latest_matching_file(workspace_root, ["vocab.json"])
        if not vocab:
            # Fallback: search in resolved base model
            resolved = _resolve_xtts_base_model(spec_key)
            if isinstance(resolved, dict) and "tokenizer_file" in resolved:
                vocab = Path(resolved["tokenizer_file"])
        if not vocab:
            raise FileNotFoundError("XTTS training completed but vocab.json was not found.")

        speaker = _latest_matching_file(workspace_root, ["speakers_xtts.pth"])
        if not speaker:
            # Search candidate directories for speakers_xtts.pth
            resolved = _resolve_xtts_base_model(spec_key)
            if isinstance(resolved, dict) and "xtts_checkpoint" in resolved:
                cand = Path(resolved["xtts_checkpoint"]).parent / "speakers_xtts.pth"
                if cand.is_file():
                    speaker = cand
            if not speaker:
                # Search all snapshots and shared folders
                hf_repo_name = "models--coqui--XTTS-v2" if spec_key == "xtts_v2" else "models--coqui--XTTS-v1"
                version_str = "v2.0" if spec_key == "xtts_v2" else "v1.1"
                folder_name = f"XTTS_{version_str}_original_model_files"
                for base in [_MODELS_DIR, _MODELS_DIR / "tts", _PROJECT_ROOT / "models"]:
                    # Check folder_name
                    cand = base / folder_name / "speakers_xtts.pth"
                    if cand.is_file():
                        speaker = cand
                        break
                    # Check snapshots
                    hf_dir = base / hf_repo_name / "snapshots"
                    if hf_dir.is_dir():
                        try:
                            for sub in hf_dir.iterdir():
                                if sub.is_dir():
                                    cand = sub / "speakers_xtts.pth"
                                    if cand.is_file():
                                        speaker = cand
                                        break
                        except Exception:
                            pass
                    if speaker:
                        break
            if not speaker:
                # Download it to models/tts
                _notify(None, "speakers_xtts.pth not found locally. Downloading base speaker file...")
                try:
                    import urllib.request
                    version_str = "v2.0" if spec_key == "xtts_v2" else "v1.1"
                    dest_dir = (_MODELS_DIR / "tts") if (_MODELS_DIR / "tts").is_dir() else _MODELS_DIR
                    dest_path = dest_dir / f"XTTS_{version_str}_original_model_files" / "speakers_xtts.pth"
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    url = f"https://coqui.gateway.scarf.sh/hf-coqui/XTTS-{'v2' if spec_key == 'xtts_v2' else 'v1'}/main/speakers_xtts.pth"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=15) as response:
                        dest_path.write_bytes(response.read())
                    speaker = dest_path
                except Exception as dl_err:
                    _notify(None, f"Warning: Failed to download speakers_xtts.pth: {dl_err}. Creating a dummy speaker file.")
                    dest_dir = (_MODELS_DIR / "tts") if (_MODELS_DIR / "tts").is_dir() else _MODELS_DIR
                    dest_path = dest_dir / f"XTTS_{version_str}_original_model_files" / "speakers_xtts.pth"
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    dest_path.write_bytes(b"")
                    speaker = dest_path

        ready_vocab = ready_dir / "vocab.json"
        ready_speaker = ready_dir / "speakers_xtts.pth"
        shutil.copy2(vocab, ready_vocab)
        shutil.copy2(speaker, ready_speaker)
        artifacts["vocab"] = str(ready_vocab)
        artifacts["speaker_file"] = str(ready_speaker)

    artifacts_path = ready_dir / "artifacts.json"
    artifacts_path.write_text(json.dumps(_json_ready(artifacts), indent=2), encoding="utf-8")
    artifacts["artifacts_file"] = str(artifacts_path)
    return artifacts


def _normalize_dataset_dir(dataset_dir: str | None, output_root: str) -> Path:
    if dataset_dir:
        path = _resolve_user_path(dataset_dir, must_exist=True, expect_directory=True)
    else:
        path = _resolve_user_path(output_root, expect_directory=True) / "dataset" / "LJSpeech-1.1"
    if not path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {path}")
    return path


def load_dataset_info(dataset_dir: str) -> dict[str, Any]:
    info_path = _resolve_user_path(dataset_dir, must_exist=True, expect_directory=True) / "dataset_info.json"
    if info_path.exists():
        return json.loads(info_path.read_text(encoding="utf-8"))
    return {}


def train_model(
    *,
    model_key: str,
    output_root: str,
    dataset_dir: str | None = None,
    language: str = "en",
    epochs: int = 10,
    batch_size: int = 8,
    grad_accum: int = 1,
    max_audio_seconds: int = 11,
    restore_path: str | None = None,
    use_pretrained: bool = True,
    extra_overrides_json: str | None = None,
    dry_run: bool = False,
    progress: ProgressCallback = None,
    stream_logs: bool = True,
    sample_epoch_interval: int = 0,
    sample_text: str = "",
) -> dict[str, Any]:
    spec = get_model_spec(model_key)
    dataset_root = _normalize_dataset_dir(dataset_dir, output_root)
    dataset_info = load_dataset_info(str(dataset_root))
    output_root_path = _resolve_user_path(output_root, expect_directory=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    training_root = output_root_path / "training_runs" / model_key / timestamp
    training_root.mkdir(parents=True, exist_ok=True)

    if model_key == "piper":
        from utils.piper_utils import (
            ensure_monotonic_align_compiled,
            resolve_piper_checkpoint,
            download_piper_checkpoint,
            preprocess_piper_dataset,
            train_piper_model,
            export_piper_onnx
        )
        ensure_monotonic_align_compiled()
        
        # Resolve and download pretrained checkpoint if applicable
        base_ckpt_path = None
        config_path = None
        quality = "medium"
        sample_rate = 22050
        espeak_language = language.lower().replace("_", "-")

        if restore_path:
            base_ckpt_path = Path(restore_path)
            config_path = base_ckpt_path.parent / "config.json"
            if not config_path.exists():
                json_files = list(base_ckpt_path.parent.glob("*.json"))
                if json_files:
                    config_path = json_files[0]
                else:
                    _notify(progress, "Checkpoint config not found locally. Resolving a base config...")
                    checkpoint_info = resolve_piper_checkpoint(language)
                    _, config_path = download_piper_checkpoint(checkpoint_info, progress)

            if config_path and config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    ckpt_config = json.load(f)
                sample_rate = ckpt_config.get("audio", {}).get("sample_rate", 22050)
                quality = ckpt_config.get("audio", {}).get("quality", "medium")
                espeak_language = ckpt_config.get("espeak", {}).get("voice") or ckpt_config.get("language", {}).get("code") or espeak_language
        elif use_pretrained:
            _notify(progress, f"Resolving Piper checkpoint for language: {language}...")
            checkpoint_info = resolve_piper_checkpoint(language)
            _notify(progress, f"Downloading checkpoint: {checkpoint_info['voice']} ({checkpoint_info['quality']})")
            base_ckpt_path, config_path = download_piper_checkpoint(checkpoint_info, progress)

            with open(config_path, "r", encoding="utf-8") as f:
                ckpt_config = json.load(f)
            sample_rate = ckpt_config.get("audio", {}).get("sample_rate", 22050)
            quality = checkpoint_info.get("quality", "medium")
            espeak_language = checkpoint_info["locale"].lower().replace("_", "-")
        else:
            _notify(progress, f"Training Piper model from scratch for language: {language}...")

        preprocessed_dir = training_root / "preprocessed"
        if not config_path:
            config_path = preprocessed_dir / "config.json"

        run_summary = {
            "model_key": spec.key,
            "model_label": spec.label,
            "training_root": str(training_root),
            "preprocessed_dir": str(preprocessed_dir),
            "dataset_dir": str(dataset_root),
            "base_checkpoint": str(base_ckpt_path) if base_ckpt_path else "",
            "base_config": str(config_path),
            "espeak_language": espeak_language,
            "sample_rate": sample_rate,
            "quality": quality,
        }
        if dry_run:
            run_summary["status"] = "dry-run"
            return run_summary
            
        # 1. Preprocess dataset
        _notify(progress, "Preprocessing dataset for Piper...")
        preprocess_piper_dataset(dataset_root, preprocessed_dir, espeak_language, sample_rate)
        
        # 2. Overwrite configuration with base checkpoint's config
        shutil.copy2(config_path, preprocessed_dir / "config.json")
        
        # 3. Train the model
        _notify(progress, f"Training Piper model for {epochs} epochs...")
        log_path = training_root / "training.log"
        try:
            log_output = train_piper_model(
                preprocessed_dir=preprocessed_dir,
                base_ckpt_path=base_ckpt_path,
                epochs=epochs,
                batch_size=batch_size,
                quality=quality,
                stream_logs=stream_logs,
                progress_callback=progress,
                sample_epoch_interval=sample_epoch_interval,
                sample_text=sample_text,
                config_path=config_path,
                output_dir=training_root
            )
            log_path.write_text(log_output, encoding="utf-8")
        except Exception as e:
            if log_path.exists():
                log_output = log_path.read_text(encoding="utf-8")
            else:
                log_output = str(e)
            raise RuntimeError(
                f"Piper training failed. See {log_path}\n\n"
                f"LOGS:\n{_tail_text(log_output, ERROR_LOG_TAIL_CHARS)}"
            ) from e
            
        # 4. Find trained checkpoint and export to ONNX
        lightning_logs_dir = preprocessed_dir / "lightning_logs"
        trained_ckpt = _latest_matching_file(lightning_logs_dir, ["**/*.ckpt", "*.ckpt"])
        if not trained_ckpt:
            trained_ckpt = _latest_matching_file(training_root, ["**/*.ckpt", "*.ckpt"])
        if not trained_ckpt:
            raise FileNotFoundError("No training checkpoint .ckpt file was produced by Piper training.")
            
        _notify(progress, "Exporting trained model to ONNX...")
        ready_dir = training_root / "ready"
        ready_dir.mkdir(parents=True, exist_ok=True)
        ready_onnx = ready_dir / "model.onnx"
        
        export_piper_onnx(trained_ckpt, ready_onnx, config_path)
        
        artifacts = {
            "model_key": spec.key,
            "model_label": spec.label,
            "family": spec.family,
            "training_root": str(training_root),
            "dataset_dir": str(dataset_root),
            "checkpoint": str(ready_onnx),
            "config": str(ready_onnx) + ".json",
            "reference_wav": "",
            "log_path": str(log_path),
            "unused_overrides": {},
        }
        artifacts_path = ready_dir / "artifacts.json"
        artifacts_path.write_text(json.dumps(_json_ready(artifacts), indent=2), encoding="utf-8")
        artifacts["artifacts_file"] = str(artifacts_path)
        return artifacts

    computed_restore_path = _download_restore_path(model_key, use_pretrained, restore_path, progress)
    extra_overrides = json.loads(extra_overrides_json) if extra_overrides_json else {}
    if extra_overrides_json and not isinstance(extra_overrides, dict):
        raise ValueError("extra_overrides_json must be a JSON object.")

    reference_wav = _pick_reference_wav(dataset_root, dataset_info)
    workspace_root, script_path = _prepare_workspace(model_key, dataset_root, training_root)
    unused_overrides = _patch_recipe_script(
        script_path,
        spec_key=model_key,
        dataset_dir=dataset_root,
        language=language,
        epochs=epochs,
        batch_size=batch_size,
        grad_accum=grad_accum,
        max_audio_seconds=max_audio_seconds,
        restore_path=computed_restore_path,
        extra_overrides=extra_overrides,
        reference_wav=str(reference_wav) if reference_wav else "",
    )

    run_summary = {
        "model_key": spec.key,
        "model_label": spec.label,
        "training_root": str(training_root),
        "workspace_root": str(workspace_root),
        "dataset_dir": str(dataset_root),
        "script_path": str(script_path),
        "restore_path": computed_restore_path or "",
        "unused_overrides": unused_overrides,
    }
    if dry_run:
        run_summary["status"] = "dry-run"
        return run_summary

    _notify(progress, f"Starting training for {spec.label}...")
    log_path = training_root / "training.log"
    stdout_lines: list[str] = []

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=str(workspace_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True
    )
    register_active_process(process)
    try:
        if process.stdout:
            for line in process.stdout:
                stdout_lines.append(line)
                if stream_logs:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                if progress:
                    progress(line)
        process.wait()
    finally:
        register_active_process(None)

    full_log = "".join(stdout_lines)
    log_path.write_text(full_log, encoding="utf-8")
    
    if process.returncode != 0:
        raise RuntimeError(
            f"Training failed for {spec.label}. See {log_path}\n\n"
            f"LOGS:\n{_tail_text(full_log, ERROR_LOG_TAIL_CHARS)}"
        )
    artifacts = _finalize_training_artifacts(
        spec_key=model_key,
        training_root=training_root,
        dataset_dir=dataset_root,
        reference_wav=str(reference_wav) if reference_wav else "",
    )
    artifacts["log_path"] = str(log_path)
    artifacts["unused_overrides"] = unused_overrides
    return artifacts


def find_latest_artifacts(output_root: str, model_key: str | None = None) -> dict[str, Any]:
    base = _resolve_user_path(output_root, must_exist=True, expect_directory=True)
    search_root = base / "training_runs"
    if model_key:
        search_root = search_root / model_key
    artifact_file = _latest_matching_file(search_root, ["artifacts.json"])
    if not artifact_file:
        raise FileNotFoundError(f"No trained model artifacts were found under {search_root}")
    artifacts = json.loads(artifact_file.read_text(encoding="utf-8"))
    artifacts["artifacts_file"] = str(artifact_file)
    return artifacts


def load_artifacts(artifacts_path_or_dir: str, model_key: str | None = None) -> dict[str, Any]:
    path = _resolve_user_path(artifacts_path_or_dir, must_exist=True)
    if path.is_dir():
        artifacts_file = path / "artifacts.json"
        if not artifacts_file.exists():
            artifacts_file = path / "ready" / "artifacts.json"
        if not artifacts_file.exists():
            if model_key:
                return find_latest_artifacts(str(path), model_key)
            raise FileNotFoundError(f"Could not find artifacts.json inside {path}")
    else:
        artifacts_file = path
    artifacts = json.loads(artifacts_file.read_text(encoding="utf-8"))
    artifacts["artifacts_file"] = str(artifacts_file)
    return artifacts


def _load_xtts_runtime(artifacts: dict[str, Any]) -> Xtts:
    cache_key = json.dumps({
        "family": artifacts["family"],
        "checkpoint": artifacts["checkpoint"],
        "config": artifacts["config"],
        "vocab": artifacts.get("vocab"),
        "speaker_file": artifacts.get("speaker_file"),
    }, sort_keys=True)
    if cache_key in MODEL_CACHE:
        return MODEL_CACHE[cache_key]
    config = XttsConfig()
    config.load_json(artifacts["config"])
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_path=artifacts["checkpoint"],
        vocab_path=artifacts["vocab"],
        speaker_file_path=artifacts["speaker_file"],
        use_deepspeed=False,
    )
    if torch.cuda.is_available():
        model.cuda()
    MODEL_CACHE[cache_key] = model
    return model


def _download_vocoder(vocoder_model_id: str | None, progress: ProgressCallback) -> tuple[str | None, str | None]:
    if not vocoder_model_id:
        return None, None
    _notify(progress, f"Downloading vocoder '{vocoder_model_id}'...")
    vocoder_path, vocoder_config, _ = ModelManager(progress_bar=True).download_model(vocoder_model_id)
    return vocoder_path, vocoder_config


def _load_tts_runtime(artifacts: dict[str, Any], progress: ProgressCallback) -> TTS:
    cache_key = json.dumps({
        "family": artifacts["family"],
        "checkpoint": artifacts["checkpoint"],
        "config": artifacts["config"],
        "vocoder": artifacts.get("vocoder_path"),
        "vocoder_config": artifacts.get("vocoder_config"),
    }, sort_keys=True)
    if cache_key in MODEL_CACHE:
        return MODEL_CACHE[cache_key]
    vocoder_path = artifacts.get("vocoder_path")
    vocoder_config = artifacts.get("vocoder_config")
    if not vocoder_path and artifacts.get("default_vocoder_id"):
        vocoder_path, vocoder_config = _download_vocoder(artifacts["default_vocoder_id"], progress)
        artifacts["vocoder_path"] = vocoder_path
        artifacts["vocoder_config"] = vocoder_config
    runtime = TTS(
        model_path=artifacts["checkpoint"],
        config_path=artifacts["config"],
        vocoder_path=vocoder_path,
        vocoder_config_path=vocoder_config,
        gpu=torch.cuda.is_available(),
        progress_bar=False,
    )
    MODEL_CACHE[cache_key] = runtime
    return runtime


def synthesize(
    *,
    artifacts_path_or_dir: str,
    text: str,
    output_file: str,
    model_key: str | None = None,
    language: str = "en",
    speaker_wav: str | None = None,
    progress: ProgressCallback = None,
) -> dict[str, Any]:
    if not text.strip():
        raise ValueError("Text is required for synthesis.")
    artifacts = load_artifacts(artifacts_path_or_dir, model_key=model_key)
    output_path = _resolve_user_path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    speaker_reference = speaker_wav or artifacts.get("reference_wav")

    if artifacts["family"] == "xtts":
        if not speaker_reference:
            raise ValueError("XTTS inference requires a speaker reference WAV.")
        _notify(progress, "Loading XTTS model...")
        model = _load_xtts_runtime(artifacts)
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=speaker_reference,
            gpt_cond_len=model.config.gpt_cond_len,
            max_ref_length=model.config.max_ref_len,
            sound_norm_refs=model.config.sound_norm_refs,
        )
        _notify(progress, "Generating speech...")
        output = model.inference(
            text=text,
            language=language,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=model.config.temperature,
            length_penalty=model.config.length_penalty,
            repetition_penalty=model.config.repetition_penalty,
            top_k=model.config.top_k,
            top_p=model.config.top_p,
            enable_text_splitting=True,
        )
        waveform = torch.tensor(output["wav"]).unsqueeze(0)
        _save_waveform(output_path, waveform, 24000)
    elif artifacts["family"] == "piper":
        _notify(progress, "Loading Piper model and generating speech...")
        from utils.piper_utils import synthesize_piper
        synthesize_piper(
            onnx_path=artifacts["checkpoint"],
            config_path=artifacts["config"],
            text=text,
            output_wav_path=str(output_path)
        )
    else:
        _notify(progress, "Loading TTS model...")
        runtime = _load_tts_runtime(artifacts, progress)
        _notify(progress, "Generating speech...")
        runtime.tts_to_file(text=text, file_path=str(output_path), split_sentences=True)

    return {
        "model_key": artifacts["model_key"],
        "output_file": str(output_path),
        "speaker_wav": speaker_reference or "",
        "artifacts_file": artifacts["artifacts_file"],
    }


def list_supported_models() -> list[dict[str, Any]]:
    return [
        {
            **asdict(spec),
            "recipe_path": str(spec.recipe_path),
            "train_script_path": str(spec.train_script_path),
        }
        for spec in MODEL_SPECS
    ]


def format_exception(exc: Exception) -> str:
    return f"{exc}\n\n{traceback.format_exc()}"


def default_test_output(output_root: str) -> str:
    return str(_resolve_user_path(output_root, expect_directory=True) / "samples" / f"sample_{int(time.time())}.wav")


def dropdown_choices() -> list[tuple[str, str]]:
    return list_model_choices()
