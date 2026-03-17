from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "speech-2.8-hd": {
        "lang": "multi",
        "model": "speech-2.8-hd",
        "repo": "minimax/speech-2.8-hd",
        "voice": "English_Graceful_Lady",
        "samplerate": default_engine_settings[TTS_ENGINES['MINIMAX']]['samplerate'],
    },
    "speech-2.8-turbo": {
        "lang": "multi",
        "model": "speech-2.8-turbo",
        "repo": "minimax/speech-2.8-turbo",
        "voice": "English_Graceful_Lady",
        "samplerate": default_engine_settings[TTS_ENGINES['MINIMAX']]['samplerate'],
    },
}
