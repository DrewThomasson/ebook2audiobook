import threading, warnings

from lib.conf import tts_dir, devices
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
    def __init__(self, wav_file: str)->None:
        self.wav_file = wav_file
        self.device = None
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
            torch.backends.cudnn.enabled = False
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() and getattr(torch.version, 'hip', None) is None
            else 'xpu' if hasattr(torch, 'xpu') and torch.xpu.is_available()
            else 'mps' if torch.backends.mps.is_available()
            else 'cpu'
        )
        key = self.device.type
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
                    pipeline.to(self.device)
                    _pipeline_cache[key] = pipeline
        if pipeline:
            y, sr = librosa.load(self.wav_file, sr=16000, mono=True)
            waveform = torch.from_numpy(y).float().unsqueeze(0)
            return pipeline, waveform, sr
        return None, None, None

    def detect(self, vad_ratio_thresh:float=0.05)->tuple[bool, dict[str, float|bool]]:
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
                background_detected = non_speech_ratio > vad_ratio_thresh
                return background_detected, {
                    "non_speech_ratio": non_speech_ratio,
                    "background_detected": background_detected
                }
            return False, {}
        finally:
            with _pipeline_lock:
                for p in list(_pipeline_cache.values()):
                    try:
                        p.to('cpu')
                    except Exception:
                        pass
                _pipeline_cache.clear()
            pipeline = waveform = sr = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
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