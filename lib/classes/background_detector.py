import os
import numpy as np
import librosa

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from lib.conf import tts_dir
from lib.models import default_voice_detection_model

class BackgroundDetector:

    def __init__(self, wav_file: str):
        self.wav_file   = wav_file
        model = Model.from_pretrained(default_voice_detection_model, cache_dir=tts_dir)
        self.pipeline = VoiceActivityDetection(segmentation=model)
        hyper_params = {
          # onset/offset activation thresholds
          "onset": 0.5, "offset": 0.5,
          # remove speech regions shorter than that many seconds.
          "min_duration_on": 0.0,
          # fill non-speech regions shorter than that many seconds.
          "min_duration_off": 0.0
        }
        self.pipeline.instantiate(hyper_params)

    def detect(self, vad_ratio_thresh: float=0.05):
        diarization     = self.pipeline(self.wav_file)
        speech_segments = [(s.start, s.end) for s in diarization.get_timeline()]
        total_duration  = librosa.get_duration(path=self.wav_file)
        speech_time     = sum(end - start for start, end in speech_segments)
        non_speech_ratio = 1 - (speech_time / total_duration)
        status = non_speech_ratio > vad_ratio_thresh
        report = {
            'non_speech_ratio': non_speech_ratio,
            'background_detected': status
        }
        return status, report