import os
import platform
import argparse

tmp_dir = os.path.abspath(os.path.join('..', 'tmp'))
models_dir = os.path.abspath(os.path.join('..', 'models'))
tts_dir = os.path.join(models_dir, 'tts')

os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['CALIBRE_NO_NATIVE_FILEDIALOGS'] = '1'
os.environ['DO_NOT_TRACK'] = 'true'
os.environ['CALIBRE_TEMP_DIR'] = tmp_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = tmp_dir
os.environ['HUGGINGFACE_HUB_CACHE'] = tts_dir
os.environ['HF_HOME'] = tts_dir
os.environ['HF_DATASETS_CACHE'] = tts_dir
os.environ['BARK_CACHE_DIR'] = tts_dir
os.environ['TTS_CACHE'] = tts_dir
os.environ['TORCH_HOME'] = tts_dir
os.environ['TTS_HOME'] = models_dir
os.environ['XDG_CACHE_HOME'] = models_dir
os.environ['ARGOS_TRANSLATE_PACKAGE_PATH'] = os.path.join(models_dir, 'argostranslate')
os.environ['HF_TOKEN_PATH'] = os.path.join(os.path.expanduser('~'), '.huggingface_token')
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['SUNO_OFFLOAD_CPU'] = 'False' # BARK option: False needs A GPU
os.environ['SUNO_USE_SMALL_MODELS'] = 'False' # BARK option: False needs a GPU with VRAM > 4GB
if platform.system() == 'Windows':
    os.environ['ESPEAK_DATA_PATH'] = os.path.expandvars(r"%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data")

import torch
import torchaudio
import numpy as np
from pathlib import Path
from bark import SAMPLE_RATE, preload_models
from bark.generation import codec_decode

def npz_to_wav(npz_path, output_path):
	preload_models()
	data = np.load(npz_path)
	fine_prompt = data["fine_prompt"]
	audio_array = codec_decode(fine_prompt)
	audio_tensor = torch.tensor(audio_array).unsqueeze(0)
	torchaudio.save(output_path, audio_tensor, SAMPLE_RATE)
	print(f"✅ Saved: {output_path}")

def process_all_npz_in_folder(folder_path):
	preload_models()
	for npz_file in Path(folder_path).rglob("*.npz"):
		output_path = npz_file.with_suffix(".wav")
		npz_to_wav(str(npz_file), str(output_path))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Process all NPZ files in a folder.")
	parser.add_argument("--folder_path", type=str, required=True, help="Path to the folder containing NPZ files")
	args = parser.parse_args()
	folder_path = os.path.abspath(args.folder_path)
	process_all_npz_in_folder(folder_path)
