from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "tts_models/multilingual/multi-dataset/your_tts",
        "sub": "",
        "voice": default_engine_settings[TTS_ENGINES['YOURTTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['YOURTTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['YOURTTS']]['samplerate']
    }
}