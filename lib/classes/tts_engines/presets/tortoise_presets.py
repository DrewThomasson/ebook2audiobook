import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "tts_models/[lang_iso1]/[xxx]",
        "sub": {
            "multi-dataset/tortoise-v2": ['en'],
        },
        "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'KumarDahl.wav'),
        "files": default_engine_settings[TTS_ENGINES['TORTOISE']]['files'],
        "samplerate": {
            "multi-dataset/tortoise-v2": default_engine_settings[TTS_ENGINES['TORTOISE']]['samplerate']
        }
    }
}