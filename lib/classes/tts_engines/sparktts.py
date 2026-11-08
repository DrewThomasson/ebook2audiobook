import json
from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.conf import systems, torch_matrix, transformers_caps, default_pytorch_url, default_pytorch_nightly_url
from lib.lang import legends

class SparkTTS(TTSUtils, TTSRegistry, name='sparktts'):

    def __init__(self, session:DictProxy):
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
            engine_langs = settings.get('languages', {})
            if self.language not in engine_langs:
                error = legends['error_language_not_supported_engine'].format(lang=self.language, engine=tts_engine)
                raise ValueError(error)
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = legends['error_invalid_fine_tuned'].format(model=fine_tuned, models=list(self.models.keys()))
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate', 'voice'):
                if required_key not in model_cfg:
                    error = legends['error_fine_tuned_missing_key'].format(model=fine_tuned, key=required_key)
                    raise ValueError(error)
            self.params['samplerate'] = model_cfg['samplerate']
            self.model_repo = model_cfg['repo']
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            self.worker_device = self.device
            self.fine_tuned_params = self._sanitize_sampling_params({
                key.removeprefix('sparktts_'): cast_type(self.session[key]) if self.session.get(key) is not None else cast_type(settings[key.removeprefix('sparktts_')])
                for key, cast_type in {
                    'sparktts_temperature': float,
                    'sparktts_top_k': int,
                    'sparktts_top_p': float,
                    'sparktts_tokens_per_char': int,
                    'sparktts_max_new_tokens': int
                }.items()
            })
            # --- own uv venv: lib/classes/tts_engines/venvs/sparktts ---
            # every package follows upstream's requirements.txt, torch included: e2a's device detection
            # only tells which PyTorch index (or fallback) serves this machine
            progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            self.venv_dir = os.path.join(engine_dir, 'venvs', tts_engine)
            self.venv_python = os.path.join(self.venv_dir, 'Scripts', 'python.exe') if sys.platform == systems['WINDOWS'] else os.path.join(self.venv_dir, 'bin', 'python')
            self.worker_script = os.path.join(engine_dir, 'workers', f'{tts_engine}_worker.py')
            # upstream is not a package: the worker imports sparktts from its extracted repo root
            self.src_dir = os.path.join(self.venv_dir, 'src', 'Spark-TTS')
            # model and whisper as plain folders under models/tts (see the worker for why); whisper sits at
            # models/tts itself, one copy for every engine using it
            self.model_dir = os.path.join(self.cache_dir, tts_engine, settings['repo'].replace('/', '--'))
            self.asr_dir = os.path.join(self.cache_dir, settings['asr_model'].replace('/', '--'))
            self.worker_env = {k: v for k, v in os.environ.items() if k not in ('PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV', 'CONDA_PREFIX', 'CONDA_DEFAULT_ENV', 'CONDA_PYTHON_EXE', 'CONDA_SHLVL', '__PYVENV_LAUNCHER__')}
            self.worker_env['VIRTUAL_ENV'] = self.venv_dir
            self.worker_env['PATH'] = os.pathsep.join([os.path.dirname(self.venv_python), self.worker_env.get('PATH', '')])
            self.worker_env['PYTHONUNBUFFERED'] = '1'
            # a python uv has to download for the venv is kept with the venvs, so a docker volume
            # on lib/classes/tts_engines/venvs (or deleting that folder) covers everything
            self.worker_env['UV_PYTHON_INSTALL_DIR'] = os.path.join(engine_dir, 'venvs', '.python')
            if self.worker_device != devices['CUDA']['proc']:
                # keep the worker off the GPU entirely
                self.worker_env['CUDA_VISIBLE_DEVICES'] = '-1'
                self.worker_env['HIP_VISIBLE_DEVICES'] = '-1'
            # device family and python come from e2a's own detection (.device_info.json, written by
            # DeviceInstaller): torch is never imported here
            from lib.classes.device_installer import DeviceInstaller
            device_installer = DeviceInstaller()
            device_info = device_installer.load_device_info() or {}
            # Spark-TTS' own python (settings), unless python_env's is older: then python_env's, as the
            # fallback's wheels are built for it
            venv_python = settings['python']
            if device_info.get('pyvenv') and tuple(device_info['pyvenv'][:2]) < tuple(int(x) for x in settings['python'].split('.')[:2]):
                venv_python = '.'.join(str(v) for v in device_info['pyvenv'][:2])
            # --torch-backend gets the tag e2a picked for this machine (cu126 keeps Pascal kernels,
            # mps uses the PyPI build). 'auto' only reads the driver version: a Pascal card on a
            # recent driver would get cu128+/cu130 wheels without sm_61 kernels.
            torch_backend = {devices['MPS']['proc']: devices['CPU']['proc']}.get(device_info.get('tag'), device_info.get('tag')) or 'auto'
            # newest torch e2a ships for this device tag (torch_matrix 'last'); a matrix bump reinstalls
            matrix_entry = torch_matrix.get(device_info.get('tag')) or {}
            marker_file = os.path.join(self.venv_dir, '.e2a_installed.json')
            installed = {}
            if os.path.exists(marker_file):
                try:
                    with open(marker_file, 'r', encoding='utf-8') as f:
                        installed = json.load(f)
                except Exception:
                    installed = {}
            # e2a's own package lists are part of the marker: changing them gives existing venvs one install pass
            expected = {'source': settings['source'], 'device': torch_backend, 'torch': matrix_entry.get('last'), 'requirements': settings['requirements_exclude'] + settings['requirements_extra']}
            if not os.path.exists(self.venv_python) or not os.path.isdir(self.src_dir) or any(installed.get(k) != v for k, v in expected.items()):
                uv_bin = device_installer.uv_bin
                uv_pip = [uv_bin, 'pip', 'install', '--python', self.venv_python]
                # the pinned source first, without the venv: its requirements.txt carries upstream's torch
                # spec, so a device that cannot run sparktts stops before any venv is created
                # (python_env's interpreter, stdlib only)
                extract_script = '\n'.join([
                    'import os, sys, shutil, tarfile, urllib.request',
                    'url, dst = sys.argv[1], sys.argv[2]',
                    'shutil.rmtree(dst, ignore_errors=True)',
                    'os.makedirs(dst)',
                    'archive = os.path.join(dst, "source.tar.gz")',
                    'urllib.request.urlretrieve(url, archive)',
                    'with tarfile.open(archive, "r:gz") as tar:',
                    '    root = tar.getmembers()[0].name.split("/")[0]',
                    '    tar.extractall(dst, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))',
                    'os.unlink(archive)',
                    'os.rename(os.path.join(dst, root), os.path.join(dst, "Spark-TTS"))'
                ])
                msg = legends['msg_venv_fetching_source'].format(engine=tts_engine)
                print(msg)
                if progress_bar is not None:
                    progress_bar(0.0, desc=msg)
                cmd = [sys.executable, '-c', extract_script, settings['source'], os.path.dirname(self.src_dir)]
                if not SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, env=self.worker_env).result:
                    error = legends['error_venv_install_failed'].format(engine=tts_engine, step=' '.join(cmd))
                    raise RuntimeError(error)
                # the package list is upstream's own requirements.txt from the extracted tree, minus
                # settings['requirements_exclude'], plus settings['requirements_extra']; names only when
                # settings['requirements_unpinned'] (upstream pins every package to one dated release)
                requirements = []
                with open(os.path.join(self.src_dir, settings['requirements_file']), 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        name = re.match(r'[A-Za-z0-9][A-Za-z0-9._-]*', line)
                        # option and comment lines never match a name: dropped too
                        if name and re.sub(r'[-_.]+', '-', name.group(0)).lower() not in settings['requirements_exclude']:
                            requirements.append(name.group(0) if settings['requirements_unpinned'] else line)
                requirements_file = os.path.join(self.venv_dir, 'requirements.e2a.txt')
                os.makedirs(self.venv_dir, exist_ok=True)
                with open(requirements_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(requirements + settings['requirements_extra']) + '\n')
                # torch: torch_matrix 'last' for this device tag, unless upstream locks torch or caps it
                # below that version: then upstream's own spec. Upstream's floor stops older devices.
                from packaging.requirements import Requirement
                from packaging.specifiers import SpecifierSet
                from packaging.version import Version
                torch_line = f"torch=={matrix_entry['last']}" if matrix_entry.get('last') else 'torch'
                torch_spec = SpecifierSet()
                for line in requirements:
                    try:
                        requirement = Requirement(line)
                    except Exception:
                        continue
                    if re.sub(r'[-_.]+', '-', requirement.name).lower() == 'torch' and requirement.specifier:
                        torch_spec &= requirement.specifier
                        locked = any(spec.operator in ('==', '===') for spec in requirement.specifier)
                        if locked or not matrix_entry.get('last') or not requirement.specifier.contains(Version(matrix_entry['last']), prereleases=True):
                            torch_line = line
                torch_floor = next((spec.version for spec in torch_spec if spec.operator in ('>=', '>', '~=')), str(torch_spec))
                # e2a's newest torch for this device is below upstream's floor: stop here with the clear
                # alert, before any venv exists
                if matrix_entry.get('last') and any(spec.operator in ('>=', '>', '~=') and not SpecifierSet(str(spec)).contains(Version(matrix_entry['last']), prereleases=True) for spec in torch_spec):
                    error = legends['error_venv_torch_unsupported'].format(engine=tts_engine, min=torch_floor, version=matrix_entry['last'])
                    # this device cannot run sparktts: leave nothing behind
                    import shutil
                    shutil.rmtree(self.venv_dir, ignore_errors=True)
                    raise ValueError(error)
                if not os.path.exists(self.venv_python):
                    msg = legends['msg_venv_creating'].format(engine=tts_engine, dir=self.venv_dir)
                    print(msg)
                    if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                    # --allow-existing: keeps the source fetched above, and repairs a venv whose interpreter
                    # link died (docker image rebuilt) without wiping the folder
                    cmd = [uv_bin, 'venv', '--allow-existing', '--python', venv_python, self.venv_dir]
                    if not SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, env=self.worker_env).result:
                        error = legends['error_venv_install_failed'].format(engine=tts_engine, step=' '.join(cmd))
                        raise RuntimeError(error)
                # transformers releases need a recent enough torch: e2a's transformers_caps ({torch floor:
                # transformers cap}) applied to the torch the venv gets, like DeviceInstaller does for python_env
                transformers_cap = []
                planned_torch = re.fullmatch(r'torch==([0-9][0-9A-Za-z.+]*)', torch_line)
                if planned_torch:
                    for torch_below, cap in sorted(transformers_caps.items(), key=lambda item: Version(item[0])):
                        if Version(planned_torch.group(1)) < Version(torch_below):
                            transformers_cap = [f'transformers<{cap}']
                            break
                # wheels only, so no platform ever needs a compiler: the resolver takes the newest release
                # that has a wheel there; the few pure-python sdist-only packages are let through
                wheels_only = ['--only-binary', ':all:'] + [arg for pkg in settings['packages_sdist'] for arg in ('--no-binary', pkg)]
                # 1. upstream's requirements and torch from the device's PyTorch index, in one resolution.
                # Only for tags uv has a backend for: jetson / windows rocm go straight to the fallback.
                backend_ok = False
                if re.fullmatch(r'auto|cpu|xpu|cu\d+|rocm[\d.]+', torch_backend):
                    msg = legends['msg_venv_installing'].format(engine=tts_engine, pkgs=f'{tts_engine} requirements ({torch_line}, {torch_backend})')
                    print(msg)
                    if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                    backend_ok = SubprocessPipe(uv_pip + ['--torch-backend', torch_backend] + wheels_only + ['-r', requirements_file, torch_line] + transformers_cap, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, env=self.worker_env).result
                if not backend_ok:
                    # 2. no uv backend for this tag, or no build there: e2a's DeviceInstaller installs its
                    # device-proven torch into the venv. It runs on the venv's interpreter, so python_exec
                    # and its installed-version checks are the venv's (PY_CMD forced: e2a's own environment
                    # may point it at python_env), then the requirements resolve around that torch.
                    device_script = '\n'.join([
                        'import sys, json',
                        'from lib.conf import NATIVE',
                        'from lib.classes.device_installer import DeviceInstaller',
                        'installer = DeviceInstaller()',
                        'info = installer.load_device_info()',
                        'sys.exit(installer.install_device_packages(json.dumps(info) if info else installer.check_device_info(NATIVE)))'
                    ])
                    fallback_env = dict(self.worker_env, PY_CMD=self.venv_python)
                    # the fallback installs e2a's device-proven torch, the one python_env runs here (read
                    # from its metadata, torch is not imported): below upstream's floor, stop now
                    from importlib.metadata import version as package_version, PackageNotFoundError
                    try:
                        env_torch = package_version('torch')
                    except PackageNotFoundError:
                        env_torch = None
                    if env_torch and torch_spec and not torch_spec.contains(Version(env_torch), prereleases=True):
                        error = legends['error_venv_torch_unsupported'].format(engine=tts_engine, min=torch_floor, version=env_torch)
                        # this device cannot run sparktts: leave no unusable venv behind
                        import shutil
                        shutil.rmtree(self.venv_dir, ignore_errors=True)
                        raise ValueError(error)
                    msg = legends['msg_venv_installing'].format(engine=tts_engine, pkgs='torch (DeviceInstaller)')
                    print(msg)
                    if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                    cmd = [self.venv_python, '-c', device_script]
                    if not SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, env=fallback_env).result:
                        error = legends['error_venv_install_failed'].format(engine=tts_engine, step=' '.join(cmd))
                        raise RuntimeError(error)
                    # hold torch / torchaudio to exactly what DeviceInstaller installed, or the resolver
                    # swaps them for the newest PyPI torch as soon as a package wants a newer one. URL
                    # wheels (jetson, windows rocm) are held by their direct_url.json URL, index wheels by
                    # version, with their PyTorch index when the version carries a local tag.
                    pins_script = '\n'.join([
                        'import json, importlib.metadata as metadata',
                        'pins = []',
                        'versions = {}',
                        'for name in ("torch", "torchaudio"):',
                        '    try:',
                        '        dist = metadata.distribution(name)',
                        '    except metadata.PackageNotFoundError:',
                        '        continue',
                        '    versions[name] = dist.version',
                        '    direct = json.loads(dist.read_text("direct_url.json") or "null")',
                        '    pins.append(name + " @ " + direct["url"] if direct and direct.get("url") else name + "==" + dist.version)',
                        'print(json.dumps({"pins": pins, "versions": versions}))'
                    ])
                    probe = subprocess.run([self.venv_python, '-c', pins_script], env=fallback_env, capture_output=True, text=True, timeout=120)
                    pins_info = json.loads(probe.stdout.strip() or '{}') if probe.returncode == 0 else {}
                    torch_pins = pins_info.get('pins', [])
                    fallback_torch = pins_info.get('versions', {}).get('torch')
                    if fallback_torch and torch_spec and not torch_spec.contains(Version(fallback_torch), prereleases=True):
                        error = legends['error_venv_torch_unsupported'].format(engine=tts_engine, min=torch_floor, version=fallback_torch)
                        # this device cannot run sparktts: leave no unusable venv behind
                        import shutil
                        shutil.rmtree(self.venv_dir, ignore_errors=True)
                        raise ValueError(error)
                    # transformers cap for the torch DeviceInstaller installed (jetson: 2.4 / 2.5)
                    transformers_cap = []
                    if fallback_torch:
                        for torch_below, cap in sorted(transformers_caps.items(), key=lambda item: Version(item[0])):
                            if Version(fallback_torch) < Version(torch_below):
                                transformers_cap = [f'transformers<{cap}']
                                break
                    index_args = []
                    for pin in torch_pins:
                        if '==' in pin and '+' in pin:
                            local_tag = pin.split('+', 1)[1]
                            index_args += ['--extra-index-url', f"{default_pytorch_nightly_url if '.dev' in pin else default_pytorch_url}/{local_tag}"]
                    if index_args:
                        index_args += ['--index-strategy', 'unsafe-best-match']
                    msg = legends['msg_venv_installing'].format(engine=tts_engine, pkgs=f'{tts_engine} requirements')
                    print(msg)
                    if progress_bar is not None:
                        progress_bar(0.0, desc=msg)
                    cmd = uv_pip + wheels_only + index_args + ['-r', requirements_file] + torch_pins + transformers_cap
                    if not SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=0, msg=msg, env=fallback_env).result:
                        error = legends['error_venv_install_failed'].format(engine=tts_engine, step=' '.join(cmd))
                        raise RuntimeError(error)
                try:
                    import shutil
                    # Ask the venv's python where its site-packages directory is
                    site_packages = subprocess.check_output(
                        [self.venv_python, '-c', 'import sysconfig; print(sysconfig.get_paths()["purelib"])'],
                        text=True
                    ).strip()
                    # Locate the source sitecustomize.py (3 levels up from lib/classes/tts_engines)
                    sitecustomize_src = os.path.abspath(os.path.join(engine_dir, '..', '..', '..', 'components', 'sitecustomize.py'))
                    sitecustomize_dst = os.path.join(site_packages, 'sitecustomize.py')
                    if os.path.exists(sitecustomize_src):
                        shutil.copy2(sitecustomize_src, sitecustomize_dst)
                        print(f"Copied sitecustomize.py to {sitecustomize_dst}")
                    else:
                        print(f"Warning: sitecustomize.py not found at {sitecustomize_src}")
                except Exception as e:
                    print(f"Warning: Failed to copy sitecustomize.py: {e}")
                # jetson: before the probe, which imports what the worker does
                device_installer.link_os_libgomp(self.venv_dir, device_info)
                # same import path as the worker: from the tree root, BiCodec, transformers' Qwen2 and Whisper
                probe_script = '\n'.join([
                    'import sys',
                    'sys.path.insert(0, ".")',
                    # same torch.distributed stubs as the worker, for torch built without distributed (jetson, macOS vulkan)
                    'import types, torch, torch.distributed',
                    'if not torch.distributed.is_available():',
                    '    for attr, value in (("ReduceOp", types.SimpleNamespace(SUM="sum", AVG="avg", PRODUCT="product", MIN="min", MAX="max")), ("is_initialized", lambda: False), ("get_rank", lambda: 0), ("get_world_size", lambda: 1)):',
                    '        if not hasattr(torch.distributed, attr):',
                    '            setattr(torch.distributed, attr, value)',
                    'import soundfile',
                    'from sparktts.models.audio_tokenizer import BiCodecTokenizer',
                    'from sparktts.utils.token_parser import TASK_TOKEN_MAP',
                    'from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline'
                ])
                probe = subprocess.run([self.venv_python, '-c', probe_script], cwd=self.src_dir, env=self.worker_env, capture_output=True, text=True, timeout=600)
                if probe.returncode != 0:
                    error = legends['error_venv_install_failed'].format(engine=tts_engine, step=f'import sparktts: {probe.stderr.strip()[-500:]}')
                    raise RuntimeError(error)
                installed = dict(expected)
                with open(marker_file, 'w', encoding='utf-8') as f:
                    json.dump(installed, f, indent=2)
            # jetson: the venv's bundled libgomp copies link to the OS one (DeviceInstaller.link_os_libgomp), checked at
            # every start so a venv installed before is fixed too
            device_installer.link_os_libgomp(self.venv_dir, device_info)
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            msg = legends['msg_loading_tts_model'].format(model=self.tts_key)
            print(msg)
            self.cleanup_memory()
            settings = default_engine_settings[self.session['tts_engine']]
            cmd = [
                self.venv_python, '-u', self.worker_script,
                '--src', self.src_dir,
                '--repo', self.model_repo,
                '--model_dir', self.model_dir,
                '--device', self.worker_device,
                '--asr_model', settings['asr_model'],
                '--asr_dir', self.asr_dir,
                '--cache_dir', os.path.join(self.venv_dir, 'refs'),
                '--ref_max', str(settings['ref_max']),
                # the reference transcript is only part of the prompt when Whisper hears one of these
                '--ref_languages', ','.join(dict.fromkeys(settings['languages'].values()))
            ]
            engine = loaded_tts.get(self.tts_key)
            if isinstance(engine, SubprocessPipe) and (engine.cmd != cmd or engine.process is None or engine.process.poll() is not None):
                # dead worker, or one serving another model/device under this key
                loaded_tts.pop(self.tts_key, None)
                engine.stop()
                engine = None
            if not engine:
                msg = legends['msg_worker_starting'].format(engine=self.session['tts_engine'], model=self.model_repo, device=self.worker_device)
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
                        # only the voice path crosses the pipe: the worker cuts the reference, transcribes and
                        # tokenizes it once per voice file, and keeps it
                        reply = self.engine.send({
                            'op': 'tts',
                            'text': part,
                            'voice': self.params['current_voice'],
                            'file': part_file,
                            **self.fine_tuned_params
                        })
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
