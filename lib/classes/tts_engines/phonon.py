from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.conf import systems
from lib.lang import legends

class Phonon(TTSUtils, TTSRegistry, name='phonon'):

    def __init__(self, session:DictProxy):
        try:
            import platform
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
            # speakers: voice file -> built-in voice it is converted from (one gender detection per voice)
            self.params = {'speakers': {}}
            tts_engine = self.session.get('tts_engine')
            # effective language for TTS (target when translating, else source)
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
            if tts_engine not in default_engine_settings:
                error = legends['error_invalid_tts_engine'].format(engine=tts_engine)
                raise ValueError(error)
            settings = default_engine_settings[tts_engine]
            if self.language not in settings.get('languages', {}):
                error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
                raise ValueError(error)
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('samplerate', 'voice', 'checkpoints', 'speaker'):
                if required_key not in model_cfg:
                    error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                    raise ValueError(error)
            self.params['samplerate'] = model_cfg['samplerate']
            self.checkpoint = model_cfg['checkpoints'].get(self.language)
            if self.checkpoint is None:
                error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
                raise ValueError(error)
            # the preset's catalog voice (a voice preset), else None: the checkpoint's own default voice
            self.speaker_preset = model_cfg['speaker']
            self.speaker = self.speaker_preset
            # one engine per checkpoint, shared by every voice preset of its language: the voice travels with each call
            self.session['model_cache'] = self.tts_key = f"{tts_engine}-{self.checkpoint['repo'].rsplit('/', 1)[-1]}"
            self.model_dir = os.path.join(self.cache_dir, tts_engine, self.checkpoint['repo'].replace('/', '--'))
            self.voices_dir = os.path.join(self.cache_dir, tts_engine, settings['voices_repo'].replace('/', '--'))
            self.xtts_speakers = self._load_xtts_builtin_list()
            # ptts' PyPI wheels build no GPU backend: Phonon runs on CPU, the voice conversion keeps the session device
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            if self.device != devices['CPU']['proc']:
                msg = legends['msg_phonon_cpu'].format(engine=tts_engine, device=self.device)
                print(msg)
            # Linux / Windows x86_64 wheels are x86-64-v3: importing ptts without AVX2 / FMA / F16C kills the whole
            # process (SIGILL, no python exception), so the flags are checked before the import. macOS x86_64 has no floor
            machine = platform.machine().lower()
            if machine in ('x86_64', 'amd64') and sys.platform != systems['MACOS']:
                cpu_flags = set()
                if os.path.exists('/proc/cpuinfo'):
                    with open('/proc/cpuinfo', 'r', encoding='utf-8', errors='replace') as f:
                        features = re.search(r'^(?:Features|flags)\s*:\s*(.*)$', f.read(), re.M)
                    cpu_flags = set(features.group(1).split()) if features else set()
                elif sys.platform == systems['WINDOWS']:
                    import ctypes
                    # PF_AVX2_INSTRUCTIONS_AVAILABLE 40 (AVX2 CPUs all have FMA and F16C)
                    cpu_flags = {'avx2', 'fma', 'f16c'} if ctypes.windll.kernel32.IsProcessorFeaturePresent(40) else set()
                missing = [flag for flag in settings['cpu_flags'] if flag not in cpu_flags]
                if missing:
                    error = legends['error_phonon_cpu_flags'].format(engine=tts_engine, flags=', '.join(missing))
                    raise RuntimeError(error)
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = legends['msg_loading_tts_model'].format(model=self.tts_key)
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                settings = default_engine_settings[self.session['tts_engine']]
                progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
                if progress_bar is not None:
                    progress_bar(0.0, desc=msg)
                # plain folder under models/tts/phonon, complete once the marker exists (preload_models.py writes the same
                # one): ptts gets a local path, so it never touches the network
                marker_file = os.path.join(self.model_dir, '.e2a_complete')
                if not os.path.exists(marker_file):
                    from huggingface_hub import snapshot_download
                    from huggingface_hub.errors import GatedRepoError
                    try:
                        snapshot_download(self.checkpoint['repo'], local_dir=self.model_dir, allow_patterns=settings['checkpoint_files'])
                    except GatedRepoError:
                        # Phonon 40m: the account of e2a's HF_TOKEN has to accept its (auto-approved) conditions
                        error = legends['error_orpheus_gated'].format(repo=self.checkpoint['repo'])
                        raise RuntimeError(error)
                    open(marker_file, 'w').close()
                import ptts
                engine = ptts.TTS(
                    self.model_dir,
                    device=devices['CPU']['proc'],
                    quant=settings['quant'],
                    temperature=float(settings['temperature']),
                    lang=settings['languages'][self.language],
                    conditions={'duration_delta': float(settings['duration_delta'])} if settings['duration_delta'] else None
                )
                # in-process object, always cached: dropping it from loaded_tts frees it (unload_tts_manager /
                # cleanup_models_cache)
                loaded_tts[self.tts_key] = engine
            self.params['samplerate'] = int(engine.sample_rate)
            msg = legends['msg_tts_loaded'].format(model=self.tts_key)
            print(msg)
            return engine
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise RuntimeError(error) from e

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        part_file = f'{os.path.splitext(sentence_file)[0]}.{self.session["tts_engine"]}.wav'
        try:
            import torch
            import numpy as np
            import soundfile as sf
            from lib.classes.tts_engines.common.audio import is_audio_data_valid, detect_gender
            if self.engine:
                settings = default_engine_settings[self.session['tts_engine']]
                sentence_parts = self._split_sentence_on_sml(sentence)
                self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
                if self.params.get('inline_voice'):
                    self.params['current_voice'] = self.params['inline_voice']
                else:
                    self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                    if self.params['current_voice'] is None and error is not None:
                        return False, error
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
                        # re-read per part: an inline [voice:…] tag can switch the voice in the middle of the sentence.
                        # No voice file: the preset's voice. A voice file: a built-in voice converted to it
                        # (default_vc_model), the same-gender catalog voice for the internal preset
                        current_voice = self.params['current_voice']
                        use_zs = current_voice is not None
                        speaker = self.speaker
                        if use_zs and self.speaker_preset is None:
                            if current_voice not in self.params['speakers']:
                                gender = detect_gender(current_voice)
                                self.params['speakers'][current_voice] = next((name for name, voice in self.checkpoint['voices'].items() if gender is not None and voice[1] == gender), self.speaker)
                            speaker = self.params['speakers'][current_voice]
                        if speaker is not None and speaker not in self.engine.voices:
                            # catalog voice: downloaded once into models/tts/phonon, then registered on the shared engine
                            voice_name = f"voices/{self.checkpoint['voices'][speaker][0]}.safetensors"
                            voice_file = os.path.join(self.voices_dir, voice_name)
                            if not os.path.exists(voice_file):
                                from huggingface_hub import hf_hub_download
                                hf_hub_download(repo_id=settings['voices_repo'], filename=voice_name, local_dir=self.voices_dir)
                            self.engine.add_voice(speaker, voice_file)
                        if use_zs and not self.engine_zs:
                            # loaded on the first voice file only: the built-in voices never need it
                            self.engine_zs = self._load_engine_zs(self.device)
                            if not self.engine_zs:
                                error = legends['error_engine_not_loaded'].format(engine=self.tts_zs_key)
                                return False, error
                        samplerate = int(self.engine.sample_rate)
                        if use_zs:
                            # a voice conversion that speaks the text itself (task "tts", qwen3_tts) does not need Phonon
                            if not self.engine_zs.resynthesis:
                                self.engine.save(part_file, part, voice=speaker)
                            # voice conversion worker (VoiceConversion, default_vc_model): only paths and the text cross the
                            # pipe, the worker cuts and keeps one reference clip per voice file and the server resamples both sides itself
                            vc_file = f'{os.path.splitext(part_file)[0]}.vc.wav'
                            reply = self.engine_zs.send({
                                'op': 'vc',
                                'source': os.path.abspath(part_file),
                                'voice': os.path.abspath(current_voice),
                                'file': os.path.abspath(vc_file),
                                'text': part,
                                'language': self.language
                            })
                            if not reply.get('ok'):
                                # no retry: core.py unloads the engine, which stops the VC worker. A GPU server that died counts
                                # against its package (dropped on the second death, CPU last)
                                if reply.get('server_exited') and self.engine_zs.backend != 'cpu':
                                    self.engine_zs.gpu_crashes[self.engine_zs.package_name] = self.engine_zs.gpu_crashes.get(self.engine_zs.package_name, 0) + 1
                                if os.path.exists(vc_file):
                                    os.unlink(vc_file)
                                error = f"convert() error: {reply.get('error')} segment: {part}"
                                print(error)
                                return False, error
                            audio_part, zs_samplerate = sf.read(vc_file, dtype='float32')
                            os.unlink(vc_file)
                            if audio_part.ndim > 1:
                                audio_part = audio_part.mean(axis=1)
                            audio_part = self._resample_audiodata(audio_part, int(zs_samplerate), samplerate)
                        else:
                            # copied: the array comes from the Rust side, torch.from_numpy wants a writable one
                            audio_part = np.array(self.engine.synth(part, voice=speaker), dtype=np.float32)
                        if os.path.exists(part_file):
                            os.unlink(part_file)
                        if not is_audio_data_valid(audio_part):
                            error = 'audio_part not valid'
                            return False, error
                        self.params['samplerate'] = samplerate
                        part_tensor = self._tensor_type(audio_part).reshape(1, -1)
                        if part_tensor.numel() == 0:
                            error = 'part_tensor not valid'
                            return False, error
                        self.audio_segments.append(part_tensor)
                        if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                            silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                            self.audio_segments.append(torch.zeros(1, int(self.params['samplerate'] * silence_time)))
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
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()', e)
        finally:
            if os.path.exists(part_file):
                try:
                    os.unlink(part_file)
                except OSError:
                    pass

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
