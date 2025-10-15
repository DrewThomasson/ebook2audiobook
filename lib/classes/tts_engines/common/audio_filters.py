import numpy as np
import torch
import subprocess
import shutil

from typing import Any, Optional, Union, Callable
from scipy.io import wavfile as wav
from scipy.signal import find_peaks

def detect_gender(voice_path:str)->Optional[str]:
    try:
        samplerate, signal = wav.read(voice_path)
        # Ensure mono
        if signal.ndim > 1:
            signal = np.mean(signal, axis=1)
        # FFT and positive frequency range
        fft_spectrum = np.abs(np.fft.fft(signal))
        freqs = np.fft.fftfreq(len(fft_spectrum), d=1.0 / samplerate)
        positive_freqs = freqs[: len(freqs) // 2]
        positive_magnitude = fft_spectrum[: len(fft_spectrum) // 2]
        # Peak detection (20% threshold of max amplitude)
        peaks, _ = find_peaks(positive_magnitude, height=np.max(positive_magnitude) * 0.2)
        if len(peaks) == 0:
            return None
        # Detect first strong peak within human voice pitch range (75–300 Hz)
        for peak in peaks:
            freq = positive_freqs[peak]
            if 75.0 <= freq <= 300.0:
                return "female" if freq > 135.0 else "male"
        return None
    except Exception as e:
        error = f"detect_gender() error: {voice_path}: {e}"
        print(error)
        return None

def trim_audio(audio_data: Union[list[float], Tensor], samplerate: int, silence_threshold: float = 0.003, buffer_sec: float = 0.005) -> Tensor:
    # Ensure audio_data is a PyTorch tensor
    if isinstance(audio_data, list):
        audio_data = torch.tensor(audio_data, dtype=torch.float32)
    if isinstance(audio_data, Tensor):
        if audio_data.ndim != 1:
            error = "audio_data must be a 1D tensor (mono audio)."
            raise ValueError(error)
            return torch.tensor([], dtype=torch.float32)  # just for static analyzers
        if audio_data.is_cuda:
            audio_data = audio_data.cpu()
        # Detect non-silent indices
        non_silent_indices = torch.where(audio_data.abs() > silence_threshold)[0]
        if len(non_silent_indices) == 0:
            return torch.tensor([], dtype=audio_data.dtype)  # Preserves dtype
        # Calculate start and end trimming indices with buffer
        start_index = max(non_silent_indices[0].item() - int(buffer_sec * samplerate), 0)
        end_index = min(non_silent_indices[-1].item() + int(buffer_sec * samplerate), audio_data.size(0))
        return audio_data[start_index:end_index]
    error = "audio_data must be a PyTorch tensor or a list of numerical values."
    raise TypeError(error)
    return torch.tensor([], dtype=torch.float32)

def normalize_audio(input_file:str, output_file:str, samplerate:int)->bool:
    filter_complex = (
        'agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
        'afftdn=nf=-70,'
        'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
        'loudnorm=I=-14:TP=-3:LRA=7:linear=true,'
        'equalizer=f=150:t=q:w=2:g=1,'
        'equalizer=f=250:t=q:w=2:g=-3,'
        'equalizer=f=3000:t=q:w=2:g=2,'
        'equalizer=f=5500:t=q:w=2:g=-4,'
        'equalizer=f=9000:t=q:w=2:g=-2,'
        'highpass=f=63[audio]'
    )
    ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', input_file]
    ffmpeg_cmd += [
        '-filter_complex', filter_complex,
        '-map', '[audio]',
        '-ar', str(samplerate),
        '-y', output_file
    ]
    try:
        subprocess.run(
            ffmpeg_cmd,
            env={},
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='ignore'
        )
        return True
    except subprocess.CalledProcessError as e:
        error = f"normalize_audio() error: {input_file}: {e}"
        print(error)
        return False

def is_audio_data_valid(audio_data:Any)->bool:
    if audio_data is None:
        return False
    if isinstance(audio_data, torch.Tensor):
        return audio_data.numel() > 0
    if isinstance(audio_data, (list, tuple)):
        return len(audio_data) > 0
    try:
        if isinstance(audio_data, np.ndarray):
            return audio_data.size > 0
    except ImportError:
        pass
    return False