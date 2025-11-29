import os
import gc
import torch
import shutil
import regex as re

from typing import Any, Union, Dict
from safetensors.torch import save_file
from pathlib import Path
from torch import Tensor
from torch.nn import Module

def cleanup_memory()->None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()

def model_size_bytes(model:Module)->int:
	total = 0
	for t in list(model.parameters()) + list(model.buffers()):
		if isinstance(t, Tensor):
			total += t.nelement() * t.element_size()
	return total

def loaded_tts_size_gb(loaded_tts:Dict[str, Module])->float:
	total_bytes = 0
	for model in loaded_tts.values():
		try:
			total_bytes += model_size_bytes(model)
		except Exception:
			pass
	gb = total_bytes / (1024 ** 3)
	return round(gb, 2)


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

def convert_pt_to_safetensors(pth_path:str, delete_original:bool=False)->str:
    pth_path = Path(pth_path)
    if not pth_path.exists():
        error = f'File not found: {pth_path}'
        print(error)
        raise FileNotFoundError()
    if not (pth_path.suffix in ['.pth', '.pt']):
        error = f'Expected a .pth or .pt file, got: {pth_path.suffix}'
        print(error)
        raise ValueError(error)
    safe_dir = pth_path.parent / "safetensors"
    safe_dir.mkdir(exist_ok=True)
    safe_path = safe_dir / pth_path.with_suffix('.safetensors').name
    msg = f'Converting {pth_path.name} → safetensors/{safe_path.name}'
    print(msg)
    try:
        try:
            state = torch.load(str(pth_path), map_location='cpu', weights_only=True)
        except Exception:
            error = f'⚠️ weights_only load failed for {pth_path.name}, retrying unsafely (trusted file).'
            print(error)
            state = torch.load(str(pth_path), map_location='cpu', weights_only=False)
        if isinstance(state, dict) and "model" in state:
            state = state["model"]
        flattened = {}
        for k, v in state.items():
            if isinstance(v, dict):
                for subk, subv in v.items():
                    flattened[f"{k}.{subk}"] = subv
            else:
                flattened[k] = v
        state = {k: v for k, v in flattened.items() if isinstance(v, torch.Tensor)}
        for k, v in list(state.items()):
            state[k] = v.clone().detach()
        save_file(state, str(safe_path))
        if delete_original:
            pth_path.unlink(missing_ok=True)
            msg = f'Deleted original: {pth_path}'
            print(msg)
        msg = f'Saved: {safe_path}'
        print(msg)
        return str(safe_path)
    except Exception as e:
        error = f'Failed to convert {pth_path.name}: {e}'
        print(error)
        raise

def ensure_safe_checkpoint(checkpoint_dir:str)->list[str]:
    safe_files = []
    if os.path.isfile(checkpoint_dir):
        if not (checkpoint_dir.endswith('.pth') or checkpoint_dir.endswith('.pt')):
            error = f'Invalid checkpoint file: {checkpoint_dir}'
            raise ValueError(error)
        if not is_safetensors_file(checkpoint_dir):
            try:
                safe_path = convert_pt_to_safetensors(checkpoint_dir, False)
                msg = f'Created safetensors version of {os.path.basename(checkpoint_dir)} → {safe_path}'
                print(msg)
                safe_files.append(safe_path)
            except Exception as e:
                error = f'Failed to convert {os.path.basename(checkpoint_dir)}: {e}'
                print(error)
        else:
            safe_files.append(checkpoint_dir)
        return safe_files
    if not os.path.isdir(checkpoint_dir):
        raise FileNotFoundError(f"Invalid checkpoint_dir: {checkpoint_dir}")
    for root, _, files in os.walk(checkpoint_dir):
        for fname in files:
            if fname.endswith(".pth") or fname.endswith(".pt"):
                pth_path = os.path.join(root, fname)
                if is_safetensors_file(pth_path):
                    safe_files.append(pth_path)
                    continue
                try:
                    safe_path = convert_pt_to_safetensors(pth_path, False)
                    msg = f'Created safetensors version of {os.path.relpath(pth_path, checkpoint_dir)} → {os.path.relpath(safe_path, checkpoint_dir)}'
                    print(msg)
                    safe_files.append(safe_path)
                except Exception as e:
                    error = f'Failed to convert {fname}: {e}'
                    print(error)
    return safe_files