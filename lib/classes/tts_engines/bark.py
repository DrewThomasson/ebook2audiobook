from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class Bark(TTSUtils, TTSRegistry, name='bark'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            self.params['samplerate'] = self.models[self.session['fine_tuned']]['samplerate']
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
                    """
                    hf_repo = self.models[self.session['fine_tuned']]['repo']
                    hf_sub = self.models[self.session['fine_tuned']]['sub']
                    text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                    coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                    fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                    checkpoint_dir = os.path.dirname(text_model_path)
                    engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_dir=checkpoint_dir)
                    """
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
    """
    def _check_bark_npz(self, voice_path:str, bark_dir:str, speaker:str)->bool:
        try:
            if self.session['language'] in default_engine_settings[TTS_ENGINES['BARK']].get('languages', {}):
                pth_voice_dir = os.path.join(bark_dir, speaker)
                pth_voice_file = os.path.join(pth_voice_dir,f'{speaker}.pth')
                if os.path.exists(pth_voice_file):
                    return True
                else:
                    os.makedirs(pth_voice_dir,exist_ok=True)
                    key = f"{TTS_ENGINES['BARK']}-internal"
                    default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                    default_text = Path(default_text_file).read_text(encoding="utf-8")
                    fine_tuned_params = {
                        key.removeprefix("bark_"):cast_type(self.session[key])
                        for key,cast_type in{
                            "bark_text_temp":float,
                            "bark_waveform_temp":float
                        }.items()
                        if self.session.get(key) is not None
                    }
                    with torch.no_grad():
                        result = self.engine.synthesize(
                            default_text,
                            speaker_wav=voice_path,
                            speaker=speaker,
                            voice_dir=pth_voice_dir,
                            **fine_tuned_params
                        )
                    del result
                    msg = f"Saved file: {pth_voice_file}"
                    print(msg)
                    return True
            else:
                return True
        except Exception as e:
            error = f'_check_bark_npz() error: {e}'
            print(error)
            return False
    """
 
    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            speaker = None
            if self.engine:
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_index}.{default_audio_proc_format}')
                sentence_parts = re.split(default_sml_pattern, sentence)
                self.audio_segments = []
                for part in sentence_parts:
                    part = part.strip()
                    if not part or (part and sum(c.isalnum() for c in part) < 3):
                        continue
                    if default_sml_pattern.fullmatch(part):
                        if not self._convert_sml(part):
                            error = f'_convert_sml failed: {part}'
                            print(error)
                            return False
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        if self._set_voice():
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
                            if speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                                bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                            else:
                                bark_dir = os.path.join(os.path.dirname(self.params['voice_path']), 'bark')
                                """
                                if not self._check_bark_npz(self.params['voice_path'], bark_dir, speaker):
                                    error = 'Could not create pth voice file!'
                                    print(error)
                                    return False
                                """
                            pth_voice_dir = os.path.join(bark_dir, speaker)
                            pth_voice_file = os.path.join(bark_dir, speaker, f'{speaker}.pth')
                            self.engine.synthesizer.voice_dir = pth_voice_dir
                            tts_dyn_params = {}
                            if not os.path.exists(pth_voice_file) or speaker not in self.engine.speakers:
                                tts_dyn_params['speaker_wav'] = self.params['voice_path']
                            fine_tuned_params = {
                                key.removeprefix("bark_"): cast_type(self.session[key])
                                for key, cast_type in {
                                    "bark_text_temp": float,
                                    "bark_waveform_temp": float
                                }.items()
                                if self.session.get(key) is not None
                            }
                            with torch.no_grad():
                                """
                                result = self.engine.synthesize(
                                    part,
                                    #speaker_wav=self.params['voice_path'],
                                    speaker=speaker,
                                    voice_dir=pth_voice_dir,
                                    **fine_tuned_params
                                )
                                """
                                self.engine.to(device)
                                audio_part = self.engine.tts(
                                    text=part,
                                    speaker=speaker,
                                    voice_dir=pth_voice_dir,
                                    **tts_dyn_params,
                                    **fine_tuned_params
                                )
                                self.engine.to('cpu')
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
            error = f'Bark.convert(): {e}'
            raise ValueError(e)
            return False

    def create_vtt(self, all_sentences:list)->bool:
        audio_dir = self.session['chapters_dir_sentences']
        vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
        if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
            return True
        return False