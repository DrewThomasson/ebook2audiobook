from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

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
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            self.params['samplerate'] = self.models[self.session['fine_tuned']]['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            #np.random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
            print(msg)
            self._cleanup_memory()
            engine = loaded_tts.get(self.tts_key, False)
            if not engine:
                if self.session['custom_model'] is not None:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    model_path = self.models[self.session['fine_tuned']]['repo']
                    engine = self._load_api(self.tts_key, model_path)
            if engine and engine is not None:
                msg = f'TTS {self.tts_key} Loaded!'
                return engine
            else:
                error = 'load_engine() failed!'
                raise ValueError(error)
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise ValueError(error)

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            if self.engine:
                final_sentence_file = os.path.join(self.session['sentences_dir'], f'{sentence_index}.{default_audio_proc_format}')
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                sentence_parts = default_frontend_sml_pattern.split(sentence)
                self.audio_segments = []
                for part in sentence_parts:
                    part = part.strip()
                    if not part or not any(c.isalnum() for c in part):
                        continue
                    if default_frontend_sml_pattern.fullmatch(part):
                        if not self._convert_sml(part):
                            error = f'_convert_sml failed: {part}'
                            print(error)
                            return False
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        speaker_argument = {}
                        not_supported_punc_pattern = re.compile(r'[—]')
                        part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                        if self._set_voice():
                            if self.params['voice_path'] is not None:
                                speaker_wav = self.params['voice_path']
                                speaker_argument = {"speaker_wav": speaker_wav}
                            else:
                                voice_key = default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2']
                                speaker_argument = {"speaker": voice_key}                         
                            with torch.no_grad():
                                self.engine.to(device)
                                if device == devices['CPU']['proc']:
                                    audio_part = self.engine.tts(
                                        text=part,
                                        language=language,
                                        **speaker_argument
                                    )
                                else:
                                    with torch.autocast(
                                        device_type=device,
                                        dtype=self.amp_dtype
                                    ):
                                        audio_part = self.engine.tts(
                                            text=part,
                                            language=language,
                                            **speaker_argument
                                        )
                                self.engine.to(devices['CPU']['proc'])
                            if is_audio_data_valid(audio_part):
                                src_tensor = self._tensor_type(audio_part)
                                part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                                if part_tensor is not None and part_tensor.numel() > 0:
                                    if part[-1].isalnum() or part[-1] == '—':
                                        part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                    self.audio_segments.append(part_tensor)
                                    if not re.search(r'\w$', part, flags=re.UNICODE):
                                        silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                        break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                        self.audio_segments.append(break_tensor.clone())
                                    del part_tensor
                                else:
                                    error = f"part_tensor not valid"
                                    print(error)
                                    return False
                            else:
                                error = f"audio_part not valid"
                                print(error)
                                return False
                        else:
                            return False
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    torchaudio.save(final_sentence_file, segment_tensor, self.params['samplerate'], format=default_audio_proc_format)
                    del segment_tensor
                    self._cleanup_memory()
                    self.audio_segments = []
                    if not os.path.exists(final_sentence_file):
                        error = f"Cannot create {final_sentence_file}"
                        print(error)
                        return False
                return True
            else:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                print(error)
                return False
        except Exception as e:
            error = f'YourTTS.convert(): {e}'
            raise ValueError(e)
            return False

    def create_vtt(self, all_sentences:list)->bool:
        audio_dir = self.session['sentences_dir']
        vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
        if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
            return True
        return False