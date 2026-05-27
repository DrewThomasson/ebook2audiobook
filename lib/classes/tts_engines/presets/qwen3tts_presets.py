import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['samplerate']
    },
    "custom_voice": {
        "lang": "multi",
        "repo": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['samplerate']
    }
}
