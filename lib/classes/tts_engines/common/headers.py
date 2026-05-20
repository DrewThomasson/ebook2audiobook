import sys, os, shutil, random, subprocess, uuid, wave, regex as re

from typing import Any
from pathlib import Path
from multiprocessing.managers import DictProxy

from lib.classes.std_filter import StderrFilter
from lib.classes.std_filter import StdoutFilter
from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.utils import TTSUtils
from lib.conf import tts_dir, devices, default_audio_proc_format
from lib.conf_models import TTS_ENGINES, TTS_VOICE_CONVERSION, TTS_SML, SML_TAG_PATTERN, loaded_tts, default_vc_model, default_engine_settings, tts_engines_from_coqui

__all__ = [
    "sys",
    "os",
    "shutil",
    "random",
    "subprocess",
    "uuid",
    "wave",
    "re",
    "Any",
    "Path",
    "DictProxy",
    "StderrFilter",
    "StdoutFilter",
    "TTSRegistry",
    "TTSUtils",
    "tts_dir",
    "devices",
    "default_audio_proc_format",
    "TTS_ENGINES",
    "TTS_VOICE_CONVERSION",
    "TTS_SML",
    "SML_TAG_PATTERN", 
    "loaded_tts",
    "default_vc_model",
    "default_engine_settings",
    "tts_engines_from_coqui"
]