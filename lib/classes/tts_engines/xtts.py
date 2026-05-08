from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

def _has_loop_artifact(audio, rate: int, min_run: int = 4) -> bool:
    try:
        import numpy as np
        from scipy.signal import correlate
        if hasattr(audio, 'cpu'):
            audio = audio.cpu().numpy()
        audio = np.asarray(audio, dtype=np.float32).flatten()
        win_ms=0.2
        if len(audio) < rate * win_ms:
            return False
        win = int(rate * 0.2)
        min_lag = int(rate * 0.002)
        max_lag = int(rate * 0.02)
        peak_lags = []
        for start in range(int(rate * win_ms/2), len(audio) - win, int(rate * win_ms/2)):
            chunk = audio[start:start + win]
            peak = float(np.max(np.abs(chunk)))
            if peak < 0.001:
                peak_lags.append(-1)
                continue
            chunk = chunk / peak
            corr = correlate(chunk, chunk, mode='full')
            corr = corr[len(corr) // 2:]
            corr = corr / corr[0]
            peak_lags.append(int(np.argmax(corr[min_lag:max_lag])))
        if not peak_lags:
            return False
        max_run = cur_run = 1
        for i in range(1, len(peak_lags)):
            if peak_lags[i] != -1 and abs(peak_lags[i] - peak_lags[i - 1]) <= 0:
                cur_run += 1
                if cur_run > max_run:
                    max_run = cur_run
            else:
                cur_run = 1
        detected = max_run >= min_run
        #print(f'Loop check: max_run={max_run} -> {"ARTIFACT" if detected else "ok"}')
        return detected
    except Exception as e:
        print(f'_has_loop_artifact() error: {e}')
        return False

def _save_artifact(audio, rate: int, part: str, attempt: int, artifacts_dir: str, sentence_file: str) -> None:
    try:
        import torch, torchaudio, re as _re
        os.makedirs(artifacts_dir, exist_ok=True)
        safe = _re.sub(r'[^\w\-]', '_', part.strip()[:40])
        sentence_num = os.path.splitext(os.path.basename(sentence_file))[0]
        path = os.path.join(artifacts_dir, f'artifact_s{sentence_num}_attempt{attempt}_{safe}.wav')
        tensor = torch.tensor(audio).unsqueeze(0)
        torchaudio.save(path, tensor, rate)
        print(f'Artifact saved: {path}')
    except Exception as e:
        print(f'_save_artifact() error: {e}')

#sys.stderr = StdoutFilter(sys.stdout)

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
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {"latent_embedding":{}}
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
        try:
            from huggingface_hub import hf_hub_download
            msg = f'Loading TTS {self.tts_key} model, it takes a while, please be patient…'
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                if self.session['custom_model'] is not None:
                    try:
                        config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][0])
                        checkpoint_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][1])
                        vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][2])
                        self.tts_key = f'{self.session["tts_engine"]}-{self.session["custom_model"]}'
                        engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.device)
                    except Exception as e:
                        error = f'load_engine(): custom checkpoint loading failed: {e}'
                        raise RuntimeError(error) from e
                else:
                    try:
                        hf_repo = self.models[self.session['fine_tuned']]['repo']
                        if self.session['fine_tuned'] == 'internal':
                            hf_sub = ''
                            if self.speakers_path is None:
                                self.speakers_path = hf_hub_download(repo_id=hf_repo, filename='speakers_xtts.pth', cache_dir=self.cache_dir)
                        else:
                            hf_sub = self.models[self.session['fine_tuned']]['sub']
                        config_path = hf_hub_download(repo_id=hf_repo, filename=f'{hf_sub}{self.models[self.session["fine_tuned"]]["files"][0]}', cache_dir=self.cache_dir)
                        checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f'{hf_sub}{self.models[self.session["fine_tuned"]]["files"][1]}', cache_dir=self.cache_dir)
                        vocab_path = hf_hub_download(repo_id=hf_repo, filename=f'{hf_sub}{self.models[self.session["fine_tuned"]]["files"][2]}', cache_dir=self.cache_dir)
                        engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.device)
                    except Exception as e:
                        error = f'load_engine(): HuggingFace checkpoint loading failed: {e}'
                        raise RuntimeError(error) from e
            if engine:
                msg = f'TTS {self.tts_key} Loaded!'
                print(msg)
                return engine
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise RuntimeError(error) from e

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            import torchaudio
            import numpy as np
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
                fine_tuned_params = {
                    key.removeprefix('xtts_'): cast_type(self.session[key])
                    for key, cast_type in {
                        'xtts_temperature': float,
                        #'xtts_codec_temperature': float,
                        'xtts_length_penalty': float,
                        'xtts_num_beams': int,
                        'xtts_repetition_penalty': float,
                        #'xtts_cvvp_weight': float,
                        'xtts_top_k': int,
                        'xtts_top_p': float,
                        'xtts_speed': float,
                        #'xtts_gpt_cond_len': int,
                        #'xtts_gpt_batch_size': int,
                        'xtts_enable_text_splitting': bool
                    }.items()
                    if self.session.get(key) is not None
                }
                self.audio_segments = []
                _artifacts_dir = os.path.join(self.session.get('sentences_dir', ''), 'artifacts')
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
                        trim_audio_buffer = 0.006
                        if part.endswith("'"):
                            part = part[:-1]
                        part = part.replace('.', ';\n')
                        #part = part.replace(',', ';')
                        if self.params['current_voice'] is not None and self.params['current_voice'] in self.params['latent_embedding'].keys():
                            self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.params['latent_embedding'][self.params['current_voice']]
                        else:
                            msg = 'Computing speaker latents…'
                            print(msg)
                            if self.speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys():
                                self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.xtts_speakers[default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'][self.speaker]].values()
                            else:
                                self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.engine.get_conditioning_latents(audio_path=[self.params['current_voice']], load_sr=44100, sound_norm_refs=True)
                            self.params['latent_embedding'][self.params['current_voice']] = self.params['gpt_cond_latent'], self.params['speaker_embedding']
                        print(f' -> MODEL: {part!r}')
                        _attempt = 0
                        _retry_params = dict(fine_tuned_params)
                        while True:
                            with torch.inference_mode():
                                with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                    result = self.engine.inference(
                                        text=part,
                                        language=self.session['language_iso1'],
                                        gpt_cond_latent=self.params['gpt_cond_latent'],
                                        speaker_embedding=self.params['speaker_embedding'],
                                        **_retry_params
                                    )
                            audio_part = result.get('wav')
                            if torch.is_tensor(audio_part):
                                audio_part = audio_part.detach().cpu()
                            if not _has_loop_artifact(audio_part, self.params['samplerate']):
                                break
                            #_save_artifact(audio_part, self.params['samplerate'], part, _attempt, _artifacts_dir, sentence_file)
                            _attempt += 1
                            _retry_params['repetition_penalty'] = min(
                                fine_tuned_params.get('repetition_penalty', 5.0) + _attempt * 1.0, 20.0
                            )
                            _retry_params['temperature'] = min(
                                fine_tuned_params.get('temperature', 0.1) + _attempt * 0.05, 1.0
                            )
                            if _retry_params['repetition_penalty'] >= 20.0:
                                print('Loop artifact persists after max retries, using anyway…')
                                break
                        if is_audio_data_valid(audio_part):
                            src_tensor = self._tensor_type(audio_part)
                            part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                            if part_tensor is not None and part_tensor.numel() > 0:
                                if part[-1].isalnum() or part[-1] == '—':
                                    part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                self.audio_segments.append(part_tensor)
                                del part_tensor
                                if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                                    silence_time = 0.5
                                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                    self.audio_segments.append(break_tensor.clone())
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