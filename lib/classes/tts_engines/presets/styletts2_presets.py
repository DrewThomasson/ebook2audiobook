from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    "internal": {
        "lang": "eng",
        "repo": "yl4579/StyleTTS2-LibriTTS",
        "voice": default_engine_settings[TTS_ENGINES['STYLETTS2']]['voice'],
        "files": ["Models/LibriTTS/config.yml", "Models/LibriTTS/epochs_2nd_00020.pth"],
        "samplerate": 24000
    },
    "ljspeech": {
        "lang": "eng",
        "repo": "yl4579/StyleTTS2-LJSpeech",
        "voice": default_engine_settings[TTS_ENGINES['STYLETTS2']]['voice'],
        "files": ["Models/LJSpeech/config.yml", "Models/LJSpeech/epoch_2nd_00100.pth"],
        "samplerate": 24000
    }
}
