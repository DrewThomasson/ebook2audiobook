# components/audiocraft/audiocraft.py
import argparse
import os
import warnings
import torch
import torchaudio
from audiocraft.models import MusicGen

def main()->None:
    parser = argparse.ArgumentParser(description='Generate Audiocraft interlude.')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt for MusicGen.')
    parser.add_argument('--duration', type=int, default=60, help='Duration of the audio in seconds.')
    parser.add_argument('--output', type=str, required=True, help='Output file path (e.g., .flac).')
    parser.add_argument('--samplerate', type=int, default=24000, help='Output sample rate, must match the chapters for a clean concat.')
    parser.add_argument('--channels', type=int, default=1, choices=[1, 2], help='Output channels: 1 mono, 2 stereo.')
    args = parser.parse_args()
    # torch 2.1 deprecation notice triggered by audiocraft's EnCodec layers, harmless
    warnings.filterwarnings('ignore', message='torch.nn.utils.weight_norm is deprecated')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # medium (1.5B) is loaded as fp32 on CPU (~6GB, swaps on low-RAM hosts) so CPU uses small (300M, ~1.2GB); medium stays for CUDA
    # stereo checkpoints render true stereo (distinct L/R), duplicating a mono render would only give dual mono
    model_name = f"facebook/musicgen-{'stereo-' if args.channels == 2 else ''}{'medium' if device == 'cuda' else 'small'}"
    print(f'Loading {model_name} on {device}...')
    try:
        model = MusicGen.get_pretrained(model_name, device=device)
    except Exception as e:
        if model_name.endswith('-small'):
            raise
        print(f'Medium model failed ({e}), falling back to small...')
        model_name = model_name.replace('-medium', '-small')
        model = MusicGen.get_pretrained(model_name, device=device)
    model.set_generation_params(duration=args.duration)
    wav = model.generate([args.prompt], progress=True)
    audio_tensor = wav[0].cpu()
    sample_rate = model.sample_rate
    output_path = args.output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if audio_tensor.dtype != torch.float32:
        audio_tensor = audio_tensor.float()
    # match the chapters' exact format: ffmpeg's concat demuxer breaks timestamps at the joins when the sample rate changes mid-list
    if audio_tensor.shape[0] != args.channels:
        audio_tensor = audio_tensor.mean(dim=0, keepdim=True) if args.channels == 1 else audio_tensor.repeat(2, 1)
    if sample_rate != args.samplerate:
        audio_tensor = torchaudio.functional.resample(audio_tensor, sample_rate, args.samplerate)
        sample_rate = args.samplerate
    torchaudio.save(output_path, audio_tensor, sample_rate)
    print(f'Saved interlude to {output_path}')

if __name__ == '__main__':
    main()