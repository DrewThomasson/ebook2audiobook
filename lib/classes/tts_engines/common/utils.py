import os
import gc
import torch
import shutil
import regex as re

from typing import Any, Union
from safetensors.torch import save_file
from pathlib import Path
from lib.models import loaded_tts, TTS_ENGINES
from lib.functions import context

def cleanup_garbage():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()

def append_sentence2vtt(sentence_obj:dict[str, Any], path:str)->Union[int, bool]:

    def format_timestamp(seconds:float)->str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{s:06.3f}"

    try:
        index = 1
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "-->" in line:
                        index += 1
        if index > 1 and "resume_check" in sentence_obj and sentence_obj["resume_check"] < index:
            return index  # Already written
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(float(sentence_obj["start"]))
            end = format_timestamp(float(sentence_obj["end"]))
            text = re.sub(r"[\r\n]+", " ", str(sentence_obj["text"])).strip()
            f.write(f"{start} --> {end}\n{text}\n\n")
        return index + 1
    except Exception as e:
        error = f"append_sentence2vtt() error: {e}"
        print(error)
        return False

def is_safetensors_file(path:str)->bool:
    try:
        with open(path, 'rb') as f:
            header = f.read(32)
            return b'safetensors' in header
    except Exception:
        return False

def convert_single_pth_to_safetensors(pth_path:str, delete_original:bool=False)->str:
    pth_path = Path(pth_path)
    if not pth_path.exists():
        error = f'File not found: {pth_path}'
        raise FileNotFoundError()
    if pth_path.suffix != '.pth':
        error = f'Expected a .pth file, got: {pth_path.suffix}'
        raise ValueError(error)
    safe_path = pth_path.with_suffix('.safetensors')
    msg = f'Converting {pth_path.name} → {safe_path.name}'
    print(msg)
    state = torch.load(str(pth_path), map_location='cpu', weights_only=True)
    save_file(state, str(safe_path))
    if delete_original:
        pth_path.unlink(missing_ok=True)
        msg = f'Deleted original: {pth_path}'
        print(msg)
    return str(safe_path)

def ensure_safe_checkpoint(checkpoint_dir:str)->list[str]:
    # NEW: allow both single file and directory
    if os.path.isfile(checkpoint_dir):
        if not checkpoint_dir.endswith('.pth'):
            raise ValueError(f"Invalid checkpoint file: {checkpoint_dir}")
        safe_files = []
        if not is_safetensors_file(checkpoint_dir):
            try:
                safe_path = convert_single_pth_to_safetensors(checkpoint_dir, delete_original=False)
                shutil.move(safe_path, checkpoint_dir)
                msg = f'Replaced {os.path.basename(checkpoint_dir)} with safetensors content'
                print(msg)
                safe_files.append(checkpoint_dir)
            except Exception as e:
                error = f'Failed to convert {os.path.basename(checkpoint_dir)}: {e}'
                print(error)
        else:
            safe_files.append(checkpoint_dir)
        return safe_files

    # existing behavior for directories
    if not os.path.isdir(checkpoint_dir):
        raise FileNotFoundError(f"Invalid checkpoint_dir: {checkpoint_dir}")

    safe_files = []
    for fname in os.listdir(checkpoint_dir):
        if fname.endswith(".pth"):
            pth_path = os.path.join(checkpoint_dir, fname)
            if not is_safetensors_file(pth_path):
                try:
                    safe_path = convert_single_pth_to_safetensors(pth_path, delete_original=False)
                    shutil.move(safe_path, pth_path)
                    msg = f'Replaced {fname} with safetensors content'
                    print(msg)
                    safe_files.append(pth_path)
                except Exception as e:
                    error = f'Failed to convert {fname}: {e}'
                    print(error)
            else:
                safe_files.append(pth_path)
    return safe_files