from lib.conf_models import TTS_ENGINES, default_engine_settings

# OpenVoice V2 base speakers: one MeloTTS checkpoint per language (myshell-ai/MeloTTS-*), each with the speakers its
# config.json spk2id names, the first one is the language's default. A voice file is cloned onto the speaker's output by
# OpenVoice's ToneColorConverter, from that speaker's own tone color embedding (OpenVoiceV2 base_speakers/ses/<speaker>.pth,
# named as upstream's demo_part3 does: lowercase, _ as -). English defaults to MeloTTS' newest English model; the five
# accents of its first English model are speaker presets.
# Keep the keys in sync with default_engine_settings[TTS_ENGINES['OPENVOICE']]['languages'].
checkpoints = {
    "eng": {"repo": "myshell-ai/MeloTTS-English-v3", "speakers": ["EN-Newest"]},
    "spa": {"repo": "myshell-ai/MeloTTS-Spanish", "speakers": ["ES"]},
    "fra": {"repo": "myshell-ai/MeloTTS-French", "speakers": ["FR"]},
    "zho": {"repo": "myshell-ai/MeloTTS-Chinese", "speakers": ["ZH"]},
    "jpn": {"repo": "myshell-ai/MeloTTS-Japanese", "speakers": ["JP"]},
    "kor": {"repo": "myshell-ai/MeloTTS-Korean", "speakers": ["KR"]}
}

# MeloTTS' first English model: American, British, Indian, Australian and default accents
english_accents = {"repo": "myshell-ai/MeloTTS-English", "speakers": ["EN-Default", "EN-US", "EN-BR", "EN_INDIA", "EN-AU"]}

models = {
    # each language's own checkpoint and default speaker; a voice file is cloned onto it
    "internal": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['OPENVOICE']]['repo'],
        "sub": "",
        "checkpoints": checkpoints,
        "speaker": None,
        "voice": default_engine_settings[TTS_ENGINES['OPENVOICE']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['OPENVOICE']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['OPENVOICE']]['samplerate']
    },
    # one preset per base speaker, listed for its language only: that speaker, also as the source of a voice file
    **{
        speaker.lower().replace('_', '-'): {
            "lang": None,
            "languages": {lang: default_engine_settings[TTS_ENGINES['OPENVOICE']]['languages'][lang]},
            "repo": checkpoint['repo'],
            "sub": "",
            "checkpoints": {lang: checkpoint},
            "speaker": speaker,
            "voice": default_engine_settings[TTS_ENGINES['OPENVOICE']]['voice'],
            "files": default_engine_settings[TTS_ENGINES['OPENVOICE']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['OPENVOICE']]['samplerate']
        }
        for lang, checkpoint in list(checkpoints.items()) + [("eng", english_accents)]
        for speaker in checkpoint['speakers']
    }
}
