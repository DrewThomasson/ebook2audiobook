import os, subprocess, shutil, json

from typing import Any, Union, TYPE_CHECKING
from lib.classes.subprocess_pipe import SubprocessPipe


if TYPE_CHECKING:
    from torch import Tensor

def detect_gender(voice_path:str)->str|None:
    try:
        import numpy as np
        from scipy.signal import find_peaks
        from scipy.io import wavfile as wav
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

def trim_audio(audio_data: Union[list[float], 'Tensor'], samplerate: int, silence_threshold: float = 0.003, buffer_sec: float = 0.005)->'Tensor':
    import torch
    # Ensure audio_data is a PyTorch tensor
    if isinstance(audio_data, list):
        audio_data = torch.tensor(audio_data, dtype=torch.float32)
    if isinstance(audio_data, torch.Tensor):
        if audio_data.ndim != 1:
            error = "audio_data must be a 1D tensor (mono audio)."
            print(error)
            return torch.tensor([], dtype=torch.float32)
        if audio_data.device.type != "cpu":
            audio_data = audio_data.cpu()
        # Detect non-silent indices
        non_silent_indices = torch.where(audio_data.abs() > silence_threshold)[0]
        if len(non_silent_indices) == 0:
            return torch.tensor([], dtype=audio_data.dtype)
        # Calculate start and end trimming indices with buffer
        start_index = max(non_silent_indices[0].item() - int(buffer_sec * samplerate), 0)
        end_index = min(non_silent_indices[-1].item() + int(buffer_sec * samplerate), audio_data.size(0))
        return audio_data[start_index:end_index]
    error = 'audio_data must be a PyTorch tensor or a list of numerical values.'
    print(error)
    return torch.tensor([], dtype=torch.float32)
    
def _extract_mediainfo_durations(data:dict|list)->dict[str, float]:
    durations: dict[str, float] = {}
    if isinstance(data, list):
        media_blocks = data
    else:
        media_blocks = [data]
    for block in media_blocks:
        media = block.get("media")
        if not media:
            continue
        media_list = media if isinstance(media, list) else [media]
        for m in media_list:
            ref = m.get("@ref")
            if not ref:
                continue
            ref = os.path.realpath(ref)

            for track in m.get("track", []):
                raw = track.get("Duration")
                if not raw:
                    continue
                try:
                    durations[ref] = float(raw)
                    break
                except (TypeError, ValueError):
                    continue
    return durations

def get_audio_duration(filepath:str)->float:
    mediainfo = shutil.which("mediainfo")
    if not mediainfo:
        return 0.0
    cmd = [mediainfo, "--Output=JSON", filepath]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        durations = _extract_mediainfo_durations(data)
        return durations.get(os.path.realpath(filepath), 0.0)
    except subprocess.CalledProcessError as e:
        DependencyError(e)
        return 0.0
    except Exception as e:
        print(f"get_audio_duration() Error: Failed to process {filepath}: {e}")
        return 0.0

def get_audiolist_duration(filepaths:list[str])->dict[str, float]:
    durations = {os.path.realpath(p): 0.0 for p in filepaths}
    mediainfo = shutil.which("mediainfo")
    if not mediainfo:
        return durations
    try:
        cmd = [mediainfo, "--Output=JSON", *filepaths]
        out = subprocess.check_output(cmd, text=True)
        data = json.loads(out)
        extracted = _extract_mediainfo_durations(data)
        for path in durations:
            if path in extracted:
                durations[path] = extracted[path]
    except Exception:
        pass
    return durations

def normalize_audio(input_file:str, output_file:str, samplerate:int, is_gui_process:bool)->bool:
    try:
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            error = 'ffmpeg not found'
            print(error)
            return False
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
        cmd = [ffmpeg, '-hide_banner', '-nostats', '-i', input_file]
        cmd += [
            '-filter_complex', filter_complex,
            '-map', '[audio]',
            '-ar', str(samplerate),
            '-y', output_file
        ]
        proc_pipe = SubprocessPipe(
            cmd,
            is_gui_process=is_gui_process,
            total_duration=get_audio_duration(str(input_file)),
            msg='Normalize'
        )
        return proc_pipe.result
    except Exception as e:
        print(f'normalize_audio() error: {input_file}: {e}')
        return False

def is_audio_data_valid(audio_data:Any)->bool:
    if audio_data is None:
        return False
    try:
        import torch
        if isinstance(audio_data, torch.Tensor):
            return audio_data.numel() > 0
    except ImportError:
        pass
    if isinstance(audio_data, (list, tuple)):
        return len(audio_data) > 0
    try:
        import numpy as np
        if isinstance(audio_data, np.ndarray):
            return audio_data.size > 0
    except ImportError:
        pass
    return False