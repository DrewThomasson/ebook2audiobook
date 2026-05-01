from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
   "internal": {
        "lang": "multi",
        "repo": "tts_models/[lang_iso1]/[xxx]",
        "sub": {
            "mai/tacotron2-DDC": ['fr', 'es'],
            "thorsten/tacotron2-DDC": ['de'],
            "ljspeech/tacotron2-DDC": ['en']            
        },
        "voice": default_engine_settings[TTS_ENGINES['TACOTRON2']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['TACOTRON2']]['files'],
        "samplerate": {
            "mai/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate'],
            "thorsten/tacotron2-DDC": 24000,
            "ljspeech/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate']
        },
    }
}