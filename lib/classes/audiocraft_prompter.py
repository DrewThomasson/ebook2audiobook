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
        if not project_dir.exists():
            msg = 'Setting up Audiocraft uv environment (Python 3.10)...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            
            try:
                # Helper to run pip install within the venv context
                # We use --no-build-isolation for all steps after torch to allow 
                # xformers to see torch during compilation
                def _install(pkgs:list[str], isolation:bool=False)->None:
                    cmd = ['uv', 'pip', 'install']
                    if not isolation:
                        cmd.append('--no-build-isolation')
                    cmd.extend(pkgs)
                    subprocess.run(cmd, cwd=project_dir, check=True)

                # Step A: Create venv with explicit Python 3.10
                # Note: Ensure python3.10 is installed on your system or accessible by uv
                subprocess.run(['uv', 'venv', '--python', '3.10'], cwd=project_dir, check=True)
                
                # Step B: Install Torch/Torchaudio FIRST (with build isolation enabled initially 
                # to get core wheels, though usually safe without. But crucially, they MUST be present 
                # before xformers builds).
                # Actually, standard practice for xformers issues is to install torch normally, 
                # then install the rest with --no-build-isolation.
                subprocess.run([
                    'uv', 'pip', 'install', 
                    'torch==2.1.0', 
                    'torchaudio==2.1.0'
                ], cwd=project_dir, check=True)

                # Step C: Install av and transformers (dependencies for audiocraft)
                # Using --no-build-isolation ensures they link against the existing torch
                _install([
                    'av==12.3.0',
                    'transformers==4.39.3'
                ], isolation=False)

                # Step D: Install audiocraft LAST
                # This triggers xformers compilation, which will now succeed because torch is visible
                _install([
                    'audiocraft'
                ], isolation=False)
                
                # Mark success
                marker_file.touch()
                print('Audiocraft environment setup complete.')
                
            except subprocess.CalledProcessError as e:
                error_msg = f'Failed to setup Audiocraft env: {e.stderr}'
                print(error_msg)
                # Clean up the half-installed mess so next run tries again cleanly
                if project_dir.exists():
                    shutil.rmtree(project_dir, ignore_errors=True)
                raise RuntimeError(error_msg)
            except FileNotFoundError:
                error_msg = 'uv command not found. Please install uv (https://docs.astral.sh/uv/) to use Audiocraft interludes.'
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
        cmd = [
            'uv', 'run', '--project', self.uv_project_path,
            'python', 'audiocraft.py',
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