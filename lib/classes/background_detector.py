import threading, warnings

from typing import Any
from lib.conf import DEVICE_SYSTEM, systems, tts_dir, devices
from lib.conf_models import default_voice_detection_model

_pipeline_cache = {}
_pipeline_lock = threading.Lock()

def pyannote_patch()->None:
    '''Restore APIs removed in torchaudio >=2.9 that pyannote.audio's
    transitive deps (speechbrain, asteroid-filterbanks, silero-vad, …)
    still call at import time, and route pyannote.audio 4.x's I/O
    through soundfile instead of torchcodec (which is broken on
    Windows ROCm builds and unnecessary for our preloaded-dict path).
    Idempotent: safe to call from both app entrypoint and lazy paths.
    '''
    import torchaudio
    # Silence pyannote.audio.core.io's torchcodec warning. Must run
    # before `from pyannote.audio import ...` triggers io.py import.
    warnings.filterwarnings(
        'ignore',
        message=r'(?s).*torchcodec is not installed correctly.*',
        category=UserWarning,
    )
    if not hasattr(torchaudio, 'list_audio_backends'):
        def _list_audio_backends()->list:
            backends = []
            try:
                from torchaudio.utils import ffmpeg_utils
                if ffmpeg_utils.get_versions():
                    backends.append('ffmpeg')
            except Exception:
                pass
            try:
                import soundfile
                backends.append('soundfile')
            except Exception:
                pass
            return backends
        torchaudio.list_audio_backends = _list_audio_backends
    if not hasattr(torchaudio, 'AudioMetaData'):
        class _AudioMetaData:
            def __init__(self, sample_rate:int=0, num_frames:int=0,
                         num_channels:int=0, bits_per_sample:int=0,
                         encoding:str='UNKNOWN')->None:
                self.sample_rate = sample_rate
                self.num_frames = num_frames
                self.num_channels = num_channels
                self.bits_per_sample = bits_per_sample
                self.encoding = encoding
        torchaudio.AudioMetaData = _AudioMetaData
    # Replace pyannote.audio.core.io.Audio's torchcodec-backed loader
    # with a soundfile-backed one. Preloaded {'waveform','sample_rate'}
    # dicts short-circuit to the original code path (no decoding); any
    # file-path input is decoded by soundfile then handed back to the
    # original as an in-memory dict so its resampling/channel logic
    # still applies.
    try:
        import torch, soundfile as sf
        from pyannote.audio.core import io as _pa_io
        if not getattr(_pa_io, '_e2a_sf_patched', False):
            _orig_call = _pa_io.Audio.__call__
            def _sf_call(self, file, **kw):
                if isinstance(file, dict) and 'waveform' in file:
                    return _orig_call(self, file, **kw)
                path = file['audio'] if isinstance(file, dict) else file
                data, sr = sf.read(str(path), dtype='float32', always_2d=True)
                # soundfile -> (frames, channels); pyannote -> (channels, frames)
                waveform = torch.from_numpy(data.T.copy())
                return _orig_call(
                    self,
                    {'waveform': waveform, 'sample_rate': sr},
                    **kw,
                )
            _pa_io.Audio.__call__ = _sf_call
            _pa_io._e2a_sf_patched = True
    except Exception:
        pass

class BackgroundDetector:
    def __init__(self, wav_file:str, device:str)->None:
        self.wav_file = wav_file
        self.device = device
        self.torch_device = None
        self.total_duration = self._get_duration()

    def _get_duration(self)->float:
        try:
            import librosa
            return float(librosa.get_duration(path=self.wav_file))
        except Exception:
            return 0.0

    def _get_props(self)->tuple:
        import torch, librosa
        pyannote_patch()
        from pyannote.audio import Model
        from pyannote.audio.pipelines import VoiceActivityDetection
        from pyannote.audio.utils.reproducibility import ReproducibilityWarning
        warnings.filterwarnings('ignore', category=ReproducibilityWarning)
        # MIOpen on Windows ROCm fails to JIT pyannote's dropout kernel
        # (miopenStatusUnknownError). On ROCm builds, torch.backends.cudnn
        # maps to MIOpen; disabling it routes ops to native ATen kernels.
        # Cost is negligible for VAD-sized models.
        if getattr(torch.version, 'hip', None) is not None:
            if DEVICE_SYSTEM == systems['WINDOWS']:
                torch.backends.cudnn.enabled = False
        self.torch_device = torch.device(
            devices['CUDA']['proc'] if (self.device == devices['CUDA']['proc'] and getattr(torch.version, 'hip', None) is None) or (getattr(torch.version, 'hip', None) is not None and DEVICE_SYSTEM != systems['WINDOWS'])
            else devices['XPU']['proc'] if hasattr(torch, devices['XPU']['proc']) and torch.xpu.is_available()
            else devices['MPS']['proc'] if torch.backends.mps.is_available()
            else devices['CPU']['proc']
        )
        key = self.torch_device.type
        pipeline = _pipeline_cache.get(key)
        if pipeline is None:
            with _pipeline_lock:
                pipeline = _pipeline_cache.get(key)
                if pipeline is None:
                    model = Model.from_pretrained(
                        default_voice_detection_model,
                        cache_dir=tts_dir
                    )
                    model.eval()
                    batch_size = 1 if devices['JETSON']['found'] else 32
                    pipeline = VoiceActivityDetection(segmentation=model, batch_size=batch_size)
                    if key == devices['CUDA']['proc'] and not devices['JETSON']['found']:
                        torch.backends.cuda.matmul.allow_tf32 = True
                        torch.backends.cudnn.allow_tf32 = True
                    pipeline.instantiate({
                        "min_duration_on": 0.0,
                        "min_duration_off": 0.0
                    })
                    _pipeline_cache[key] = pipeline
        if pipeline:
            # detect() parks cached pipelines on CPU when done: move back on every retrieval
            pipeline.to(self.torch_device)
            y, sr = librosa.load(self.wav_file, sr=16000, mono=True)
            waveform = torch.from_numpy(y).float().unsqueeze(0)
            return pipeline, waveform, sr
        return None, None, None

    @staticmethod
    def _measure_levels(y:Any, sr:int, annotation:Any)->dict[str, float|None]:
        '''VAD tells when someone speaks, not whether something else plays
        under the voice: a music bed under continuous speech is one long
        speech segment, and a pause filled with music has the same duration
        as a silent one. So background is measured as level, not duration:
          gap_db    median level of the non-speech frames (pauses, intro,
                    outro) relative to the speech level. Silent pauses sit
                    at the room tone, a bed keeps them filled.
          floor_db  spectral floor under the speech frames: per-bin 10th
                    percentile over per-bin mean power, 60-7000 Hz. Speech
                    is sparse in time-frequency so its floor stays low, a
                    continuous bed lifts it even when VAD finds no pause.
        Digital silence (padding, fades to zero) is left out so it neither
        hides a bed nor counts as a pause.
        '''
        import numpy as np, librosa
        n_fft = 512
        hop = int(sr * 0.010)
        min_frames = int(0.5 * sr / hop)
        levels = dict(speech_db=None, gap_db=None, floor_db=None)
        spec = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, win_length=int(sr * 0.025))) ** 2
        frame_db = 10 * np.log10(spec.mean(axis=0) + 1e-12)
        times = librosa.frames_to_time(np.arange(frame_db.shape[0]), sr=sr, hop_length=hop)
        speech = np.zeros(frame_db.shape[0], dtype=bool)
        for segment in annotation.itersegments():
            speech |= (times >= segment.start) & (times < segment.end)
        live = frame_db > -90.0
        voiced = speech & live
        if voiced.sum() < min_frames:
            return levels
        speech_db = float(np.percentile(frame_db[voiced], 95))
        levels['speech_db'] = speech_db
        pauses = ~speech & live
        if pauses.sum() >= min_frames:
            levels['gap_db'] = float(np.median(frame_db[pauses])) - speech_db
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        band = (freqs >= 60.0) & (freqs < 7000.0)
        voiced_spec = spec[band][:, voiced]
        floor = np.percentile(voiced_spec, 10, axis=1).sum()
        mean = voiced_spec.mean(axis=1).sum()
        levels['floor_db'] = float(10 * np.log10(floor / (mean + 1e-20) + 1e-12))
        return levels

    def detect(self, gap_thresh_db:float=-27.0, floor_thresh_db:float=-28.0)->tuple[bool, dict[str, float|bool|None]]:
        # thresholds: no false positive on clean LibriSpeech read speech, music bed
        # caught down to ~-18 dB under the voice, pink noise down to ~-20 dB
        import gc, torch
        pipeline, waveform, sr = self._get_props()
        try:
            if (
                pipeline is not None
                and waveform is not None
                and waveform.numel() > 0
                and sr is not None
                and sr > 0
            ):
                file = {
                    "waveform": waveform,
                    "sample_rate": sr
                }
                with torch.inference_mode():
                    annotation = pipeline(file)
                speech_time = sum(
                    segment.end - segment.start
                    for segment in annotation.itersegments()
                )
                non_speech_ratio = 1.0 - (
                    speech_time / self.total_duration if self.total_duration > 0 else 0.0
                )
                levels = self._measure_levels(waveform.squeeze(0).cpu().numpy(), sr, annotation)
                if levels['speech_db'] is None:
                    # no usable speech found: let the separator try, as the old ratio (~1.0) did
                    background_detected = True
                else:
                    background_detected = bool(
                        (levels['gap_db'] is not None and levels['gap_db'] > gap_thresh_db)
                        or (levels['floor_db'] is not None and levels['floor_db'] > floor_thresh_db)
                    )
                return background_detected, {
                    "non_speech_ratio": non_speech_ratio,
                    "gap_db": levels['gap_db'],
                    "floor_db": levels['floor_db'],
                    "background_detected": background_detected
                }
            return False, {}
        finally:
            # Park cached pipelines on CPU so they don't hold accelerator memory
            # while Demucs (or other heavy models) loads later in extract_voice().
            # Keep them in _pipeline_cache so subsequent detect() calls can reuse
            # them without reloading from disk; _get_props() is expected to call
            # .to(self.torch_device) on retrieval.
            with _pipeline_lock:
                for p in _pipeline_cache.values():
                    try:
                        p.to('cpu')
                    except Exception:
                        pass
            # Drop local refs to free any short-lived tensors / annotations
            pipeline = waveform = sr = None
            gc.collect()
            if torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
                except Exception:
                    pass
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                try:
                    torch.xpu.empty_cache()
                except Exception:
                    pass
            if torch.backends.mps.is_available():
                try:
                    torch.mps.empty_cache()
                except Exception:
                    pass
