import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['OMNIVOICE']]['repo'],
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['OMNIVOICE']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['OMNIVOICE']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['OMNIVOICE']]['samplerate']
    }
}