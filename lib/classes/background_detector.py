import os
import numpy as np
import librosa
from pyannote.audio import Pipeline

class BackgroundDetector:

    def __init__(self, wav_file: str, models_dir: str):
        self.wav_file   = wav_file
        self.models_dir = models_dir
        self.vad_pipeline = Pipeline.from_pretrained("zermok/voice-activity-detection")

    def detect(self, vad_ratio_thresh: float=0.05):
        diarization     = self.vad_pipeline(self.wav_file)
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