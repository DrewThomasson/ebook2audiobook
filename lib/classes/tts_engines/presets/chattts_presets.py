import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        # zero-shot: clones the voice file (its DVAE codes + its Whisper transcript)
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['CHATTTS']]['repo'],
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['CHATTTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['CHATTTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['CHATTTS']]['samplerate']
    }
}
