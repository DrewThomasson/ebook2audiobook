from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "tts_models/[lang_iso1]/[xxx]",
        "sub": {
            "ljspeech/glow-tts": ['en'],
            "mai/glow-tts": ['uk'],
            "mai_male/glow-tts": ['it'],
            "custom/glow-tts": ['fa'],
            "common-voice/glow-tts": ['be', 'tr']
        },
        "voice": None,
        "files": default_engine_settings[TTS_ENGINES['GLOWTTS']]['files'],
        "samplerate": {
            "ljspeech/glow-tts": default_engine_settings[TTS_ENGINES['GLOWTTS']]['samplerate'],
            "mai/glow-tts": 16000,
            "mai_male/glow-tts": 16000,
            "custom/glow-tts": 24000,
            "common-voice/glow-tts": default_engine_settings[TTS_ENGINES['GLOWTTS']]['samplerate']
        }
    }
}

