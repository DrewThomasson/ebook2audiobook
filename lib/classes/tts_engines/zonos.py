import json
from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.conf import systems
from lib.lang import legends

class Zonos(TTSUtils, TTSRegistry, name='zonos'):
    # GPU packages whose server died during a conversion, per e2a process: package -> crash count. One crash restarts
    # the same package (driver aborts can be rare), a second one drops it until e2a restarts (next GPU package, else CPU)
    gpu_crashes = {}

    def __init__(self, session:DictProxy):
        # ZONOS2 (Zyphra zonos2.cpp): a native zonos2-server package per platform (default_engine_settings
        # ['packages']) plus the GGUF weights, driven by workers/zonos_worker.py. No torch and no venv.
        try:
            import platform, tarfile, zipfile, urllib.request
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
            engine_langs = settings.get('languages', {})
            if self.language not in engine_langs:
               error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
               raise ValueError(error)
            self.language_code = engine_langs[self.language]
            fine_tuned = self.session.get('fine_tuned')
            show_alert = getattr(sys.modules.get('lib.core'), 'show_alert', None)
            progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
            if fine_tuned == 'hybrid':
               # Zonos v0.1's hybrid backbone has no ZONOS2 equivalent: sessions saved with it move to the default
               fine_tuned = self.session['fine_tuned'] = 'internal'
               self.session['model_cache'] = self.tts_key = f'{tts_engine}-{fine_tuned}'
               msg = legends['msg_zonos2_hybrid_gone'].format(model=fine_tuned)
               if show_alert is not None:
                  show_alert(self.session['id'], {'type': 'warning', 'msg': msg})
               else:
                  print(msg)
            if fine_tuned not in self.models:
               error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
               raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'file', 'samplerate', 'voice'):
               if required_key not in model_cfg:
                  error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                  raise ValueError(error)
            self.params['samplerate'] = model_cfg['samplerate']
            self.model_repo = model_cfg['repo']
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            self.fine_tuned_params = {
               key.removeprefix('zonos_'): cast_type(self.session[key]) if self.session.get(key) is not None else cast_type(settings[key.removeprefix('zonos_')])
               for key, cast_type in {
                  'zonos_emotion_enabled': bool,
                  'zonos_emotion_strength': float,
                  'zonos_emotion_cfg_scale': float,
                  'zonos_speaking_rate': float
               }.items()
            }
            # happy, sad, angry, surprised (0..1), valence, arousal (-1..1): one session key per slider
            self.fine_tuned_params['emotion'] = {
               name: float(self.session[f'zonos_emotion_{name}']) if self.session.get(f'zonos_emotion_{name}') is not None else float(default)
               for name, default in settings['emotion'].items()
            }
            # --- the zonos2-server package for this machine ---
            machine = platform.machine().lower()
            gpu_wanted = self.session['device'] != devices['CPU']['proc']
            packages = settings['packages']
            jetpack = board_sm = None
            if sys.platform == systems['LINUX'] and os.path.exists('/etc/nv_tegra_release'):
               # L4T release -> JetPack major (R35 = 5, R36 = 6, R38+ = 7); board -> GPU architecture
               with open('/etc/nv_tegra_release', 'r', encoding='utf-8', errors='replace') as f:
                  l4t = re.search(r'R(\d+)', f.read())
               jetpack = {35: 5, 36: 6}.get(int(l4t.group(1)), 7 if int(l4t.group(1)) >= 38 else None) if l4t else None
               try:
                  with open('/proc/device-tree/model', 'r', encoding='utf-8', errors='replace') as f:
                     board = f.read()
                  board_sm = 110 if 'Thor' in board else 87 if 'Orin' in board else 72 if 'Xavier' in board else None
               except OSError:
                  board_sm = None
            if sys.platform == systems['LINUX'] and machine in ('x86_64', 'amd64'):
               candidates = (['linux-x64-cuda13', 'linux-x64-cuda12'] if self.device == devices['CUDA']['proc'] else []) + (['linux-x64-vulkan', 'linux-x64-vulkan-zyphra'] if gpu_wanted else []) + ['linux-x64-cpu-avx2', 'linux-x64-cpu-sse42', 'linux-x64-cpu-zyphra', 'linux-x64-vulkan-zyphra']
            elif sys.platform == systems['LINUX'] and machine in ('aarch64', 'arm64'):
               if jetpack is not None:
                  candidates = [k for k, v in packages.items() if v.get('jetpack') == jetpack and board_sm in v.get('sm', [])] + (['linux-aarch64-cuda13'] if jetpack >= 7 else [])
               else:
                  candidates = ['linux-aarch64-cuda13', 'linux-aarch64-cuda12'] if self.device == devices['CUDA']['proc'] else []
               candidates = (candidates if gpu_wanted else []) + ['linux-aarch64-v82', 'linux-aarch64']
            elif sys.platform == systems['WINDOWS'] and machine in ('amd64', 'x86_64'):
               # CPU builds without Vulkan first: they start even where no vulkan-1.dll exists (old GPUs, VMs).
               # Zyphra's Vulkan build stays the last resort with --cpu (needs vulkan-1.dll and AVX2)
               # CUDA 13 then 12, own Vulkan build (SSE4.2 CPU part: CPUs without AVX2 too) then Zyphra's (AVX2)
               candidates = (['windows-x64-cuda13', 'windows-x64-cuda12'] if self.device == devices['CUDA']['proc'] else []) + (['windows-x64-vulkan', 'windows-x64-vulkan-zyphra'] if gpu_wanted else []) + ['windows-x64-cpu-avx2', 'windows-x64-cpu-sse42', 'windows-x64-vulkan-zyphra']
            elif sys.platform == systems['MACOS']:
               # arm64: own Metal build first, Zyphra's as the GPU fallback. x86_64: Vulkan (MoltenVK) build on a GPU device
               candidates = ['macos-arm64', 'macos-arm64-metal', 'macos-arm64-cpu'] if machine == 'arm64' else (['macos-x86_64-vulkan'] if gpu_wanted else []) + ['macos-x86_64']
            else:
               candidates = []
            # CPU features the packages may need, with /proc/cpuinfo names on every OS
            cpu_flags = set()
            if os.path.exists('/proc/cpuinfo'):
               with open('/proc/cpuinfo', 'r', encoding='utf-8', errors='replace') as f:
                  features = re.search(r'^(?:Features|flags)\s*:\s*(.*)$', f.read(), re.M)
               cpu_flags = set(features.group(1).split()) if features else set()
            elif sys.platform == systems['WINDOWS']:
               import ctypes
               present = ctypes.windll.kernel32.IsProcessorFeaturePresent
               # PF_SSE4_2_INSTRUCTIONS_AVAILABLE 38, PF_AVX2_INSTRUCTIONS_AVAILABLE 40 (AVX2 CPUs all have FMA, F16C, BMI2)
               cpu_flags = ({'sse4_2'} if present(38) else set()) | ({'avx2', 'fma', 'f16c', 'bmi2'} if present(40) else set())
            glibc = platform.libc_ver()
            glibc_version = tuple(int(x) for x in re.findall(r'\d+', glibc[1])[:2]) if glibc[0] == 'glibc' and glibc[1] else (0, 0)
            machine_desc = f'{sys.platform} {machine}' + (f' JetPack {jetpack}' if jetpack else '') + (f' sm_{board_sm}' if board_sm else '')
            usable = [
               k for k in dict.fromkeys(candidates)
               if k in packages and packages[k].get('enabled', True) and set(packages[k].get('cpu_flags', [])) <= cpu_flags
               and Zonos.gpu_crashes.get(k, 0) < 2
               and glibc_version >= tuple(int(x) for x in packages[k].get('glibc_min', '0.0').split('.'))
            ]
            if not usable:
               error = legends['error_zonos2_no_package'].format(engine=tts_engine, machine=machine_desc)
               raise ValueError(error)
            # first choice, plus the CPU package to fall back on if a GPU package cannot start
            # (no Vulkan loader, an old driver, a too old system library)
            # a GPU first choice is followed by the other GPU packages (CUDA 13 -> CUDA 12, own Vulkan -> Zyphra's),
            # then by one CPU package
            attempts = [usable[0]]
            if packages[usable[0]]['gpu']:
               attempts = [k for k in usable if packages[k]['gpu']] + [k for k in usable if not packages[k]['gpu']][:1]
            if gpu_wanted and not packages[usable[0]]['gpu'] and not any(n >= 2 for n in Zonos.gpu_crashes.values()):
               msg = legends['msg_zonos2_cpu_fallback'].format(engine=tts_engine, machine=machine_desc)
               if show_alert is not None:
                  show_alert(self.session['id'], {'type': 'warning', 'msg': msg})
               else:
                  print(msg)
            # --- GGUF weights through e2a's Hugging Face cache (tts_dir) ---
            from huggingface_hub import hf_hub_download
            msg = legends['msg_zonos2_models'].format(engine=tts_engine, files=', '.join(model_cfg['files']))
            print(msg)
            if progress_bar is not None:
               progress_bar(0.0, desc=msg)
            self.model_path, self.dac_path, self.spk_path = (hf_hub_download(repo_id=self.model_repo, filename=f, cache_dir=self.cache_dir) for f in (model_cfg['file'], settings['dac'], settings['spk']))
            # the worker is stdlib only: e2a's own interpreter runs it, nothing from python_env is imported
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            self.worker_script = os.path.join(engine_dir, 'workers', f'{tts_engine}_worker.py')
            self.worker_env = {k: v for k, v in os.environ.items() if k not in ('PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', '__PYVENV_LAUNCHER__')}
            self.worker_env['PYTHONUNBUFFERED'] = '1'
            # CUDA packages that do not bundle cuBLAS / cudart find them in the NVIDIA pip packages e2a's own CUDA
            # PyTorch installed into python_env (site-packages/nvidia/<x>/lib, CUDA 13: nvidia/cu13/lib; Windows
            # also torch/lib), so a driver-only machine still runs on GPU. Sonames are per CUDA major (.so.12 / .so.13):
            # a package of another major skips these and uses a system CUDA, a bundled lib/ or falls back
            import importlib.util
            cuda_dirs = []
            for module, leaves in (('nvidia', ('lib', 'bin')), ('torch', ('',))):
               spec = importlib.util.find_spec(module)
               for root in (spec.submodule_search_locations or []) if spec else []:
                  for path in ([os.path.join(root, 'lib')] if module == 'torch' else [os.path.join(root, sub, leaf) for sub in sorted(os.listdir(root)) for leaf in leaves]):
                     if os.path.isdir(path) and any(n.lower().startswith(('libcudart', 'libcublas', 'cudart64', 'cublas64', 'cublaslt64')) for n in os.listdir(path)):
                        cuda_dirs.append(path)
            if cuda_dirs:
               var = 'PATH' if sys.platform == systems['WINDOWS'] else 'LD_LIBRARY_PATH'
               self.worker_env[var] = os.pathsep.join([p for p in self.worker_env.get(var, '').split(os.pathsep) if p] + cuda_dirs)
            for attempt, self.package_name in enumerate(attempts):
               package = packages[self.package_name]
               if package.get('macos_min'):
                 mac_major = int((platform.mac_ver()[0] or '0').split('.')[0])
                 if mac_major < package['macos_min']:
                    # too old a macOS for this package: the next one may start (Apple Silicon: own build 11+, then
                    # Zyphra's 15+), the error only when none is left
                    if attempt + 1 < len(attempts):
                       continue
                    error = legends['error_zonos2_macos_min'].format(engine=tts_engine, min=package['macos_min'], version=platform.mac_ver()[0])
                    raise ValueError(error)
               # Metal / Vulkan / CUDA builds run --gpu only when e2a's device is a GPU (cpu keeps --cpu)
               self.backend = 'gpu' if package['gpu'] and gpu_wanted else 'cpu'
               try:
                  engine_dir = os.path.dirname(os.path.abspath(__file__))
                  packages_dir = os.path.join(engine_dir, 'venvs', tts_engine)
                  if os.path.exists(os.path.join(packages_dir, 'pyvenv.cfg')):
                     # the Zonos v0.1 venv (torch, several GB) has no use with ZONOS2: replaced by its packages
                     msg = legends['msg_zonos2_old_venv'].format(dir=packages_dir)
                     print(msg)
                     shutil.rmtree(packages_dir, ignore_errors=True)
                  package_dir = os.path.join(packages_dir, self.package_name)
                  marker_file = os.path.join(package_dir, '.e2a_installed.json')
                  # downloaded once: a package folder with its install record is used as it is from then on
                  # (the record is written only after a complete download and unpacking)
                  # a folder whose record names another URL (a package key moved to another build, e.g. windows-x64-vulkan
                  # from Zyphra's to e2a's own) is downloaded again
                  try:
                     with open(marker_file, 'r', encoding='utf-8') as f:
                        installed_url = json.load(f).get('url')
                  except Exception:
                     installed_url = None
                  if installed_url != package['url']:
                     msg = legends['msg_zonos2_downloading'].format(engine=tts_engine, package=self.package_name)
                     print(msg)
                     if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                     shutil.rmtree(package_dir, ignore_errors=True)
                     os.makedirs(package_dir, exist_ok=True)
                     archive = os.path.join(package_dir, os.path.basename(package['url']))
                     try:
                        # urllib: no quarantine flag on macOS, so the unsigned binaries start without a Gatekeeper prompt
                        with urllib.request.urlopen(package['url'], timeout=60) as r, open(archive, 'wb') as f:
                           total = int(r.headers.get('Content-Length') or 0)
                           done = 0
                           while True:
                              chunk = r.read(1 << 20)
                              if not chunk:
                                 break
                              f.write(chunk)
                              done += len(chunk)
                              if progress_bar is not None and total:
                                 progress_bar(done / total, desc=msg)
                        if archive.endswith('.zip'):
                           with zipfile.ZipFile(archive) as z:
                              z.extractall(package_dir)
                        else:
                           with tarfile.open(archive, 'r:gz') as t:
                              t.extractall(package_dir, **({'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}))
                        os.unlink(archive)
                     except Exception as e:
                        shutil.rmtree(package_dir, ignore_errors=True)
                        error = legends['error_zonos2_download'].format(engine=tts_engine, package=self.package_name, error=e)
                        raise RuntimeError(error)
                     with open(marker_file, 'w', encoding='utf-8') as f:
                        json.dump({'url': package['url']}, f, indent=2)
                  # Zyphra's archives are flat, e2a's have a top folder: take the server wherever it is
                  server_name = 'zonos2-server.exe' if sys.platform == systems['WINDOWS'] else 'zonos2-server'
                  self.server_bin = next((os.path.join(root, server_name) for root, _, files in os.walk(package_dir) if server_name in files), None)
                  if self.server_bin is None:
                     shutil.rmtree(package_dir, ignore_errors=True)
                     error = legends['error_zonos2_download'].format(engine=tts_engine, package=self.package_name, error=f'{server_name} not found in the package')
                     raise RuntimeError(error)
                  if sys.platform != systems['WINDOWS']:
                     os.chmod(self.server_bin, os.stat(self.server_bin).st_mode | 0o755)
                  self.emotion_dir = os.path.join(os.path.dirname(self.server_bin), 'emotion_directions')
                  # macOS Vulkan package: it carries its own loader and MoltenVK in lib/, point the loader at that
                  # MoltenVK (the system has no Vulkan driver list), unless the user set one
                  icd = os.path.join(os.path.dirname(self.server_bin), 'lib', 'MoltenVK_icd.json')
                  if os.path.isfile(icd) and not (os.environ.get('VK_DRIVER_FILES') or os.environ.get('VK_ICD_FILENAMES')):
                     self.worker_env['VK_DRIVER_FILES'] = icd
                     self.worker_env['VK_ICD_FILENAMES'] = icd
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
            cmd = [sys.executable, '-u', self.worker_script, '--server', self.server_bin, '--model', self.model_path, '--dac', self.dac_path, '--spk', self.spk_path, '--emotion-dir', self.emotion_dir, '--backend', self.backend, '--samplerate', str(self.params['samplerate'])]
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
               # always cached, whatever the free VRAM: the worker must stay reachable
               # by unload_tts_manager() / cleanup_models_cache(), which stop it.
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
                      #trim_audio_buffer = 0.06
                      # only the voice path crosses the pipe: the worker registers each voice file
                      # once with zonos2-server and keeps its embedding id.
                      # a part ending on a word (cut at max_chars or before an SML tag) is sent closed with a comma:
                      # without punctuation zonos2 stops right on the word, with no trailing silence, and its last
                      # syllable can be lost. Only the text sent to the model changes; the comma's pause is trimmed
                      # back below (trim_audio) since part itself still ends on a word
                      reply = self.engine.send({
                         'op': 'tts',
                         'text': f'{part},' if part[-1].isalnum() else part,
                         'language': self.language_code,
                         'voice': self.params['current_voice'],
                         'file': part_file,
                         **self.fine_tuned_params,
                         # inside [emotion:...]...[/emotion] the tag wins over the panel ([emotion:neutral] = {} = plain voice)
                         **({'emotion_enabled': True, 'emotion': self.params['inline_emotion']} if self.params.get('inline_emotion') is not None else {})
                      })
                      if not reply.get('ok') and reply.get('server_exited') and self.backend == 'gpu':
                         # the GPU server died mid-sentence (a driver abort such as MoltenVK's "Completed handler
                         # provided after commit call"): restart it once, drop the package on its second death, and
                         # redo the whole sentence with a fresh engine (__init__ picks the package, CPU last)
                         crashes = Zonos.gpu_crashes[self.package_name] = Zonos.gpu_crashes.get(self.package_name, 0) + 1
                         # the worker's error carries the server's last log lines joined by ' | ': the last one is
                         # the cause (e.g. the Metal assertion), the rest is startup noise
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
                      if not is_audio_data_valid(audio_part):
                         error = 'audio_part not valid'
                         return False, error
                      self.params['samplerate'] = int(samplerate)
                      part_tensor = self._tensor_type(audio_part).reshape(1, -1)
                      if part_tensor.numel() == 0:
                         error = 'part_tensor not valid'
                         return False, error
                      #if part[-1].isalnum() or part[-1] == '—':
                      #   part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
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