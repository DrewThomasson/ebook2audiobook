import threading

from lib.conf import tts_dir
from lib.conf_models import default_voice_detection_model

_pipeline_cache = {}
_pipeline_lock = threading.Lock()

def pyannote_patch()->None:
    '''Restore APIs removed in torchaudio >=2.9 that pyannote.audio's
    transitive deps (speechbrain, asteroid-filterbanks, silero-vad, …)
    still call at import time. pyannote.audio 4.x itself moved to
    torchcodec, but those upstream packages haven't.
    Idempotent: safe to call from both app entrypoint and lazy paths.
    '''
    import torchaudio
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
                import soundfile  # noqa: F401
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
        self.device = torch.device(
            'cuda' if torch.cuda.is_available()
            else 'xpu' if hasattr(torch, 'xpu') and torch.xpu.is_available()
            else 'mps' if torch.backends.mps.is_available()
            else 'cpu'
        )
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        key = self.device.type
        if key in _pipeline_cache:
            pipeline = _pipeline_cache[key]
        with _pipeline_lock:
            if key in _pipeline_cache:
                pipeline = _pipeline_cache[key]
            else:
                model = Model.from_pretrained(
                    default_voice_detection_model,
                    cache_dir=tts_dir
                )
                pipeline = VoiceActivityDetection(segmentation=model)
                if pipeline:
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
        pipeline, waveform, sr = self._get_props()
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