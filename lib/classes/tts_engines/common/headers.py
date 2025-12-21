import os
import torch
import torchaudio
import random
import regex as re
import numpy as np

from multiprocessing.managers import DictProxy
from typing import Any
from pathlib import Path

from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.utils import TTSUtils
from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
from lib.conf import tts_dir, devices, default_audio_proc_format
from lib.conf_models import TTS_ENGINES, TTS_SML, loaded_tts, default_vc_model
from lib.conf_lang import language_tts


__all__ = [
    # std / third-party
    "os",
    "torch",
    "torchaudio",
    "random",
    "re",
    "np",

    # typing / stdlib
    "DictProxy",
    "Any",
    "Path",

    # registry & utils
    "TTSRegistry",
    "TTSUtils",
    "trim_audio",
    "is_audio_data_valid",

    # config
    "tts_dir",
    "devices",
    "default_audio_proc_format",
    "TTS_ENGINES",
    "TTS_SML",
    "loaded_tts",
    "default_vc_model",
    "language_tts",
]