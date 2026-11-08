import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        # zero-shot: clones the voice file (its audio tokens + its Whisper transcript)
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['SPARKTTS']]['repo'],
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['SPARKTTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['SPARKTTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['SPARKTTS']]['samplerate']
    }
}
