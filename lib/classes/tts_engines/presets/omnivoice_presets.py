from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "multi",
        "repo": "k2-fsa/OmniVoice",
        "voice": default_engine_settings[TTS_ENGINES['OMNIVOICE']]['voice'],
        "files": [],
        "samplerate": 24000
    }
}
