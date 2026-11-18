import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

# ZONOS3-Mini backbone (Zyphra/ZONOS3-Mini gguf/): Q4_0 routed experts, Q8_0 mixers, the rest F16/F32 (0.66 GB), plus the
# shared ZAC keep2 decoder, speaker encoder and steering bundle. The only quantization Zyphra publishes
models = {
    name: {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['ZONOS3']]['repo'],
        "sub": "",
        "file": file,
        "voice": default_engine_settings[TTS_ENGINES['ZONOS3']]['voice'],
        "files": [file, default_engine_settings[TTS_ENGINES['ZONOS3']]['zac'], default_engine_settings[TTS_ENGINES['ZONOS3']]['spk'], default_engine_settings[TTS_ENGINES['ZONOS3']]['steer']],
        "samplerate": default_engine_settings[TTS_ENGINES['ZONOS3']]['samplerate']
    }
    for name, file in (("internal", "gguf/backbone-ptq.gguf"),)
}
