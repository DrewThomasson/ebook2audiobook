from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "hexgrad/Kokoro-82M",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES["KOKORO"]]["voice"],
        "files": default_engine_settings[TTS_ENGINES["KOKORO"]]["files"],
        "samplerate": default_engine_settings[TTS_ENGINES["KOKORO"]]["samplerate"],
    }
}
