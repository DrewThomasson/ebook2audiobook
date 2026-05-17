from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "rhasspy/piper-voices",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['PIPER']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['PIPER']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['PIPER']]['samplerate']
    }
}
