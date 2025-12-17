import torch
import librosa
import threading

from pyannote.audio import Model, Audio
from pyannote.core import SlidingWindowFeature
from lib.conf import tts_dir
from lib.models import default_voice_detection_model


_MODEL_CACHE = {}
_MODEL_LOCK = threading.Lock()


class BackgroundDetector:

	def __init__(self, wav_file: str):
		self.wav_file = wav_file
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.total_duration = librosa.get_duration(path=self.wav_file)

		self.audio = Audio(sample_rate=16000, mono=True)

	def _get_model(self) -> Model:
		"""
		Return a segmentation model instance safe for multiprocessing
		and multithreading. One model per process/device.
		"""
		key = self.device.type

		if key in _MODEL_CACHE:
			return _MODEL_CACHE[key]

		with _MODEL_LOCK:
			if key in _MODEL_CACHE:
				return _MODEL_CACHE[key]

			model = Model.from_pretrained(
				default_voice_detection_model,
				cache_dir=tts_dir
			)

			model.to(self.device)
			model.eval()
			_MODEL_CACHE[key] = model
			return model

	def _speech_time_from_segmentation(
		self,
		segmentation: SlidingWindowFeature,
		threshold: float = 0.5
	) -> float:
		data = segmentation.data

		if data.ndim == 2:
			speech_frames = (data >= threshold).any(axis=1)
		else:
			speech_frames = data >= threshold

		window = segmentation.sliding_window
		return float(speech_frames.sum() * window.step)

	def detect(self, vad_ratio_thresh: float = 0.05) -> tuple[bool, dict[str, float | bool]]:
		model = self._get_model()

		waveform, sample_rate = self.audio(self.wav_file)

		waveform = waveform.to(self.device)

		with torch.no_grad():
			segmentation = model(waveform)

		speech_time = self._speech_time_from_segmentation(segmentation)
		non_speech_ratio = 1.0 - (
			speech_time / self.total_duration if self.total_duration > 0 else 0.0
		)

		background_detected = non_speech_ratio > vad_ratio_thresh

		return background_detected, {
			"non_speech_ratio": non_speech_ratio,
			"background_detected": background_detected
		}