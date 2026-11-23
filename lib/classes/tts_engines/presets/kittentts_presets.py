import re
from lib.conf_models import TTS_ENGINES, default_engine_settings

# KittenTTS 2 models (KittenML, Hugging Face) and their built-in voices by e2a language, in upstream's order except the
# first one, the language's default (upstream's own default_voice for English, the voice named after the language where
# one exists, else a news anchor or presenter: plain read speech).
# kitten-tts-2 (Stellon Labs Community License): voices/voices.json, grouped by the language their name carries (the
# others are English). A voice file is cloned by the model itself, whatever the preset.
# Keep the keys in sync with default_engine_settings[TTS_ENGINES['KITTENTTS']]['languages'].
kitten2 = {
    "repo": "KittenML/kitten-tts-2",
    "voices": {
        "eng": ["Bruno", "AirportAnnouncer", "Alfred", "AudiobookNarratorFemale", "Bella", "BoredTeenager", "CalmHostageNegotiator", "Claire", "Dante", "Diana", "Dolores", "Edith", "Eleanor", "Elliot", "FairytaleNarratorWhimsical", "Frank", "Grace", "GrandmaBedtimeStory", "GriefEulogy", "Herbert", "Hugo", "Iris", "Jasper", "Julian", "Kiki", "Laurence", "Leo", "Luna", "Maeve", "Marcus", "Martha", "Matthew", "Miles", "NervousFirstDate", "NewsAnchorFemale", "Otis", "PilotCabinAnnouncement", "Raven", "Reginald", "Rosie", "Sable", "Saoirse", "SarcasticCoworker", "Serena", "Victor", "Victoria", "Vincent", "Walter", "WeatherPresenterCheerful", "Willow"],
        "ara": ["Arabic", "ArabicFalconer", "ArabicMother", "ArabicNews"],
        "zho": ["Chinese", "ChineseLivestreamSeller", "ChineseNewsCctv", "ChineseXianxiaMaster"],
        "nld": ["DutchWeatherPresenter", "DutchBaker", "DutchGrandpaStory"],
        "fra": ["French", "FrenchDocumentary", "FrenchGrandmereRecette", "FrenchTeacher", "FrenchWaiter"],
        "deu": ["German", "GermanKneipe", "GermanProfessor", "GermanTrainAnnouncement"],
        "hin": ["Hindi", "HindiBollywoodDrama", "HindiCollegeFriends", "HindiDadiKahani", "HindiYogaTeacher"],
        "ind": ["IndonesianNewsAnchor", "IndonesianTourGuide"],
        "ita": ["Italian", "ItalianFashionDesigner", "ItalianFootballFan", "ItalianGondolier", "ItalianNonnaKitchen", "ItalianOperaTenor"],
        "jpn": ["JapaneseGrandma", "JapaneseAnimeHeroine", "JapaneseSalarymanApology", "JapaneseTrainConductor"],
        "kor": ["KoreanNewsAnchor", "KoreanGrandpaAdvice", "KoreanKdramaConfession"],
        "pol": ["PolishNewsAnchor", "PolishBabciaPierogi", "PolishMountainGuide", "PolishPoetryStudent"],
        "por": ["Portuguese", "PortugueseBeach", "PortugueseBusiness", "PortugueseFado", "PortugueseGrandpaFarm", "PortugueseNewsAnchor"],
        "rus": ["Russian", "RussianBabushka", "RussianFairyTale", "RussianHockeyCheer", "RussianLiteratureTeacher", "RussianSpaceControl", "RussianTaxiDriver"],
        "spa": ["Spanish", "SpanishAbuela", "SpanishBreakupSad", "SpanishNews", "SpanishTango"],
        "tur": ["TurkishNewsAnchor", "TurkishFisherman", "TurkishGrandmaCooking"]
    }
}

# kitten-tts-2-mini / nano / pico (Apache 2.0): config.json voices per language, upstream's order (its first voice is the
# language's default). mini also lists the English character voices under the other European languages. A voice file
# converts the preset's voice with default_vc_model. mini's Japanese is left out: its G2P (misaki ja) needs pyopenjtalk,
# which has no wheel on any platform (a C++ build); kitten-tts-2 speaks Japanese.
tiny = {
    "mini": {
        "repo": "KittenML/kitten-tts-2-mini",
        "voices": {
            "eng": ["Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent", "Max", "Danny"],
            "deu": ["Lena", "Greta", "Jonas", "Felix", "Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent"],
            "spa": ["Lucia", "Carmen", "Javier", "Diego", "Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent"],
            "ita": ["Giulia", "Chiara", "Marco", "Luca", "Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent"],
            "por": ["Beatriz", "Camila", "Rafael", "Thiago", "Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent"],
            "rus": ["Anastasia", "Natasha", "Dmitri", "Ivan", "Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Diana", "Otis", "Vincent"],
            "hin": ["Priya", "Ananya", "Arjun", "Vikram"],
            "dan": ["Freja", "Mads", "Rasmus"],
            "fin": ["Aino", "Helmi", "Eero", "Juho", "Ville"],
            "fra": ["Camille", "Chloe", "Manon", "Louis", "Antoine", "Julien", "Mathis", "Etienne"],
            "kor": ["Seoyeon", "Minjun", "Jihoon"],
            "nld": ["Sanne", "Fenna", "Daan", "Bram", "Joris"],
            "swe": ["Astrid", "Elsa", "Oskar"],
            "swh": ["Zawadi", "Neema", "Baraka", "Juma"],
            "tur": ["Elif", "Zeynep"]
        }
    },
    "nano": {
        "repo": "KittenML/kitten-tts-2-nano",
        "voices": {
            "eng": ["Eleanor", "Martha", "Serena", "Iris", "Grace", "Edith", "Otis", "Vincent", "Max", "Danny"],
            "deu": ["Anna", "Mia", "Lukas", "Paul"],
            "spa": ["Sofia", "Elena", "Pablo", "Mateo"],
            "ita": ["Francesca", "Alessandro", "Giorgio", "Davide"],
            "por": ["Juliana", "Larissa", "Gustavo", "Caio"],
            "rus": ["Olga", "Tatiana", "Sergei", "Alexei"],
            "hin": ["Priya", "Ananya", "Arjun", "Vikram"],
            "fra": ["Juliette", "Gabriel", "Nicolas"]
        }
    },
    "pico": {
        "repo": "KittenML/kitten-tts-2-pico",
        "voices": {
            "eng": ["Eleanor", "Edith", "Otis", "Frank"],
            "deu": ["Anna", "Mia", "Lukas", "Paul"],
            "spa": ["Sofia", "Elena", "Pablo", "Mateo"],
            "ita": ["Francesca", "Alessandro", "Giorgio", "Davide"],
            "por": ["Juliana", "Larissa", "Gustavo", "Caio"],
            "rus": ["Olga", "Tatiana", "Sergei", "Alexei"],
            "hin": ["Priya", "Arjun"],
            "fra": ["Amelie", "Lea", "Theo", "Baptiste"]
        }
    }
}

# one model per (preset, language): "family" picks the worker's loader (kitten2: KittenTTS 2, tiny: mini / nano / pico),
# "speaker" the built-in voice it speaks with
def _checkpoint(family:str, repo:str, speaker:str)->dict:
    return {"family": family, "repo": repo, "speaker": speaker}

def _key(name:str)->str:
    # preset name (fine_tuned, also the CLI value): AudiobookNarratorFemale -> audiobook_narrator_female
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

_settings = default_engine_settings[TTS_ENGINES['KITTENTTS']]
_common = {
    "sub": "",
    "voice": _settings['voice'],
    "files": _settings['files'],
    "samplerate": _settings['samplerate']
}

models = {
    # kitten-tts-2 with each language's default voice; the languages it has no built-in voice for (Danish, Finnish,
    # Swedish, Swahili) speak with kitten-tts-2-mini's
    "internal": {
        "lang": "multi",
        "repo": kitten2['repo'],
        "checkpoints": {
            lang: _checkpoint("kitten2", kitten2['repo'], kitten2['voices'][lang][0]) if lang in kitten2['voices'] else _checkpoint("tiny", tiny['mini']['repo'], tiny['mini']['voices'][lang][0])
            for lang in _settings['languages']
        },
        **_common
    },
    # each small model with each of its languages' default voice, listed for its languages only
    **{
        family: {
            "lang": None,
            "languages": {lang: _settings['languages'][lang] for lang in cfg['voices']},
            "repo": cfg['repo'],
            "checkpoints": {lang: _checkpoint("tiny", cfg['repo'], voices[0]) for lang, voices in cfg['voices'].items()},
            **_common
        }
        for family, cfg in tiny.items()
    },
    # one preset per kitten-tts-2 built-in voice, listed for its language only
    **{
        _key(voice): {
            "lang": None,
            "languages": {lang: _settings['languages'][lang]},
            "repo": kitten2['repo'],
            "checkpoints": {lang: _checkpoint("kitten2", kitten2['repo'], voice)},
            **_common
        }
        for lang, voices in kitten2['voices'].items()
        for voice in voices
    },
    # one preset per small model voice (<model>_<voice>), listed for the languages it speaks
    **{
        f'{family}_{_key(voice)}': {
            "lang": None,
            "languages": {lang: _settings['languages'][lang] for lang, voices in cfg['voices'].items() if voice in voices},
            "repo": cfg['repo'],
            "checkpoints": {lang: _checkpoint("tiny", cfg['repo'], voice) for lang, voices in cfg['voices'].items() if voice in voices},
            **_common
        }
        for family, cfg in tiny.items()
        for voice in dict.fromkeys(v for voices in cfg['voices'].values() for v in voices)
    }
}
