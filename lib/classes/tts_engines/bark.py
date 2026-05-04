from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

#sys.stderr = StdoutFilter(sys.stdout)

class Bark(TTSUtils, TTSRegistry, name='bark'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            #self.pth_voice_file = None
            self.resampler_cache = {}
            self.audio_segments = []
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
            self.model_path = model_cfg['repo']
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
            engine = self._load_api(self.tts_key, self.model_path, 'cpu') # self.device, Waiting coqui-tts dev fix with cuda
        if engine:
            msg = f'TTS {self.tts_key} Loaded!'
            print(msg)
            return engine
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
                self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else Path(self.models[self.session['fine_tuned']]['voice']).stem
                if self.speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                    bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                else:
                    bark_dir = os.path.join(os.path.dirname(self.params['current_voice']), 'bark')
                pth_voice_dir = os.path.join(bark_dir, self.speaker)
                if not os.path.exists(pth_voice_dir):
                    os.makedirs(pth_voice_dir, exist_ok=True)
                #pth_voice_file = os.path.join(bark_dir, self.speaker, f'{self.speaker}.pth')
                self.engine.synthesizer.voice_dir = pth_voice_dir
                fine_tuned_params = {
                    key.removeprefix('bark_'): cast_type(self.session[key])
                    for key, cast_type in {
                        'bark_text_temp': float,
                        'bark_waveform_temp': float
                    }.items()
                    if self.session.get(key) is not None
                }
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
                        '''
                            [laughter]
                            [laughs]
                            [sighs]
                            [music]
                            [gasps]
                            [clears throat]
                            — or … for hesitations
                            ♪ for song lyrics
                            CAPITALIZATION for emphasis of a word
                            [MAN] and [WOMAN] to bias Bark toward male and female speakers, respectively
                        '''
                        speaker_argument = {}
                        if (self.engine.speakers is not None and self.speaker not in self.engine.speakers) or self.engine.speakers is None:
                            speaker_argument['speaker_wav'] = self.params['current_voice']
                        import torchaudio as _ta
                        import torch as _t
                        print(f'[bark-pre] current_voice={self.params["current_voice"]}')
                        print(f'[bark-pre] speaker={self.speaker}')
                        print(f'[bark-pre] pth_voice_dir={pth_voice_dir}')
                        _a, _s = _ta.load(self.params['current_voice'])
                        print(f'[bark-pre] voice load: shape={tuple(_a.shape)} ndim={_a.ndim} sr={_s} dtype={_a.dtype}')
                        print(f'[bark-pre] bark target_sr={self.engine.synthesizer.tts_model.config.sample_rate}')
                        print(f'[bark-pre] cache files in pth_voice_dir: {os.listdir(pth_voice_dir) if os.path.exists(pth_voice_dir) else "missing"}')
                        print(f'[bark-pre] speaker_argument={speaker_argument}')
                        print(f'[bark-pre] engine.speakers={self.engine.speakers}')
                        with torch.inference_mode():
                            #with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                            audio_part = self.engine.tts(
                                text=part,
                                speaker=self.speaker,
                                voice_dir=pth_voice_dir,
                                **speaker_argument,
                                **fine_tuned_params
                            )
                        if torch.is_tensor(audio_part):
                            audio_part = audio_part.detach().cpu()
                        if is_audio_data_valid(audio_part):
                            src_tensor = self._tensor_type(audio_part)
                            part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                            if part_tensor is not None and part_tensor.numel() > 0:
                                if part[-1].isalnum() or part[-1] == '—':
                                    part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                self.audio_segments.append(part_tensor)
                                del part_tensor
                                """
                                if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                    self.audio_segments.append(break_tensor.clone())
                                """
                            else:
                                error = f'part_tensor not valid'
                                return False, error
                        else:
                            error = f'audio_part not valid'
                            return False, error
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    #torchaudio.save(sentence_file, segment_tensor, self.params['samplerate'])
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
            return False, self.log_exception(f'{self.__class__.__name__}.convert()',e)

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False