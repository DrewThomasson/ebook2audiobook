from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "BreezeBlue/Breeze-TTS-2",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES["BREEZE"]]["voice"],
        "files": default_engine_settings[TTS_ENGINES["BREEZE"]]["files"],
        "samplerate": default_engine_settings[TTS_ENGINES["BREEZE"]]["samplerate"],
    }
}
