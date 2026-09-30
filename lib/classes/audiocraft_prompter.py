import os
import subprocess
import shutil
import logging
import json
import platform

from typing import Optional
from pathlib import Path
from transformers import pipeline
from lib.conf import components_dir

class AudiocraftPrompter:

    def __init__(self, device_info_str:str='')->None:
        self.uv_project_path = os.path.join(components_dir, 'audiocraft')
        self.device_info_str = device_info_str or ''
        venv_dir = Path(self.uv_project_path) / 'python_env'
        # subprocess env built from scratch instead of inherited: only OS/network essentials pass, nothing from the e2a process (HF_HOME, XDG_*, TMPDIR, OMP_NUM_THREADS, PYTHON*...)
        keep_vars = ('PATH', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TERM', 'SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'COMSPEC', 'PATHEXT', 'USERPROFILE', 'USERNAME', 'HOMEDRIVE', 'HOMEPATH', 'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'PROGRAMFILES', 'TEMP', 'TMP', 'NUMBER_OF_PROCESSORS', 'PROCESSOR_ARCHITECTURE', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE')
        self.env_vars = {key: value for key, value in os.environ.items() if key.upper() in keep_vars}
        self.env_vars['VIRTUAL_ENV'] = str(venv_dir)
        self.env_vars['PATH'] = str(venv_dir / ('Scripts' if os.name == 'nt' else 'bin')) + os.pathsep + self.env_vars.get('PATH', '')
        self._ensure_audiocraft_env()
        self.classifier = None
        self.prompt_map = {
            'action and suspense': 'fast tempo, cinematic percussion, tense strings, dramatic trailer music',
            'melancholic and emotional': 'slow piano, melancholic cello, ambient reverb, emotional cinematic score',
            'peaceful and ambient': 'lo-fi beats, soft acoustic guitar, relaxing nature sounds, calm background music',
            'epic and orchestral': 'massive brass, epic choir, soaring strings, hans zimmer style, 120 bpm',
            'sci-fi and electronic': 'synthwave, pulsing bass, atmospheric synth pads, futuristic, blade runner vibe'
        }
        self.candidate_labels = list(self.prompt_map.keys())

    def _get_venv_python(self)->str:
        if os.name == 'nt':
            return str(Path(self.uv_project_path) / 'python_env' / 'Scripts' / 'python.exe')
        return str(Path(self.uv_project_path) / 'python_env' / 'bin' / 'python')

    def _ensure_audiocraft_env(self)->None:
        project_dir = Path(self.uv_project_path)
        venv_dir = project_dir / 'python_env'
        marker_file = project_dir / '.audiocraft_installed'
        try:
            device_info = json.loads(self.device_info_str) if self.device_info_str else {}
        except json.JSONDecodeError:
            device_info = {}
        name = str(device_info.get('name') or 'cpu').lower()
        tag = str(device_info.get('tag') or 'cpu').lower()
        pyvenv = device_info.get('pyvenv') or [3, 11]
        py_version = f'{pyvenv[0]}.{pyvenv[1]}'
        is_macos = platform.system() == 'Darwin'
        is_intel_mac = is_macos and platform.machine() == 'x86_64'
        # the venv is rebuilt whenever the recipe or the hardware it was built for changes
        env_version = f'3|{name}|{tag}|{py_version}'
        if venv_dir.exists() and (not marker_file.exists() or marker_file.read_text().strip() != env_version):
            print('Detected incomplete or outdated Audiocraft installation. Cleaning up python_env...')
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f'Warning: Could not fully clean up old env: {e}')
        if not venv_dir.exists():
            msg = f'Setting up Audiocraft uv environment (Python {py_version}, {name}/{tag})...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            marker_file.unlink(missing_ok=True)
            (project_dir / 'override.txt').unlink(missing_ok=True)
            try:
                env_vars = self.env_vars
                subprocess.run(['uv', 'venv', 'python_env', '--python', py_version], cwd=project_dir, check=True, env=env_vars)
                def _install(pkgs:list[str], index_url:str|None=None)->None:
                    cmd = ['uv', 'pip', 'install']
                    if index_url:
                        cmd.extend(['--index-url', index_url])
                    cmd.extend(pkgs)
                    subprocess.run(cmd, cwd=project_dir, check=True, env=env_vars)
                # torch build picked from e2a's hardware detection: PyPI on macOS (Intel stops at 2.2.2), the matching PyTorch index
                # for CUDA/ROCm/XPU/CPU, and the CPU build where e2a relies on custom wheels (Jetson, Windows ROCm)
                torch_index = 'https://download.pytorch.org/whl/cpu'
                torch_pkgs = ['torch']
                if is_intel_mac:
                    torch_index = None
                    torch_pkgs = ['torch==2.2.2', 'numpy<2']
                elif is_macos:
                    torch_index = None
                elif name == 'cuda' and tag.replace('win-', '').startswith('cu'):
                    torch_index = f"https://download.pytorch.org/whl/{tag.replace('win-', '')}"
                elif name == 'rocm' and tag.startswith('rocm'):
                    torch_index = f'https://download.pytorch.org/whl/{tag}'
                elif name == 'xpu':
                    torch_index = 'https://download.pytorch.org/whl/xpu'
                elif name != 'cpu':
                    print(f'No standard PyTorch index for {name}/{tag}: interludes will be generated on CPU.')
                print('Step 1/3: Installing torch...')
                _install(torch_pkgs, torch_index)
                torch_version = subprocess.run([self._get_venv_python(), '-I', '-c', 'import torch;print(torch.__version__)'], capture_output=True, text=True, check=True, env=env_vars).stdout.strip()
                torch_base = tuple(int(v) for v in torch_version.split('+')[0].split('.')[:2])
                # transformers silently disables torch below its minimum (install still succeeds), so it is capped by the installed torch
                transformers_pkg = 'transformers<5.1' if torch_base < (2, 5) else 'transformers<5.8' if torch_base < (2, 6) else 'transformers'
                print(f'Step 2/3: Installing {transformers_pkg} for torch {torch_version}...')
                _install([transformers_pkg, 'soundfile', 'scipy', 'sentencepiece', 'protobuf'] + (['numpy<2'] if torch_base < (2, 3) else []))
                print('Step 3/3: Checking the environment...')
                subprocess.run([self._get_venv_python(), '-I', '-c', 'import sys, scipy, soundfile, transformers.utils as u; sys.exit(0 if u.is_torch_available() else 1)'], check=True, env=env_vars)
                marker_file.write_text(env_version)
                print('Audiocraft environment setup complete.')
            except subprocess.CalledProcessError as e:
                error_msg = f'Failed to setup Audiocraft env: {e}'
                print(error_msg)
                if venv_dir.exists():
                    shutil.rmtree(venv_dir, ignore_errors=True)
                raise RuntimeError(error_msg)
            except FileNotFoundError:
                error_msg = 'uv command not found. Please install uv.'
                print(error_msg)
                raise RuntimeError(error_msg)

    def load_model(self)->None:
        if self.classifier is None:
            import torch
            # the checkpoint carries a legacy position_ids buffer that transformers 5 reports as UNEXPECTED, harmless: mute that report for this load only
            report_logger = logging.getLogger('transformers.utils.loading_report')
            report_level = report_logger.level
            report_logger.setLevel(logging.ERROR)
            try:
                self.classifier = pipeline(
                    'zero-shot-classification',
                    model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
                    device=-1,
                    dtype=torch.float32,
                    trust_remote_code=True
                )
            finally:
                report_logger.setLevel(report_level)

    def generate_prompt(self, text:str)->str:
        self.load_model()
        truncated_text = text[:1000]
        result = self.classifier(truncated_text, self.candidate_labels)
        best_vibe = result['labels'][0]
        return self.prompt_map.get(best_vibe, 'neutral ambient background music, seamless loop')

    def generate_interlude(self, prompt:str, output_path:str, duration:int=30, samplerate:int=24000, channels:int=2)->Optional[str]:
        venv_python = self._get_venv_python()
        script_path = Path(self.uv_project_path) / 'audiocraft.py'
        if not script_path.exists():
            raise FileNotFoundError(f'Audiocraft script not found at {script_path}')
        # -I keeps the script dir off sys.path and ignores the parent's PYTHON* vars, -u streams download/progress output live
        cmd = [
            venv_python,
            '-I',
            '-u',
            str(script_path),
            '--prompt', prompt,
            '--duration', str(duration),
            '--output', output_path,
            '--samplerate', str(samplerate),
            '--channels', str(channels),
            '--device_info', self.device_info_str
        ]
        try:
            subprocess.run(cmd, check=True, env=self.env_vars)
            if os.path.exists(output_path):
                return output_path
            return None
        except subprocess.CalledProcessError as e:
            print(f'Audiocraft error: exit code {e.returncode}')
            return None
        except Exception as e:
            print(f'Audiocraft exception: {e}')
            return None