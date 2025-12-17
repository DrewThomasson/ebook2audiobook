import torch
import librosa
import threading

from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from lib.conf import tts_dir
from lib.models import default_voice_detection_model


_PIPELINE_CACHE = {}
_PIPELINE_LOCK = threading.Lock()


class BackgroundDetector:

	def __init__(self, wav_file: str):
		self.wav_file = wav_file
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.total_duration = librosa.get_duration(path=self.wav_file)

	def _get_pipeline(self) -> VoiceActivityDetection:
		"""
		Return a VoiceActivityDetection pipeline instance that is safe
		for multithreading and multiprocessing.

		One pipeline per process/device.
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
				"onset": 0.5,
				"offset": 0.5,
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