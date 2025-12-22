import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    TTS_ENGINES['YOURTTS']: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/your_tts",
            "sub": "",
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['YOURTTS']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['YOURTTS']]['samplerate']
        }
    }
}