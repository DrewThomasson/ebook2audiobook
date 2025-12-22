import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    TTS_ENGINES['FAIRSEQ']: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['FAIRSEQ']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['FAIRSEQ']]['samplerate']
        }
    }
}