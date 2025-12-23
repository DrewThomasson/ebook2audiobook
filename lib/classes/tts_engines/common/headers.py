import os, torch, torchaudio, random, uuid, regex as re, numpy as np

from typing import Any
from pathlib import Path
from multiprocessing.managers import DictProxy
from huggingface_hub import hf_hub_download

from lib.conf import tts_dir, devices, default_audio_proc_format
from lib.conf_models import TTS_ENGINES, TTS_SML, TTS_VOICE_CONVERSION, loaded_tts, default_vc_model, default_engine_settings
from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.utils import TTSUtils
from lib.classes.tts_engines.common.audio import detect_gender, trim_audio, is_audio_data_valid

__all__ = [
    "os",
    "torch",
    "torchaudio",
    "random",
    "uuid",
    "re",
    "np",
    "Any",
    "Path",
    "DictProxy",
    "hf_hub_download",
    "TTSRegistry",
    "TTSUtils",
    "detect_gender",
    "trim_audio",
    "is_audio_data_valid",
    "tts_dir",
    "devices",
    "default_audio_proc_format",
    "TTS_ENGINES",
    "TTS_SML",
    "TTS_VOICE_CONVERSION",
    "loaded_tts",
    "default_vc_model",
    "default_engine_settings"
]