import torch
import librosa
import threading

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from lib.conf import tts_dir
from lib.conf_models import default_voice_detection_model


_PIPELINE_CACHE = {}
_PIPELINE_LOCK = threading.Lock()

class BackgroundDetector:

    def __init__(self, wav_file: str):
        self.wav_file = wav_file
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.total_duration = librosa.get_duration(path=self.wav_file)

    def _get_pipeline(self) -> VoiceActivityDetection:
        """
        Return a cached voice activity detection pipeline for the current device.
        This method uses a per-device cache backed by a global dictionary
        (`_PIPELINE_CACHE`) and protects lazy initialization with a global lock
        (`_PIPELINE_LOCK`). The implementation follows a double-checked locking
        pattern:
        1. Check the cache without acquiring the lock for the common fast path.
        2. If the pipeline is missing, acquire the lock and check the cache again
           to avoid recreating the pipeline if another thread initialized it in
           the meantime.
        3. If still missing, create, configure, move to the appropriate device,
           and store the pipeline in the cache.
        This approach avoids repeatedly constructing the expensive pipeline while
        remaining safe when multiple threads share the same process-wide cache.
        """
        key = self.device.type
        if key in _PIPELINE_CACHE:
            return _PIPELINE_CACHE[key]
        with _PIPELINE_LOCK:
            if key in _PIPELINE_CACHE:
                return _PIPELINE_CACHE[key]
            model = Model.from_pretrained(
                default_voice_detection_model,
                cache_dir=tts_dir
            )
            pipeline = VoiceActivityDetection(segmentation=model)
            pipeline.instantiate({
                "min_duration_on": 0.0,
                "min_duration_off": 0.0
            })
            pipeline.to(self.device)
            _PIPELINE_CACHE[key] = pipeline
            return pipeline
    def detect(self, vad_ratio_thresh: float = 0.05) -> tuple[bool, dict[str, float | bool]]:
        pipeline = self._get_pipeline()
        annotation = pipeline(self.wav_file)
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