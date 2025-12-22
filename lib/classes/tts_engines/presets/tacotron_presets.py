import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    TTS_ENGINES['TACOTRON2']: {
       "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang_iso1]/[xxx]",
            "sub": {
                "mai/tacotron2-DDC": ['fr', 'es', 'nl'],
                "thorsten/tacotron2-DDC": ['de'],
                "kokoro/tacotron2-DDC": ['ja'],
                "ljspeech/tacotron2-DDC": ['en'],
                "baker/tacotron2-DDC-GST": ['zh-CN']              
            },
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['TACOTRON2']]['files'],
            "samplerate": {
                "mai/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate'],
                "thorsten/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate'],
                "kokoro/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate'],
                "ljspeech/tacotron2-DDC": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate'],
                "baker/tacotron2-DDC-GST": default_engine_settings[TTS_ENGINES['TACOTRON2']]['samplerate']
            },
        }
    }
}