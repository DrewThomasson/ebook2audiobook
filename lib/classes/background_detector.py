import torch, librosa, threading
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from lib.conf import tts_dir
from lib.conf_models import default_voice_detection_model

_pipeline_cache = {}
_pipeline_lock = threading.Lock()

class BackgroundDetector:

	def __init__(self, wav_file: str):
		self.wav_file = wav_file
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		self.total_duration = self._get_duration()

	def _get_duration(self) -> float:
		try:
			return float(librosa.get_duration(path=self.wav_file))
		except Exception:
			return 0.0

	def _load_waveform(self) -> tuple[torch.Tensor, int]:
		y, sr = librosa.load(self.wav_file, sr=16000, mono=True)
		waveform = torch.from_numpy(y).float().unsqueeze(0)
		return waveform, sr

	def _get_pipeline(self) -> VoiceActivityDetection:
		key = self.device.type
		if key in _pipeline_cache:
			return _pipeline_cache[key]
		with _pipeline_lock:
			if key in _pipeline_cache:
				return _pipeline_cache[key]
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
			_pipeline_cache[key] = pipeline
			return pipeline

	def detect(self, vad_ratio_thresh: float = 0.05) -> tuple[bool, dict[str, float | bool]]:
		pipeline = self._get_pipeline()
		waveform, sr = self._load_waveform()
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