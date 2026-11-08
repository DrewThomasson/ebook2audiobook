import os, sys, re, json, shutil, platform, tarfile, zipfile, urllib.request
from multiprocessing.managers import DictProxy
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.conf import systems, devices, tts_dir
from lib.conf_models import TTS_VOICE_CONVERSION, default_vc_model, default_engine_settings, audiocpp_packages, audiocpp_asr, audiocpp_repo
from lib.lang import legends

class VoiceConversion(SubprocessPipe):
    # The voice conversion of the built-in voice engines (piper, vits, fairseq, glowtts, tacotron, orpheus): a voice file
    # picked for them turns their output into that voice with default_vc_model (TTS_VOICE_CONVERSION) on audio.cpp's
    # native server, driven by workers/audiocpp_worker.py. A SubprocessPipe itself, cached in loaded_tts under the engine's
    # tts_zs_key, so unload_tts_manager() / cleanup_models_cache() stop it like any worker.
    # The engines send {"op": "vc", "source", "voice", "file", "text", "language"} whatever the model (send() below):
    # task "vc" converts source (worker --vc-only), task "tts" speaks text in the voice (the worker's clone op), and then
    # resynthesis is True: the engine does not run its own voice for it.
    # Also the one place for the audiocpp_server packages (packages(), install()), shared with the audio.cpp TTS engines
    # (AudioCpp).
    # GPU packages whose server died during a conversion, per e2a process: package -> crash count (shared by the audio.cpp
    # engines and the voice conversion, they run the same packages). One crash restarts the same package, a second one
    # drops it until e2a restarts (next GPU package, else CPU)
    gpu_crashes = {}

    def __init__(self, session:DictProxy)->None:
        try:
            from huggingface_hub import hf_hub_download
            from lib.classes.tts_engines.common.preset_loader import load_engine_presets
            self.session = session
            show_alert = getattr(sys.modules.get('lib.core'), 'show_alert', None)
            progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
            # effective language (target when translating, else source), as the engines
            self.language = session['translate'] if session.get('translate_enabled') and session.get('translate') else session.get('language')
            self.vc_model = default_vc_model.rsplit('/', 1)[-1]
            cfg = TTS_VOICE_CONVERSION[self.vc_model]
            settings = default_engine_settings[cfg['engine']] if cfg.get('engine') else None
            if cfg['task'] == 'tts' and self.language not in settings['languages']:
                # it speaks the text: only in its engine's languages
                msg = legends['msg_vc_model_fallback'].format(vc_model=self.vc_model, lang=self.language, fallback=cfg['fallback'])
                if show_alert is not None:
                    show_alert(session['id'], {'type': 'warning', 'msg': msg})
                else:
                    print(msg)
                self.vc_model = cfg['fallback']
                cfg = TTS_VOICE_CONVERSION[self.vc_model]
                settings = default_engine_settings[cfg['engine']] if cfg.get('engine') else None
            self.resynthesis = cfg['task'] == 'tts'
            # task "tts": e2a language -> the model's code (send())
            self.languages = settings['languages'] if self.resynthesis else None
            family_cfg = settings['audiocpp'] if settings else {}
            engine_name = cfg.get('engine') or cfg['family']
            attempts, gpu_wanted = VoiceConversion.packages(session, engine_name)
            # the GGUF of the engine's internal preset (Chatterbox, Qwen3-TTS: the very file their engine uses) or the listed
            # one, real files under models/tts/audiocpp/<repo>/ for the reason given in AudioCpp.__init__
            preset = load_engine_presets(cfg['engine'])['internal'] if cfg.get('engine') else {'repo': audiocpp_repo, 'files': cfg['files']}
            asr_files = audiocpp_asr['files'] if self.resynthesis and family_cfg.get('ref_text') else []
            msg = legends['msg_zonos2_models'].format(engine=engine_name, files=', '.join(os.path.basename(f) for f in preset['files'] + asr_files))
            print(msg)
            if progress_bar is not None:
                progress_bar(0.0, desc=msg)
            self.model_path = [hf_hub_download(repo_id=preset['repo'], filename=f, cache_dir=tts_dir, local_dir=os.path.join(tts_dir, 'audiocpp', preset['repo'].replace('/', '--'))) for f in preset['files']][0]
            asr_path = [hf_hub_download(repo_id=audiocpp_repo, filename=f, cache_dir=tts_dir, local_dir=os.path.join(tts_dir, 'audiocpp', audiocpp_repo.replace('/', '--'))) for f in asr_files][0] if asr_files else ''
            worker_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workers', 'audiocpp_worker.py')
            for attempt, self.package_name in enumerate(attempts):
                package = audiocpp_packages[self.package_name]
                self.backend = package.get('backend', 'cpu') if package['gpu'] and gpu_wanted else 'cpu'
                # the worker is stdlib only. conf.py's OMP_NUM_THREADS=1 is for e2a's torch: the server (OpenMP build) sizes its own pool
                worker_env = {k: v for k, v in os.environ.items() if k not in ('PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', '__PYVENV_LAUNCHER__', 'OMP_NUM_THREADS')}
                worker_env['PYTHONUNBUFFERED'] = '1'
                try:
                    server_bin = VoiceConversion.install(self.package_name, engine_name, worker_env)
                    cmd = [sys.executable, '-u', worker_script, '--server', server_bin, '--model', self.model_path, '--family', cfg['family'], '--backend', self.backend]
                    if self.resynthesis:
                        # the engine's clone, as AudioCpp.load_engine() starts it (reference transcript by the ASR model)
                        cmd += [
                            '--load-options', json.dumps({**family_cfg['load'], **family_cfg['load_by_language'].get(self.language, {})}), '--session-options', json.dumps(family_cfg['session']), '--request-options', json.dumps(family_cfg['request']),
                            '--ref-min', str(family_cfg['ref_min']), '--ref-max', str(family_cfg['ref_max']), '--ref-text', family_cfg['ref_text'] or 'none', '--ref-fallback', json.dumps(family_cfg['ref_fallback']),
                            '--asr-model', asr_path, '--asr-family', audiocpp_asr['family'], '--samplerate', str(settings['samplerate']), '--clone'
                        ] + (['--language-option'] if family_cfg['language_option'] else []) + (['--speaker-label'] if family_cfg['speaker_label'] else [])
                    else:
                        cmd += ['--ref-max', str(cfg['ref_max']), '--vc-route', cfg.get('route', ''), '--vc-only']
                    msg = legends['msg_worker_starting'].format(engine=engine_name, model=os.path.basename(self.model_path), device=f'{self.package_name}, {self.backend}')
                    print(msg)
                    if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                    SubprocessPipe.__init__(self, cmd, is_gui_process=session['is_gui_process'], total_duration=0, msg=msg, keep_alive=True, env=worker_env)
                    if not self.result:
                        error = legends['error_worker_failed'].format(engine=engine_name, error=self.ready_info.get('error'))
                        raise RuntimeError(error)
                    break
                except Exception as e:
                    if getattr(self, 'process', None) is not None:
                        self.stop()
                    if attempt + 1 >= len(attempts):
                        raise
                    msg = legends['msg_zonos2_gpu_failed'].format(engine=engine_name, package=self.package_name, error=e)
                    if show_alert is not None:
                        show_alert(session['id'], {'type': 'warning', 'msg': msg})
                    else:
                        print(msg)
        except Exception as e:
            error = f'VoiceConversion.__init__() error: {e}'
            raise RuntimeError(error) from e

    def send(self, request:dict)->dict:
        # the engines' request -> the worker's: task "tts" speaks the text in the voice, task "vc" converts the source
        if self.resynthesis:
            request = {'op': 'tts', 'text': request['text'], 'language': self.languages.get(request.get('language') or self.language, ''), 'voice': request['voice'], 'file': request['file']}
        else:
            request = {'op': 'vc', 'source': request['source'], 'voice': request['voice'], 'file': request['file']}
        return SubprocessPipe.send(self, request)

    @staticmethod
    def packages(session:DictProxy, engine_name:str)->tuple:
        # the audiocpp_server packages to try on this machine for session['device'], best first. Returns
        # (attempts, gpu_wanted); raises when no package fits the machine
        show_alert = getattr(sys.modules.get('lib.core'), 'show_alert', None)
        machine = platform.machine().lower()
        gpu_wanted = session['device'] != devices['CPU']['proc']
        # CUDA packages for NVIDIA devices only: ROCm and XPU go to Vulkan, MPS to Metal
        cuda_wanted = session['device'] in [devices['CUDA']['proc'], devices['JETSON']['proc']]
        packages = audiocpp_packages
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
            # own builds first (older glibc, bundled CUDA runtime), audio.cpp's official ones (glibc 2.38+) after
            candidates = (['linux-x64-cuda13', 'linux-x64-cuda12'] if cuda_wanted else []) + (['linux-x64-vulkan', 'linux-x64-vulkan-acpp'] if gpu_wanted else []) + ['linux-x64-cpu-avx2', 'linux-x64-cpu-sse42', 'linux-x64-cpu-acpp']
        elif sys.platform == systems['LINUX'] and machine in ('aarch64', 'arm64'):
            if jetpack is not None:
                candidates = [k for k, v in packages.items() if v.get('jetpack') == jetpack and board_sm in v.get('sm', [])]
            else:
                candidates = ['linux-aarch64-cuda13', 'linux-aarch64-cuda12'] if cuda_wanted else []
            # Vulkan after CUDA: the GPU path of a Jetson without a CUDA package (Xavier, JetPack 5), the fallback of one with
            candidates = ((candidates + ['linux-aarch64-vulkan']) if gpu_wanted else []) + ['linux-aarch64-v82', 'linux-aarch64']
        elif sys.platform == systems['WINDOWS'] and machine in ('amd64', 'x86_64'):
            candidates = (['windows-x64-cuda13-acpp', 'windows-x64-cuda12-acpp'] if cuda_wanted else []) + (['windows-x64-vulkan-acpp'] if gpu_wanted else []) + ['windows-x64-cpu-acpp']
        elif sys.platform == systems['MACOS']:
            # own builds start on macOS 11, the official ones on 13.3. arm64: Metal (the same archive runs --backend
            # cpu). x86_64: Vulkan through MoltenVK (own build only), else CPU
            candidates = ((['macos-arm64', 'macos-arm64-acpp'] if gpu_wanted else []) + ['macos-arm64-cpu', 'macos-arm64-cpu-acpp']) if machine == 'arm64' else ((['macos-x86_64-vulkan'] if gpu_wanted else []) + ['macos-x86_64', 'macos-x86_64-acpp'])
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
            cpu_flags = ({'sse4_2'} if present(38) else set()) | ({'avx2', 'fma', 'f16c', 'bmi2'} if present(40) else set())
        glibc = platform.libc_ver()
        glibc_version = tuple(int(x) for x in re.findall(r'\d+', glibc[1])[:2]) if glibc[0] == 'glibc' and glibc[1] else (0, 0)
        mac_version = tuple(int(x) for x in (platform.mac_ver()[0] or '0').split('.')[:2]) if sys.platform == systems['MACOS'] else (0, 0)
        machine_desc = f'{sys.platform} {machine}' + (f' JetPack {jetpack}' if jetpack else '') + (f' sm_{board_sm}' if board_sm else '')
        usable = [
            k for k in dict.fromkeys(candidates)
            if k in packages and packages[k].get('enabled', True) and set(packages[k].get('cpu_flags', [])) <= cpu_flags
            and VoiceConversion.gpu_crashes.get(k, 0) < 2
            and glibc_version >= tuple(int(x) for x in packages[k].get('glibc_min', '0.0').split('.'))
            and mac_version >= tuple(int(x) for x in packages[k].get('macos_min', '0.0').split('.'))
        ]
        if not usable:
            if sys.platform == systems['MACOS'] and any(k in packages and packages[k].get('enabled', True) for k in candidates):
                error = legends['error_zonos2_macos_min'].format(engine=engine_name, min=min(packages[k].get('macos_min', '0') for k in candidates if k in packages and packages[k].get('enabled', True)), version=platform.mac_ver()[0])
            else:
                error = legends['error_zonos2_no_package'].format(engine=engine_name, machine=machine_desc)
            raise ValueError(error)
        # first choice, then the other GPU packages, then one CPU package to fall back on if a GPU one cannot start
        attempts = [usable[0]]
        if packages[usable[0]]['gpu']:
            attempts = [k for k in usable if packages[k]['gpu']] + [k for k in usable if not packages[k]['gpu']][:1]
        if gpu_wanted and not packages[usable[0]]['gpu'] and not any(n >= 2 for n in VoiceConversion.gpu_crashes.values()):
            msg = legends['msg_zonos2_cpu_fallback'].format(engine=engine_name, machine=machine_desc)
            if show_alert is not None:
                show_alert(session['id'], {'type': 'warning', 'msg': msg})
            else:
                print(msg)
        return attempts, gpu_wanted

    @staticmethod
    def install(package_name:str, engine_name:str, worker_env:dict)->str:
        # the package under lib/classes/tts_engines/venvs/audiocpp/<package>, downloaded on first use (or unpacked from
        # the offline copy in models/tts/audiocpp/packages/<package>/). Returns the
        # audiocpp_server path; worker_env gets the Vulkan driver list of the own macOS Vulkan package
        progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
        engines_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        package = audiocpp_packages[package_name]
        package_dir = os.path.join(engines_dir, 'venvs', 'audiocpp', package_name)
        marker_file = os.path.join(package_dir, '.e2a_installed.json')
        # downloaded once: a package folder with its install record is used as it is from then on; a record
        # naming other urls (version bump, package moved to another build) is downloaded again
        try:
            with open(marker_file, 'r', encoding='utf-8') as f:
                installed_urls = json.load(f).get('urls')
        except Exception:
            installed_urls = None
        if installed_urls != package['urls']:
            # an archive tools/preload_models.py put in models/tts/audiocpp/packages/<package>/ (offline installs) is taken
            # from there, no network
            offline_dir = os.path.join(tts_dir, 'audiocpp', 'packages', package_name)
            offline = all(os.path.isfile(os.path.join(offline_dir, os.path.basename(url))) for url in package['urls'])
            msg = legends['msg_audiocpp_offline_package' if offline else 'msg_zonos2_downloading'].format(engine=engine_name, package=package_name)
            print(msg)
            if progress_bar is not None:
                progress_bar(0.0, desc=msg)
            shutil.rmtree(package_dir, ignore_errors=True)
            os.makedirs(package_dir, exist_ok=True)
            try:
                # Windows CUDA: the bin archive and its cudart archive unpack into the same folder
                for url in package['urls']:
                    archive = os.path.join(package_dir, os.path.basename(url))
                    if offline:
                        shutil.copyfile(os.path.join(offline_dir, os.path.basename(url)), archive)
                    else:
                        # urllib: no quarantine flag on macOS, so the unsigned binaries start without a Gatekeeper prompt
                        with urllib.request.urlopen(url, timeout=60) as r, open(archive, 'wb') as f:
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
                error = legends['error_zonos2_download'].format(engine=engine_name, package=package_name, error=e)
                raise RuntimeError(error)
            with open(marker_file, 'w', encoding='utf-8') as f:
                json.dump({'urls': package['urls']}, f, indent=2)
        server_name = 'audiocpp_server.exe' if sys.platform == systems['WINDOWS'] else 'audiocpp_server'
        server_bin = next((os.path.join(root, server_name) for root, _, files in os.walk(package_dir) if server_name in files), None)
        if server_bin is None:
            shutil.rmtree(package_dir, ignore_errors=True)
            error = legends['error_zonos2_download'].format(engine=engine_name, package=package_name, error=f'{server_name} not found in the package')
            raise RuntimeError(error)
        if sys.platform != systems['WINDOWS']:
            os.chmod(server_bin, os.stat(server_bin).st_mode | 0o755)
        # own macOS Vulkan package: it carries its loader and MoltenVK in lib/, unless the user set a driver list
        icd = os.path.join(os.path.dirname(server_bin), 'lib', 'MoltenVK_icd.json')
        if os.path.isfile(icd) and not (os.environ.get('VK_DRIVER_FILES') or os.environ.get('VK_ICD_FILENAMES')):
            worker_env['VK_DRIVER_FILES'] = icd
            worker_env['VK_ICD_FILENAMES'] = icd
        return server_bin
