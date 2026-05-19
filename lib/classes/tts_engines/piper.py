from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

#sys.stderr = StdoutFilter(sys.stdout)

class Piper(TTSUtils, TTSRegistry, name='piper'):

    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.tts_zs_key = default_vc_model.rsplit('/', 1)[-1]
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {"semitones": {}}
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
            tts_engine = self.session.get('tts_engine')
            if tts_engine not in default_engine_settings:
                error = f'Invalid tts_engine {tts_engine}.'
                raise ValueError(error)
            engine_langs = default_engine_settings[tts_engine].get('languages', {})
            if self.language not in engine_langs:
                error = f'Language {self.language} not supported by engine {tts_engine}.'
                raise ValueError(error)
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}'
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate'):
                if required_key not in model_cfg:
                    error = f'fine_tuned model {fine_tuned} is missing required key {required_key}.'
                    raise ValueError(error)
            piper_lang = engine_langs[self.language]
            sub_list = default_engine_settings[tts_engine].get('sub', {})
            voice_file = self.session.get('block_voice', self.session['voice'])
            voice_name = Path(voice_file).stem if voice_file is not None else None
            self.model_path =  voice_name if any(voice_name in voices for voices in sub_list.values()) else sub_list[piper_lang][0]
            self.is_builtin_voice = any(voice_name in voices for voices in sub_list.values())
            if not self.model_path :
                error = f'No piper voice code mapped for language {self.language} ({piper_lang}).'
                raise ValueError(error)
            self.params['samplerate'] = model_cfg['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            self.engine = self.load_engine()
            if self.engine is not None and hasattr(self.engine, 'output_sample_rate'):
                self.params['samplerate'] = int(self.engine.output_sample_rate)
            self.engine_zs = self._load_engine_zs(self.device)
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                if self.session['custom_model'] is not None:
                    model_dir = self.session['custom_model']
                    config_path = None
                    onnx_path = None
                    for fname in os.listdir(model_dir):
                        full = os.path.join(model_dir, fname)
                        if fname == 'config.onnx.json' and config_path is None:
                            config_path = full
                        elif fname == 'model.onnx' and onnx_path is None:
                            onnx_path = full
                    custom_model_name = os.path.basename(os.path.normpath(model_dir))
                    self.tts_key = f"{self.session['tts_engine']}-{custom_model_name}"
                else:
                    from piper.download_voices import download_voice
                    self.tts_key = f"{self.session['tts_engine']}-{self.model_path}"
                    download_dir = Path(self.cache_dir) / self.session['tts_engine']
                    download_dir.mkdir(parents=True, exist_ok=True)
                    onnx_path = download_dir / f'{self.model_path}.onnx'
                    config_path = download_dir / f'{self.model_path}.onnx.json'
                    if not (onnx_path.exists() and config_path.exists()):
                        msg = f'Downloading piper model {self.model_path} → {download_dir}'
                        print(msg)
                        download_voice(self.model_path, download_dir)
                try:
                    from piper import PiperVoice
                    engine = loaded_tts.get(key)
                    if engine:
                        return engine
                    use_cuda = self.device == devices['CUDA']['proc']
                    engine = PiperVoice.load(onnx_path, config_path=config_path, use_cuda=use_cuda)
                    self.output_sample_rate = int(engine.config.sample_rate)
                    try:
                        spk_map = getattr(engine.config, 'speaker_id_map', None) or {}
                        self.speakers = list(spk_map.keys()) if spk_map else None
                    except Exception:
                        self.speakers = None
                    vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                except Exception as e:
                    error = f'_load_piper() error: {e}'
                    print(error)
                    raise
            if engine:
                msg = f'TTS {self.tts_key} Loaded!'
                print(msg)
                return engine
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)
        except Exception as e:
            error = f"load_engine() error: {e}"
            raise RuntimeError(error) from e

    def tts(self, text:str, **_:Any)->Any:
        import numpy as np
        chunks = []
        for chunk in self.engine.synthesize(text):
            arr = chunk.audio_float_array
            if arr is not None and arr.size > 0:
                chunks.append(arr)
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks).astype(np.float32, copy=False)

    def tts_to_file(self, text:str, file_path:str, **_:Any)->str:
        import wave
        with wave.open(file_path, 'wb') as wav_file:
            self.engine.synthesize_wav(text, wav_file)
        return file_path

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            import torchaudio
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid, detect_gender
            if self.engine:
                sentence_parts = self._split_sentence_on_sml(sentence)
                self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
                if self.params.get('inline_voice'):
                    self.params['current_voice'] = self.params['inline_voice']
                else:
                    self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                    if self.params['current_voice'] is None and error is not None:
                        return False, error
                self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else None
                self.audio_segments = []
                use_zs = self.params['current_voice'] is not None
                if use_zs and not self.engine_zs:
                    error = f'Engine {self.tts_zs_key} is None'
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
                             use_zs = self.params['current_voice'] is not None
                        else:
                            return False, error
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        try:
                            if use_zs:
                                tmp_in_wav = os.path.join(proc_dir, f'{uuid.uuid4()}.wav')
                                tmp_out_wav = os.path.join(proc_dir, f'{uuid.uuid4()}.wav')
                                result = False
                                # Piper is ONNX; autocast is a no-op here but harmless and keeps parity.
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
                                    msg = f'Cloned voice seems to be {current_voice_gender}\nBuiltin voice seems to be {voice_builtin_gender}'
                                    print(msg)
                                    if voice_builtin_gender != current_voice_gender:
                                        semitones = -4 if current_voice_gender == 'male' else 4
                                        msg = f'Adapting builtin voice frequencies from the clone voice…'
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
                                        error = f'Subprocess error: {e.stderr}'
                                        DependencyError(error)
                                        return False, error
                                    except FileNotFoundError as e:
                                        error = f'File not found: {e}'
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
                                part_tensor = self._tensor_type(audio_part).detach().unsqueeze(0)
                                if part_tensor.numel() == 0:
                                    error = 'part_tensor not valid'
                                    return False, error
                            else:
                                error = f'audio_part not valid'
                                return False, error
                        except IndexError as e:
                            error = f'tts_to_file() error at {e} segment: {part}'
                            print(error)
                            audio_part = False
                            pass
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                        error = f'audio_save() error: cannot save {sentence_file}'
                        return False, error
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
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()',e)

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
