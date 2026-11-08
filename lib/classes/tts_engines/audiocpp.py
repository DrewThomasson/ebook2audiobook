import json
from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.classes.tts_engines.common.voice_conversion import VoiceConversion
from lib.conf_models import TTS_VOICE_CONVERSION, default_vc_model, audiocpp_packages, audiocpp_asr, audiocpp_engines, audiocpp_repo
from lib.lang import legends

class AudioCpp(TTSUtils):

    def __init__(self, session:DictProxy):
        # audio.cpp (0xShug0/audio.cpp): a native audiocpp_server package per platform (audiocpp_packages, shared by
        # every audio.cpp engine) plus the GGUF weights of the fine_tuned preset, driven by workers/audiocpp_worker.py.
        # No torch, no venv
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
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
            fine_tuned = self.session.get('fine_tuned')
            show_alert = getattr(sys.modules.get('lib.core'), 'show_alert', None)
            progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
            if fine_tuned not in self.models:
               error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
               raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'files', 'samplerate', 'voice'):
               if required_key not in model_cfg:
                  error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                  raise ValueError(error)
            self.family_cfg = settings['audiocpp']
            self.family = self.family_cfg['family']
            # a preset may speak fewer languages than its engine (IndexTTS2 v2)
            languages = model_cfg.get('languages') or settings['languages']
            if self.language not in languages:
               error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=f'{tts_engine} ({fine_tuned})')
               raise ValueError(error)
            self.language_code = languages[self.language]
            # built-in voice for this language (engines that do not clone)
            self.voice_id = self.family_cfg['voice_ids'].get(self.language, self.family_cfg['voice_ids'].get('*', ''))
            # one package per language (PocketTTS), with its load options
            model_files = model_cfg.get('files_by_language', {}).get(self.language, model_cfg['files'])
            self.load_options = {**self.family_cfg['load'], **self.family_cfg['load_by_language'].get(self.language, {})}
            self.params['samplerate'] = model_cfg['samplerate']
            self.model_repo = model_cfg['repo']
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            # --- the audiocpp_server package for this machine (VoiceConversion: shared with the VC stage of the built-in voice engines) ---
            attempts, gpu_wanted = VoiceConversion.packages(self.session, tts_engine)
            # --- GGUF weights through e2a's Hugging Face cache (tts_dir) ---
            from huggingface_hub import hf_hub_download
            # cloning engines taking a reference transcript also get the ASR model, loaded by the worker only for a voice it
            # has never transcribed, then unloaded. Built-in voice engines get default_vc_model for a picked voice file, run in
            # the same server; one that speaks the text again (task "tts") would only replace this engine, so they take its
            # fallback then
            asr_files = audiocpp_asr['files'] if self.family_cfg['clone'] and self.family_cfg['ref_text'] else []
            self.vc_cfg = TTS_VOICE_CONVERSION[default_vc_model.rsplit('/', 1)[-1]]
            self.vc_cfg = self.vc_cfg if self.vc_cfg['task'] == 'vc' else TTS_VOICE_CONVERSION[self.vc_cfg['fallback']]
            vc_preset = load_engine_presets(self.vc_cfg['engine'])['internal'] if self.vc_cfg.get('engine') else {'repo': audiocpp_repo, 'files': self.vc_cfg['files']}
            vc_files = vc_preset['files'] if not self.family_cfg['clone'] else []
            msg = legends['msg_zonos2_models'].format(engine=tts_engine, files=', '.join(os.path.basename(f) for f in model_files + asr_files + vc_files))
            print(msg)
            if progress_bar is not None:
               progress_bar(0.0, desc=msg)
            # real files under models/tts/audiocpp/<repo>/, not the Hugging Face cache: a cache file is a symlink to an
            # extension-less blob (huggingface_hub 2's shared store, models/tts/blobs/<xx>/<hash>), and audiocpp_server
            # resolves symlinks (weakly_canonical) then picks the tensor format from the file extension, so it rejects the
            # blob ("unsupported tensor source format"). local_dir keeps the repo layout, so sidecars (pocket_tts
            # embeddings/) land beside the model file, and a file already in the cache is copied instead of downloaded
            self.model_path = [hf_hub_download(repo_id=self.model_repo, filename=f, cache_dir=self.cache_dir, local_dir=os.path.join(self.cache_dir, 'audiocpp', self.model_repo.replace('/', '--'))) for f in model_files][0]
            self.asr_path = [hf_hub_download(repo_id=audiocpp_repo, filename=f, cache_dir=self.cache_dir, local_dir=os.path.join(self.cache_dir, 'audiocpp', audiocpp_repo.replace('/', '--'))) for f in asr_files][0] if asr_files else ''
            self.vc_path = [hf_hub_download(repo_id=vc_preset['repo'], filename=f, cache_dir=self.cache_dir, local_dir=os.path.join(self.cache_dir, 'audiocpp', vc_preset['repo'].replace('/', '--'))) for f in vc_files][0] if vc_files else ''
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            self.worker_script = os.path.join(engine_dir, 'workers', 'audiocpp_worker.py')
            # the worker is stdlib only. conf.py's OMP_NUM_THREADS=1 is for e2a's torch: the server (OpenMP build) sizes its own pool
            self.worker_env = {k: v for k, v in os.environ.items() if k not in ('PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', '__PYVENV_LAUNCHER__', 'OMP_NUM_THREADS')}
            self.worker_env['PYTHONUNBUFFERED'] = '1'
            if self.family_cfg['espeak']:
               # Kokoro phonemizes through eSpeak-ng: the library and data e2a's launchers export (else eSpeak's own defaults)
               espeak_library = os.environ.get('PHONEMIZER_ESPEAK_LIBRARY', '')
               espeak_data = os.environ.get('ESPEAK_DATA_PATH', '')
               if espeak_library and os.path.isfile(espeak_library):
                  self.worker_env['AUDIOCPP_ESPEAK_LIBRARY'] = espeak_library
               if espeak_data and os.path.isfile(os.path.join(espeak_data, 'phontab')):
                  self.worker_env['AUDIOCPP_ESPEAK_DATA'] = espeak_data
            for attempt, self.package_name in enumerate(attempts):
               package = audiocpp_packages[self.package_name]
               self.backend = package.get('backend', 'cpu') if package['gpu'] and gpu_wanted else 'cpu'
               try:
                  self.server_bin = VoiceConversion.install(self.package_name, tts_engine, self.worker_env)
                  self.engine = self.load_engine()
                  break
               except Exception as e:
                  if attempt + 1 >= len(attempts):
                     raise
                  msg = legends['msg_zonos2_gpu_failed'].format(engine=tts_engine, package=self.package_name, error=e)
                  if show_alert is not None:
                     show_alert(self.session['id'], {'type': 'warning', 'msg': msg})
                  else:
                     print(msg)
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = legends['msg_loading_tts_model'].format(model=self.tts_key)
            print(msg)
            self.cleanup_memory()
            cmd = [
               sys.executable, '-u', self.worker_script, '--server', self.server_bin, '--model', self.model_path, '--family', self.family, '--backend', self.backend,
               '--load-options', json.dumps(self.load_options), '--session-options', json.dumps(self.family_cfg['session']), '--request-options', json.dumps(self.family_cfg['request']),
               '--ref-min', str(self.family_cfg['ref_min']), '--ref-max', str(self.family_cfg['ref_max'] if self.family_cfg['clone'] else self.vc_cfg['ref_max']), '--ref-text', self.family_cfg['ref_text'] or 'none', '--ref-fallback', json.dumps(self.family_cfg['ref_fallback']),
               '--asr-model', self.asr_path, '--asr-family', audiocpp_asr['family'], '--vc-model', self.vc_path, '--vc-family', self.vc_cfg['family'], '--vc-route', self.vc_cfg.get('route', ''), '--samplerate', str(self.params['samplerate'])
            ] + (['--language-option'] if self.family_cfg['language_option'] else []) + (['--clone'] if self.family_cfg['clone'] else []) + (['--speaker-label'] if self.family_cfg['speaker_label'] else [])
            engine = loaded_tts.get(self.tts_key)
            if isinstance(engine, SubprocessPipe) and (engine.cmd != cmd or engine.process is None or engine.process.poll() is not None):
               # dead worker, or one serving another model/package/backend under this key
               loaded_tts.pop(self.tts_key, None)
               engine.stop()
               engine = None
            if not engine:
               msg = legends['msg_worker_starting'].format(engine=self.session['tts_engine'], model=os.path.basename(self.model_path), device=f'{self.package_name}, {self.backend}')
               print(msg)
               progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
               if progress_bar is not None:
                  progress_bar(0.0, desc=msg)
               engine = SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, keep_alive=True, env=self.worker_env)
               if not engine.result:
                  error = legends['error_worker_failed'].format(engine=self.session['tts_engine'], error=engine.ready_info.get('error'))
                  raise RuntimeError(error)
               # always cached, whatever the free VRAM: the worker must stay reachable by
               # unload_tts_manager() / cleanup_models_cache(), which stop it
               loaded_tts[self.tts_key] = engine
            self.params['samplerate'] = int(engine.ready_info.get('samplerate', self.params['samplerate']))
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
            from lib.classes.tts_engines.common.audio import is_audio_data_valid
            if self.engine:
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
                      # only the voice path crosses the pipe: the worker cuts one reference clip per voice file and keeps it.
                      # Built-in voice engines: voice None = their own voice (voice_id), a voice file = converted to it
                      reply = self.engine.send({
                         'op': 'tts',
                         'text': part,
                         'language': self.language_code,
                         'voice': self.params['current_voice'],
                         'voice_id': self.voice_id,
                         'file': part_file
                      })
                      if not reply.get('ok') and reply.get('server_exited') and self.backend != 'cpu':
                         # the GPU server died mid-sentence (driver abort): restart it once, drop the package on its second
                         # death, and redo the whole sentence with a fresh engine (__init__ picks the package, CPU last)
                         crashes = VoiceConversion.gpu_crashes[self.package_name] = VoiceConversion.gpu_crashes.get(self.package_name, 0) + 1
                         error = str(reply.get('error') or '')
                         error = (error.split(': ', 1)[0] + ': ' + error.split(' | ')[-1]) if ' | ' in error else error
                         msg = legends['msg_zonos2_gpu_restart' if crashes < 2 else 'msg_zonos2_gpu_dropped'].format(engine=self.session['tts_engine'], package=self.package_name, error=error)
                         show_alert = getattr(sys.modules.get('lib.core'), 'show_alert', None)
                         if show_alert is not None:
                            show_alert(self.session['id'], {'type': 'warning', 'msg': msg})
                         else:
                            print(msg)
                         loaded_tts.pop(self.tts_key, None)
                         self.engine.stop()
                         self.engine = None
                         self.__init__(self.session)
                         return self.convert(sentence_file, sentence, **kwargs)
                      if not reply.get('ok'):
                         # no retry: core.py unloads the engine, which stops the worker
                         error = f"convert() error: {reply.get('error')} segment: {part}"
                         print(error)
                         return False, error
                      audio_part, samplerate = sf.read(part_file, dtype='float32')
                      os.unlink(part_file)
                      if audio_part.ndim > 1:
                         audio_part = audio_part.mean(axis=1)
                      if not is_audio_data_valid(audio_part):
                         error = 'audio_part not valid'
                         return False, error
                      if int(samplerate) != self.params['samplerate']:
                         # the preset's rate was a guess: silences already queued ([break] before the first reply) are
                         # rebuilt at the real one
                         self.audio_segments = [torch.zeros(1, int(seg.shape[-1] * int(samplerate) / self.params['samplerate'])) for seg in self.audio_segments]
                         self.params['samplerate'] = int(samplerate)
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

# one registered engine per audio.cpp family (TTS_ENGINES), all run by AudioCpp
for _acpp_engine in audiocpp_engines:
    type(f"AudioCpp_{_acpp_engine}", (AudioCpp, TTSRegistry), {}, name=_acpp_engine)
