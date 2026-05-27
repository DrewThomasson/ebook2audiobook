import sys
import os
qwen_path = os.path.abspath(os.path.dirname(__file__))
if qwen_path not in sys.path:
    sys.path.insert(0, qwen_path)

from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.classes.vram_detector import VRAMDetector



class Qwen3TTS(TTSUtils, TTSRegistry, name='qwen3tts'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            # effective language for TTS (target when translating, else source)
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
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
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = f'Loading TTS {self.tts_key} model, it takes a while, please be patient…'
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                from qwen_tts import Qwen3TTSModel
                import torch
                model_cfg = self.models[self.session['fine_tuned']]
                hf_repo = model_cfg['repo']
                device_map = self.device
                if device_map == 'cpu':
                    dtype = torch.float32
                    attn_implementation = "eager"
                else:
                    dtype = torch.bfloat16 if self.amp_dtype == torch.bfloat16 else torch.float16
                    attn_implementation = "eager" if self.device == 'mps' else "flash_attention_2"
                print(f"Loading Qwen3TTSModel from {hf_repo} on {self.device} with {dtype}...")
                try:
                    engine = Qwen3TTSModel.from_pretrained(
                        hf_repo,
                        device_map=device_map,
                        dtype=dtype,
                        attn_implementation=attn_implementation,
                        cache_dir=self.cache_dir
                    )
                except Exception as ex:
                    print(f"Failed to load with attn_implementation={attn_implementation}, retrying with eager. Error: {ex}")
                    engine = Qwen3TTSModel.from_pretrained(
                        hf_repo,
                        device_map=device_map,
                        dtype=dtype,
                        attn_implementation="eager",
                        cache_dir=self.cache_dir
                    )
                vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                if self.session['free_vram_gb'] > models_loaded_size_gb:
                    loaded_tts[self.tts_key] = engine
            if engine:
                msg = f'TTS {self.tts_key} Loaded!'
                print(msg)
                return engine
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise RuntimeError(error) from e

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            import numpy as np
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
            if not self.engine:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error
            self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
            if self.params.get('inline_voice'):
                self.params['current_voice'] = self.params['inline_voice']
            else:
                self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                if self.params['current_voice'] is None and error is not None:
                    return False, error
            qwen_lang_map = default_engine_settings[self.session['tts_engine']]['languages']
            qwen_lang = qwen_lang_map.get(self.language, "English")
            fine_tuned = self.session.get('fine_tuned')
            sentence_parts = self._split_sentence_on_sml(sentence)
            self.audio_segments = []
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
                try:
                    num_words = len(part.split())
                    max_new_tokens = max(200, num_words * 20)
                    if fine_tuned == 'custom_voice':
                        speaker_name = Path(self.params['current_voice']).stem if self.params['current_voice'] else "Vivian"
                        supported_speakers = {s.lower(): s for s in ["Vivian", "Ryan", "Bella", "Diana", "Jack", "John", "Lilly", "Sarah", "Tom"]}
                        speaker = supported_speakers.get(speaker_name.lower(), "Vivian")
                        wavs, sr = self.engine.generate_custom_voice(
                            text=part,
                            language=qwen_lang,
                            speaker=speaker,
                            instruct="",
                            max_new_tokens=max_new_tokens
                        )
                    else:
                        ref_audio = self.params['current_voice']
                        if not ref_audio or not os.path.exists(ref_audio):
                            ref_audio = default_engine_settings[self.session['tts_engine']]['voice']
                        wavs, sr = self.engine.generate_voice_clone(
                            text=part,
                            language=qwen_lang,
                            ref_audio=ref_audio,
                            x_vector_only_mode=True,
                            max_new_tokens=max_new_tokens
                        )
                    if wavs and len(wavs) > 0:
                        audio_part = wavs[0]
                        if torch.is_tensor(audio_part):
                            audio_part = audio_part.detach().cpu().numpy()
                        if isinstance(audio_part, np.ndarray):
                            audio_part = audio_part.astype(np.float32)
                        part_tensor = self._tensor_type(audio_part).unsqueeze(0)
                        if part_tensor.numel() == 0:
                            error = 'part_tensor is empty'
                            return False, error
                        self.audio_segments.append(part_tensor)
                        if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                            silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                            self.audio_segments.append(torch.zeros(1, int(self.params['samplerate'] * silence_time)))
                    else:
                        error = 'No audio returned from Qwen3-TTS'
                        return False, error
                except Exception as ex:
                    return False, self.log_exception(f'Qwen3TTS.convert() generation loop', ex)
            if self.audio_segments:
                segment_tensor = torch.cat(self.audio_segments, dim=-1)
                if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                    error = f'audio_save() error: cannot save {sentence_file}'
                    return False, error
                self.audio_segments = []
                if not os.path.exists(sentence_file):
                    error = f'Cannot create {sentence_file}'
                    return False, error
            return True, None
        except Exception as e:
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()', e)

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
