from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "fishaudio/s2-pro",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES["FISH"]]["voice"],
        "files": default_engine_settings[TTS_ENGINES["FISH"]]["files"],
        "samplerate": default_engine_settings[TTS_ENGINES["FISH"]]["samplerate"],
    }
}
