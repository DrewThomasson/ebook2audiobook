import hashlib
import math
import os
import shutil
import subprocess
import tempfile
import threading
import uuid

# Conditional imports for Kokoro TTS dependencies
try:
    import numpy as np
    import regex as re
    import soundfile as sf
    import torch
    import torchaudio
    from huggingface_hub import hf_hub_download
    
    # Try importing kokoro-specific dependencies
    try:
        from kokoro import generate  # Kokoro TTS main function
        KOKORO_AVAILABLE = True
    except ImportError:
        # Fallback if kokoro package not available
        KOKORO_AVAILABLE = False
    
    # Import common utils with all their dependencies
    try:
        from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
        from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid
    except ImportError as utils_import_error:
        print(f"Warning: Common utils import failed: {utils_import_error}. Using fallback implementations.")
        # Fallback implementations
        def unload_tts(*args, **kwargs): pass
        def append_sentence2vtt(*args, **kwargs): return 1
        def detect_gender(*args, **kwargs): return "unknown"
        def trim_audio(audio, *args, **kwargs): return audio
        def normalize_audio(audio, *args, **kwargs): return audio
        def is_audio_data_valid(audio_data): 
            return isinstance(audio_data, np.ndarray) and len(audio_data) > 0
    KOKORO_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    KOKORO_DEPENDENCIES_AVAILABLE = False
    KOKORO_AVAILABLE = False
    _missing_dependency_error = str(e)
    # Define placeholder functions for when dependencies are missing
    def unload_tts(*args, **kwargs): pass
    def append_sentence2vtt(*args, **kwargs): return 1
    def detect_gender(*args, **kwargs): return "unknown"
    def trim_audio(audio, *args, **kwargs): return audio if hasattr(audio, 'shape') else torch.zeros(1, 1000)
    def normalize_audio(audio, *args, **kwargs): return audio if hasattr(audio, 'shape') else torch.zeros(1, 1000)
    def is_audio_data_valid(audio_data): 
        try:
            import numpy as np
            return isinstance(audio_data, np.ndarray) and len(audio_data) > 0
        except:
            return False
    def generate(*args, **kwargs): 
        try:
            import numpy as np
            return np.array([])
        except:
            return []

from pathlib import Path
from pprint import pprint

from lib import *

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

class Coqui:

    def __init__(self, session):
        try:
            if not KOKORO_DEPENDENCIES_AVAILABLE:
                raise ImportError(f"Kokoro TTS dependencies not available: {_missing_dependency_error}. Please install: pip install torch torchaudio numpy soundfile huggingface_hub kokoro-tts")
            
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
            # Add semitones cache to support voice cloning pitch adaptation (like VITS path)
            self.params = {TTS_ENGINES['KOKORO']: {"semitones": {}}}
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
                if self.session['tts_engine'] == TTS_ENGINES['KOKORO']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        model_path = self._get_default_model_path()
                        tts = self._load_api(self.tts_key, model_path, self.session['device'])

            # If a reference voice is provided, attempt to load the voice conversion engine
            # to enable "cloning" via VC, similar to the VITS path.
            if self.session.get('voice'):
                tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                if not tts_vc:
                    # Load VC model using a generic TTS API loader (separate from Kokoro)
                    tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model, self.session['device'])

            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            error = f'build() error: {e}'
            print(error)
            return False

    def _get_default_model_path(self):
        """Get the default Kokoro model based on language"""
        # Default to English model
        lang_code = self.session.get('language', 'eng')
        
        # Default models mapping for Kokoro
        default_models = {
            'en': 'Kokoro-82M',
            'eng': 'Kokoro-82M'
        }
        
        model_name = default_models.get(lang_code, 'Kokoro-82M')
        return model_name

    def _load_api(self, key, model_path, device):
        # Kokoro TTS model loader
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_key, self.tts_vc_key])
            with lock:
                # Download the model files if needed
                model_file, config_file = self._download_model(model_path)
                
                if not KOKORO_AVAILABLE:
                    print("Kokoro TTS package not available. Please install with: pip install kokoro-tts")
                    return False
                
                # Load Kokoro model
                tts = self._load_kokoro_model(model_file, config_file, device)
                if tts:
                    loaded_tts[key] = {"engine": tts, "config": config_file} 
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

    def _load_kokoro_model(self, model_file, config_file, device):
        """Load Kokoro model with appropriate configuration"""
        try:
            # Create a simple wrapper for Kokoro TTS functionality
            class KokoroWrapper:
                def __init__(self, model_path, config_path, device):
                    self.model_path = model_path
                    self.config_path = config_path
                    self.device = device
                    
                def synthesize(self, text):
                    """Synthesize text using Kokoro TTS"""
                    try:
                        # Use the kokoro generate function
                        # This is a placeholder - actual implementation depends on Kokoro API
                        audio_data = generate(text, model_path=self.model_path, device=self.device)
                        return audio_data
                    except Exception as e:
                        print(f"Kokoro synthesis error: {e}")
                        return np.array([])
            
            return KokoroWrapper(model_file, config_file, device)
        except Exception as e:
            print(f"Error loading Kokoro model: {e}")
            return None

    def _load_vc_engine(self, key, model_path, device):
        # Generic TTS/VC model loader (used for voice conversion engine), similar to coqui.py
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_vc_key])
            with lock:
                try:
                    from TTS.api import TTS as CoquiAPI  # Lazy import to avoid hard dependency if not needed
                except Exception as e:
                    print(f"Voice conversion dependencies not available: {e}. Install Coqui TTS to enable cloning.")
                    return False
                tts = CoquiAPI(model_path)
                if tts:
                    if device == 'cuda':
                        tts.cuda()
                    else:
                        tts.to(device)
                    loaded_tts[key] = {"engine": tts, "config": None}
                    msg = f'{model_path} (VC) Loaded!'
                    print(msg)
                    return tts
                else:
                    print('VC engine could not be created!')
        except Exception as e:
            print(f'_load_vc_engine() error: {e}')
        return False

    def _download_model(self, model_name):
        """Download Kokoro model files from HuggingFace"""
        try:
            # Create model directory
            model_dir = os.path.join(tts_dir, 'kokoro', model_name)
            os.makedirs(model_dir, exist_ok=True)
            
            # Determine the files to download based on model type
            if 'GGUF' in model_name:
                model_file = os.path.join(model_dir, 'kokoro-v0_19.q8_0.gguf')
                config_file = os.path.join(model_dir, 'config.json')
                files_to_download = ['kokoro-v0_19.q8_0.gguf', 'config.json']
            else:
                model_file = os.path.join(model_dir, 'model.pth')
                config_file = os.path.join(model_dir, 'config.json')
                files_to_download = ['model.pth', 'config.json']
            
            # Check if files already exist
            if all(os.path.exists(os.path.join(model_dir, f)) for f in files_to_download):
                return model_file, config_file
            
            # Get the appropriate repository
            repo_mapping = {
                'Kokoro-82M': 'hexgrad/Kokoro-82M',
                'Kokoro-82M-GGUF': 'hexgrad/Kokoro-82M-GGUF'
            }
            
            repo_id = repo_mapping.get(model_name, 'hexgrad/Kokoro-82M')
            
            # Download each file
            for filename in files_to_download:
                try:
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        local_dir=model_dir,
                        local_dir_use_symlinks=False
                    )
                except Exception as e:
                    print(f"Failed to download {filename}: {e}")
                    # Continue with other files
                    
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
                model_file = os.path.join(checkpoint_dir, 'model.pth')
                config_file = os.path.join(checkpoint_dir, 'config.json')
                tts = self._load_kokoro_model(model_file, config_file, device)
                
            if tts:
                loaded_tts[key] = {"engine": tts, "config": config_file}
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

    def _synthesize_with_kokoro(self, tts, sentence):
        """Synthesize a sentence with Kokoro and return a numpy array."""
        try:
            audio_data = tts.synthesize(sentence)
            if isinstance(audio_data, np.ndarray) and len(audio_data) > 0:
                return audio_data
        except Exception as e:
            print(f"Kokoro synthesis error: {e}")
        return np.array([])

    def convert(self, sentence_number, sentence):
        try:
            speaker = None
            audio_data = False
            trim_audio_buffer = 0.004
            settings = self.params[self.session['tts_engine']]
            final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            sentence = sentence.strip()

            # Reference voice path (if provided) enables VC-based cloning akin to VITS path
            settings['voice_path'] = self.session.get('voice', None)

            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if tts:
                if sentence and sentence[-1].isalnum():
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
                    # First, synthesize with Kokoro
                    audio_sentence = self._synthesize_with_kokoro(tts, sentence)

                    # If a reference voice is provided, perform VC-based cloning like VITS path
                    if settings.get('voice_path'):
                        try:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")

                            # Save Kokoro synthesis to tmp_in_wav
                            if is_audio_data_valid(audio_sentence):
                                sf.write(tmp_in_wav, audio_sentence, settings['samplerate'], subtype="PCM_16")
                            else:
                                # Nothing synthesized, fall back to silent segment
                                sf.write(tmp_in_wav, np.zeros(int(settings['samplerate'] * 0.1)), settings['samplerate'], subtype="PCM_16")

                            # Determine and cache semitones shift based on gender detection
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = detect_gender(settings['voice_path'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                                print(msg)
                                if voice_builtin_gender != voice_path_gender and voice_path_gender in ['male', 'female'] and voice_builtin_gender in ['male', 'female']:
                                    semitones = -4 if voice_path_gender == 'male' else 4
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    semitones = 0
                                settings['semitones'][settings['voice_path']] = semitones

                            # Pitch shift if needed using sox
                            if semitones > 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(settings['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                                except Exception as e:
                                    print(f"Pitch shift failed: {e}")
                                    tmp_out_wav = tmp_in_wav
                            else:
                                tmp_out_wav = tmp_in_wav

                            # Load VC engine and perform conversion
                            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                            if not tts_vc:
                                tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model, self.session['device'])
                            if tts_vc:
                                # Use VC samplerate
                                settings['samplerate'] = TTS_VOICE_CONVERSION[self.tts_vc_key]['samplerate']
                                source_wav = self._resample_wav(tmp_out_wav, settings['samplerate'])
                                target_wav = self._resample_wav(settings['voice_path'], settings['samplerate'])
                                audio_sentence = tts_vc.voice_conversion(
                                    source_wav=source_wav,
                                    target_wav=target_wav
                                )
                                # Cleanup
                                if os.path.exists(source_wav) and source_wav != tmp_out_wav:
                                    os.remove(source_wav)
                            else:
                                print(f'Engine {self.tts_vc_key} is None; skipping voice cloning.')

                            # Cleanup temp files
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav) and tmp_out_wav != tmp_in_wav:
                                os.remove(tmp_out_wav)
                        except Exception as e:
                            print(f"Kokoro VC cloning path failed, proceeding with Kokoro voice only. Error: {e}")

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
            error = f'Coqui.convert(): {e}'
            raise ValueError(e)
        return False