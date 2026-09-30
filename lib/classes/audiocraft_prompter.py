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
        """Returns the absolute path to the python executable inside the target venv."""
        if os.name == 'nt': # Windows
            return str(Path(self.uv_project_path) / '.venv' / 'Scripts' / 'python.exe')
        else: # Linux/Mac
            return str(Path(self.uv_project_path) / '.venv' / 'bin' / 'python')

    def _ensure_audiocraft_env(self)->None:
        project_dir = Path(self.uv_project_path)
        venv_dir = project_dir / '.venv'
        marker_file = project_dir / '.audiocraft_installed'

        # 1. Check if environment is incomplete (failed install)
        if venv_dir.exists() and not marker_file.exists():
            print('Detected incomplete Audiocraft installation. Cleaning up...')
            try:
                shutil.rmtree(project_dir)
            except Exception as e:
                print(f'Warning: Could not fully clean up old env: {e}')

        # 2. Create fresh environment if missing
        if not project_dir.exists() or not venv_dir.exists():
            msg = 'Setting up Audiocraft uv environment (Python 3.10)...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            
            try:
                # Step A: Create venv with explicit Python 3.10
                # We run this in the project dir so .venv is created there
                subprocess.run(['uv', 'venv', '--python', '3.10'], cwd=project_dir, check=True)
                
                # Get the path to the new venv's python interpreter
                venv_python = self._get_venv_python()
                
                # Prepare environment variables for subsequent commands
                # UV_PYTHON forces uv to use this specific interpreter/venv
                env_vars = os.environ.copy()
                env_vars['UV_PYTHON'] = venv_python
                
                # Helper to run pip install INSIDE the specific venv using UV_PYTHON
                def _install(pkgs:list[str])->None:
                    cmd = ['uv', 'pip', 'install'] + pkgs
                    # Pass the custom env vars to ensure uv targets the correct venv
                    subprocess.run(cmd, cwd=project_dir, check=True, env=env_vars)

                # Step B: Install Build Dependencies FIRST
                # sphn requires maturin. xformers requires torch (installed next).
                print('Installing build dependencies (maturin)...')
                _install(['maturin'])

                # Step C: Install Torch/Torchaudio
                # Must be present before xformers/audiocraft build
                print('Installing torch/torchaudio...')
                _install([
                    'torch==2.1.0',
                    'torchaudio==2.1.0'
                ])
                
                # Step D: Install av and transformers
                print('Installing av/transformers...')
                _install([
                    'av==12.3.0',
                    'transformers==4.39.3'
                ])
                
                # Step E: Install audiocraft LAST
                # Now that torch, maturin, and other deps are in the venv, this will succeed
                print('Installing audiocraft...')
                _install([
                    'audiocraft'
                ])
                
                # Mark success
                marker_file.touch()
                print('Audiocraft environment setup complete.')
                
            except subprocess.CalledProcessError as e:
                error_msg = f'Failed to setup Audiocraft env: {e}'
                print(error_msg)
                # Clean up the half-installed mess so next run tries again cleanly
                if project_dir.exists():
                    shutil.rmtree(project_dir, ignore_errors=True)
                raise RuntimeError(error_msg)
            except FileNotFoundError:
                error_msg = 'uv command not found. Please install uv.'
                print(error_msg)
                raise RuntimeError(error_msg)

    def load_model(self)->None:
        if self.classifier is None:
            import torch
            # Force float32 to avoid "LayerNormKernelImpl not implemented for Half" on CPU/macOS
            self.classifier = pipeline(
                'zero-shot-classification', 
                model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli', 
                device=-1, # CPU
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
        # Ensure we run the script using the SPECIFIC venv python, not the system python
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
            # Run directly with the venv python. No need for 'uv run' if we invoke the binary directly.
            # This is faster and more reliable than relying on uv's project detection.
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