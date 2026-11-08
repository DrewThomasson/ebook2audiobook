from lib.conf_models import TTS_ENGINES, default_engine_settings

# Orpheus fine-tuned checkpoints per language: English (ungated copy of canopylabs/orpheus-3b-0.1-ft) and the
# multilingual research release (canopylabs, gated: HF_TOKEN of an account that accepted their conditions). Spanish and
# Italian share one checkpoint. Speakers in upstream's order (English: conversational realism), the first one is the
# language's default; gender picks the built-in speaker a voice file is converted from (None: unknown, never picked
# for it). The speaker is a name written into the prompt, not an embedding.
# Keep the keys in sync with default_engine_settings[TTS_ENGINES['ORPHEUS']]['languages'].
checkpoints = {
    "eng": {"repo": "unsloth/orpheus-3b-0.1-ft", "speakers": {"tara": "female", "leah": "female", "jess": "female", "leo": "male", "dan": "male", "mia": "female", "zac": "male", "zoe": "female"}},
    "fra": {"repo": "canopylabs/3b-fr-ft-research_release", "speakers": {"pierre": "male", "amelie": "female", "marie": "female"}},
    "deu": {"repo": "canopylabs/3b-de-ft-research_release", "speakers": {"jana": "female", "thomas": "male", "max": "male"}},
    "kor": {"repo": "canopylabs/3b-ko-ft-research_release", "speakers": {"유나": "female", "준서": "male"}},
    "hin": {"repo": "canopylabs/3b-hi-ft-research_release", "speakers": {"ऋतिका": "female"}},
    "zho": {"repo": "canopylabs/3b-zh-ft-research_release", "speakers": {"长乐": None, "白芷": None}},
    "spa": {"repo": "canopylabs/3b-es_it-ft-research_release", "speakers": {"javi": "male", "sergio": "male", "maria": "female"}},
    "ita": {"repo": "canopylabs/3b-es_it-ft-research_release", "speakers": {"pietro": "male", "giulia": "female", "carlo": "male"}}
}

# preset names (fine_tuned, also the CLI value) for the speakers not written in latin letters
romanized = {"유나": "yuna", "준서": "junseo", "ऋतिका": "ritika", "长乐": "changle", "白芷": "baizhi"}

models = {
    # each language's own checkpoint and default speaker; a voice file picks a same-gender speaker
    "internal": {
        "lang": "multi",
        "repo": default_engine_settings[TTS_ENGINES['ORPHEUS']]['repo'],
        "sub": "",
        "checkpoints": checkpoints,
        "speaker": None,
        "voice": default_engine_settings[TTS_ENGINES['ORPHEUS']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['ORPHEUS']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['ORPHEUS']]['samplerate']
    },
    # one preset per built-in speaker, listed for its language only: that speaker, also as the source of a voice file
    **{
        romanized.get(speaker, speaker): {
            "lang": None,
            "languages": {lang: default_engine_settings[TTS_ENGINES['ORPHEUS']]['languages'][lang]},
            "repo": checkpoint['repo'],
            "sub": "",
            "checkpoints": {lang: checkpoint},
            "speaker": speaker,
            "voice": default_engine_settings[TTS_ENGINES['ORPHEUS']]['voice'],
            "files": default_engine_settings[TTS_ENGINES['ORPHEUS']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['ORPHEUS']]['samplerate']
        }
        for lang, checkpoint in checkpoints.items()
        for speaker in checkpoint['speakers']
    }
}
