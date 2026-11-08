import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        # v2ProPlus, reference-free: works from the voice file alone, no transcript needed
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['repo'],
        "sub": "",
        "version": "v2ProPlus",
        "weights": ["v2Pro/s2Gv2ProPlus.pth"],
        "voice": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['samplerate']
    },
    "v5turbo": {
        # v5 uses the vocoder, which needs the reference's text: the worker transcribes it once per voice
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['repo'],
        "sub": "",
        "version": "v5turbo",
        "weights": ["gsv-v5-pretrained/s2Gv5turbo.pth", "gsv-v5-pretrained/vocoder.pth"],
        "voice": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['files'],
        "samplerate": 48000
    },
    "v5dev": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['repo'],
        "sub": "",
        "version": "v5dev",
        "weights": ["gsv-v5-pretrained/s2Gv5dev.pth", "gsv-v5-pretrained/vocoder.pth"],
        "voice": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['GPTSOVITS']]['files'],
        "samplerate": 48000
    }
}