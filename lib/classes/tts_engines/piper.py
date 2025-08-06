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
from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

class Coqui:

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
            self.params = {TTS_ENGINES['PIPER']: {}}
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
                if self.session['tts_engine'] == TTS_ENGINES['PIPER']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        model_path = self._get_default_model_path()
                        tts = self._load_api(self.tts_key, model_path, self.session['device'])
            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            error = f'build() error: {e}'
            print(error)
            return False

    def _get_default_model_path(self):
        """Get the default Piper model based on language"""
        # Default to English model
        lang_code = self.session.get('language', 'eng')
        piper_lang = language_tts.get('piper', {}).get(lang_code, 'en')
        
        # Default models mapping
        default_models = {
            'en': 'en_US-lessac-medium',
            'de': 'de_DE-karlsson-low', 
            'es': 'es_ES-mms-medium',
            'fr': 'fr_FR-mls-medium',
            'it': 'it_IT-mms-medium',
            'ru': 'ru_RU-mms-medium',
            'ja': 'ja_JP-mms-medium',
            'ko': 'ko_KR-mms-medium',
            'zh': 'zh_CN-mms-medium'
        }
        
        model_name = default_models.get(piper_lang, 'en_US-lessac-medium')
        return model_name

    def _load_api(self, key, model_path, device):
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_key, self.tts_vc_key])
            with lock:
                from piper import PiperVoice
                # Download the model files if needed
                model_file, config_file = self._download_model(model_path)
                tts = PiperVoice.load(model_file, config_file)
                if tts:
                    loaded_tts[key] = {"engine": tts, "config": None} 
                    msg = f'{model_path} Loaded!'
                    print(msg)
                    return tts
                else:
                    error = 'TTS engine could not be created!'
                    print(error)
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
        return False

    def _download_model(self, model_name):
        """Download Piper model files from HuggingFace"""
        try:
            # Create model directory
            model_dir = os.path.join(tts_dir, 'piper', model_name)
            os.makedirs(model_dir, exist_ok=True)
            
            model_file = os.path.join(model_dir, f'{model_name}.onnx')
            config_file = os.path.join(model_dir, f'{model_name}.onnx.json')
            
            # Check if files already exist
            if os.path.exists(model_file) and os.path.exists(config_file):
                return model_file, config_file
            
            # Parse model name to get the correct path
            # Example: en_US-lessac-medium -> en/en_US/lessac/medium/
            parts = model_name.split('-')
            if len(parts) >= 3:
                lang_country = parts[0]  # en_US
                voice_name = parts[1]    # lessac  
                quality = parts[2]       # medium
                
                # Extract language code (en from en_US)
                lang_code = lang_country.split('_')[0]
                
                # Build the HuggingFace path
                hf_path = f"{lang_code}/{lang_country}/{voice_name}/{quality}/"
            else:
                # Fallback for unexpected format
                hf_path = f"en/en_US/lessac/medium/"
            
            repo_id = "rhasspy/piper-voices"
            
            # Download model file
            hf_hub_download(
                repo_id=repo_id,
                filename=f"{hf_path}{model_name}.onnx",
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            # Download config file  
            hf_hub_download(
                repo_id=repo_id,
                filename=f"{hf_path}{model_name}.onnx.json",
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            
            # The files are downloaded with their full path, move them to the expected location
            downloaded_model = os.path.join(model_dir, hf_path, f"{model_name}.onnx")
            downloaded_config = os.path.join(model_dir, hf_path, f"{model_name}.onnx.json")
            
            if os.path.exists(downloaded_model):
                shutil.move(downloaded_model, model_file)
            if os.path.exists(downloaded_config):
                shutil.move(downloaded_config, config_file)
            
            # Clean up the directory structure
            lang_dir = os.path.join(model_dir, lang_code)
            if os.path.exists(lang_dir):
                shutil.rmtree(lang_dir)
                
            return model_file, config_file
            
        except Exception as e:
            error = f'_download_model() error: {e}'
            print(error)
            # Fall back to local model if available
            return model_file, config_file

    def _load_checkpoint(self, **kwargs):
        global lock
        try:
            key = kwargs.get('key')
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            tts_engine = kwargs.get('tts_engine')
            device = kwargs.get('device')
            unload_tts(device, [self.tts_key])
            with lock:
                checkpoint_dir = kwargs.get('checkpoint_dir')
                from piper import PiperVoice
                model_file = os.path.join(checkpoint_dir, 'model.onnx')
                config_file = os.path.join(checkpoint_dir, 'config.json')
                tts = PiperVoice.load(model_file, config_file)
                
            if tts:
                loaded_tts[key] = {"engine": tts, "config": None}
                msg = f'{tts_engine} Loaded!'
                print(msg)
                return tts
            else:
                error = 'TTS engine could not be created!'
                print(error)
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
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
                    if self.session['tts_engine'] == TTS_ENGINES['PIPER']:
                        # Use Piper TTS to synthesize audio
                        audio_chunks = list(tts.synthesize(sentence))
                        if audio_chunks:
                            # Concatenate audio chunks
                            audio_arrays = []
                            for chunk in audio_chunks:
                                audio_arrays.append(chunk.audio_float_array)
                            
                            if audio_arrays:
                                audio_sentence = np.concatenate(audio_arrays)
                            else:
                                audio_sentence = np.array([])
                        else:
                            audio_sentence = np.array([])
                            
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
            error = f'Coquit.convert(): {e}'
            raise ValueError(e)
        return False