# components/audiocraft/audiocraft.py
import argparse
import os
import torch
import torchaudio
from audiocraft.models import MusicGen

def main()->None:
    parser = argparse.ArgumentParser(description='Generate Audiocraft interlude.')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt for MusicGen.')
    parser.add_argument('--duration', type=int, default=60, help='Duration of the audio in seconds.')
    parser.add_argument('--output', type=str, required=True, help='Output file path (e.g., .flac).')
    args = parser.parse_args()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # Note: musicgen-medium is ~2GB. If VRAM/RAM is tight, consider 'facebook/musicgen-small'
    model_name = 'facebook/musicgen-medium'
    try:
        model = MusicGen.get_pretrained(model_name, device=device)
    except Exception as e:
        print(f'Medium model failed ({e}), falling back to small...')
        model_name = 'facebook/musicgen-small'
        model = MusicGen.get_pretrained(model_name, device=device)
    model.set_generation_params(duration=args.duration)
    wav = model.generate([args.prompt])
    audio_tensor = wav[0].cpu()
    sample_rate = model.sample_rate
    output_path = args.output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if audio_tensor.dtype != torch.float32:
        audio_tensor = audio_tensor.float()
    torchaudio.save(output_path, audio_tensor, sample_rate)
    print(f'Saved interlude to {output_path}')

if __name__ == '__main__':
    main()