import hashlib
import math
import os
import shutil
import subprocess
import tempfile
import threading
import uuid

import numpy as np
import regex as re
import soundfile as sf
import torch
import torchaudio

from huggingface_hub import hf_hub_download
from pathlib import Path
from pprint import pprint

from lib import *
try:
    from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
    from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid
except ImportError as e:
    # Fallback for missing dependencies during development/testing
    print(f"Warning: Some TTS engine utilities not available: {e}")
    
    def unload_tts(*args, **kwargs):
        pass
    
    def append_sentence2vtt(*args, **kwargs):
        return 1
        
    def detect_gender(*args, **kwargs):
        return "unknown"
        
    def trim_audio(audio_tensor, *args, **kwargs):
        return audio_tensor
        
    def normalize_audio(*args, **kwargs):
        return True
        
    def is_audio_data_valid(audio_data):
        return audio_data is not None

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

class F5TTS:

    def __init__(self, session):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
            self.tts_vc_key = default_vc_model.rsplit('/', 1)[-1]
            self.is_bf16 = True if self.session['device'] == 'cuda' and torch.cuda.is_bf16_supported() == True else False
            self.npz_path = None
            self.npz_data = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.params = {TTS_ENGINES['F5TTS']: {}}
            self.params[self.session['tts_engine']]['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt')    
            self.resampler_cache = {}
            self.audio_segments = []
            self._build()
        except Exception as e:
            error = f'__init__() error: {e}'
            print(error)
            return None

    def _build(self):
        try:
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                if self.session['tts_engine'] == TTS_ENGINES['F5TTS']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                        tts = self._load_api(self.tts_key, model_path, self.session['device'])
            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            error = f'build() error: {e}'
            print(error)
            return False

    def _load_api(self, key, model_path, device):
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_key, self.tts_vc_key])
            with lock:
                from f5_tts.api import F5TTS as F5TTSModel
                tts = F5TTSModel(model="F5TTS_v1_Base", device=device)
                if tts:
                    loaded_tts[key] = {"engine": tts, "config": None} 
                    msg = f'F5-TTS {model_path} Loaded!'
                    print(msg)
                    return tts
                else:
                    error = 'F5-TTS engine could not be created!'
                    print(error)
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
        return False
        
    def _tensor_type(self, audio_data):
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data, np.ndarray):  
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data, list):  
            return torch.tensor(audio_data, dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")
            
    def _get_resampler(self, orig_sr, target_sr):
        key = (orig_sr, target_sr)
        if key not in self.resampler_cache:
            self.resampler_cache[key] = torchaudio.transforms.Resample(
                orig_freq=orig_sr, new_freq=target_sr
            )
        return self.resampler_cache[key]

    def _resample_wav(self, wav_path, expected_sr):
        waveform, orig_sr = torchaudio.load(wav_path)
        if orig_sr == expected_sr and waveform.size(0) == 1:
            return wav_path
        if waveform.size(0) > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if orig_sr != expected_sr:
            resampler = self._get_resampler(orig_sr, expected_sr)
            waveform = resampler(waveform)
        wav_tensor = waveform.squeeze(0)
        wav_numpy = wav_tensor.cpu().numpy()
        tmp_fh = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path, wav_numpy, expected_sr, subtype="PCM_16")
        return tmp_path

    def convert(self, sentence_number, sentence):
        try:
            speaker = None
            audio_data = False
            trim_audio_buffer = 0.004
            settings = self.params[self.session['tts_engine']]
            final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            sentence = sentence.strip()
            settings['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'ref.wav') if self.session['custom_model'] is not None
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            if settings['voice_path'] is not None:
                speaker = re.sub(r'\.wav$', '', os.path.basename(settings['voice_path']))
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if tts:
                if sentence[-1].isalnum():
                    sentence = f'{sentence} —'
                if sentence == TTS_SML['break']:
                    break_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(0.3, 0.6) * 100) / 100))) # 0.4 to 0.7 seconds
                    self.audio_segments.append(break_tensor.clone())
                    return True
                elif sentence == TTS_SML['pause']:
                    pause_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(1.0, 1.8) * 100) / 100))) # 1.0 to 1.8 seconds
                    self.audio_segments.append(pause_tensor.clone())
                    return True
                else:
                    if self.session['tts_engine'] == TTS_ENGINES['F5TTS']:
                        # F5-TTS specific generation
                        nfe_step = self.session.get('nfe_step') or default_engine_settings[TTS_ENGINES['F5TTS']].get('nfe', 32)
                        cfg_strength = self.session.get('cfg_strength') or default_engine_settings[TTS_ENGINES['F5TTS']].get('cfg_strength', 2.0)
                        
                        # Generate audio with F5-TTS
                        audio_sentence, _ = tts.infer(
                            ref_file=settings['voice_path'],
                            ref_text="",  # Let F5-TTS auto-transcribe
                            gen_text=sentence,
                            show_info=lambda x: None,  # Suppress info prints
                            progress=lambda x: x,      # Suppress progress bars
                            target_rms=0.1,
                            cross_fade_duration=0.15,
                            sway_sampling_coef=-1,
                            cfg_strength=cfg_strength,
                            nfe_step=nfe_step,
                            speed=1.0,
                            remove_silence=True
                        )
                        
                    if is_audio_data_valid(audio_sentence):
                        sourceTensor = self._tensor_type(audio_sentence)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        if sentence[-1].isalnum() or sentence[-1] == '—':
                            audio_tensor = trim_audio(audio_tensor.squeeze(), settings['samplerate'], 0.003, trim_audio_buffer).unsqueeze(0)
                        self.audio_segments.append(audio_tensor)
                        if not re.search(r'\w$', sentence, flags=re.UNICODE):
                            break_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(0.3, 0.6) * 100) / 100)))
                            self.audio_segments.append(break_tensor.clone())
                        if self.audio_segments:
                            audio_tensor = torch.cat(self.audio_segments, dim=-1)
                            start_time = self.sentences_total_time
                            duration = audio_tensor.shape[-1] / settings['samplerate']
                            end_time = start_time + duration
                            self.sentences_total_time = end_time
                            sentence_obj = {
                                "start": start_time,
                                "end": end_time,
                                "text": sentence,
                                "resume_check": self.sentence_idx
                            }
                            self.sentence_idx = append_sentence2vtt(sentence_obj, self.vtt_path)
                            if self.sentence_idx:
                                torchaudio.save(final_sentence_file, audio_tensor, settings['samplerate'], format=default_audio_proc_format)
                                del audio_tensor
                        self.audio_segments = []
                        if os.path.exists(final_sentence_file):
                            return True
                        else:
                            error = f"Cannot create {final_sentence_file}"
                            print(error)
            else:
                error = f"convert() error: {self.session['tts_engine']} is None"
                print(error)
        except Exception as e:
            error = f'F5TTS.convert(): {e}'
            raise ValueError(e)
        return False