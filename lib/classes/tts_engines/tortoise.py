from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

#sys.stderr = StdoutFilter(sys.stdout)

class Tortoise(TTSUtils, TTSRegistry, name='tortoise'):

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
            tts_engine = self.session.get('tts_engine')
            # effective language for TTS (target when translating, else source)
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
            fine_tuned = self.session.get('fine_tuned')
            if tts_engine not in default_engine_settings:
                error = f'Invalid tts_engine {tts_engine}.'
                raise ValueError(error)
            engine_langs = default_engine_settings[tts_engine].get('languages', {})
            if self.language not in engine_langs:
                error = f'Language {self.language} not supported by engine {tts_engine}.'
                raise ValueError(error)
            iso_dir = engine_langs[self.language]
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}'
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate', 'sub'):
                if required_key not in model_cfg:
                    error = f'fine_tuned model {fine_tuned} is missing required key {required_key}.'
                    raise ValueError(error)
            sub_dict = model_cfg['sub']
            sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
            if sub is None:
                error = f'{tts_engine} checkpoint for {self.language} not found.'
                raise KeyError(error)
            self.params['samplerate'] = model_cfg['samplerate'][sub]
            self.model_path = model_cfg['repo'].replace('[lang_iso1]', iso_dir).replace('[xxx]', sub)
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
        if not engine:
            #if self.session['custom_model'] is not None:
            #    error = f"{self.session['tts_engine']} custom model not implemented yet!"
            #    raise NotImplementedError(error)
            self.tts_key = self.model_path
            try:
                engine = self._load_api(self.tts_key, self.model_path, self.device)
            except Exception as e:
                error = 'load_engine(): _load_api() failed'
                raise RuntimeError(error) from e
        if engine:
            msg = f'TTS {self.tts_key} Loaded!'
            print(msg)
            return engine
        error = 'load_engine(): engine is None'
        raise RuntimeError(error)

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
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
                        if part.endswith("'"):
                            part = part[:-1]
                        part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                        speaker_argument = {}
                        self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else Path(self.models[self.session['fine_tuned']]['voice']).stem
                        if self.speaker not in self.engine.speakers:
                            speaker_wav = self.params['current_voice']
                            speaker_argument = {"speaker_wav": [speaker_wav], "speaker": self.speaker}
                        else:
                            speaker_argument = {"speaker": self.speaker, "preset": "ultra_fast"}
                        try:
                            with torch.inference_mode():
                                #with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                audio_part = self.engine.tts(
                                    text=part,
                                    num_autoregressive_samples=1,
                                    diffusion_iterations=10,
                                    **speaker_argument
                                )
                            if audio_part is not None and len(audio_part) > 0:
                                if torch.is_tensor(audio_part):
                                    audio_part = audio_part.detach().cpu()
                                if not is_audio_data_valid(audio_part):
                                    error = 'audio_part not valid'
                                    return False, error
                                part_tensor = self._tensor_type(audio_part).detach().unsqueeze(0)
                                if part_tensor.numel() == 0:
                                    error = 'part_tensor not valid'
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