from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

#sys.stderr = StdoutFilter(sys.stdout)

class YourTTS(TTSUtils, TTSRegistry, name='yourtts'):

    def __init__(self, session:DictProxy):
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
            # yourtts-specific regional language tag passed to engine.tts(language=...)
            self.yourtts_language = self.language_iso1 if self.language_iso1 == 'en' else 'fr-fr' if self.language_iso1 == 'fr' else 'pt-br' if self.language_iso1 == 'pt' else 'en'
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
            self.model_path = model_cfg['repo'].replace("[lang]", self.language)
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
        print(msg)
        self.cleanup_memory()
        engine = loaded_tts.get(self.tts_key)
        if engine:
            msg = f"TTS {self.tts_key} already loaded"
            print(msg)
            return engine
        try:
            model_cfg = self.models[self.session['fine_tuned']]
            model_path = model_cfg['repo']
        except KeyError as e:
            error = f"Invalid fine_tuned model '{self.session['fine_tuned']}'"
            raise KeyError(error) from e
        try:
            engine = self._load_api(self.tts_key, model_path, self.device)
            if engine is None:
                error = '_load_api() returned None'
                raise RuntimeError(error)
            msg = f'TTS {self.tts_key} Loaded!'
            print(msg)
            return engine
        except Exception as e:
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            import torchaudio
            #import numpy as np
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
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                        speaker_argument = {}
                        if self.params['current_voice'] is not None:
                            speaker_wav = self.params['current_voice']
                            speaker_argument = {"speaker_wav": speaker_wav}
                        else:
                            self.speaker = default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2']
                            speaker_argument = {"speaker": self.speaker}
                        try:
                            with torch.inference_mode():
                                with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                    audio_part = self.engine.tts(
                                        text=part,
                                        language=self.yourtts_language,
                                        **speaker_argument
                                    )
                            if audio_part is not None and len(audio_part) > 0:
                                if torch.is_tensor(audio_part):
                                    audio_part = audio_part.detach().cpu()
                                if is_audio_data_valid(audio_part):
                                    src_tensor = self._tensor_type(audio_part)
                                    part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                                    if part_tensor is not None and part_tensor.numel() > 0:
                                        if part[-1].isalnum() or part[-1] == '—':
                                            part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                        self.audio_segments.append(part_tensor)
                                    else:
                                        error = f'part_tensor not valid'
                                        return False, error
                                else:
                                    error = f'audio_part not valid'
                                    return False, error
                            else:
                                error = f'audio_part not valid'
                                return False, error
                        except IndexError as e:
                            error = f'tts() error at {e} segment: {part}'
                            print(error)
                            audio_part = False
                            pass
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    #torchaudio.save(sentence_file, segment_tensor, self.params['samplerate'])
                    if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                        error = f'audio_save() error: cannot save {sentence_file}'
                        return False, error
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
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()',e)

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False