import os
import numpy as np
import librosa
from pyannote.audio import Pipeline

class BackgroundDetector:

    def __init__(self, wav_file: str, models_dir: str):
        self.wav_file   = wav_file
        self.models_dir = models_dir
        self.vad_pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection", use_auth_token=os.environ['HF_TOKEN'])

    def detect(self,
               frame_s: float = 1.0,
               overlap: float = 0.5,
               rms_db_thresh: float = None,
               energy_sigma_mul: float = 1.5,
               flatness_thresh: float = 0.3,
               zcr_thresh: float = 0.3,
               vad_ratio_thresh: float = 0.5):
        # --- load & frame the audio ---
        y, sr = librosa.load(self.wav_file, sr=None, mono=True)
        frame_len = int(frame_s * sr)
        hop_len   = int(frame_len * (1 - overlap))

        # --- compute spectral features ---
        rms      = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
        flatness = librosa.feature.spectral_flatness(y=y, n_fft=frame_len, hop_length=hop_len)[0]
        zcr      = librosa.feature.zero_crossing_rate(y, frame_length=frame_len, hop_length=hop_len)[0]

        # --- RMS flag (absolute dB or relative) ---
        if rms_db_thresh is not None:
            rms_db    = 20 * np.log10(rms + 1e-9)
            rms_flag  = (rms_db > rms_db_thresh).mean() > 0.5
        else:
            mean_rms  = rms.mean()
            std_rms   = rms.std()
            thresh    = mean_rms + energy_sigma_mul * std_rms
            rms_flag  = (rms > thresh).mean() > 0.5

        # --- flatness & ZCR flags ---
        flatness_flag = (flatness > flatness_thresh).any()
        zcr_flag = (zcr > zcr_thresh).any()

        # --- VAD (non-speech) flag ---
        # run the pipeline to get speech time segments
        diarization    = self.vad_pipeline(self.wav_file)
        speech_segments = [(s.start, s.end) for s in diarization.get_timeline()]
        total_duration = librosa.get_duration(filename=self.wav_file)
        speech_time    = sum(end - start for start, end in speech_segments)
        non_speech_ratio = 1 - (speech_time / total_duration)
        vad_flag       = non_speech_ratio > vad_ratio_thresh

        # --- combine into status & report ---
        status = any([rms_flag, flatness_flag, zcr_flag, vad_flag])
        report = {
            'rms_flag':              rms_flag,
            'flatness_flag':         flatness_flag,
            'zcr_flag':              zcr_flag,
            'vad_non_speech_ratio':  non_speech_ratio,
            'vad_flag':              vad_flag,
        }
        return status, report