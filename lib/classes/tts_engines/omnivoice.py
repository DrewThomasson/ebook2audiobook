import os
import sys
import subprocess
from unittest.mock import MagicMock

# 1. Dynamic check & install of requirements
try:
    import accelerate
    import tensorboardX
    import webdataset
    import librosa
except ImportError:
    print("OmniVoice dependencies missing. Installing from omnivoice-requirments.txt...")
    req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "omnivoice-requirments.txt"))
    if os.path.exists(req_path):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
    else:
        # Fallback if omnivoice-requirments.txt is not found
        subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers>=5.3.0", "accelerate", "tensorboardX", "webdataset", "librosa"])
    import accelerate
    import tensorboardX
    import webdataset
    import librosa

# 2. Add OmniVoice directory to sys.path
omnivoice_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "omnivoice_src"))
if omnivoice_src_path not in sys.path:
    sys.path.insert(0, omnivoice_src_path)

from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class OmniVoiceEngine(TTSUtils, TTSRegistry, name='omnivoice'):

    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.xtts_speakers = self._load_xtts_builtin_list()
            
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}'
                raise ValueError(error)
                
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate'):
                if required_key not in model_cfg:
                    error = f'fine_tuned model {fine_tuned} is missing required key {required_key}.'
                    raise ValueError(error)
                    
            self.params['samplerate'] = model_cfg['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            
            # Map language code
            self.lang_map = default_engine_settings[self.session['tts_engine']].get('languages', {})
            ebook_lang = self.session.get('language')
            self.language = self.lang_map.get(ebook_lang, 'en')
            
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self) -> Any:
        msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
        print(msg)
        self.cleanup_memory()
        
        engine = loaded_tts.get(self.tts_key)
        if engine:
            msg = f"TTS {self.tts_key} already loaded"
            print(msg)
            return engine
            
        try:
            import torch
            from omnivoice import OmniVoice
            
            model_cfg = self.models[self.session['fine_tuned']]
            hf_repo = model_cfg['repo']
            
            print(f"Loading OmniVoice model from {hf_repo} on device {self.device}...")
            model = OmniVoice.from_pretrained(
                hf_repo,
                device_map=self.device,
                torch_dtype=self.amp_dtype
            )
            
            loaded_tts[self.tts_key] = model
            print("OmniVoice model Loaded Successfully!")
            return model
        except Exception as e:
            error = f"load_engine() failure: {e}"
            raise RuntimeError(error) from e

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        try:
            import torch
            import numpy as np
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
            
            if self.engine:
                sentence_parts = self._split_sentence_on_sml(sentence)
                not_supported_punc_pattern = re.compile(r'[—]')
                
                self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
                if self.params.get('inline_voice'):
                    self.params['current_voice'] = self.params['inline_voice']
                else:
                    self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                    if self.params['current_voice'] is None and error is not None:
                        return False, error
                    if self.session['voice'] == self.params['block_voice']:
                        self.session['voice'] = self.params['current_voice']
                    self.params['block_voice'] = self.params['current_voice']
                    
                self.audio_segments = []
                ref_audio_path = self.params['current_voice']
                instruct = kwargs.get('instruct', None)
                
                for part in sentence_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        success, error = self._convert_sml(part)
                        if not success:
                            return False, error
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                        
                    # Normalize punctuation
                    part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                    
                    with torch.inference_mode():
                        generate_kwargs = {}
                        if ref_audio_path and os.path.exists(ref_audio_path):
                            generate_kwargs['ref_audio'] = ref_audio_path
                        elif instruct:
                            generate_kwargs['instruct'] = instruct
                            
                        speed = kwargs.get('speed', self.session.get('speed', 1.0))
                        if speed != 1.0:
                            generate_kwargs['speed'] = speed
                            
                        for k in ['denoise', 'num_step', 'guidance_scale', 't_shift', 'postprocess_output']:
                            if k in kwargs:
                                generate_kwargs[k] = kwargs[k]
                                
                        outputs = self.engine.generate(
                            text=part,
                            language=self.language,
                            **generate_kwargs
                        )
                        
                        if outputs and len(outputs) > 0:
                            audio_part = outputs[0]
                        else:
                            error = 'OmniVoice generate returned no audio'
                            return False, error
                            
                    if is_audio_data_valid(audio_part):
                        src_tensor = self._tensor_type(audio_part)
                        part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                        if part_tensor is not None and part_tensor.numel() > 0:
                            self.audio_segments.append(part_tensor)
                            del part_tensor
                        else:
                            error = 'part_tensor not valid'
                            return False, error
                    else:
                        error = 'audio_part not valid'
                        return False, error
                        
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                        error = f'audio_save() error: cannot save {sentence_file}'
                        return False, error
                    del segment_tensor
                    self.cleanup_memory()
                    self.audio_segments = []
                    if not os.path.exists(sentence_file):
                        error = f'Cannot create {sentence_file}'
                        return False, error
                return True, None
            else:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error
        except Exception as e:
            self.cleanup_memory()
            return False, self.log_exception(f'{self.__class__.__name__}.convert()', e)

    def create_vtt(self, all_sentences: list) -> bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
