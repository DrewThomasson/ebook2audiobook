from lib.conf_models import TTS_ENGINES, default_engine_settings

# F5-TTS checkpoints per language: the official v1 base (zh & en) and the community models of upstream's
# src/f5_tts/infer/SHARED.md. repo / ckpt / vocab are Hugging Face paths, arch the DiT config the checkpoint was
# trained with (SHARED.md "Config": the v1 family keeps DiT's own defaults, the v0 family sets text_mask_padding False
# and pe_attn_head 1). All of them decode with the vocos-mel-24khz vocoder and read text through upstream's own
# frontend (kanji to pinyin included, which is how the Japanese model was trained: its vocab holds pinyin + kana).
# Optional per checkpoint: ema False = the checkpoint's raw weights (model_state_dict) instead of its EMA ones,
# tashkeel True = Arabic text diacritized before synthesis, ref_max = reference window in s (else the engine's),
# habibi = Habibi-TTS text format (dialect id of the Unified model, "none" for the specialized ones).
# Keep the keys in sync with default_engine_settings[TTS_ENGINES['F5TTS']]['languages'].
f5tts_v1_base = {"dim": 1024, "depth": 22, "heads": 16, "ff_mult": 2, "text_dim": 512, "conv_layers": 4}
f5tts_v1_small = {"dim": 768, "depth": 18, "heads": 12, "ff_mult": 2, "text_dim": 512, "conv_layers": 4}
f5tts_v0_base = {"dim": 1024, "depth": 22, "heads": 16, "ff_mult": 2, "text_dim": 512, "text_mask_padding": False, "conv_layers": 4, "pe_attn_head": 1}
f5tts_v0_small = {"dim": 768, "depth": 18, "heads": 12, "ff_mult": 2, "text_dim": 512, "text_mask_padding": False, "conv_layers": 4, "pe_attn_head": 1}
# Habibi-TTS (SWivid, the F5-TTS authors): F5TTS_v1_Base fine-tuned on Arabic dialects. The Unified model takes a dialect
# id (UNK = the reference voice's dialect, upstream's default), the specialized single-dialect ones (stronger accent,
# checkpoint step per dialect) take none
habibi_unified = {"repo": "SWivid/Habibi-TTS", "ckpt": "Unified/model_200000.safetensors", "vocab": "Unified/vocab.txt", "arch": f5tts_v1_base}
habibi_specialized = {"MSA": 200000, "SAU": 200000, "UAE": 100000, "ALG": 100000, "IRQ": 100000, "EGY": 100000, "MAR": 100000}
habibi_dialects = ("MSA", "SAU", "UAE", "ALG", "IRQ", "EGY", "MAR", "OMN", "TUN", "LEV", "SDN", "LBY")

checkpoints = {
    "eng": {"repo": "SWivid/F5-TTS", "ckpt": "F5TTS_v1_Base/model_1250000.safetensors", "vocab": "F5TTS_v1_Base/vocab.txt", "arch": f5tts_v1_base},
    "zho": {"repo": "SWivid/F5-TTS", "ckpt": "F5TTS_v1_Base/model_1250000.safetensors", "vocab": "F5TTS_v1_Base/vocab.txt", "arch": f5tts_v1_base},
    "fra": {"repo": "RASPIAUDIO/F5-French-MixedSpeakers-reduced", "ckpt": "model_last_reduced.pt", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    "deu": {"repo": "hvoss-techfak/F5-TTS-German", "ckpt": "model_f5tts_german.pt", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    "ita": {"repo": "alien79/F5-TTS-italian", "ckpt": "model_159600.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    "rus": {"repo": "hotstone228/F5-TTS-Russian", "ckpt": "model_last.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    # SHARED.md gives no config line for it: fine-tuned from the v0 base (model_1200000, before v1 existed)
    "spa": {"repo": "jpgallegoar/F5-Spanish", "ckpt": "model_1200000.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    "fin": {"repo": "AsmoKoskinen/F5-TTS_Finnish_Model", "ckpt": "model_common_voice_fi_vox_populi_fi_20241206.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_base},
    "hin": {"repo": "SPRINGLab/F5-Hindi-24KHz", "ckpt": "model_2500000.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_small},
    # full training checkpoint (5.4 GB): the worker keeps its EMA weights only
    "jpn": {"repo": "Jmica/F5TTS", "ckpt": "JA_21999120/model_21999120.pt", "vocab": "JA_21999120/vocab_japanese.txt", "arch": f5tts_v0_base},
    "ara": {**habibi_unified, "habibi": "UNK"},
    "lav": {"repo": "RaivisDejus/F5-TTS-Latvian", "ckpt": "model.safetensors", "vocab": "vocab.txt", "arch": f5tts_v0_base}
}

# SILMA TTS v1 (ar & en, F5-TTS 1.1.7 compatible, config.yaml of the repo): its own inference uses the raw weights,
# diacritizes Arabic text (CATT) and cuts references at 8 s
silma = {"repo": "silma-ai/silma-tts", "ckpt": "model.pt", "vocab": "vocab.txt", "arch": f5tts_v1_small, "ema": False, "tashkeel": True, "ref_max": 8.05}

models = {
    "internal": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['F5TTS']]['repo'],
        "sub": "",
        "checkpoints": checkpoints,
        "voice": default_engine_settings[TTS_ENGINES['F5TTS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['F5TTS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['F5TTS']]['samplerate']
    },
    # Arabic only: Habibi's Unified model with each dialect id, its specialized checkpoints, and SILMA
    **{
        name: {
            "lang": "ara",
            "repo": checkpoint['repo'],
            "sub": "",
            "checkpoints": {"ara": checkpoint},
            "voice": default_engine_settings[TTS_ENGINES['F5TTS']]['voice'],
            "files": default_engine_settings[TTS_ENGINES['F5TTS']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['F5TTS']]['samplerate']
        }
        for name, checkpoint in
        [(dialect.lower(), {**habibi_unified, "habibi": dialect}) for dialect in habibi_dialects]
        + [(f"{dialect.lower()}_specialized", {"repo": "SWivid/Habibi-TTS", "ckpt": f"Specialized/{dialect}/model_{step}.safetensors", "vocab": f"Specialized/{dialect}/vocab.txt", "arch": f5tts_v1_base, "habibi": "none"}) for dialect, step in habibi_specialized.items()]
        + [("silma", silma)]
    }
}
