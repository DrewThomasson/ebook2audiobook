from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "tts_models/[lang_iso1]/[xxx]",
        "sub": {
            "css10/vits": ['es','hu','fi','fr','nl','ru','el'],
            "custom/vits": ['ca'],
            "custom/vits-female": ['bn', 'fa'],
            "cv/vits": ['bg','cs','da','et','ga','hr','lt','lv','mt','pt','ro','sk','sl','sv'],
            "mai/vits": ['uk'],
            "mai_female/vits": ['pl'],
            "mai_male/vits": ['it'],
            "openbible/vits": ['ewe','hau','lin','tw_akuapem','tw_asante','yor'],
            "vctk/vits": ['en'],
            "thorsten/vits": ['de']
        },
        "voice": None,
        "files": default_engine_settings[TTS_ENGINES['VITS']]['files'],
        "samplerate": {
            "css10/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "custom/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "custom/vits-female": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "cv/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "mai/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "mai_female/vits": 24000,
            "mai_male/vits": 16000,
            "openbible/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "vctk/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
            "thorsten/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate']
        }
    }
}
