from lib.conf_models import TTS_ENGINES, default_engine_settings, audiocpp_repo

# audio.cpp GGUF packages per engine (Hugging Face audio-cpp/audio.cpp-gguf unless "repo" says otherwise), files as in
# audio.cpp's model_specs/<family>.json packages[].files: the first file is the model path given to audiocpp_server, the
# others are sidecars the Hugging Face snapshot keeps beside it. "internal" is audio.cpp's default package (IndexTTS2:
# 2.5, for its five languages). files_by_language: one package per language (PocketTTS). languages: a preset speaking
# fewer languages than its engine (IndexTTS2 v2), listed only for those
packages = {
    TTS_ENGINES['BREEZE_TTS']: [("internal", ["Breeze-TTS-2-GGUF/breeze-tts-2-q8_0.gguf"]), ("q4_0", ["Breeze-TTS-2-GGUF/breeze-tts-2-q4_0.gguf"]), ("bf16", ["Breeze-TTS-2-GGUF/breeze-tts-2-bf16.gguf"])],
    TTS_ENGINES['CHATTERBOX']: [("internal", ["Chatterbox-GGUF/chatterbox-q8_0.gguf"]), ("f16", ["Chatterbox-GGUF/chatterbox-f16.gguf"])],
    TTS_ENGINES['CONFUCIUS4_TTS']: [("internal", ["Confucius4-TTS-GGUF/confucius4-tts-orig.gguf"])],
    TTS_ENGINES['COSYVOICE3']: [("internal", ["CosyVoice3-GGUF/cosyvoice3-q8_0.gguf"]), ("f32", ["CosyVoice3-GGUF/cosyvoice3-f32.gguf"])],
    TTS_ENGINES['DOTS_TTS']: [("internal", ["DotTTS-SOAR-GGUF/dots-tts-soar-q8_0.gguf"]), ("soar_bf16", ["DotTTS-SOAR-GGUF/dots-tts-soar-bf16.gguf"]), ("meanflow", ["DotTTS-MF-GGUF/dots-tts-mf-q8_0.gguf"]), ("meanflow_bf16", ["DotTTS-MF-GGUF/dots-tts-mf-bf16.gguf"])],
    TTS_ENGINES['DRAMABOX']: [("internal", ["DramaBox-GGUF/dramabox-q8_0.gguf"])],
    TTS_ENGINES['FIRERED_AUDIO']: [("internal", ["FireRedAudio-GGUF/firered-audio-q8_0.gguf"]), ("orig", ["FireRedAudio-GGUF/firered-audio-orig.gguf"])],
    TTS_ENGINES['FIREREDTTS3']: [("internal", ["FireRedTTS3-Instruct-GGUF/fireredtts3-instruct-q8_0.gguf"]), ("instruct_orig", ["FireRedTTS3-Instruct-GGUF/fireredtts3-instruct-orig.gguf"]), ("base", ["FireRedTTS3-Base-GGUF/fireredtts3-base-q8_0.gguf"]), ("base_orig", ["FireRedTTS3-Base-GGUF/fireredtts3-base-orig.gguf"])],
    TTS_ENGINES['FISH_AUDIO']: [("internal", ["Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-q8_0.gguf"]), ("bf16", ["Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-bf16.gguf"])],
    TTS_ENGINES['HIGGS_AUDIO_TTS']: [("internal", ["Higgs-Audio-v3-TTS-4B-GGUF/higgs-audio-v3-tts-4b-q8_0.gguf"]), ("bf16", ["Higgs-Audio-v3-TTS-4B-GGUF/higgs-audio-v3-tts-4b-bf16.gguf"])],
    TTS_ENGINES['INDEX_TTS2']: [("internal", ["IndexTTS2.5-GGUF/index-tts2_5-q8_0.gguf"]), ("v2_5_f16", ["IndexTTS2.5-GGUF/index-tts2_5-f16.gguf"]), ("v2_5_orig", ["IndexTTS2.5-GGUF/index-tts2_5-orig.gguf"]), ("v2", ["IndexTTS2-GGUF/index-tts2-q8_0.gguf"], {"languages": {"zho": "zh", "eng": "en"}}), ("v2_f16", ["IndexTTS2-GGUF/index-tts2-f16.gguf"], {"languages": {"zho": "zh", "eng": "en"}}), ("v2_orig", ["IndexTTS2-GGUF/index-tts2-orig.gguf"], {"languages": {"zho": "zh", "eng": "en"}})],
    TTS_ENGINES['IRODORI_TTS']: [("internal", ["Irodori-TTS-v4-Small-GGUF/irodori-tts-v4-small-q8_0.gguf"]), ("f16", ["Irodori-TTS-v4-Small-GGUF/irodori-tts-v4-small-f16.gguf"]), ("anime", ["Irodori-TTS-v4-Small-GGUF/irodori-tts-v4.1-anime-q8_0.gguf"]), ("v3_500m", ["Irodori-TTS-500M-v3-GGUF/irodori-tts-500m-v3-q8_0.gguf"]), ("v3_500m_f16", ["Irodori-TTS-500M-v3-GGUF/irodori-tts-500m-v3-f16.gguf"])],
    TTS_ENGINES['KOKORO_TTS']: [("internal", ["Kokoro-82M-GGUF/kokoro-82m-q8_0.gguf"]), ("bf16", ["Kokoro-82M-GGUF/kokoro-82m-bf16.gguf"])],
    TTS_ENGINES['KUGELAUDIO']: [("internal", ["KugelAudio-0-Open-GGUF/kugelaudio-0-open-q8_0.gguf"]), ("bf16", ["KugelAudio-0-Open-GGUF/kugelaudio-0-open-bf16.gguf"]), ("q4_k", ["KugelAudio-0-Open-GGUF/kugelaudio-0-open-q4_k.gguf"])],
    TTS_ENGINES['MAGPIE_TTS']: [("internal", ["MagpieTTS-Multilingual-357M-GGUF/magpie-tts-multilingual-357m-q8_0.gguf"]), ("orig", ["MagpieTTS-Multilingual-357M-GGUF/magpie-tts-multilingual-357m-orig.gguf"])],
    TTS_ENGINES['MAYA1']: [("internal", ["Maya1-GGUF/maya1-orig.gguf"]), ("q8_0", ["Maya1-GGUF/maya1-q8_0.gguf"])],
    TTS_ENGINES['MIOTTS']: [("internal", ["MioTTS-1.7B-GGUF/miotts-1.7b-q8_0.gguf"]), ("bf16", ["MioTTS-1.7B-GGUF/miotts-1.7b-bf16.gguf"]), ("orig", ["MioTTS-1.7B-GGUF/miotts-1.7b-orig.gguf"])],
    TTS_ENGINES['MOSS_TTS_LOCAL']: [("internal", ["MOSS-TTS-Local-v1.5-GGUF/moss-tts-local-v1.5-q8_0.gguf"]), ("bf16", ["MOSS-TTS-Local-v1.5-GGUF/moss-tts-local-v1.5-bf16.gguf"])],
    TTS_ENGINES['MOSS_TTS_NANO']: [("internal", ["MOSS-TTS-Nano-100M-GGUF/moss-tts-nano-100m-q8_0.gguf"]), ("bf16", ["MOSS-TTS-Nano-100M-GGUF/moss-tts-nano-100m-bf16.gguf"])],
    TTS_ENGINES['NEUTTS']: [("internal", ["NeuTTS-2E-GGUF/neutts-2e-orig.gguf"])],
    TTS_ENGINES['POCKET_TTS']: [
        ("internal", ["PocketTTS-GGUF/english/pocket-tts-english-q8_0.gguf", "PocketTTS-GGUF/english/embeddings/alba.safetensors"], {"files_by_language": {"eng": ["PocketTTS-GGUF/english/pocket-tts-english-q8_0.gguf", "PocketTTS-GGUF/english/embeddings/alba.safetensors"], "fra": ["PocketTTS-GGUF/french/pocket-tts-french-q8_0.gguf", "PocketTTS-GGUF/french/embeddings/cosette.safetensors"], "deu": ["PocketTTS-GGUF/german/pocket-tts-german-q8_0.gguf"], "ita": ["PocketTTS-GGUF/italian/pocket-tts-italian-q8_0.gguf"], "por": ["PocketTTS-GGUF/portuguese/pocket-tts-portuguese-q8_0.gguf"], "spa": ["PocketTTS-GGUF/spanish/pocket-tts-spanish-q8_0.gguf"]}}),
        ("bf16", ["PocketTTS-GGUF/english/pocket-tts-english-bf16.gguf", "PocketTTS-GGUF/english/embeddings/alba.safetensors"], {"files_by_language": {"eng": ["PocketTTS-GGUF/english/pocket-tts-english-bf16.gguf", "PocketTTS-GGUF/english/embeddings/alba.safetensors"], "fra": ["PocketTTS-GGUF/french/pocket-tts-french-bf16.gguf", "PocketTTS-GGUF/french/embeddings/cosette.safetensors"], "deu": ["PocketTTS-GGUF/german/pocket-tts-german-bf16.gguf"], "ita": ["PocketTTS-GGUF/italian/pocket-tts-italian-bf16.gguf"], "por": ["PocketTTS-GGUF/portuguese/pocket-tts-portuguese-bf16.gguf"], "spa": ["PocketTTS-GGUF/spanish/pocket-tts-spanish-bf16.gguf"]}})
    ],
    TTS_ENGINES['QWEN3_TTS']: [("internal", ["Qwen3-TTS-12Hz-1.7B-Base-GGUF/qwen3-tts-12hz-1.7b-base-q8_0_v2.gguf"]), ("bf16", ["Qwen3-TTS-12Hz-1.7B-Base-GGUF/qwen3-tts-12hz-1.7b-base-bf16.gguf"]), ("0_6b", ["Qwen3-TTS-12Hz-0.6B-Base-GGUF/qwen3-tts-12hz-0.6b-base-q8_0.gguf"]), ("0_6b_bf16", ["Qwen3-TTS-12Hz-0.6B-Base-GGUF/qwen3-tts-12hz-0.6b-base-bf16.gguf"])],
    TTS_ENGINES['SUPERTONIC']: [("internal", ["Supertonic-3-GGUF/supertonic-3-orig.gguf"]), ("q8_0", ["Supertonic-3-GGUF/supertonic-3-q8_0.gguf"]), ("f16", ["Supertonic-3-GGUF/supertonic-3-f16.gguf"])],
    TTS_ENGINES['VIBEVOICE']: [("internal", ["VibeVoice-1.5B-GGUF/vibevoice-1.5b-q8_0.gguf"]), ("bf16", ["VibeVoice-1.5B-GGUF/vibevoice-1.5b-bf16.gguf"]), ("7b", ["vibevoice-7b-q8_0.gguf"], {"repo": "audio-cpp/VibeVoice-7B-GGUF"})],
    TTS_ENGINES['VOXCPM2']: [("internal", ["VoxCPM2-GGUF/voxcpm2-q8_0.gguf"]), ("bf16", ["VoxCPM2-GGUF/voxcpm2-bf16.gguf"]), ("orig", ["VoxCPM2-GGUF/voxcpm2-orig.gguf"])],
    TTS_ENGINES['VOXTRAL_TTS']: [("internal", ["Voxtral-4B-TTS-2603-GGUF/voxtral-4b-tts-2603-bf16.gguf"]), ("q8_0", ["Voxtral-4B-TTS-2603-GGUF/voxtral-4b-tts-2603-q8_0.gguf"])]
}
models = {
    engine: {
        name: {
            "lang": None if extra[0].get("languages") else "multi",
            "repo": audiocpp_repo,
            "sub": "",
            "file": files[0],
            "files": files,
            "voice": default_engine_settings[engine]['voice'],
            "samplerate": default_engine_settings[engine]['samplerate'],
            **extra[0]
        }
        for name, files, *extra in [(*preset, {}) if len(preset) == 2 else preset for preset in presets]
    }
    for engine, presets in packages.items()
}
