import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

# ZONOS2 backbone quantizations (Zyphra/ZONOS2-GGUF): bigger = closer to the full model, more (V)RAM
# internal Q4_K ~4.9 GB, q6_k ~6.8 GB, q8_0 ~8.5 GB (plus the shared DAC decoder and speaker encoder)
models = {
    name: {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['ZONOS']]['repo'],
        "sub": "",
        "file": file,
        "voice": default_engine_settings[TTS_ENGINES['ZONOS']]['voice'],
        "files": [file, default_engine_settings[TTS_ENGINES['ZONOS']]['dac'], default_engine_settings[TTS_ENGINES['ZONOS']]['spk']],
        "samplerate": default_engine_settings[TTS_ENGINES['ZONOS']]['samplerate']
    }
    for name, file in (("internal", "zonos2-q4_k.gguf"), ("q6_k", "zonos2-q6_k.gguf"), ("q8_0", "zonos2-q8_0.gguf"))
}
