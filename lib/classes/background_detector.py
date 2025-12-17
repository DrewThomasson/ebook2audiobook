import os
import torch
import librosa

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from lib.conf import tts_dir
from lib.models import default_voice_detection_model

class BackgroundDetector:

	def __init__(self, wav_file:str):
        self.wav_file = wav_file

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = Model.from_pretrained(
            default_voice_detection_model,
            cache_dir=tts_dir
        )

        self.pipeline = VoiceActivityDetection(segmentation=model)
        hyper_params = {
            # onset/offset activation thresholds
            "onset":0.5,"offset":0.5,
            # remove speech regions shorter than that many seconds.
            "min_duration_on":0.0,
            # fill non-speech regions shorter than that many seconds.
            "min_duration_off":0.0
        }
        self.pipeline.instantiate(hyper_params)
        self.pipeline.to(device)
        self.total_duration = librosa.get_duration(path=self.wav_file)

	def detect(self, vad_ratio_thresh:float=0.05)->tuple[bool, dict[str, float | bool]]:
		annotation = self.pipeline(self.wav_file)

		speech_time = sum(
			segment.end - segment.start
			for segment in annotation.itersegments()
		)

		non_speech_ratio = 1.0 - (speech_time / self.total_duration if self.total_duration > 0 else 0.0)

		background_detected = non_speech_ratio > vad_ratio_thresh

		report = {
			"non_speech_ratio": non_speech_ratio,
			"background_detected": background_detected,
		}

		return background_detected, report