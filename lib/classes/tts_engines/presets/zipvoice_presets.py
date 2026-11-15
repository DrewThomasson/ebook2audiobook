from lib.conf_models import TTS_ENGINES, default_engine_settings

# ZipVoice checkpoints per language: k2-fsa's own (zh & en) and the community fine-tunes on Hugging Face that keep its
# architecture (123M params, 24 kHz 100-bin Vocos mels, so every vocoder below decodes every one of them).
# repo / ckpt / config / tokens are Hugging Face paths; config (model.json) and tokens (tokens.txt) come from
# assets_repo when the checkpoint ships without them (fine-tunes of the base model keep its config and token table).
# model: "zipvoice" (flow matching with classifier-free guidance, 2 passes a step) or "zipvoice_distill" (guidance as an
# input embedding, 1 pass a step, 4 to 8 steps).
# tokenizer: "emilia" (English through espeak-ng en-us + Chinese through pinyin, by script), "espeak" (espeak-ng voice
# lang, IPA tokens), "simple" (characters); lowercase: the character table has no capitals.
# onnx: {"text_encoder", "fm_decoder"} instead of ckpt, for releases that only ship k2-fsa's ONNX export (run on cpu by
# onnxruntime, whatever the device). prefix: key prefix of the weights to strip (a transformers wrapper's "model.").
# fallback: the checkpoint used instead when a gated repo refuses the download (HF_TOKEN's account did not accept it).
# Optional sampling defaults of the checkpoint (else the engine's): num_step, guidance_scale, t_shift; speed_factor
# multiplies the speed; short_text = ViZipVoice's slower speech on 1 to 4 word sentences; ref_max = reference window (s).
# Keep the internal keys in sync with default_engine_settings[TTS_ENGINES['ZIPVOICE']]['languages'].
zipvoice_base = {"repo": "k2-fsa/ZipVoice", "ckpt": "zipvoice/model.safetensors", "config": "zipvoice/model.json", "tokens": "zipvoice/tokens.txt", "model": "zipvoice", "tokenizer": "emilia"}
# LuxTTS' acoustic model is this file byte for byte (YatharthS/LuxTTS model.pt, same sha256): its sampler is upstream's
# Euler written another way, so only its sampling settings and its 48 kHz vocoder make LuxTTS
zipvoice_distill = {"repo": "k2-fsa/ZipVoice", "ckpt": "zipvoice_distill/model.safetensors", "config": "zipvoice_distill/model.json", "tokens": "zipvoice_distill/tokens.txt", "model": "zipvoice_distill", "tokenizer": "emilia", "num_step": 8, "guidance_scale": 3.0}
# LuxTTS' own settings (README "Inference with sampling params" and luxvoice.py: speed x1.3 inside generate())
luxtts = {**zipvoice_distill, "num_step": 4, "t_shift": 0.9, "speed_factor": 1.3}
# karim1993: Arabic (395 h: Common Voice, ArVoice, MGB2) and Serbian (CLARIN 11356/1834 + 11356/1679), each with its
# distilled model; espeak-ng tokens in the base token table
arabic_base = {"repo": "karim1993/zipvoice-ar-finetuned", "ckpt": "zipvoice_ar/epoch-26-avg-4.pt", "config": "zipvoice_ar/model.json", "tokens": "zipvoice_ar/tokens.txt", "model": "zipvoice", "tokenizer": "espeak", "lang": "ar"}
arabic_distill = {"repo": "karim1993/zipvoice-ar-finetuned", "ckpt": "zipvoice_distill_ar/checkpoint-2000.pt", "config": "zipvoice_distill_ar/model.json", "tokens": "zipvoice_distill_ar/tokens.txt", "model": "zipvoice_distill", "tokenizer": "espeak", "lang": "ar", "num_step": 8, "guidance_scale": 3.0}
serbian_base = {"repo": "karim1993/zipvoice-sr-finetuned", "ckpt": "zipvoice_sr/epoch-15-avg-4.safetensors", "config": "zipvoice_sr/model.json", "tokens": "zipvoice_sr/tokens.txt", "model": "zipvoice", "tokenizer": "espeak", "lang": "sr"}
serbian_distill = {"repo": "karim1993/zipvoice-sr-finetuned", "ckpt": "zipvoice_distill_sr/checkpoint-2000.safetensors", "config": "zipvoice_distill_sr/model.json", "tokens": "zipvoice_distill_sr/tokens.txt", "model": "zipvoice_distill", "tokenizer": "espeak", "lang": "sr", "num_step": 8, "guidance_scale": 3.0}
# DhVaani-0.5 (ARTPARK-IISc, 27 Indic languages + English, cased character tokens read as they are): upstream's model
# code (its bundled _backend only trims the tokenizer and the lhotse-free mel extractor, same output), weights under its
# transformers wrapper's "model.". The repo is gated: when HF_TOKEN's account has not accepted it, its ungated ONNX export
# (same tokens.txt / model.json; k2-fsa's export format, fp32: the int8 one trades quality for size) runs on cpu instead
dhvaani_onnx = {"repo": "Bbkblo/DhVaani-0.5-ONNX", "onnx": {"text_encoder": "text_encoder.onnx", "fm_decoder": "fm_decoder.onnx"}, "config": "model.json", "tokens": "tokens.txt", "model": "zipvoice", "tokenizer": "simple"}
dhvaani = {"repo": "ARTPARK-IISc/DhVaani-0.5", "ckpt": "model.safetensors", "prefix": "model.", "config": "model.json", "tokens": "tokens.txt", "model": "zipvoice", "tokenizer": "simple", "fallback": dhvaani_onnx}
# DhVaani's languages (its model card) -> e2a's iso-639-3 codes: Dogri as dgo, Konkani as gom, Nepali as npi, Odia as ory
# (Rajasthani has no e2a code)
dhvaani_languages = ("asm", "ben", "brx", "dgo", "guj", "hin", "hne", "bho", "kan", "kas", "gom", "mai", "mag", "mal", "mni", "mar", "npi", "ory", "pan", "san", "sat", "snd", "tam", "tel", "urd")
# ViZipVoice (contextboxai, ~6500 h Vietnamese + 500 h English, character tokens with capitals, fp16 state dict)
vizipvoice = {"repo": "contextboxai/ViZipvoice", "ckpt": "checkpoint-1860000.pt", "config": "model.json", "tokens": "tokens.txt", "model": "zipvoice", "tokenizer": "simple", "short_text": True}

checkpoints = {
    "eng": zipvoice_base,
    "zho": zipvoice_base,
    "ara": arabic_base,
    "srp": serbian_base,
    # ErikUPV's Catalan fine-tune (Common Voice 17, cleaned): the checkpoint alone, config and tokens are the base
    # model's; its evaluation ran 25 steps
    "cat": {"repo": "ebellob/ZipVoice-CA", "ckpt": "zipvoice_ca.pt", "assets_repo": "k2-fsa/ZipVoice", "config": "zipvoice/model.json", "tokens": "zipvoice/tokens.txt", "model": "zipvoice", "tokenizer": "espeak", "lang": "ca", "num_step": 25},
    # hynt: 2500 h (PhoAudioBook, ViVoice, TeacherDinh-UEH), espeak-ng vi; its config is named config.json
    "vie": {"repo": "hynt/ZipVoice-Vietnamese-2500h", "ckpt": "iter-525000-avg-2.pt", "config": "config.json", "tokens": "tokens.txt", "model": "zipvoice", "tokenizer": "espeak", "lang": "vi"},
    # fav-kky (University of West Bohemia): trained from scratch on ParlaSpeech-CZ (1100 h), lowercase characters
    "ces": {"repo": "fav-kky/ZipVoice", "ckpt": "zipvoice_cs_ParlaSpeech/model.pt", "config": "zipvoice_cs_ParlaSpeech/model.json", "tokens": "zipvoice_cs_ParlaSpeech/tokens.txt", "model": "zipvoice", "tokenizer": "simple", "lowercase": True},
    # TheBurgstall: base model fine-tuned on ~28 h of Finnish (CSS10 audiobook mixed in), a 1.8 GB training checkpoint
    # (the worker keeps its weights only); config and tokens are the base model's
    "fin": {"repo": "TheBurgstall/ZipVoice-Suomi-12k", "ckpt": "checkpoint-12000.pt", "assets_repo": "k2-fsa/ZipVoice", "config": "zipvoice/model.json", "tokens": "zipvoice/tokens.txt", "model": "zipvoice", "tokenizer": "espeak", "lang": "fi"},
    **{lang: dhvaani for lang in dhvaani_languages}
}

# distilled checkpoints: 8 steps, one pass each (~4x faster than the base models)
distilled = {"eng": zipvoice_distill, "zho": zipvoice_distill, "ara": arabic_distill, "srp": serbian_distill}

def preset(checkpoints:dict, vocoder:str, lang:str='multi')->dict:
    # lang "multi" lists the preset for every engine language; a preset for some languages only lists them in
    # "languages" (gradio shows it when the TTS language is one of them)
    return {
        "lang": lang,
        "languages": {} if lang == 'multi' else {key: default_engine_settings[TTS_ENGINES['ZIPVOICE']]['languages'][key] for key in checkpoints},
        "repo": default_engine_settings[TTS_ENGINES['ZIPVOICE']]['repo'],
        "sub": "",
        "checkpoints": checkpoints,
        "vocoder": vocoder,
        "voice": default_engine_settings[TTS_ENGINES['ZIPVOICE']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['ZIPVOICE']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['ZIPVOICE']]['vocoders'][vocoder]['samplerate']
    }

models = {
    # each language's checkpoint, upstream's 24 kHz Vocos (the vocoder every checkpoint was trained and evaluated with)
    "internal": preset(checkpoints, 'vocos'),
    # the same checkpoints through LuxTTS' 48 kHz vocoder (trained on English: the band under 4 kHz stays Vocos')
    "internal_48k": preset(checkpoints, 'lux48k'),
    "distill": preset(distilled, 'vocos', ''),
    # LuxTTS: the distilled model at 4 steps with its own settings and its 48 kHz vocoder (en & zh), and the other
    # distilled checkpoints through that vocoder
    "luxtts": preset({**distilled, "eng": luxtts, "zho": luxtts}, 'lux48k', ''),
    "vizipvoice": preset({"vie": vizipvoice}, 'vocos', 'vie')
}
