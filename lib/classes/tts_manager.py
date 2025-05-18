import os
import numpy as np
import regex as re
import shutil
import soundfile as sf
import subprocess
import tempfile
import torch
import torchaudio
import threading
import uuid

from huggingface_hub import hf_hub_download
from pathlib import Path
from scipy.io import wavfile as wav
from scipy.signal import find_peaks

from lib.models import *
from lib.conf import voices_dir, models_dir, default_audio_proc_format
from lib.lang import language_tts

_original_multinomial = torch.multinomial

def _safe_multinomial(input, num_samples, replacement=False, *, generator=None, out=None):
	with torch.no_grad():
		input = torch.nan_to_num(input, nan=0.0, posinf=0.0, neginf=0.0)
		input = torch.clamp(input, min=0.0)
		sum_input = input.sum(dim=-1, keepdim=True)
		input = input / (sum_input + 1e-9)  # Normalize
	return _original_multinomial(input, num_samples, replacement=replacement, generator=generator, out=out)

torch.multinomial = _safe_multinomial

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.params = {}
        self.sentences_total_time = 0.0
        self.sentence_idx = 1
        self.vtt_path = os.path.splitext(session['epub_path'])[0] + '.vtt'
        self._build()
 
    def _build(self):
        model_path = None
        config_path = None
        vocab_path = None
        if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
            from lib.classes.tts_engines.coqui import Coqui
            self.params['tts'] = Coqui(self.session)
        else:
            print('Other TTS engines coming soon!')
        if self.params['tts'] is None:
            error = 'TTS engine could not be created!'
            print(error)

    def _tensor_type(self, audio_data):
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data, np.ndarray):  
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data, list):  
            return torch.tensor(audio_data, dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")

    def _append_sentence_to_vtt(self, sentence_obj, path):
        def format_timestamp(seconds):
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return f"{int(h):02}:{int(m):02}:{s:06.3f}"

        index = 1
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if "-->" in line:
                        index += 1
        if index > 1 and "resume_check" in sentence_obj and sentence_obj["resume_check"] < index:
            return index  # Already written
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\r\n\r\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(sentence_obj["start"])
            end = format_timestamp(sentence_obj["end"])
            text = sentence_obj["text"].replace("\n", " ").strip()
            f.write(f"{start} --> {end}\n{text}\r\n\r\n")
        return index + 1

    def convert_sentence_to_audio(self):
        try:
            audio_data = None
            if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
                return Coqui.convert()
            else:
                print('Other TTS engines coming soon!')    
                return False
        except Exception as e:
            error = f'convert_sentence_to_audio(): {e}'
            raise ValueError(e)
            return False