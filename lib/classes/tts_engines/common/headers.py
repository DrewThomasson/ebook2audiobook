import os, shutil, random, subprocess, uuid, regex as re

from typing import Any
from pathlib import Path
from multiprocessing.managers import DictProxy

from lib.conf import tts_dir, devices, default_audio_proc_format
from lib.conf_models import TTS_ENGINES, TTS_VOICE_CONVERSION, TTS_SML, SML_TAG_PATTERN, loaded_tts, default_vc_model, default_engine_settings
from lib.classes.tts_registry import TTSRegistry
__all__ = [
    "os",
    "shutil",
    "random",
    "subprocess",
    "uuid",
    "re",
    "Any",
    "Path",
    "DictProxy",
    "TTSRegistry",
    "tts_dir",
    "devices",
    "default_audio_proc_format",
    "TTS_ENGINES",
    "TTS_VOICE_CONVERSION",
    "TTS_SML",
    "SML_TAG_PATTERN", 
    "loaded_tts",
    "default_vc_model",
    "default_engine_settings"
]