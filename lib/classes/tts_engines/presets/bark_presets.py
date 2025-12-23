import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "tts_models/multilingual/multi-dataset/bark", # load_checkpoint => erogol/bark, suno/bark, rsxdalv/suno. load_api => tts_models/multilingual/multi-dataset/bark
        "sub": "", # {"big-bf16": "big-bf16/", "small-bf16": "small-bf16/", "big": "big/", "small": "small/"}
        "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'KumarDahl.wav'),
        "files": default_engine_settings[TTS_ENGINES['BARK']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['BARK']]['samplerate']
    }
}