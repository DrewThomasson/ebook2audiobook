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

import argparse
import os
import re
import json
from pathlib import Path

import gradio as gr

from utils.pipeline import (
    default_test_output,
    dropdown_choices,
    find_latest_artifacts,
    format_exception,
    load_artifacts,
    prepare_dataset,
    synthesize,
    train_model,
    pause_training,
    resume_training,
)

LANGUAGE_CHOICES = [
    "en",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "pl",
    "tr",
    "ru",
    "nl",
    "cs",
    "ar",
    "zh",
    "hu",
    "ko",
    "ja",
]
WHISPER_CHOICES = ["large-v3", "large-v2", "large", "medium", "small", "base"]
MODEL_CHOICES = [(label, key) for key, label in dropdown_choices()]


class PreprocessProgressTracker:
    def __init__(self, progress_bar: gr.Progress):
        self.progress_bar = progress_bar
        self.last_fraction = 0.0
        
    def __call__(self, message: str) -> None:
        if "complete" in message.lower() or "finished" in message.lower():
            self.last_fraction = 1.0
            self.progress_bar(1.0, desc=message)
            return
            
        match = re.search(r"Processing\s+(\d+)\s*/\s*(\d+)", message)
        if match:
            curr = int(match.group(1))
            total = int(match.group(2))
            self.last_fraction = 0.8 * (curr / total)
            self.progress_bar(self.last_fraction, desc=message)
            return
            
        match2 = re.search(r"Extracting voice blueprints:\s*(\d+)\s*/\s*(\d+)", message)
        if match2:
            curr = int(match2.group(1))
            total = int(match2.group(2))
            self.last_fraction = 0.8 + 0.15 * (curr / total)
            self.progress_bar(self.last_fraction, desc=message)
            return
            
        self.progress_bar(self.last_fraction, desc=message[:60] + "..." if len(message) > 60 else message)


class TrainingProgressTracker:
    def __init__(self, progress_bar: gr.Progress, total_epochs: int):
        self.progress_bar = progress_bar
        self.total_epochs = total_epochs
        self.current_epoch = 0
        self.start_epoch = None
        
    def __call__(self, log_line: str) -> None:
        if "complete" in log_line.lower() or "finished" in log_line.lower():
            self.progress_bar(1.0, desc=log_line.strip())
            return
            
        epoch_match = re.search(r"Epoch\s+(\d+)\s*/\s*(\d+)", log_line)
        if epoch_match:
            epoch_num = int(epoch_match.group(1))
            total_num = int(epoch_match.group(2))
            if self.start_epoch is None:
                self.start_epoch = epoch_num
            self.current_epoch = epoch_num
            self.total_epochs = max(total_num - self.start_epoch, 1)
            relative_epoch = self.current_epoch - self.start_epoch
        else:
            epoch_match2 = re.search(r"Epoch\s*:\s*(\d+)", log_line, re.IGNORECASE)
            if not epoch_match2:
                epoch_match2 = re.search(r"epoch\s*=\s*(\d+)", log_line, re.IGNORECASE)
            if epoch_match2:
                epoch_num = int(epoch_match2.group(1))
                if self.start_epoch is None:
                    self.start_epoch = epoch_num
                self.current_epoch = epoch_num
                relative_epoch = self.current_epoch - self.start_epoch
            else:
                relative_epoch = None
                
        if relative_epoch is not None and self.total_epochs > 0:
            fraction = min(max(relative_epoch / self.total_epochs, 0.0), 1.0)
            self.progress_bar(fraction, desc=f"Training: Epoch {self.current_epoch}/{self.total_epochs + (self.start_epoch or 0)}")
        else:
            clean = log_line.strip()
            if clean:
                desc = clean[:60] + "..." if len(clean) > 60 else clean
                if self.total_epochs > 0 and self.current_epoch > 0:
                    start = self.start_epoch or 0
                    rel = self.current_epoch - start
                    fraction = min(max(rel / self.total_epochs, 0.0), 1.0)
                else:
                    fraction = 0.0
                self.progress_bar(fraction, desc=desc)


def list_datasets(output_root: str | None) -> list[str]:
    if not output_root:
        return []
    try:
        base = Path(output_root) / "dataset"
        if not base.exists():
            return []
        paths = []
        for p in base.iterdir():
            if p.is_dir() and ((p / "metadata.csv").exists() or (p / "metadata_train.csv").exists()):
                paths.append(str(p.resolve()))
        return sorted(paths)
    except Exception:
        return []


def list_trained_models(output_root: str | None, model_key: str | None) -> list[tuple[str, str]]:
    if not output_root:
        return []
    try:
        base = Path(output_root) / "training_runs"
        if not base.exists():
            return []
        
        choices = []
        search_dirs = [base / model_key] if model_key else list(base.iterdir())
        
        for model_dir in search_dirs:
            if not model_dir.is_dir():
                continue
            for run_dir in model_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                artifacts_file = run_dir / "ready" / "artifacts.json"
                if artifacts_file.exists():
                    label = f"{model_dir.name} - {run_dir.name}"
                    choices.append((label, str(artifacts_file.resolve())))
        return sorted(choices, key=lambda x: x[0], reverse=True)
    except Exception:
        return []


def get_adaptive_defaults(model_key: str, dataset_dir: gr.Dropdown | str | None) -> tuple[int, int]:
    epochs = 10
    batch_size = 8
    
    resolved_dir = None
    if dataset_dir:
        val = getattr(dataset_dir, "value", dataset_dir)
        if isinstance(val, str) and val.strip():
            resolved_dir = val.strip()
            
    duration_seconds = 0.0
    if resolved_dir:
        try:
            info_file = Path(resolved_dir) / "dataset_info.json"
            if info_file.exists():
                info = json.loads(info_file.read_text(encoding="utf-8"))
                duration_seconds = float(info.get("total_audio_seconds", 0.0))
        except Exception:
            pass
            
    is_piper = "piper" in model_key.lower() if model_key else False
    
    if is_piper:
        if duration_seconds == 0:
            epochs = 100
            batch_size = 8
        elif duration_seconds < 120:
            epochs = 300
            batch_size = 8
        elif duration_seconds < 600:
            epochs = 150
            batch_size = 8
        else:
            epochs = 80
            batch_size = 16
    else:
        if duration_seconds == 0:
            epochs = 10
            batch_size = 8
        elif duration_seconds < 120:
            epochs = 12
            batch_size = 4
        elif duration_seconds < 600:
            epochs = 8
            batch_size = 4
        else:
            epochs = 5
            batch_size = 8
            
    return epochs, batch_size


def update_dataset_choices(out_root: str | None) -> gr.Dropdown:
    choices = list_datasets(out_root)
    return gr.update(choices=choices)


def update_trained_models(out_root: str | None, model_key: str | None) -> gr.Dropdown:
    choices = list_trained_models(out_root, model_key)
    val = choices[0][1] if choices else None
    return gr.update(choices=choices, value=val)


def update_resume_models(out_root: str | None, model_key: str | None) -> gr.Dropdown:
    choices = [("None", "")] + list_trained_models(out_root, model_key)
    return gr.update(choices=choices, value="")


def resolve_resume_checkpoint(artifacts_file_path: str) -> str:
    if not artifacts_file_path:
        return ""
    try:
        with open(artifacts_file_path, "r", encoding="utf-8") as f:
            artifacts = json.load(f)
        family = artifacts.get("family")
        training_root = Path(artifacts.get("training_root"))
        
        if family == "piper":
            # Search for .ckpt files in the training root (or preprocessed/lightning_logs)
            from utils.pipeline import _latest_matching_file
            ckpt = _latest_matching_file(training_root, ["**/*.ckpt", "*.ckpt"])
            if ckpt:
                return str(ckpt.resolve())
        else:
            # Search for best_model.pth or other .pth files in workspace
            from utils.pipeline import _latest_matching_file
            pth = _latest_matching_file(training_root / "workspace", ["**/best_model.pth", "**/*.pth"])
            if pth:
                return str(pth.resolve())
            # Fallback to ready checkpoint if workspace is cleaned up or empty
            ready_pth = Path(artifacts.get("checkpoint"))
            if ready_pth.exists():
                return str(ready_pth.resolve())
    except Exception as e:
        print(f"Error resolving resume checkpoint: {e}")
    return ""


def _path_value(value):
    return getattr(value, "name", value) if value else None


def _gradio_progress(progress: gr.Progress | None):
    if progress is None:
        return None

    def callback(message: str) -> None:
        progress(0, desc=message)

    return callback


def _clean_audio_path(path_val):
    if not path_val:
        return None
    try:
        p = Path(path_val)
        if p.exists() and p.is_file():
            return str(p.resolve())
    except Exception:
        pass
    return None


def preprocess_dataset(audio_files, audio_dir, transcript_file, language, whisper_model, out_path, dataset_name, diarize_speakers, expected_speakers=0, diarize_threshold=0.3, progress=gr.Progress()):
    try:
        tracker = PreprocessProgressTracker(progress)
        result = prepare_dataset(
            output_root=out_path,
            audio_files=audio_files,
            audio_dir=audio_dir or None,
            transcript_file=_path_value(transcript_file),
            language=language,
            whisper_model_name=whisper_model,
            dataset_name=dataset_name or "LJSpeech-1.1",
            diarize_speakers=diarize_speakers,
            expected_speakers=int(expected_speakers or 0),
            diarize_threshold=float(diarize_threshold or 0.3),
            progress=tracker,
        )
        
        speakers_list = result.get("all_speakers", [])
        speaker_choices = []
        
        if speakers_list:
            for s in speakers_list:
                dir_name = Path(s["dataset_dir"]).name
                label = f"{dir_name} (Duration: {s['total_audio_seconds']}s, Clips: {s['created_sample_count']})"
                speaker_choices.append((label, s["dataset_dir"]))
            
            message = f"Dataset split into {len(speakers_list)} speakers. Select speaker below to preview and activate."
            default_speaker_dir = speakers_list[0]["dataset_dir"]
            default_ref = speakers_list[0]["reference_wav"]
            default_info = f"**Dataset path**: `{default_speaker_dir}`\n**Duration**: {speakers_list[0]['total_audio_seconds']} seconds\n**Total clips**: {speakers_list[0]['created_sample_count']}"
        else:
            message = f"Dataset ready with {result['created_sample_count']} samples at {result['dataset_dir']}"
            default_speaker_dir = result["dataset_dir"]
            default_ref = result["reference_wav"]
            default_info = f"**Dataset path**: `{default_speaker_dir}`\n**Duration**: {result['total_audio_seconds']} seconds\n**Total clips**: {result['created_sample_count']}"
            
        choices = list_datasets(out_path)
        if default_speaker_dir not in choices:
            choices.append(default_speaker_dir)
            choices = sorted(choices)

        show_speakers = gr.update(visible=bool(speakers_list), choices=speaker_choices, value=default_speaker_dir if speakers_list else None)
        show_container = gr.update(visible=bool(speakers_list))
        
        return (
            message,
            default_speaker_dir,
            result["metadata_train"],
            result["metadata_val"],
            default_ref,
            gr.update(choices=choices, value=default_speaker_dir),
            default_ref,
            show_speakers,
            show_container,
            _clean_audio_path(default_ref),
            default_info,
            speakers_list,
        )
    except Exception as exc:
        return (
            format_exception(exc), "", "", "", "",
            gr.update(choices=list_datasets(out_path), value=None), "",
            gr.update(visible=False, choices=[]), gr.update(visible=False),
            None, "", []
        )


def preprocess_re_diarize(dataset_dir, expected_speakers, diarize_threshold, out_path, progress=gr.Progress()):
    try:
        if not dataset_dir:
            raise ValueError("No dataset directory selected. Please select a valid dataset directory.")
        tracker = PreprocessProgressTracker(progress)
        from utils.pipeline import re_diarize_dataset
        result = re_diarize_dataset(
            dataset_dir=dataset_dir,
            expected_speakers=int(expected_speakers or 0),
            diarize_threshold=float(diarize_threshold or 0.35),
            progress=tracker,
        )
        
        speakers_list = result.get("all_speakers", [])
        speaker_choices = []
        
        if speakers_list:
            for s in speakers_list:
                dir_name = Path(s["dataset_dir"]).name
                label = f"{dir_name} (Duration: {s['total_audio_seconds']}s, Clips: {s['created_sample_count']})"
                speaker_choices.append((label, s["dataset_dir"]))
            
            message = f"Dataset re-diarized into {len(speakers_list)} speakers. Select speaker below to preview and activate."
            default_speaker_dir = speakers_list[0]["dataset_dir"]
            default_ref = speakers_list[0]["reference_wav"]
            default_info = f"**Dataset path**: `{default_speaker_dir}`\n**Duration**: {speakers_list[0]['total_audio_seconds']} seconds\n**Total clips**: {speakers_list[0]['created_sample_count']}"
        else:
            message = f"Dataset ready with {result['created_sample_count']} samples at {result['dataset_dir']}"
            default_speaker_dir = result["dataset_dir"]
            default_ref = result["reference_wav"]
            default_info = f"**Dataset path**: `{default_speaker_dir}`\n**Duration**: {result['total_audio_seconds']} seconds\n**Total clips**: {result['created_sample_count']}"
            
        choices = list_datasets(out_path)
        if default_speaker_dir not in choices:
            choices.append(default_speaker_dir)
            choices = sorted(choices)

        show_speakers = gr.update(visible=bool(speakers_list), choices=speaker_choices, value=default_speaker_dir if speakers_list else None)
        show_container = gr.update(visible=bool(speakers_list))
        
        return (
            message,
            default_speaker_dir,
            result["metadata_train"],
            result["metadata_val"],
            default_ref,
            gr.update(choices=choices, value=default_speaker_dir),
            default_ref,
            show_speakers,
            show_container,
            _clean_audio_path(default_ref),
            default_info,
            speakers_list,
        )
    except Exception as exc:
        return (
            format_exception(exc), "", "", "", "",
            gr.update(choices=list_datasets(out_path), value=None), "",
            gr.update(visible=False, choices=[]), gr.update(visible=False),
            None, "", []
        )


def run_training(model_key, dataset_dir, language, num_epochs, batch_size, grad_accum, out_path, max_audio_length, restore_path, use_pretrained, extra_overrides_json, sample_epoch_interval=0, sample_text="", progress=gr.Progress()):
    try:
        tracker = TrainingProgressTracker(progress, int(num_epochs))
        result = train_model(
            model_key=model_key,
            output_root=out_path,
            dataset_dir=dataset_dir or None,
            language=language,
            epochs=int(num_epochs),
            batch_size=int(batch_size),
            grad_accum=int(grad_accum),
            max_audio_seconds=int(max_audio_length),
            restore_path=restore_path or None,
            use_pretrained=use_pretrained,
            extra_overrides_json=extra_overrides_json or None,
            progress=tracker,
            sample_epoch_interval=int(sample_epoch_interval),
            sample_text=sample_text,
        )
        message = f"Training finished. Ready artifacts saved in {Path(result['training_root']) / 'ready'}"
        
        updated_models = list_trained_models(out_path, model_key)
        new_val = updated_models[0][1] if updated_models else None
        
        return (
            message,
            result["training_root"],
            result["artifacts_file"],
            result["checkpoint"],
            result["config"],
            result.get("reference_wav", ""),
            result["artifacts_file"],
            result.get("reference_wav", ""),
            model_key,
            gr.update(choices=updated_models, value=new_val),
            gr.update(choices=[("None", "")] + updated_models, value=""),
        )
    except Exception as exc:
        return format_exception(exc), "", "", "", "", "", "", "", model_key, gr.update(), gr.update()


def locate_artifacts(out_path, model_key):
    try:
        artifacts = find_latest_artifacts(out_path, model_key=model_key or None)
        updated_models = list_trained_models(out_path, model_key)
        new_val = artifacts["artifacts_file"]
        return (
            f"Loaded latest artifacts for {artifacts['model_label']}",
            artifacts["training_root"],
            artifacts["artifacts_file"],
            artifacts["checkpoint"],
            artifacts["config"],
            artifacts.get("reference_wav", ""),
            artifacts["artifacts_file"],
            artifacts.get("reference_wav", ""),
            artifacts["model_key"],
            gr.update(choices=updated_models, value=new_val),
        )
    except Exception as exc:
        return format_exception(exc), "", "", "", "", "", "", "", model_key, gr.update()


def inspect_artifacts(artifacts_path, model_key):
    try:
        artifacts = load_artifacts(artifacts_path, model_key=model_key or None)
        return (
            f"Artifacts loaded for {artifacts['model_label']}",
            artifacts["training_root"],
            artifacts["artifacts_file"],
            artifacts["checkpoint"],
            artifacts["config"],
            artifacts.get("reference_wav", ""),
            artifacts.get("reference_wav", ""),
        )
    except Exception as exc:
        return format_exception(exc), "", "", "", "", "", ""


def run_inference(artifacts_path, model_key, language, tts_text, speaker_audio_file, out_path, progress=gr.Progress()):
    try:
        result = synthesize(
            artifacts_path_or_dir=artifacts_path,
            model_key=model_key or None,
            text=tts_text,
            language=language,
            speaker_wav=speaker_audio_file or None,
            output_file=default_test_output(out_path),
            progress=_gradio_progress(progress),
        )
        return "Speech generated.", _clean_audio_path(result["output_file"]), _clean_audio_path(result.get("speaker_wav"))
    except ValueError as exc:
        # Display validation/user errors cleanly in the GUI status
        return f"Error: {exc}", None, None
    except Exception as exc:
        return format_exception(exc), None, None


def on_model_change(selected_model):
    try:
        from utils.model_registry import get_model_spec
        spec = get_model_spec(selected_model)
        req = spec.requires_speaker_wav
    except Exception:
        req = False
    return gr.update(visible=req), gr.update(visible=req)


def on_select_speaker(selected_dir, speakers_state):
    if not selected_dir or not speakers_state:
        return gr.update(), "", "", "", gr.update()
    
    speaker_info = next((s for s in speakers_state if s["dataset_dir"] == selected_dir), None)
    if not speaker_info:
        return gr.update(), "", "", "", gr.update()
        
    info_md = f"**Dataset path**: `{selected_dir}`\n**Duration**: {speaker_info['total_audio_seconds']} seconds\n**Total clips**: {speaker_info['created_sample_count']}"
    ref_wav = speaker_info["reference_wav"]
    
    return selected_dir, ref_wav, _clean_audio_path(ref_wav), info_md, gr.update(value=selected_dir)


def select_trained_model(val):
    return val


def on_training_params_change(model_key, dataset_dir):
    epochs, batch_size = get_adaptive_defaults(model_key, dataset_dir)
    return epochs, batch_size


def update_training_options(model_key, language, use_pretrained):
    try:
        from utils.model_registry import get_model_spec
        spec = get_model_spec(model_key)
        model_label = spec.label
        official_model_id = spec.official_model_id
        family = spec.family
    except Exception as exc:
        return f"Error loading model spec: {exc}", gr.update()

    # 1. XTTS family
    if family == "xtts":
        msg = f"🟢 **{model_label}** is a multilingual model supporting all listed languages.\n\n"
        if use_pretrained:
            msg += f"Fine-tuning will start from the official pre-trained multilingual checkpoint: `{official_model_id}`."
        else:
            msg += "**Training from scratch** (random initialization). *Note: training a large GPT model like XTTS from scratch requires massive amounts of data and compute. Fine-tuning is highly recommended.*"
        return msg, gr.update(interactive=True)

    # 2. Piper family
    elif family == "piper":
        from utils.piper_utils import resolve_piper_checkpoint
        try:
            checkpoint_info = resolve_piper_checkpoint(language)
            resolved_lang = checkpoint_info.get("lang")
            normalized_req_lang = language.split("-")[0].split("_")[0].lower()

            if resolved_lang == normalized_req_lang:
                msg = f"🟢 **Piper TTS** has a pre-trained checkpoint for `{language}`: `{checkpoint_info['voice']}` ({checkpoint_info['quality']}).\n\n"
                if use_pretrained:
                    msg += f"Fine-tuning will download and use the official `{language}` pre-trained checkpoint."
                else:
                    msg += "**Training from scratch** (random initialization). *Note: Training from scratch is not recommended unless you have a very large dataset and plan to train for many steps.*"
                return msg, gr.update(interactive=True)
            else:
                msg = f"🟡 **Piper TTS** has no official pre-trained checkpoint mapped for `{language}`.\n\n"
                if use_pretrained:
                    msg += f"Fine-tuning will default to using the English base model (`{checkpoint_info['voice']}`) as a starting point (cross-lingual transfer)."
                else:
                    msg += "**Training from scratch** (random initialization). *Note: Training from scratch is not recommended unless you have a very large dataset and plan to train for many steps.*"
                return msg, gr.update(interactive=True)
        except Exception as e:
            msg = f"🟡 **Piper TTS** pre-trained checkpoint check failed: {e}. Defaulting to training from scratch or cross-lingual transfer."
            return msg, gr.update(interactive=True)

    # 3. Single-language models
    else:
        if language == "en":
            if official_model_id:
                msg = f"🟢 **{model_label}** has a pre-trained English checkpoint mapped: `{official_model_id}`.\n\n"
                if use_pretrained:
                    msg += "Fine-tuning will download and use this pre-trained base model."
                else:
                    msg += "**Training from scratch** (random initialization). This means the model weights start completely blank."
                return msg, gr.update(interactive=True)
            else:
                msg = f"🟡 **{model_label}** has no official pre-trained checkpoint mapped.\n\n"
                msg += "**Training from scratch** (random initialization) is required. *Training from scratch means the model starts with random weights and requires a larger dataset (hours of audio) and longer training (e.g. 100k+ steps) to sound intelligible.*"
                return msg, gr.update(value=False, interactive=False)
        else:
            msg = f"❌ **{model_label}** is a single-language model designed for English. There is no pre-trained checkpoint mapped for `{language}`.\n\n"
            msg += "**Training from scratch** (random initialization) is required. *Training from scratch means the model starts with random weights and requires a larger dataset (hours of audio) and longer training (e.g. 100k+ steps) to sound intelligible.*\n\n"
            msg += f"✨ **Automatic Recipe Optimization**: The backend will dynamically adapt the recipe at runtime to use `\"multilingual_cleaners\"` and the `{language}` phonemizer, ensuring it compiles and trains successfully on your dataset."
            return msg, gr.update(value=False, interactive=False)


def preprocess_and_train(
    audio_files, audio_dir, transcript_file, language, whisper_model, out_path, dataset_name, diarize_speakers,
    expected_speakers, diarize_threshold,
    model_key, train_language, num_epochs, batch_size, grad_accum, max_audio_length, restore_path, use_pretrained, extra_overrides_json,
    sample_epoch_interval, sample_text,
    tts_text,
    progress=gr.Progress()
):
    try:
        progress(0, desc="Starting step 1: Preprocessing dataset...")
        preprocess_res = preprocess_dataset(
            audio_files, audio_dir, transcript_file, language, whisper_model, out_path, dataset_name, diarize_speakers,
            expected_speakers, diarize_threshold, progress
        )
        status_msg, dataset_dir = preprocess_res[0], preprocess_res[1]
        if not dataset_dir or "failed" in status_msg.lower():
            train_status_msg = f"Training skipped because dataset preparation failed: {status_msg}"
            empty_train = (train_status_msg, "", "", "", "", "", "", "", model_key, gr.update(), gr.update())
            empty_infer = (f"Inference skipped: Preprocessing failed.", None, None)
            return empty_train + preprocess_res + empty_infer
            
        progress(0.4, desc="Preprocessing complete! Starting step 2: Training model...")
        
        train_res = run_training(
            model_key, dataset_dir, train_language, num_epochs, batch_size, grad_accum, out_path, max_audio_length, restore_path, use_pretrained, extra_overrides_json,
            sample_epoch_interval, sample_text,
            progress
        )
        artifacts_file_val = train_res[2]
        speaker_ref_val = train_res[7]
        
        if not artifacts_file_val or "failed" in train_res[0].lower():
            train_status_msg = f"Inference skipped because training failed: {train_res[0]}"
            empty_infer = (train_status_msg, None, None)
            return train_res + preprocess_res + empty_infer
            
        progress(0.9, desc="Training complete! Starting step 3: Generating test speech...")
        
        infer_res = run_inference(
            artifacts_file_val, model_key, train_language, tts_text, speaker_ref_val, out_path, progress
        )
        return train_res + preprocess_res + infer_res
    except Exception as exc:
        err = format_exception(exc)
        empty_train = (f"Pipeline error: {err}", "", "", "", "", "", "", "", model_key, gr.update(), gr.update())
        empty_prep = (err, "", "", "", "", gr.update(choices=list_datasets(out_path), value=None), "", gr.update(visible=False, choices=[]), gr.update(visible=False), None, "", [])
        empty_infer = (f"Pipeline error: {err}", None, None)
        return empty_train + empty_prep + empty_infer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Coqui TTS fine-tuning web UI")
    parser.add_argument("--share", action="store_true", default=False)
    parser.add_argument("--port", type=int, default=5003)
    parser.add_argument("--out_path", type=str, default=str(Path.cwd() / "finetune_models"))
    parser.add_argument("--num_epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--grad_acumm", type=int, default=1)
    parser.add_argument("--max_audio_length", type=int, default=11)
    args = parser.parse_args()

    theme = gr.themes.Origin(
        primary_hue="green",
        secondary_hue="amber",
        neutral_hue="gray",
        radius_size="lg",
        font_mono=["JetBrains Mono", "monospace", "Consolas", "Menlo", "Liberation Mono"],
    )

    css_str = """
    .primary-btn {
        background: linear-gradient(90deg, #22c55e 0%, #eab308 100%) !important;
        color: white !important;
        border: none !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .primary-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4) !important;
    }
    .primary-btn:active {
        transform: translateY(0);
    }
    """

    with gr.Blocks(title="Universal TTS Finetune", theme=theme, css=css_str) as demo:
        gr.Markdown(
            "# Universal TTS Finetune\n"
            "Prepare an LJSpeech-style dataset, fine-tune a supported Coqui recipe, and test the trained model."
        )

        with gr.Tab("1 - Prepare dataset"):
            out_path = gr.Textbox(label="Output root", value=args.out_path)
            dataset_name = gr.Textbox(label="Dataset name", value="dataset_1")
            audio_upload = gr.File(
                file_count="multiple",
                label="Audio files (wav, mp3, flac, m4a, ogg)",
            )
            audio_dir = gr.Textbox(label="Audio folder path (optional)", value="")
            transcript_file = gr.File(label="Optional transcript map (csv, tsv, pipe-delimited txt, or json)")
            language = gr.Dropdown(label="Dataset language", choices=LANGUAGE_CHOICES, value="en")
            whisper_model = gr.Dropdown(label="Whisper model", choices=WHISPER_CHOICES, value="small")
            diarize_speakers = gr.Checkbox(label="Diarize speakers (split multi-speaker audio)", value=False)
            with gr.Row(visible=False) as diarize_options:
                expected_speakers = gr.Slider(label="Expected speaker count (0 for auto)", minimum=0, maximum=20, step=1, value=0)
                diarize_threshold = gr.Slider(label="Diarization threshold (distance, only if auto)", minimum=0.05, maximum=1.0, step=0.05, value=0.35)
            
            # Speaker preview group (initially hidden)
            speakers_state = gr.State([])
            with gr.Group(visible=False) as speakers_container:
                gr.Markdown("### Detected Speakers Preview")
                speaker_selector = gr.Dropdown(label="Select Speaker", choices=[])
                speaker_preview_audio = gr.Audio(label="Speaker Sample Audio", interactive=False)
                speaker_details = gr.Markdown("")
            
            dataset_status = gr.Textbox(label="Status", interactive=False)
            dataset_dir = gr.Textbox(label="Dataset directory")
            train_csv = gr.Textbox(label="Train metadata")
            val_csv = gr.Textbox(label="Validation metadata")
            dataset_reference = gr.Textbox(label="Reference WAV")
            with gr.Row():
                prepare_btn = gr.Button(value="Step 1 - Create dataset", elem_classes=["primary-btn"])
                prepare_and_train_btn = gr.Button(value="Create dataset & Start training", variant="secondary")
            
            with gr.Accordion("Re-diarize an Existing Dataset", open=False):
                gr.Markdown("Select a previously created dataset (mixed or diarized) and re-run speaker diarization using updated settings without re-transcribing.")
                re_diarize_source = gr.Dropdown(
                    label="Select dataset to re-diarize",
                    choices=list_datasets(args.out_path),
                    value=None,
                    allow_custom_value=True,
                    interactive=True,
                )
                with gr.Row():
                    re_diarize_expected = gr.Slider(label="Expected speaker count (0 for auto)", minimum=0, maximum=20, step=1, value=0)
                    re_diarize_thresh = gr.Slider(label="Diarization threshold (distance, only if auto)", minimum=0.05, maximum=1.0, step=0.05, value=0.35)
                re_diarize_btn = gr.Button(value="Re-diarize Dataset", variant="secondary")

        with gr.Tab("2 - Train model"):
            model_key = gr.Dropdown(label="Model", choices=MODEL_CHOICES, value="xtts_v2")
            model_checkpoint_warning = gr.Markdown(
                value="🟢 **XTTS v2** is a multilingual model supporting all listed languages.\n\nFine-tuning will start from the official pre-trained multilingual checkpoint: `tts_models/multilingual/multi-dataset/xtts_v2`."
            )
            train_dataset_dir = gr.Dropdown(
                label="Dataset directory",
                choices=list_datasets(args.out_path),
                value=None,
                allow_custom_value=True,
                interactive=True,
            )
            train_language = gr.Dropdown(label="Model language (XTTS/Piper support multilingual)", choices=LANGUAGE_CHOICES, value="en")
            with gr.Row():
                restore_model_dropdown = gr.Dropdown(
                    label="Resume from previous training run",
                    choices=[("None", "")] + list_trained_models(args.out_path, "xtts_v2"),
                    value=None,
                    interactive=True,
                )
                restore_path = gr.Textbox(label="Optional checkpoint to continue from", value="")
            use_pretrained = gr.Checkbox(label="Auto-download matching pretrained model when available", value=True)
            num_epochs = gr.Slider(label="Epochs", minimum=1, maximum=1000, step=1, value=args.num_epochs)
            batch_size = gr.Slider(label="Batch size", minimum=1, maximum=128, step=1, value=args.batch_size)
            grad_accum = gr.Slider(label="Grad accumulation", minimum=1, maximum=128, step=1, value=args.grad_acumm)
            max_audio_length = gr.Slider(label="Max audio length (seconds)", minimum=2, maximum=30, step=1, value=args.max_audio_length)
            extra_overrides_json = gr.Code(
                label="Optional config overrides JSON",
                language="json",
                value="{}",
            )
            with gr.Accordion("Periodic Progress Audio Sampling (Piper Only)", open=False):
                sample_epoch_interval = gr.Slider(
                    label="Sample Interval (Epochs)",
                    minimum=0,
                    maximum=500,
                    step=10,
                    value=0,
                    info="Generate and save an audio sample every N epochs. Set to 0 to disable."
                )
                sample_text = gr.Textbox(
                    label="Sample Test Phrase",
                    value="This is a periodic audio sample to test training progress.",
                    info="Text sentence to synthesize at each interval."
                )
            train_status = gr.Textbox(label="Status", interactive=False)
            training_root = gr.Textbox(label="Training root")
            artifacts_file = gr.Textbox(label="Artifacts file")
            checkpoint_path = gr.Textbox(label="Checkpoint path")
            config_path = gr.Textbox(label="Config path")
            trained_reference = gr.Textbox(label="Reference WAV")
            with gr.Row():
                train_btn = gr.Button(value="Step 2 - Train model", elem_classes=["primary-btn"])
                pause_btn = gr.Button(value="Pause Training", variant="secondary")
                resume_btn = gr.Button(value="Resume Training", variant="secondary")
            latest_btn = gr.Button(value="Load latest trained model")

        with gr.Tab("3 - Inference"):
            infer_model_key = gr.Dropdown(label="Model", choices=MODEL_CHOICES, value="xtts_v2")
            infer_trained_model = gr.Dropdown(
                label="Select previously fine-tuned model",
                choices=list_trained_models(args.out_path, "xtts_v2"),
                value=None,
                interactive=True,
            )
            infer_artifacts = gr.Textbox(label="Artifacts file or ready/training folder", value="")
            speaker_reference_audio = gr.Textbox(label="Speaker reference WAV (Required for XTTS)", value="")
            infer_language = gr.Dropdown(label="Inference language", choices=LANGUAGE_CHOICES, value="en")
            tts_text = gr.Textbox(label="Input text", value="This fine-tuned model is ready to test.")
            infer_status = gr.Textbox(label="Status", interactive=False)
            generated_audio = gr.Audio(label="Generated audio")
            used_reference_audio = gr.Audio(label="Reference audio used")
            inspect_btn = gr.Button(value="Inspect artifacts")
            tts_btn = gr.Button(value="Step 3 - Generate speech", elem_classes=["primary-btn"])

        prepare_btn.click(
            fn=preprocess_dataset,
            inputs=[
                audio_upload,
                audio_dir,
                transcript_file,
                language,
                whisper_model,
                out_path,
                dataset_name,
                diarize_speakers,
                expected_speakers,
                diarize_threshold,
            ],
            outputs=[
                dataset_status,
                dataset_dir,
                train_csv,
                val_csv,
                dataset_reference,
                train_dataset_dir,
                speaker_reference_audio,
                speaker_selector,
                speakers_container,
                speaker_preview_audio,
                speaker_details,
                speakers_state,
            ],
        )

        re_diarize_btn.click(
            fn=preprocess_re_diarize,
            inputs=[
                re_diarize_source,
                re_diarize_expected,
                re_diarize_thresh,
                out_path,
            ],
            outputs=[
                dataset_status,
                dataset_dir,
                train_csv,
                val_csv,
                dataset_reference,
                train_dataset_dir,
                speaker_reference_audio,
                speaker_selector,
                speakers_container,
                speaker_preview_audio,
                speaker_details,
                speakers_state,
            ],
        )

        re_diarize_source.focus(
            fn=lambda op: gr.update(choices=list_datasets(op)),
            inputs=[out_path],
            outputs=[re_diarize_source],
        )

        prepare_and_train_btn.click(
            fn=preprocess_and_train,
            inputs=[
                # Preprocessing inputs
                audio_upload,
                audio_dir,
                transcript_file,
                language,
                whisper_model,
                out_path,
                dataset_name,
                diarize_speakers,
                expected_speakers,
                diarize_threshold,
                # Training inputs
                model_key,
                train_language,
                num_epochs,
                batch_size,
                grad_accum,
                max_audio_length,
                restore_path,
                use_pretrained,
                extra_overrides_json,
                sample_epoch_interval,
                sample_text,
                # Inference input
                tts_text,
            ],
            outputs=[
                # Training outputs (11 items)
                train_status,
                training_root,
                artifacts_file,
                checkpoint_path,
                config_path,
                trained_reference,
                infer_artifacts,
                speaker_reference_audio,
                infer_model_key,
                infer_trained_model,
                restore_model_dropdown,
                # Preprocessing outputs (12 items)
                dataset_status,
                dataset_dir,
                train_csv,
                val_csv,
                dataset_reference,
                train_dataset_dir,
                speaker_reference_audio,
                speaker_selector,
                speakers_container,
                speaker_preview_audio,
                speaker_details,
                speakers_state,
                # Inference outputs (3 items)
                infer_status,
                generated_audio,
                used_reference_audio,
            ],
        )

        speaker_selector.change(
            fn=on_select_speaker,
            inputs=[speaker_selector, speakers_state],
            outputs=[
                dataset_dir,
                dataset_reference,
                speaker_preview_audio,
                speaker_details,
                train_dataset_dir,
            ],
        )

        train_btn.click(
            fn=run_training,
            inputs=[
                model_key,
                train_dataset_dir,
                train_language,
                num_epochs,
                batch_size,
                grad_accum,
                out_path,
                max_audio_length,
                restore_path,
                use_pretrained,
                extra_overrides_json,
                sample_epoch_interval,
                sample_text,
            ],
            outputs=[
                train_status,
                training_root,
                artifacts_file,
                checkpoint_path,
                config_path,
                trained_reference,
                infer_artifacts,
                speaker_reference_audio,
                infer_model_key,
                infer_trained_model,
                restore_model_dropdown,
            ],
        )

        latest_btn.click(
            fn=locate_artifacts,
            inputs=[out_path, model_key],
            outputs=[
                train_status,
                training_root,
                artifacts_file,
                checkpoint_path,
                config_path,
                trained_reference,
                infer_artifacts,
                speaker_reference_audio,
                infer_model_key,
                infer_trained_model,
            ],
        )

        inspect_btn.click(
            fn=inspect_artifacts,
            inputs=[infer_artifacts, infer_model_key],
            outputs=[
                infer_status,
                training_root,
                artifacts_file,
                checkpoint_path,
                config_path,
                trained_reference,
                speaker_reference_audio,
            ],
        )

        tts_btn.click(
            fn=run_inference,
            inputs=[
                infer_artifacts,
                infer_model_key,
                infer_language,
                tts_text,
                speaker_reference_audio,
                out_path,
            ],
            outputs=[infer_status, generated_audio, used_reference_audio],
        )

        def toggle_diarize_options(visible):
            return gr.update(visible=visible)

        diarize_speakers.change(
            fn=toggle_diarize_options,
            inputs=[diarize_speakers],
            outputs=[diarize_options],
        )

        model_key.change(
            fn=on_model_change,
            inputs=[model_key],
            outputs=[speaker_reference_audio, used_reference_audio],
        )
        model_key.change(
            fn=on_training_params_change,
            inputs=[model_key, train_dataset_dir],
            outputs=[num_epochs, batch_size],
        )
        model_key.change(
            fn=update_training_options,
            inputs=[model_key, train_language, use_pretrained],
            outputs=[model_checkpoint_warning, use_pretrained],
        )
        train_language.change(
            fn=update_training_options,
            inputs=[model_key, train_language, use_pretrained],
            outputs=[model_checkpoint_warning, use_pretrained],
        )
        use_pretrained.change(
            fn=lambda m, l, u: update_training_options(m, l, u)[0],
            inputs=[model_key, train_language, use_pretrained],
            outputs=[model_checkpoint_warning],
        )

        train_dataset_dir.change(
            fn=on_training_params_change,
            inputs=[model_key, train_dataset_dir],
            outputs=[num_epochs, batch_size],
        )

        infer_model_key.change(
            fn=on_model_change,
            inputs=[infer_model_key],
            outputs=[speaker_reference_audio, used_reference_audio],
        )
        infer_model_key.change(
            fn=update_trained_models,
            inputs=[out_path, infer_model_key],
            outputs=[infer_trained_model],
        )

        infer_trained_model.change(
            fn=select_trained_model,
            inputs=[infer_trained_model],
            outputs=[infer_artifacts],
        )

        out_path.change(
            fn=update_dataset_choices,
            inputs=[out_path],
            outputs=[train_dataset_dir],
        )
        out_path.change(
            fn=update_trained_models,
            inputs=[out_path, infer_model_key],
            outputs=[infer_trained_model],
        )

        def on_restore_dropdown_change(artifacts_path):
            if not artifacts_path:
                return ""
            return resolve_resume_checkpoint(artifacts_path)

        restore_model_dropdown.change(
            fn=on_restore_dropdown_change,
            inputs=[restore_model_dropdown],
            outputs=[restore_path],
        )

        model_key.change(
            fn=update_resume_models,
            inputs=[out_path, model_key],
            outputs=[restore_model_dropdown],
        )

        out_path.change(
            fn=update_resume_models,
            inputs=[out_path, model_key],
            outputs=[restore_model_dropdown],
        )

        pause_btn.click(
            fn=pause_training,
            inputs=[],
            outputs=[train_status],
        )

        resume_btn.click(
            fn=resume_training,
            inputs=[],
            outputs=[train_status],
        )

        demo.load(
            fn=update_training_options,
            inputs=[model_key, train_language, use_pretrained],
            outputs=[model_checkpoint_warning, use_pretrained],
        )

    demo.launch(share=args.share, debug=False, server_port=args.port)
