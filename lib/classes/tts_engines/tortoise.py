from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.lang import legends

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
                error = legends['error_invalid_tts_engine'].format(engine=tts_engine)
                raise ValueError(error)
            engine_langs = default_engine_settings[tts_engine].get('languages', {})
            if self.language not in engine_langs:
                error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
                raise ValueError(error)
            iso_dir = engine_langs[self.language]
            if fine_tuned not in self.models:
                error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate', 'sub', 'voice'):
                if required_key not in model_cfg:
                    error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                    raise ValueError(error)
            sub_dict = model_cfg['sub']
            sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
            if sub is None:
                error = legends['error_checkpoint_not_found'].format(engine=tts_engine, lang=self.language)
                raise KeyError(error)
            self.params['samplerate'] = model_cfg['samplerate'][sub]
            self.model_path = model_cfg['repo'].replace('[lang_iso1]', iso_dir).replace('[xxx]', sub)
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            # tortoise keeps the autoregressive GPT-2, the diffusion model and the
            # vocoder resident at the same time: in fp32 that does not fit in 4GB,
            # so ask the engine for its own half precision path on low-vram cuda.
            self.half = self.device == devices['CUDA']['proc'] and not enough_vram
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        msg = legends['msg_loading_tts_model'].format(model=self.tts_key)
        print(msg)
        self.cleanup_memory()
        self.tts_key = self.model_path
        engine = loaded_tts.get(self.tts_key)
        if not engine:
            try:
                engine = self._load_api(self.tts_key, self.model_path, self.device)
            except Exception as e:
                error = 'load_engine(): _load_api() failed'
                raise RuntimeError(error) from e
        if engine:
            # transformers 4.57 routes GPT-2 through the sdpa attention interface and the
            # new mask builder. on the jetson torch (2.4.x aarch64 wheel) that combination
            # produces a fully masked attention row -> NaN logits -> torch.multinomial()
            # raises in generation/utils.py _sample(). eager keeps the old mask-add path.
            # tortoise's GPT2InferenceModel also still assumes legacy cache tuples, which
            # 4.57 no longer hands it, so the kv cache is bypassed on the same grounds.
            autoregressive = getattr(getattr(engine, 'synthesizer', None), 'tts_model', None)
            autoregressive = getattr(autoregressive, 'autoregressive', None)
            if autoregressive is not None:
                for module in (getattr(autoregressive, 'gpt', None), getattr(autoregressive, 'inference_model', None)):
                    if module is not None and getattr(module, 'config', None) is not None:
                        module.config._attn_implementation = 'eager'
                if getattr(autoregressive, 'inference_model', None) is not None:
                    autoregressive.inference_model.kv_cache = False
            msg = legends['msg_tts_loaded'].format(model=self.tts_key)
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
                        trim_audio_buffer = 0.002
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
                                    **({'half': True} if self.half else {}),
                                    **speaker_argument
                                )
                            if audio_part is not None and len(audio_part) > 0:
                                if torch.is_tensor(audio_part):
                                    audio_part = audio_part.detach().cpu()
                                if not is_audio_data_valid(audio_part):
                                    error = 'audio_part not valid'
                                    return False, error
                                part_tensor = self._tensor_type(audio_part).unsqueeze(0)
                                if part_tensor.numel() == 0:
                                    error = 'part_tensor not valid'
                                    return False, error
                                if part[-1].isalnum() or part[-1] == '—':
                                    part_tensor = trim_audio(part_tensor.squeeze(0), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                self.audio_segments.append(part_tensor)
                            else:
                                error = 'audio_part not valid'
                                return False, error
                        except IndexError as e:
                            self.cleanup_memory()
                            error = f'convert() error at {e} segment: {part}'
                            return False, error
                        except Exception as e:
                            # free the failed part's tensors before returning False;
                            # core.py then unloads the engine via unload_tts_manager().
                            self.cleanup_memory()
                            return False, self.log_exception(f'{self.__class__.__name__}.convert() part loop', e)
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                        error = f'audio_save() error: cannot save {sentence_file}'
                        return False, error
                    self.audio_segments = []
                    if not os.path.exists(sentence_file):
                        error = legends['error_cannot_create'].format(file=sentence_file)
                        return False, error
                return True, None
            else:
                error = legends['error_tts_engine_load_failed'].format(engine=self.session['tts_engine'])
                return False, error
        except Exception as e:
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()',e)

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False