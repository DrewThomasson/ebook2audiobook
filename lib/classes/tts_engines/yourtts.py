from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class YourTTS(TTSUtils, TTSRegistry, name='yourtts'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.resampler_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            self.params['samplerate'] = self.models[self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
            using_gpu = self.session['device'] != devices['CPU']['proc']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            #np.random.seed(seed)
            torch.manual_seed(seed)
            has_cuda = (torch.version.cuda is not None and torch.cuda.is_available())
            if has_cuda:
                self._apply_cuda_policy(using_gpu=using_gpu, enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self._load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def _load_engine(self)->Any:
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
                error = '_load_engine() failed!'
                raise ValueError(error)
        except Exception as e:
            error = f'_load_engine() error: {e}'
            raise ValueError(error)
    
    def set_voice(self)->bool:
        self.params['voice_path'] = (
            self.session['voice'] if self.session['voice'] is not None 
            else self.models[self.session['fine_tuned']]['voice']
        )
        if self.params['voice_path'] is not None:
            speaker = re.sub(r'\.wav$', '', os.path.basename(self.params['voice_path']))
            if self.params['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in self.params['voice_path']:
                self.session['voice'] = self.params['voice_path'] = self._check_xtts_builtin_speakers(self.params['voice_path'], speaker)
                if not self.params['voice_path']:
                    msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                    print(msg)
                    return False
        return True

    def convert_sml(self, sml:str)->None:
        if sml == TTS_SML['break']['token']:
            silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
            break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 0.4 to 0.7 seconds
            self.audio_segments.append(break_tensor.clone())
        elif TTS_SML['pause']['match'].fullmatch(sml):
            m = TTS_SML['pause']['match'].fullmatch(sml)
            duration = float(m.group(1)) if m.group(1) is not None else None
            if duration is not None:
                silence_time = float(duration)
            else:
                silence_time = float(np.random.uniform(1.0, 1.6) * 100) / 100
            pause_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 1.0 to 1.6 seconds
            self.audio_segments.append(pause_tensor.clone())
        elif TTS_SML['voice']['match'].fullmatch(sml):
            self.session['voice'] = os.path.abspath(TTS_SML['voice'].fullmatch(sml).group(1))
            if os.path.exists(self.session['voice']):
                if not self.set_voice():
                    return False
            else:
                error = f"convert_sml() error: voice {self.session['voice']} does not exist!"
                print(error)
        return True

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            speaker = None
            if self.engine:
                final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_index}.{default_audio_proc_format}')
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                sentence_parts = re.split(default_sml_pattern, sentence)
                for part in sentence_parts:
                    part = part.strip()
                    if not part or not part.replace('—', '') or not part.isalnum() or len(part) < 2:
                        continue
                    if default_sml_pattern.fullmatch(part):
                        if not self.convert_sml(part):
                            error = f'convert_sml failed: {part}'
                            print(error)
                            return False
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        speaker_argument = {}
                        not_supported_punc_pattern = re.compile(r'[—]')
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        if self.set_voice():
                            if self.params['voice_path'] is not None:
                                speaker_wav = self.params['voice_path']
                                speaker_argument = {"speaker_wav": speaker_wav}
                            else:
                                voice_key = default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2']
                                speaker_argument = {"speaker": voice_key}
                            with torch.no_grad():
                                self.engine.to(device)
                                audio_part = self.engine.tts(
                                    text=re.sub(not_supported_punc_pattern, ' ', part),
                                    language=language,
                                    **speaker_argument
                                )
                                self.engine.to('cpu')
                            if is_audio_data_valid(audio_part):
                                src_tensor = self._tensor_type(audio_part)
                                audio_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                                if audio_tensor is not None and audio_tensor.numel() > 0:
                                    if part[-1].isalnum() or part[-1] == '—':
                                        audio_tensor = trim_audio(audio_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                    self.audio_segments.append(audio_tensor)
                                    if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                                        silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                        break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                        self.audio_segments.append(break_tensor.clone())
                                else:
                                    error = f"audio_tensor not valid"
                                    print(error)
                                    return False
                            else:
                                error = f"audio_part not valid"
                                print(error)
                                return False
                if self.audio_segments:
                    audio_tensor = torch.cat(self.audio_segments, dim=-1)
                    start_time = self.sentences_total_time
                    duration = round((audio_tensor.shape[-1] / self.params['samplerate']), 2)
                    end_time = start_time + duration
                    self.sentences_total_time = end_time
                    sentence_obj = {
                        "start": start_time,
                        "end": end_time,
                        "text": part,
                        "idx": self.sentence_idx
                    }
                    self.sentence_idx = self._append_sentence2vtt(sentence_obj, self.vtt_path)
                    if self.sentence_idx:
                        torchaudio.save(final_sentence_file, audio_tensor, self.params['samplerate'], format=default_audio_proc_format)
                        del audio_tensor
                        self._cleanup_memory()
                self.audio_segments = []
                if os.path.exists(final_sentence_file):
                    return True
                else:
                    error = f"Cannot create {final_sentence_file}"
                    print(error)
                    return False
            else:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                print(error)
                return False
        except Exception as e:
            error = f'YourTTS.convert(): {e}'
            raise ValueError(e)
            return False