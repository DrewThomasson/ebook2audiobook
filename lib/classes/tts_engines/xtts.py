from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class XTTSv2(TTSUtils, TTSRegistry, name='xtts'):

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
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {"latent_embedding":{}}
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
                    config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][0])
                    checkpoint_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][1])
                    vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][2])
                    self.tts_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                    engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path)
                else:
                    hf_repo = self.models[self.session['fine_tuned']]['repo']
                    if self.session['fine_tuned'] == 'internal':
                        hf_sub = ''
                        if self.speakers_path is None:
                            self.speakers_path = hf_hub_download(repo_id=hf_repo, filename='speakers_xtts.pth', cache_dir=self.cache_dir)
                    else:
                        hf_sub = self.models[self.session['fine_tuned']]['sub']
                    config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                    checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                    vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{self.models[self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                    engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path)
            if engine and engine is not None:
                msg = f'TTS {self.tts_key} Loaded!'
                return engine
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise ValueError(error)

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            if self.engine:
                final_sentence_file = os.path.join(self.session['sentences_dir'], f'{sentence_index}.{default_audio_proc_format}')
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                sentence_parts = re.split(default_frontend_sml_pattern, sentence)
                self.audio_segments = []
                for part in sentence_parts:
                    part = part.strip()
                    if not part or not any(c.isalnum() for c in sentence):
                        continue
                    if default_frontend_sml_pattern.fullmatch(part):
                        if not self._convert_sml(part):
                            error = f'_convert_sml failed: {part}'
                            print(error)
                            return False
                    else:
                        trim_audio_buffer = 0.006
                        if part.endswith("'"):
                            part = part[:-1]
                        part = part.replace('.', ' ;\n')
                        if self._set_voice():
                            if self.params['voice_path'] is not None and self.params['voice_path'] in self.params['latent_embedding'].keys():
                                self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.params['latent_embedding'][self.params['voice_path']]
                            else:
                                msg = 'Computing speaker latents…'
                                print(msg)
                                if self.speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys():
                                    self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.xtts_speakers[default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'][self.speaker]].values()
                                else:
                                    self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.engine.get_conditioning_latents(audio_path=[self.params['voice_path']], librosa_trim_db=30, load_sr=24000, sound_norm_refs=True)  
                                self.params['latent_embedding'][self.params['voice_path']] = self.params['gpt_cond_latent'], self.params['speaker_embedding']
                            fine_tuned_params = {
                                key.removeprefix("xtts_"): cast_type(self.session[key])
                                for key, cast_type in {
                                    "xtts_temperature": float,
                                    #"xtts_codec_temperature": float,
                                    "xtts_length_penalty": float,
                                    "xtts_num_beams": int,
                                    "xtts_repetition_penalty": float,
                                    #"xtts_cvvp_weight": float,
                                    "xtts_top_k": int,
                                    "xtts_top_p": float,
                                    "xtts_speed": float,
                                    #"xtts_gpt_cond_len": int,
                                    #"xtts_gpt_batch_size": int,
                                    "xtts_enable_text_splitting": bool
                                }.items()
                                if self.session.get(key) is not None
                            }
                            with torch.no_grad():
                                self.engine.to(device)
                                if device == devices['CPU']['proc']:
                                    result = self.engine.inference(
                                        text=part,
                                        language=self.session['language_iso1'],
                                        gpt_cond_latent=self.params['gpt_cond_latent'],
                                        speaker_embedding=self.params['speaker_embedding'],
                                        **fine_tuned_params
                                    )
                                else:
                                    with torch.autocast(
                                        device_type=device,
                                        dtype=self.amp_dtype
                                    ):
                                        result = self.engine.inference(
                                            text=part,
                                            language=self.session['language_iso1'],
                                            gpt_cond_latent=self.params['gpt_cond_latent'],
                                            speaker_embedding=self.params['speaker_embedding'],
                                            **fine_tuned_params
                                        )
                                self.engine.to(devices['CPU']['proc'])
                            audio_part = result.get('wav')
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
            error = f'Xttsv2.convert(): {e}'
            print(error)
            return False

    def create_vtt(self, all_sentences:list)->bool:
        audio_dir = self.session['sentences_dir']
        vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
        if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
            return True
        return False