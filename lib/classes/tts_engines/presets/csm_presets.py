import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        # zero-shot: clones the voice file (its Mimi frames + its Whisper transcript as the context segment)
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['CSM']]['repo'],
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['CSM']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['CSM']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['CSM']]['samplerate']
    }
}
