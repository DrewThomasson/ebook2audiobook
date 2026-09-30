# lib/classes/audiocraft_prompter.py
import os
import subprocess
import shutil
from typing import Optional
from pathlib import Path
from transformers import pipeline
from lib.conf import root_dir

class AudiocraftPrompter:
    def __init__(self)->None:
        self.uv_project_path = os.path.join(root_dir, 'components', 'audiocraft')
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
        
        # 1. Check if environment is incomplete (failed install)
        if venv_dir.exists() and not marker_file.exists():
            print('Detected incomplete Audiocraft installation. Cleaning up python_env...')
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f'Warning: Could not fully clean up old env: {e}')
                
        # 2. Create fresh environment if missing
        if not venv_dir.exists():
            msg = 'Setting up Audiocraft uv environment (Python 3.10)...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            
            try:
                # Step A: Create visible python_env with explicit Python 3.10
                subprocess.run(['uv', 'venv', 'python_env', '--python', '3.10'], cwd=project_dir, check=True)
                
                venv_python = self._get_venv_python()
                
                # Step B: Prepare isolated environment variables for uv
                env_vars = os.environ.copy()
                env_vars['VIRTUAL_ENV'] = str(venv_dir)
                venv_bin = str(venv_dir / 'bin') if os.name != 'nt' else str(venv_dir / 'Scripts')
                env_vars['PATH'] = venv_bin + os.pathsep + env_vars.get('PATH', '')
                for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'UV_PYTHON'):
                    env_vars.pop(key, None)
                    
                def _install(pkgs:list[str], no_isolation:bool=False)->None:
                    cmd = ['uv', 'pip', 'install']
                    if no_isolation:
                        cmd.append('--no-build-isolation')
                    cmd.extend(pkgs)
                    subprocess.run(cmd, cwd=project_dir, check=True, env=env_vars)
                    
                print('Installing build dependencies (Cython, maturin)...')
                _install(['Cython', 'maturin'])
                
                print('Installing torch/torchaudio...')
                _install(['torch==2.1.0', 'torchaudio==2.1.0'])
                
                print('Installing av/transformers...')
                _install(['av==12.3.0', 'transformers==4.39.3'])
                
                print('Installing audiocraft (no-build-isolation)...')
                # CRITICAL FIX: Force av==12.3.0 here to prevent uv from downgrading to av 11.x,
                # which fails to compile from source against FFmpeg 8.0+ headers on macOS.
                _install(['audiocraft', 'av==12.3.0'], no_isolation=True)
                
                marker_file.touch()
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
            self.classifier = pipeline(
                'zero-shot-classification',
                model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
                device=-1,
                torch_dtype=torch.float32,
                trust_remote_code=True
            )

    def generate_prompt(self, text:str)->str:
        self.load_model()
        truncated_text = text[:1000]
        result = self.classifier(truncated_text, self.candidate_labels)
        best_vibe = result['labels'][0]
        return self.prompt_map.get(best_vibe, 'neutral ambient background music, seamless loop')

    def generate_interlude(self, prompt:str, output_path:str, duration:int=60)->Optional[str]:
        venv_python = self._get_venv_python()
        script_path = Path(self.uv_project_path) / 'audiocraft.py'
        if not script_path.exists():
            raise FileNotFoundError(f'Audiocraft script not found at {script_path}')
        
        cmd = [
            venv_python,
            str(script_path),
            '--prompt', prompt,
            '--duration', str(duration),
            '--output', output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            if os.path.exists(output_path):
                return output_path
            return None
        except subprocess.CalledProcessError as e:
            print(f'Audiocraft error: {e.stderr}')
            return None
        except Exception as e:
            print(f'Audiocraft exception: {e}')
            return None