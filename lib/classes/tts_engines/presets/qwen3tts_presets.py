from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['repo'],
        "sub": {},
        "samplerate": default_engine_settings[TTS_ENGINES['QWEN3TTS']]['samplerate'],
        "voice": None,
        "files": [],
    },
}
