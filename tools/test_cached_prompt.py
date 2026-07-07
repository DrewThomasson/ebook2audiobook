"""Quick test: load a cached voice-clone prompt and verify it's valid."""
import sys, os, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.chdir(Path(__file__).resolve().parent.parent)

import torch

# Find a cached prompt
cached = list(Path('models/qwen3_voice_cache').glob('MorganFreeman*'))
if not cached:
    print('No MorganFreeman cache found, using first available')
    cached = list(Path('models/qwen3_voice_cache').glob('*.pt'))
    if not cached:
        print('No cached prompts found!')
        sys.exit(1)

test_file = cached[0]
print(f'Loading: {test_file.name}')
data = torch.load(test_file, map_location='cpu', weights_only=True)
print(f'Items: {len(data)}')
item = data[0]
print(f'  ref_code: {item["ref_code"]}')
print(f'  ref_spk_embedding shape: {item["ref_spk_embedding"].shape}')
print(f'  x_vector_only_mode: {item["x_vector_only_mode"]}')
print(f'  icl_mode: {item["icl_mode"]}')

# Verify the dict format generate_voice_clone expects
prompt_dict = {
    'ref_code': [d['ref_code'] for d in data],
    'ref_spk_embedding': [d['ref_spk_embedding'] for d in data],
    'x_vector_only_mode': [d['x_vector_only_mode'] for d in data],
    'icl_mode': [d['icl_mode'] for d in data],
}
print(f'\nPrompt dict keys: {list(prompt_dict.keys())}')
print('SUCCESS: cached prompt is valid')
