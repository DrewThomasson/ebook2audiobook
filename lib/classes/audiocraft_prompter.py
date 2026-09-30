import os
import subprocess
import shutil
import logging

from typing import Optional
from pathlib import Path
from transformers import pipeline
from lib.conf import components_dir

class AudiocraftPrompter:

    def __init__(self)->None:
        self.uv_project_path = os.path.join(components_dir, 'audiocraft')
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
        env_version = '2'
        if venv_dir.exists() and (not marker_file.exists() or marker_file.read_text().strip() != env_version):
            print('Detected incomplete or outdated Audiocraft installation. Cleaning up python_env...')
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f'Warning: Could not fully clean up old env: {e}')
        if not venv_dir.exists():
            msg = 'Setting up Audiocraft uv environment (Python 3.10)...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            marker_file.unlink(missing_ok=True)
            try:
                env_vars = self.env_vars
                subprocess.run(['uv', 'venv', 'python_env', '--python', '3.10'], cwd=project_dir, check=True, env=env_vars)
                def _install(pkgs:list[str], no_isolation:bool=False)->None:
                    cmd = ['uv', 'pip', 'install']
                    if no_isolation:
                        cmd.append('--no-build-isolation')
                    cmd.extend(pkgs)
                    subprocess.run(cmd, cwd=project_dir, check=True, env=env_vars)
                print('Step 1/6: Installing build tools...')
                _install(['setuptools<75', 'wheel', 'Cython', 'maturin', 'ninja'])
                print('Step 2/6: Installing numpy (must be <2 for torch 2.1.0)...')
                _install(['numpy==1.26.4'])
                print('Step 3/6: Installing torch/torchaudio...')
                _install(['torch==2.1.0', 'torchaudio==2.1.0'])
                print('Step 4/6: Installing av/transformers...')
                _install(['av==12.3.0', 'transformers==4.39.3'])
                print('Step 5/6: Creating xformers/gradio override and xformers stub...')
                override_file = project_dir / 'override.txt'
                override_file.write_text('xformers ; python_version < "0"\ngradio ; python_version < "0"\n')
                # audiocraft imports xformers.ops at module level but only runs it on the torch backend: unbind + LowerTriangularMask (used as a causal flag)
                site_packages = subprocess.run([self._get_venv_python(), '-I', '-c', "import sysconfig;print(sysconfig.get_paths()['purelib'])"], capture_output=True, text=True, check=True, env=env_vars).stdout.strip()
                xformers_dir = Path(site_packages) / 'xformers'
                os.makedirs(xformers_dir, exist_ok=True)
                (xformers_dir / '__init__.py').write_text('')
                (xformers_dir / 'ops.py').write_text(
                    'import torch\n'
                    'class LowerTriangularMask:\n'
                    '    pass\n'
                    'def unbind(x:torch.Tensor, dim:int=0)->tuple:\n'
                    '    return torch.unbind(x, dim=dim)\n'
                    'def memory_efficient_attention(*args, **kwargs)->torch.Tensor:\n'
                    "    raise NotImplementedError('xformers stub: audiocraft must stay on its torch attention backend')\n"
                )
                print('Step 6/6: Installing audiocraft (skipping xformers)...')
                # native deps must come as wheels: macOS x86_64 has none past llvmlite 0.45.1/numba 0.62.1 and none for sphn (demucs 4.1.0), so uv backtracks instead of compiling
                cmd = ['uv', 'pip', 'install', '--no-build-isolation', '--override', str(override_file), '--only-binary', 'llvmlite', '--only-binary', 'numba', '--only-binary', 'sphn', 'audiocraft', 'av==12.3.0', 'numpy==1.26.4', 'torch==2.1.0', 'torchaudio==2.1.0', 'transformers==4.39.3']
                subprocess.run(cmd, cwd=project_dir, check=True, env=env_vars)
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

    def generate_interlude(self, prompt:str, output_path:str, duration:int=60, samplerate:int=24000, channels:int=1)->Optional[str]:
        venv_python = self._get_venv_python()
        script_path = Path(self.uv_project_path) / 'audiocraft.py'
        if not script_path.exists():
            raise FileNotFoundError(f'Audiocraft script not found at {script_path}')
        # -I drops the script dir from sys.path (audiocraft.py would shadow the audiocraft package) and ignores the parent's PYTHON* vars, -u streams download/progress output live
        cmd = [
            venv_python,
            '-I',
            '-u',
            str(script_path),
            '--prompt', prompt,
            '--duration', str(duration),
            '--output', output_path,
            '--samplerate', str(samplerate),
            '--channels', str(channels)
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