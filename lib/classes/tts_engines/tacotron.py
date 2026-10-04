from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.lang import legends

#sys.stderr = StdoutFilter(sys.stdout)

class Tacotron2(TTSUtils, TTSRegistry, name='tacotron'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.tts_zs_key = default_vc_model.rsplit('/',1)[-1]
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {"semitones":{}}
            # effective language for TTS (target when translating, else source)
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
            tts_engine = self.session.get('tts_engine')
            if tts_engine not in default_engine_settings:
                error = legends['error_invalid_tts_engine'].format(engine=tts_engine)
                raise ValueError(error)
            engine_langs = default_engine_settings[tts_engine].get('languages', {})
            if self.language not in engine_langs:
                error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
                raise ValueError(error)
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate', 'sub'):
                if required_key not in model_cfg:
                    error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                    raise ValueError(error)
            sub_dict = model_cfg['sub']
            iso_dir = engine_langs[self.language]
            sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
            if sub is None:
                iso_dir = self.language
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
            self.engine = self.load_engine()
            self.engine_zs = self._load_engine_zs(self.device)
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        msg = legends['msg_loading_tts_model'].format(model=self.tts_key)
        print(msg)
        self.cleanup_memory()
        #if self.session['custom_model'] is not None:
        #    error = f"{self.session['tts_engine']} custom model not implemented yet!"
        #    raise NotImplementedError(error)
        self.tts_key = self.model_path
        engine = loaded_tts.get(self.tts_key)
        if not engine:
            try:
                engine = self._load_api(self.tts_key, self.model_path, self.device)
            except Exception as e:
                error = 'load_engine(): _load_api() failed'
                raise RuntimeError(error) from e
            try:
                m = engine.synthesizer.tts_model
                d = m.decoder
                d.prenet_dropout = 0.0
                d.attention_dropout = 0.0
                d.decoder_dropout = 0.0
                d.gate_threshold = 0.5
                d.force_gate = True
                d.gate_delay = 10
                d.max_decoder_steps = 1000
                d.attention_keeplast = True
            except Exception as e:
                error = 'load_engine(): decoder tuning failed'
                raise RuntimeError(error) from e
        if engine:
            msg = legends['msg_tts_loaded'].format(model=self.tts_key)
            print(msg)
            return engine
        error = 'load_engine(): engine is None'
        raise RuntimeError(error)

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid, detect_gender
            if self.engine:
                sentence_parts = self._split_sentence_on_sml(sentence)
                if self.language in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
                    not_supported_punc_pattern = re.compile(r'\p{P}+')
                else:
                    not_supported_punc_pattern = re.compile(r'["—…¡¿]')
                self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
                if self.params.get('inline_voice'):
                    self.params['current_voice'] = self.params['inline_voice']
                else:
                    self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                    if self.params['current_voice'] is None and error is not None:
                        return False, error
                self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else None
                proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                os.makedirs(proc_dir, exist_ok=True)
                self.audio_segments = []
                use_zs = self.params['current_voice'] is not None
                if use_zs and not self.engine_zs:
                    error = legends['error_engine_not_loaded'].format(engine=self.tts_zs_key)
                    return False, error
                if use_zs:
                    proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                    os.makedirs(proc_dir, exist_ok=True)
                for part in sentence_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        success, error = self._convert_sml(part)
                        if success:
                             self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else None
                             use_zs = self.params['current_voice'] is not None
                        else:
                            return False, error
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                    else:
                        if part.endswith("'"):
                            part = part[:-1]
                        part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                        try:
                            if use_zs:
                                tmp_in_wav = os.path.join(proc_dir, f'{uuid.uuid4()}.wav')
                                tmp_out_wav = os.path.join(proc_dir, f'{uuid.uuid4()}.wav')
                                with torch.inference_mode():
                                    with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                        self.engine.tts_to_file(
                                            text=part,
                                            file_path=tmp_in_wav
                                        )
                                if self.params['current_voice'] in self.params['semitones'].keys():
                                    semitones = self.params['semitones'][self.params['current_voice']]
                                else:
                                    current_voice_gender = detect_gender(self.params['current_voice'])
                                    voice_builtin_gender = detect_gender(tmp_in_wav)
                                    if voice_builtin_gender != current_voice_gender:
                                        semitones = -4 if current_voice_gender == 'male' else 4
                                        msg = legends['msg_voice_gender_adapt'].format(cloned=current_voice_gender, builtin=voice_builtin_gender)
                                        print(msg)
                                    else:
                                        semitones = 0
                                    self.params['semitones'][self.params['current_voice']] = semitones
                                if semitones > 0:
                                    try:
                                        cmd = [
                                            shutil.which('sox'), tmp_in_wav,
                                            '-r', str(self.params['samplerate']), tmp_out_wav,
                                            'pitch', str(semitones * 100)
                                        ]
                                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    except subprocess.CalledProcessError as e:
                                        error = legends['error_subprocess'].format(e=e.stderr)
                                        DependencyError(error)
                                        return False, error
                                    except FileNotFoundError as e:
                                        error = legends['error_file_not_found_detail'].format(e=e)
                                        DependencyError(error)
                                        return False, error
                                else:
                                    tmp_out_wav = tmp_in_wav
                                samplerate = TTS_VOICE_CONVERSION[self.tts_zs_key]['samplerate']
                                source_wav = self._resample_wav(tmp_out_wav, samplerate)
                                target_wav = self._resample_wav(self.params['current_voice'], samplerate)
                                speaker_argument = {}
                                if (self.engine_zs.speakers is not None and self.speaker not in self.engine_zs.speakers) or self.engine_zs.speakers is None:
                                    speaker_argument['target_wav'] = target_wav
                                audio_part = self.engine_zs.voice_conversion(
                                    source_wav=source_wav,
                                    speaker=self.speaker,
                                    **speaker_argument
                                )
                                if os.path.exists(tmp_in_wav):
                                    os.remove(tmp_in_wav)
                                if os.path.exists(tmp_out_wav):
                                    os.remove(tmp_out_wav)
                                if os.path.exists(source_wav):
                                    os.remove(source_wav)
                                audio_part = self._resample_audiodata(audio_part, samplerate, self.params['samplerate'])
                            else:
                                with torch.inference_mode():
                                    with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                        audio_part = self.engine.tts(
                                            text=part
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