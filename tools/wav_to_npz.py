# NOTE: to run this script you must move it to the root of ebook2audiobook

import os

os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['DO_NOT_TRACK'] = 'true'
os.environ['HUGGINGFACE_HUB_CACHE'] = tts_dir
os.environ['HF_HOME'] = tts_dir
os.environ['TRANSFORMERS_CACHE'] = tts_dir
os.environ['HF_DATASETS_CACHE'] = tts_dir
os.environ['BARK_CACHE_DIR'] = tts_dir
os.environ['TTS_CACHE'] = tts_dir
os.environ['TORCH_HOME'] = tts_dir
os.environ['TTS_HOME'] = models_dir
os.environ['XDG_CACHE_HOME'] = models_dir
os.environ['HF_TOKEN_PATH'] = os.path.join(os.path.expanduser('~'), '.huggingface_token')
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['SUNO_OFFLOAD_CPU'] = 'False'
os.environ['SUNO_USE_SMALL_MODELS'] = 'False'

import argparse
import hashlib
import numpy as np
import regex as re
import shutil
import soundfile as sf
import subprocess
import tempfile
import torch
import torchaudio
import threading
import uuid

from iso639 import languages
from huggingface_hub import hf_hub_download
from pathlib import Path
from scipy.io import wavfile as wav
from scipy.signal import find_peaks
from TTS.tts.configs.bark_config import BarkConfig
from TTS.tts.models.bark import Bark

from lib import *

import logging
logging.basicConfig(level=logging.DEBUG)


torch.hub.set_dir(models_dir)

loaded_tts = {}

def load_checkpoint(**kwargs):
    try:
        key = kwargs.get('key')
        tts_engine = kwargs.get('tts_engine')
        device = kwargs.get('device')
        checkpoint_dir = kwargs.get('checkpoint_dir')
        config = BarkConfig()
        config.CACHE_DIR = tts_dir
        config.USE_SMALLER_MODELS = os.environ.get('SUNO_USE_SMALL_MODELS', '').lower() == 'true'
        tts = Bark.init_from_config(config)
        tts.load_checkpoint(
            config,
            checkpoint_dir=checkpoint_dir,
            eval=True
        )                    
        if tts:
            if device == 'cuda':
                tts.cuda()
            else:
                tts.to(device)
            loaded_tts[key] = {"engine": tts, "config": config}
            msg = f'{tts_engine} Loaded!'
            print(msg)
            return tts
        else:
            error = 'TTS engine could not be created!'
            print(error)
    except Exception as e:
        error = f'_load_checkpoint() error: {e}'
    return False

def wav_to_npz(bark_dir, wav_dir):
    try:
        tts_internal_key = f"TTS_ENGINES['BARK']-internal"
        hf_repo = models[TTS_ENGINES['BARK']]['internal']['repo']
        hf_sub = models[TTS_ENGINES['BARK']]['internal']['sub']
        text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][0]}", cache_dir=tts_dir)
        coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][1]}", cache_dir=tts_dir)
        fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][2]}", cache_dir=tts_dir)
        checkpoint_dir = os.path.dirname(text_model_path)
        tts = load_checkpoint(tts_engine=TTS_ENGINES['BARK'], key=tts_internal_key, checkpoint_dir=checkpoint_dir, device='cpu')
        if tts:
            fine_tuned_params = {
                "text_temp": default_engine_settings[TTS_ENGINES['BARK']]['text_temp'],
                "waveform_temp": default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']
            }
            for root, dirs, files in os.walk(wav_dir):
                for file in files:
                    if file.lower().endswith('.wav'):
                        match = re.match(r"^([a-z]{2})_", file)
                        if match:
                            speaker = os.path.splitext(file)[0]
                            npz_file = f'{speaker}.npz'
                            iso1_lang = match.group(1)
                            lang_array = languages.get(part1=iso1_lang)
                            if lang_array:
                                iso3_lang = lang_array.part3
                            default_text_file = os.path.join(voices_dir, iso3_lang, 'default.txt')
                            default_text = Path(default_text_file).read_text(encoding="utf-8")
                            with torch.no_grad():
                                torch.manual_seed(67878789)
                                audio_data = tts.synthesize(
                                    default_text,
                                    loaded_tts[tts_internal_key]['config'],
                                    speaker_id=speaker,
                                    voice_dirs=bark_dir,
                                    silent=True,
                                    **fine_tuned_params
                                )
                                del audio_data
                            msg = f"Saved NPZ file: {npz_file}"
                            print(msg)
        else:
            print('tts bark not loaded')  
    except Exception as e:
        print(f'wav_to_npz() error: {e}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert WAV files to Bark NPZ format.")
    parser.add_argument("--bark_dir", type=str, required=True, help="Path to the Bark asset directory")
    parser.add_argument("--wav_dir", type=str, required=True, help="Path to the output WAV directory")
    args = parser.parse_args()
    bark_dir = os.path.abspath(args.bark_dir)
    wav_dir = os.path.abspath(args.wav_dir)
    wav_to_npz(bark_dir, wav_dir)

