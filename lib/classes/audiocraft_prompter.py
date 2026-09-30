import os
import subprocess
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
        if not venv_dir.exists():
            msg = 'Audiocraft uv environment not found. Setting up...'
            print(msg)
            os.makedirs(project_dir, exist_ok=True)
            try:
                # 1. Create the virtual environment
                subprocess.run(['uv', 'venv'], cwd=project_dir, check=True)
                
                # 2. Install torch FIRST (required for xformers build)
                # We pin to a stable version compatible with audiocraft
                subprocess.run(['uv', 'pip', 'install', 'torch', 'torchaudio'], cwd=project_dir, check=True)
                
                # 3. Install audiocraft with --no-build-isolation
                # This allows xformers to see the already-installed torch during compilation
                subprocess.run([
                    'uv', 'pip', 'install', 
                    '--no-build-isolation', 
                    'audiocraft'
                ], cwd=project_dir, check=True)
                
                print('Audiocraft environment setup complete.')
            except subprocess.CalledProcessError as e:
                print(f'Failed to setup Audiocraft env: {e}')
                raise RuntimeError(f'Audiocraft setup failed: {e.stderr}')
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
        # Ensure input is processed in float32
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