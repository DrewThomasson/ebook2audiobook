from lib.classes.tts_engines.common.headers import *

class Bark(TTSUtils, TTSRegistry, name='bark'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.tts_zs_key = default_vc_model.rsplit('/',1)[-1]
            self.pth_voice_file = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.params = {}
            self.params['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
            self.resampler_cache = {}
            self.audio_segments = []
            using_gpu = self.session['device'] != devices['CPU']['proc']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 123456
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            has_cuda = (torch.version.cuda is not None and torch.cuda.is_available())
            if has_cuda:
                self._apply_cuda_policy(using_gpu=using_gpu, enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self._load_engine()
            self.engine_zs = self._load_engine_zs()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def _load_engine(self)->Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient..."
            print(msg)
            self._cleanup_memory()
            engine = loaded_tts.get(self.tts_key, False)
            if not engine:     
                if self.session['custom_model'] is not None:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                    hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                    text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                    coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                    fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                    checkpoint_dir = os.path.dirname(text_model_path)
                    engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_dir=checkpoint_dir)
            if engine and engine is not None:
                msg = f'TTS {self.tts_key} Loaded!'
                return engine
        except Exception as e:
            error = f'_load_engine() error: {e}'
            raise ValueError(error)

    def _check_bark_npz(self, voice_path:str, bark_dir:str, speaker:str)->bool:
        try:
            if self.session['language'] in language_tts[TTS_ENGINES['BARK']].keys():
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

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            speaker = None
            audio_sentence = False
            self.params['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            if self.params['voice_path'] is not None:
                speaker = re.sub(r'\.wav$', '', os.path.basename(self.params['voice_path']))
                if self.params['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in self.params['voice_path']:
                    self.session['voice'] = self.params['voice_path'] = self._check_xtts_builtin_speakers(self.params['voice_path'], speaker)
                    if not self.params['voice_path']:
                        msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                        print(msg)
                        return False
            if self.engine:
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                self.engine.to(device)
                final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_index}.{default_audio_proc_format}')
                if sentence == TTS_SML['break']:
                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 0.4 to 0.7 seconds
                    self.audio_segments.append(break_tensor.clone())
                    return True
                elif not sentence.replace('—', '').strip() or sentence == TTS_SML['pause']:
                    silence_time = int(np.random.uniform(1.0, 1.8) * 100) / 100
                    pause_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 1.0 to 1.8 seconds
                    self.audio_segments.append(pause_tensor.clone())
                    return True
                else:
                    if sentence.endswith("'"):
                        sentence = sentence[:-1]
                    trim_audio_buffer = 0.002
                    sentence += '…' if sentence[-1].isalnum() else ''
                    '''
                        [laughter]
                        [laughs]
                        [sighs]
                        [music]
                        [gasps]
                        [clears throat]
                        — or ... for hesitations
                        ♪ for song lyrics
                        CAPITALIZATION for emphasis of a word
                        [MAN] and [WOMAN] to bias Bark toward male and female speakers, respectively
                    '''
                    if speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                        bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                    else:
                        bark_dir = os.path.join(os.path.dirname(self.params['voice_path']), 'bark')       
                        if not self._check_bark_npz(self.params['voice_path'], bark_dir, speaker):
                            error = 'Could not create pth voice file!'
                            print(error)
                            return False
                    pth_voice_dir = os.path.join(bark_dir, speaker)
                    pth_voice_file = os.path.join(bark_dir, speaker, f'{speaker}.pth')
                    fine_tuned_params = {
                        key.removeprefix("bark_"): cast_type(self.session[key])
                        for key, cast_type in {
                            "bark_text_temp": float,
                            "bark_waveform_temp": float
                        }.items()
                        if self.session.get(key) is not None
                    }
                    with torch.no_grad():
                        result = self.engine.synthesize(
                            sentence,
                            #speaker_wav=self.params['voice_path'],
                            speaker=speaker,
                            voice_dir=pth_voice_dir,
                            **fine_tuned_params
                        )
                    audio_sentence = result.get('wav')
                    if is_audio_data_valid(audio_sentence):
                        audio_sentence = audio_sentence.tolist()
                    if is_audio_data_valid(audio_sentence):
                        sourceTensor = self._tensor_type(audio_sentence)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        if sentence[-1].isalnum() or sentence[-1] == '—':
                            audio_tensor = trim_audio(audio_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                        if audio_tensor is not None and audio_tensor.numel() > 0:
                            self.audio_segments.append(audio_tensor)
                            if not re.search(r'\w$', sentence, flags=re.UNICODE) and sentence[-1] != '—':
                                silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                self.audio_segments.append(break_tensor.clone())
                            if self.audio_segments:
                                audio_tensor = torch.cat(self.audio_segments, dim=-1)
                                start_time = self.sentences_total_time
                                duration = round((audio_tensor.shape[-1] / self.params['samplerate']), 2)
                                end_time = start_time + duration
                                self.sentences_total_time = end_time
                                sentence_obj = {
                                    "start": start_time,
                                    "end": end_time,
                                    "text": sentence,
                                    "resume_check": self.sentence_idx
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
                        error = f"audio_sentence not valid"
                        print(error)
                        return False
            else:
                error = f"TTS engine {self.session['tts_engine']} could not be loaded!\nPossible reason can be not enough VRAM/RAM memory"
                print(error)
                return False
        except Exception as e:
            error = f'Bark.convert(): {e}'
            raise ValueError(e)
            return False