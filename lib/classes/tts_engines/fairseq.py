from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class Fairseq(TTSUtils, TTSRegistry, name='fairseq'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.tts_zs_key = default_vc_model.rsplit('/',1)[-1]
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {"semitones":{}}
            self.params['samplerate'] = self.models[self.session['fine_tuned']]['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            #np.random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self.load_engine()
            self.engine_zs = self._load_engine_zs()
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
                    model_path = self.models[self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                    self.tts_key = model_path
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
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device'] if devices[self.session['device'].upper()]['found'] else devices['CPU']['proc']
                sentence_parts = self._split_sentence_on_sml(sentence)
                not_supported_punc_pattern = re.compile(r"[.:—]")
                if not self._set_voice():
                    return False
                self.audio_segments = []
                for part in sentence_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        res, error = self._convert_sml(part)
                        if not res: 
                            print(error)
                            return False
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                    else:
                        trim_audio_buffer = 0.002
                        speaker_argument = {}
                        if part.endswith("'"):
                            part = part[:-1]
                        part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                        if self.params['current_voice'] is not None:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            with torch.no_grad():
                                self.engine.to(device)
                                if device == devices['CPU']['proc']:
                                    self.engine.tts_to_file(
                                        text=part,
                                        file_path=tmp_in_wav,
                                        **speaker_argument
                                    )
                                else:
                                    with torch.autocast(
                                        device_type=device,
                                        dtype=self.amp_dtype
                                    ):
                                        self.engine.tts_to_file(
                                            text=part,
                                            file_path=tmp_in_wav,
                                            **speaker_argument
                                        )
                                self.engine.to(devices['CPU']['proc'])
                            if self.params['current_voice'] in self.params['semitones'].keys():
                                semitones = self.params['semitones'][self.params['current_voice']]
                            else:
                                current_voice_gender = detect_gender(self.params['current_voice'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {current_voice_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                                print(msg)
                                if voice_builtin_gender != current_voice_gender:
                                    semitones = -4 if current_voice_gender == 'male' else 4
                                    msg = f"Adapting builtin voice frequencies from the clone voice…"
                                    print(msg)
                                else:
                                    semitones = 0
                                self.params['semitones'][self.params['current_voice']] = semitones
                            if semitones > 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(self.params['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                except subprocess.CalledProcessError as e:
                                    error = f'Subprocess error: {e.stderr}'
                                    print(error)
                                    DependencyError(e)
                                    return False
                                except FileNotFoundError as e:
                                    error = f'File not found: {e}'
                                    print(error)
                                    DependencyError(e)
                                    return False
                            else:
                                tmp_out_wav = tmp_in_wav
                            if self.engine_zs:
                                self.params['samplerate'] = TTS_VOICE_CONVERSION[self.tts_zs_key]['samplerate']
                                source_wav = self._resample_wav(tmp_out_wav, self.params['samplerate'])
                                target_wav = self._resample_wav(self.params['current_voice'], self.params['samplerate'])
                                self.engine_zs.to(device)
                                audio_part = self.engine_zs.voice_conversion(
                                    source_wav=source_wav,
                                    target_wav=target_wav
                                )
                                self.engine_zs.to(devices['CPU']['proc'])
                            else:
                                error = f'Engine {self.tts_zs_key} is None'
                                print(error)
                                return False
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                            if os.path.exists(source_wav):
                                os.remove(source_wav)
                        else:
                            with torch.no_grad():
                                self.engine.to(device)
                                if device == devices['CPU']['proc']:
                                    audio_part = self.engine.tts(
                                        text=part,
                                        **speaker_argument
                                    )
                                else:
                                    with torch.autocast(
                                        device_type=device,
                                        dtype=self.amp_dtype
                                    ):
                                        audio_part = self.engine.tts(
                                            text=part,
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
                                if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                    self.audio_segments.append(break_tensor.clone())
                            else:
                                error = f"part_tensor not valid"
                                print(error)
                                return False
                        else:
                            error = f"audio_sentence not valid"
                            print(error)
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
            error = f'Fairseq.convert(): {e}'
            raise ValueError(e)
            return False

    def create_vtt(self, all_sentences:list)->bool:
        audio_dir = self.session['sentences_dir']
        vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
        if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
            return True
        return False