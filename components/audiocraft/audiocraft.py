# components/audiocraft/audiocraft.py
import argparse
import json
import os
import warnings
import numpy as np
import soundfile as sf
import torch
from math import gcd
from scipy.signal import resample_poly
from transformers import AutoProcessor, MusicgenForConditionalGeneration, StoppingCriteria, StoppingCriteriaList
from transformers.utils import logging as hf_logging

class ProgressCriteria(StoppingCriteria):

    def __init__(self, total:int)->None:
        self.total = total
        self.step = 0

    def __call__(self, input_ids:torch.LongTensor, scores:torch.FloatTensor, **kwargs)->torch.BoolTensor:
        # never stops generation, only prints the step counter in place
        self.step += 1
        print(f'{min(self.step, self.total): 6d} / {self.total: 6d}', end='\r', flush=True)
        return torch.zeros(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)

def main()->None:
    parser = argparse.ArgumentParser(description='Generate a MusicGen interlude.')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt for MusicGen.')
    parser.add_argument('--duration', type=int, default=30, help='Duration of the audio in seconds (MusicGen max is 30).')
    parser.add_argument('--output', type=str, required=True, help='Output file path (e.g., .flac).')
    parser.add_argument('--samplerate', type=int, default=24000, help='Output sample rate, must match the chapters.')
    parser.add_argument('--channels', type=int, default=2, choices=[1, 2], help='Output channels: 1 mono, 2 stereo.')
    parser.add_argument('--device_info', type=str, default='', help='e2a device_info JSON string.')
    args = parser.parse_args()
    hf_logging.set_verbosity_error()
    warnings.filterwarnings('ignore', category=FutureWarning)
    try:
        device_info = json.loads(args.device_info) if args.device_info else {}
    except json.JSONDecodeError:
        device_info = {}
    name = str(device_info.get('name') or 'cpu').lower()
    # e2a hardware name -> torch device, checked against what this venv's torch can really use
    if name in ('cuda', 'rocm', 'jetson') and torch.cuda.is_available():
        device = 'cuda'
    elif name == 'mps' and torch.backends.mps.is_available():
        device = 'mps'
    elif name == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
        device = 'xpu'
    else:
        device = 'cpu'
    # generation settings per device: fp16 on CUDA/ROCm/XPU, medium only when the GPU has the room, small fp32 on MPS/CPU
    size = 'small'
    dtype = torch.float32
    if device == 'cuda':
        dtype = torch.float16
        if torch.cuda.mem_get_info()[0] >= 8 * 1024 ** 3:
            size = 'medium'
    elif device == 'xpu':
        dtype = torch.float16
    model_name = f"facebook/musicgen-{'stereo-' if args.channels == 2 else ''}{size}"
    print(f"Loading {model_name} on {device} ({str(dtype).replace('torch.', '')})...")
    try:
        processor = AutoProcessor.from_pretrained(model_name)
        model = MusicgenForConditionalGeneration.from_pretrained(model_name, dtype=dtype).to(device)
    except Exception as e:
        if size == 'small':
            raise
        print(f'{model_name} failed ({e}), falling back to small...')
        model_name = model_name.replace('-medium', '-small')
        processor = AutoProcessor.from_pretrained(model_name)
        model = MusicgenForConditionalGeneration.from_pretrained(model_name, dtype=dtype).to(device)
    model.eval()
    # MusicGen is trained on 30 s windows: transformers hard-caps generation there
    max_new_tokens = int(max(1, min(args.duration, 30)) * model.config.audio_encoder.frame_rate)
    inputs = processor(text=[args.prompt], padding=True, return_tensors='pt')
    try:
        with torch.inference_mode():
            audio = model.generate(**inputs.to(device), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, stopping_criteria=StoppingCriteriaList([ProgressCriteria(max_new_tokens)]))
    except Exception as e:
        if device == 'cpu':
            raise
        print(f'\nGeneration on {device} failed ({e}), retrying on cpu...')
        model = model.to('cpu', dtype=torch.float32)
        with torch.inference_mode():
            audio = model.generate(**inputs.to('cpu'), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, stopping_criteria=StoppingCriteriaList([ProgressCriteria(max_new_tokens)]))
    print()
    sample_rate = model.config.audio_encoder.sampling_rate
    audio = audio[0].float().cpu().numpy()
    if audio.shape[0] != args.channels:
        audio = audio.mean(axis=0, keepdims=True) if args.channels == 1 else np.repeat(audio, 2, axis=0)
    # match the chapters' sample rate: the final merge expects one uniform rate
    if sample_rate != args.samplerate:
        g = gcd(sample_rate, args.samplerate)
        audio = resample_poly(audio, args.samplerate // g, sample_rate // g, axis=1)
    # MusicGen levels vary a lot between prompts: peak-normalize to -1 dBFS
    peak = float(np.abs(audio).max())
    if peak > 0:
        audio = audio * (0.89 / peak)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    sf.write(args.output, np.clip(audio.T, -1.0, 1.0), args.samplerate, subtype='PCM_16')
    print(f'Saved interlude to {args.output}')

if __name__ == '__main__':
    main()
