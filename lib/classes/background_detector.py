import threading

from lib.conf import tts_dir
from lib.conf_models import default_voice_detection_model

_pipeline_cache = {}
_pipeline_lock = threading.Lock()

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
        from pyannote.audio import Model
        from pyannote.audio.pipelines import VoiceActivityDetection
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
        if pipeline is not None and waveform and sr:
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