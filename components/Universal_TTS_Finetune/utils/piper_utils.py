from __future__ import annotations

import os
import sys
import shutil
import urllib.request
import json
import subprocess
from pathlib import Path
from functools import lru_cache
import torch

from utils.model_paths import get_models_dir
_MODELS_DIR = get_models_dir()
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

def ensure_monotonic_align_compiled():
    """Auto-compiles the monotonic_align Cython extension for Piper training if not already compiled."""
    base_dir = Path(__file__).resolve().parent.parent / "piper" / "piper_train" / "vits" / "monotonic_align"
    target_dir = base_dir / "monotonic_align"
    target_dir.mkdir(exist_ok=True)
    
    # Check if compiled file exists in target_dir
    existing = list(target_dir.glob("core*.so")) + list(target_dir.glob("core*.pyd"))
    if existing:
        return
        
    print("Compiling monotonic_align Cython extension...")
    try:
        # Run setup.py in-place
        subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            cwd=str(base_dir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Move built extension files into the target monotonic_align/ directory
        built_files = list(base_dir.glob("core*.so")) + list(base_dir.glob("core*.pyd")) + list(base_dir.glob("core*.dylib"))
        for f in built_files:
            dest_file = target_dir / f.name
            if dest_file.exists():
                dest_file.unlink()
            shutil.move(str(f), str(target_dir / f.name))
        print("monotonic_align compiled successfully.")
    except Exception as e:
        print(f"Warning: Failed to compile monotonic_align Cython extension: {e}. Training might be slow or fail.")

def get_voices_json_languages() -> set[str]:
    """Retrieves all language codes and families supported by pre-built Piper models in voices.json."""
    paths = [
        _PROJECT_ROOT / "voices.json",
        _PROJECT_ROOT / "piper" / "piper" / "voices.json"
    ]
    langs = set()
    for path in paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for voice in data.values():
                        lang_info = voice.get("language", {})
                        if "code" in lang_info:
                            code = lang_info["code"].lower()
                            langs.add(code)
                            langs.add(code.replace("_", "-"))
                        if "family" in lang_info:
                            langs.add(lang_info["family"].lower())
            except Exception:
                pass
    return langs

# Used when Hugging Face cannot be reached. These entries are training
# checkpoints, not the ready-to-synthesize ONNX voices in voices.json.
_STATIC_CHECKPOINTS = {
    "en": ("en_US", "lessac", "medium", "epoch=2164-step=1355540.ckpt"),
    "es": ("es_ES", "davefx", "medium", "epoch=5629-step=1605020.ckpt"),
    "de": ("de_DE", "thorsten", "medium", "epoch=3135-step=2702056.ckpt"),
    "fr": ("fr_FR", "siwis", "medium", "epoch=3304-step=2050940.ckpt"),
}


def _piper_checkpoint_info(lang: str, locale: str, voice: str, quality: str, ckpt: str) -> dict[str, str]:
    return {
        "id": f"piper:{lang}/{locale}/{voice}/{quality}",
        "lang": lang,
        "locale": locale,
        "voice": voice,
        "quality": quality,
        "ckpt": ckpt,
        "config": "config.json",
    }


@lru_cache(maxsize=64)
def list_piper_checkpoint_choices(language: str) -> tuple[dict[str, str], ...]:
    """List actual training checkpoints for one language without downloading weights."""
    lang = language.split("-")[0].split("_")[0].lower()
    url = f"https://huggingface.co/api/datasets/rhasspy/piper-checkpoints/tree/main/{lang}?recursive=true"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            files = json.load(response)
        paths = {item["path"] for item in files if item.get("type") == "file"}
        choices_by_id = {}
        for path in sorted(paths):
            parts = path.split("/")
            if len(parts) != 5 or not path.endswith(".ckpt"):
                continue
            _, locale, voice, quality, ckpt = parts
            if f"{lang}/{locale}/{voice}/{quality}/config.json" in paths:
                info = _piper_checkpoint_info(lang, locale, voice, quality, ckpt)
                choices_by_id[info["id"]] = info
        if choices_by_id:
            return tuple(choices_by_id.values())
    except Exception as exc:
        print(f"Piper checkpoint catalog unavailable for {lang}: {exc}")
    if lang in _STATIC_CHECKPOINTS:
        return (_piper_checkpoint_info(lang, *_STATIC_CHECKPOINTS[lang]),)
    return ()


def resolve_piper_checkpoint(language: str, quality: str = "medium", checkpoint_id: str | None = None) -> dict[str, str]:
    """Resolve an exact Piper training checkpoint in the selected language."""
    lang = language.split("-")[0].split("_")[0].lower()
    choices = list_piper_checkpoint_choices(language)
    if checkpoint_id:
        for choice in choices:
            if choice["id"] == checkpoint_id:
                return choice
        raise ValueError(f"{checkpoint_id} is not an available {lang} Piper training checkpoint.")
    if not choices:
        raise LookupError(f"No Piper training checkpoint is available for {lang}.")
    preferred_voice = _STATIC_CHECKPOINTS.get(lang, ("",))[1] if lang in _STATIC_CHECKPOINTS else None
    for choice in choices:
        if choice["quality"] == quality and choice["voice"] == preferred_voice:
            return choice
    for choice in choices:
        if choice["quality"] == quality:
            return choice
    return choices[0]

def download_piper_checkpoint(checkpoint_info: dict[str, str], progress_callback=None) -> tuple[Path, Path]:
    """Downloads checkpoint ckpt and config files locally into models/piper/checkpoints/."""
    lang = checkpoint_info["lang"]
    locale = checkpoint_info["locale"]
    voice = checkpoint_info["voice"]
    quality = checkpoint_info["quality"]
    ckpt_filename = checkpoint_info["ckpt"]
    config_filename = checkpoint_info["config"]
    
    base_url = f"https://huggingface.co/datasets/rhasspy/piper-checkpoints/resolve/main/{lang}/{locale}/{voice}/{quality}"
    
    local_dir = _MODELS_DIR / "piper" / "checkpoints" / lang / locale / voice / quality
    local_dir.mkdir(parents=True, exist_ok=True)
    
    ckpt_path = local_dir / ckpt_filename
    config_path = local_dir / config_filename
    
    def _download(url: str, dest: Path, label: str):
        if dest.exists() and dest.stat().st_size > 1000000:
            return
        if progress_callback:
            progress_callback(f"Downloading {label}...")
        print(f"Downloading {url} to {dest}...")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            block_size = 1024 * 1024
            downloaded = 0
            with open(dest, "wb") as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    f.write(block)
                    downloaded += len(block)
                    if total_size > 0 and progress_callback:
                        percent = int(downloaded * 100 / total_size)
                        progress_callback(f"Downloading {label}: {percent}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
                        
    _download(f"{base_url}/{config_filename}", config_path, f"{voice} config")
    _download(f"{base_url}/{ckpt_filename}", ckpt_path, f"{voice} checkpoint")
    
    return ckpt_path, config_path

def normalize_espeak_language(language_code: str) -> str:
    """Verifies and normalizes the language code for piper_phonemize.
    If the language code raises an error when phonemizing, it falls back to the base language code (e.g. en-gb -> en).
    """
    try:
        import piper_phonemize
        # Try phonemizing a dummy word to see if voice sets up successfully
        piper_phonemize.phonemize_espeak("test", language_code)
        return language_code
    except Exception as e:
        print(f"eSpeak voice setup failed for '{language_code}': {e}")
        # Try finding a base language code
        if "-" in language_code:
            base_code = language_code.split("-")[0]
            try:
                import piper_phonemize
                piper_phonemize.phonemize_espeak("test", base_code)
                print(f"Fell back to base voice: '{base_code}'")
                return base_code
            except Exception as e_base:
                print(f"eSpeak voice setup also failed for base voice '{base_code}': {e_base}")
        elif "_" in language_code:
            base_code = language_code.split("_")[0]
            try:
                import piper_phonemize
                piper_phonemize.phonemize_espeak("test", base_code)
                print(f"Fell back to base voice: '{base_code}'")
                return base_code
            except Exception as e_base:
                print(f"eSpeak voice setup also failed for base voice '{base_code}': {e_base}")

        # If base fails, or there is no delimiter, we can fall back to 'en'
        print("Falling back to default 'en' voice.")
        return "en"

def preprocess_piper_dataset(dataset_dir: Path, output_dir: Path, language_code: str, sample_rate: int):
    """Executes piper_train.preprocess as a python subprocess to prepare the LJSpeech dataset."""
    # Normalize language code to prevent eSpeak voice setup failures
    normalized_lang = normalize_espeak_language(language_code)
    
    piper_python_src = Path(__file__).resolve().parent.parent / "piper"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(piper_python_src) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    
    cmd = [
        sys.executable,
        "-m", "piper_train.preprocess",
        "--language", normalized_lang,
        "--input-dir", str(dataset_dir),
        "--output-dir", str(output_dir),
        "--dataset-format", "ljspeech",
        "--single-speaker",
        "--sample-rate", str(sample_rate)
    ]
    print(f"Running Piper preprocessing: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)

def _check_and_generate_piper_sample(
    preprocessed_dir: Path,
    sample_epoch_interval: int,
    sample_text: str,
    config_path: Path,
    output_dir: Path,
    generated_epochs: set[int],
    progress_callback=None
):
    import re
    # Check for any .ckpt file under preprocessed_dir or its lightning_logs subdirectories
    ckpt_files = list(preprocessed_dir.glob("epoch=*-step=*.ckpt"))
    ckpt_files.extend(list((preprocessed_dir / "lightning_logs").glob("**/*.ckpt")))
    
    for ckpt in ckpt_files:
        if not ckpt.exists():
            continue
        # Parse the epoch index (e.g. epoch=99-step=1200.ckpt)
        match = re.search(r"epoch=(\d+)-step=", ckpt.name)
        if match:
            epoch_idx = int(match.group(1))
            epoch_num = epoch_idx + 1 # Convert to 1-based epoch number
            if epoch_num % sample_epoch_interval == 0 and epoch_num not in generated_epochs:
                # Double check existence to avoid race condition
                if not ckpt.exists():
                    continue
                generated_epochs.add(epoch_num)
                temp_ckpt = None
                try:
                    samples_dir = output_dir / "epoch_samples"
                    samples_dir.mkdir(parents=True, exist_ok=True)
                    temp_ckpt = samples_dir / f"epoch_{epoch_num}_temp.ckpt"
                    temp_onnx = samples_dir / f"epoch_{epoch_num}_temp.onnx"
                    temp_config = samples_dir / f"epoch_{epoch_num}_temp.onnx.json"
                    
                    # Notify
                    msg = f"\n>>> [Periodic Audio Sample] Copying checkpoint for Epoch {epoch_num} to prevent race conditions... <<<\n"
                    print(msg)
                    sys.stdout.flush()
                    if progress_callback:
                        progress_callback(msg)
                        
                    # Copy checkpoint file to temporary path immediately
                    shutil.copy2(ckpt, temp_ckpt)
                    
                    msg = f">>> Exporting checkpoint for Epoch {epoch_num} to ONNX... <<<\n"
                    print(msg)
                    sys.stdout.flush()
                    if progress_callback:
                        progress_callback(msg)
                        
                    # Export to ONNX using our copied file
                    export_piper_onnx(temp_ckpt, temp_onnx, config_path)
                    
                    # Synthesize
                    out_wav = samples_dir / f"epoch_{epoch_num}.wav"
                    msg = f">>> Synthesizing audio sample for Epoch {epoch_num}... <<<\n"
                    print(msg)
                    sys.stdout.flush()
                    if progress_callback:
                        progress_callback(msg)
                        
                    synthesize_piper(str(temp_onnx), str(temp_config), sample_text, str(out_wav))
                    
                    # Clean up temp files
                    if temp_onnx.exists():
                        temp_onnx.unlink()
                    if temp_config.exists():
                        temp_config.unlink()
                    if temp_ckpt and temp_ckpt.exists():
                        temp_ckpt.unlink()
                        
                    done_msg = f">>> Saved audio sample to: {out_wav} <<<\n\n"
                    print(done_msg)
                    sys.stdout.flush()
                    if progress_callback:
                        progress_callback(done_msg)
                except Exception as e:
                    # Cleanup on failure
                    if temp_ckpt and temp_ckpt.exists():
                        try:
                            temp_ckpt.unlink()
                        except Exception:
                            pass
                    err_msg = f"Warning: Failed to generate epoch sample for Epoch {epoch_num}: {e}\n"
                    print(err_msg)
                    sys.stdout.flush()
                    if progress_callback:
                        progress_callback(err_msg)

def train_piper_model(
    preprocessed_dir: Path,
    base_ckpt_path: Path,
    epochs: int,
    batch_size: int,
    quality: str = "medium",
    stream_logs: bool = True,
    progress_callback=None,
    sample_epoch_interval: int = 0,
    sample_text: str = "",
    config_path: Path | None = None,
    output_dir: Path | None = None,
) -> str:
    """Invokes pytorch-lightning training via piper_train as a subprocess."""
    piper_python_src = Path(__file__).resolve().parent.parent / "piper"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(piper_python_src) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    
    # Configure accelerator based on availability (Mac GPUs use mps, otherwise cpu/gpu)
    devices = 1
    if torch.cuda.is_available():
        accelerator = "gpu"
    elif torch.backends.mps.is_available():
        accelerator = "mps"
    else:
        accelerator = "cpu"
        
    cmd = [
        sys.executable,
        "-m", "piper_train",
        "--dataset-dir", str(preprocessed_dir),
        "--accelerator", accelerator,
        "--devices", str(devices),
        "--batch-size", str(batch_size),
        "--validation-split", "0.0",
        "--num-test-examples", "0",
        "--max_epochs", str(epochs),
        "--checkpoint-epochs", "1",
        "--precision", "32",
        "--quality", quality
    ]
    if base_ckpt_path:
        cmd.extend(["--resume_from_checkpoint", str(base_ckpt_path)])

    
    if progress_callback:
        progress_callback("Launching Piper training...")
        
    print(f"Running training command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True
    )
    
    try:
        from utils.pipeline import register_active_process
        register_active_process(process)
    except Exception:
        pass
        
    log_lines = []
    generated_epochs = set()
    import time
    last_check_time = 0.0
    last_dir_mtime = 0.0

    try:
        if process.stdout:
            for line in process.stdout:
                log_lines.append(line)
                if stream_logs:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                if progress_callback:
                    progress_callback(line)
                
                # Scan for checkpoints to generate progress audio samples
                if sample_epoch_interval > 0 and config_path and output_dir:
                    current_time = time.time()
                    if (current_time - last_check_time) > 0.5:
                        last_check_time = current_time
                        try:
                            current_mtime = preprocessed_dir.stat().st_mtime
                        except Exception:
                            current_mtime = 0.0
                        if current_mtime != last_dir_mtime:
                            last_dir_mtime = current_mtime
                            _check_and_generate_piper_sample(
                                preprocessed_dir=preprocessed_dir,
                                sample_epoch_interval=sample_epoch_interval,
                                sample_text=sample_text,
                                config_path=config_path,
                                output_dir=output_dir,
                                generated_epochs=generated_epochs,
                                progress_callback=progress_callback
                            )

        process.wait()
        
        # Run a final check to ensure we capture the final checkpoints
        if sample_epoch_interval > 0 and config_path and output_dir:
            _check_and_generate_piper_sample(
                preprocessed_dir=preprocessed_dir,
                sample_epoch_interval=sample_epoch_interval,
                sample_text=sample_text,
                config_path=config_path,
                output_dir=output_dir,
                generated_epochs=generated_epochs,
                progress_callback=progress_callback
            )
        
        if process.returncode != 0:
            raise RuntimeError(f"Piper training subprocess failed with code {process.returncode}")
            
        return "".join(log_lines)
    finally:
        try:
            from utils.pipeline import register_active_process
            register_active_process(None)
        except Exception:
            pass

def export_piper_onnx(ckpt_path: Path, onnx_path: Path, config_path: Path):
    """Exports PyTorch Lightning checkpoint to ONNX format and copies its configuration file."""
    piper_python_src = Path(__file__).resolve().parent.parent / "piper"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(piper_python_src) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    
    cmd = [
        sys.executable,
        "-m", "piper_train.export_onnx",
        str(ckpt_path),
        str(onnx_path)
    ]
    print(f"Running ONNX export: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)
    
    # Copy configuration file to match the onnx model path
    dest_config = Path(f"{onnx_path}.json")
    shutil.copy2(config_path, dest_config)
    print(f"ONNX model successfully exported to {onnx_path}")

def synthesize_piper(onnx_path: str, config_path: str, text: str, output_wav_path: str):
    """Generates speech wav file using ONNX Runtime and piper python_run scripts."""
    import wave
    
    piper_run_src = Path(__file__).resolve().parent.parent / "piper"
    if str(piper_run_src) not in sys.path:
        sys.path.insert(0, str(piper_run_src))
        
    from piper.voice import PiperVoice
    
    voice = PiperVoice.load(model_path=onnx_path, config_path=config_path)
    
    output_path = Path(output_wav_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize(text, wav_file)
        
    print(f"Audio successfully generated and saved to {output_wav_path}")
