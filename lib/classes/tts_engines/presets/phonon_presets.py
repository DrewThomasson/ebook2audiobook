from lib.conf_models import TTS_ENGINES, default_engine_settings

# Phonon checkpoints per language (gradium, Hugging Face): English is Phonon 31m (Apache 2.0, public), the others the
# per-language Phonon 40m (CC BY-NC 4.0, gated with auto-approved conditions: the account of e2a's HF_TOKEN accepts them
# once). Voices: gradium/phonon-voices catalog ids (embeddings, no cloning) -> (id, gender), upstream's order; the first of
# a gender is the built-in voice a voice file of that gender is converted from, gender None is never picked for it.
# Keep the keys in sync with default_engine_settings[TTS_ENGINES['PHONON']]['languages'].
checkpoints = {
    "eng": {"repo": "gradium/phonon-31m-en", "voices": {
        # en-us
        "zoey": ("NbpkqMVS3CJeq2j8", "female"), "juniper": ("NIWIOv5vTi5eRMj8", "female"), "everly": ("vjFyp2BcCyTlUmYb", "female"),
        "harper": ("4SZHfMpw-p46Ywgs", "female"), "hadley": ("bXwrkHhURL1VFJdG", "female"), "delia": ("nGzMHMPAWGaJFHOo", "female"),
        "easton": ("LMDIYE0Oa377Qh6Z", "male"), "micah": ("40QrMVgAxFiUnP9f", "male"), "trevor": ("0zLApsZfVLLNaEGl", "male"),
        "russell": ("_6Aslh2DxfmnRLmP", "male"), "preston": ("qIxlZ7Ei8KvWlyQH", "male"), "miles": ("d9XCyhjo4JhkHF1d", "male"),
        # en-gb
        "maeve": ("6PWnV0Nq4wu7RVBT", "female"), "freya": ("GgfEkEJtxZR7gnpy", "female"), "pippa": ("uem82D50GRv2Dwma", "female"),
        "elodie_rose": ("y9bQqIDnyxwqK01t", "female"), "imogen": ("gDT1nz7Ie36ZhL-C", "female"), "lottie": ("m9MxpY6IUGXtWp76", "female"),
        "bryony": ("gfP44RlHwr2kEwk7", "female"), "alfie": ("X6NceqF285Gr04gb", "male"), "hugh": ("YyKcxPG7iIgS3jsK", "male"),
        "edwin": ("zUCxzrOrugTSis03", "male"), "spencer": ("JOW0vchyswkQUMDS", "male"), "toby": ("dME3IWyZBvmh1n1q", "male"),
        "teddy": ("Zn7g6NxLqXlJb7Qi", "male"),
        # character voices (Gradium Voice Design)
        "captain_silas_blackwater": ("xPDpsV3F592srkjA", None), "morwenna_of_the_deep": ("nOykTmcH9ydsGGIc", None),
        "old_mortlake": ("lX3LavMNdlIbgEHH", None), "azgorath": ("dGyGDKo2osj7h3s7", None), "fennick_the_young_elf": ("cXoIXJ2llS8S0WOW", None),
        "the_thing_under_the_stairs": ("GXaSqMEmOg12OIYb", None), "vyrmathrax_the_ancient": ("xO8xQo3BrB8FuI6J", None),
        "grub_the_ogre": ("cYtsRSxV5q9IMehn", None), "master_aldric": ("gSgG5Tor0GPEnqzC", None), "the_snow_queen": ("NIWoEurJHMJjyUTe", None),
        "sir_bramwell": ("y2eiKxtQo2B67deU", None), "fairy_godmother": ("QXNr0SvkukLB4wPq", None)
    }},
    "fra": {"repo": "gradium/phonon-40m-fr", "voices": {
        "noemie": ("FXxJ9mANRq6BCTX5", "female"), "coralie": ("ZeSg853xFACESHHI", "female"), "tiphaine": ("0fvH6XAKvA748v2v", "female"),
        "maelys": ("s048cR1l2Jmu4k3B", "female"), "orianne": ("TUk4X11S6UytB3G6", "female"), "solene": ("YhIHaAfQ0cQPDV9R", "female"),
        "ninon": ("qtPlUYAZ4EJDuWMm", "female"), "lilou": ("4iKxBtHBRzr1YOph", "female"), "helene": ("Vvakv7iWZCUrBooR", "female"),
        "augustin": ("Tek4tJXiX6_yvXq7", "male"), "arnaud": ("aXMVwiUhITMrwPzd", "male"), "jules": ("YKeBw3OV1RgpdhLh", "male"),
        "baptiste": ("rqqeErpASHVQXHDd", "male"), "lucien": ("LIv4NaG8ay4Mhqtd", "male"), "marius": ("biuhvu17TxVKOcyy", "male")
    }},
    "deu": {"repo": "gradium/phonon-40m-de", "voices": {
        "nele": ("2A2fFf8SkDEJ8nzx", "female"), "jette": ("4Mn9VfG2wsLLEzi5", "female"), "annika": ("p6Uutkyi3j2iNAUu", "female"),
        "jule": ("MxhgvuHuUER7qjmL", "female"), "lotta": ("MOrDPn052KUlnKXk", "female"), "josefine": ("yadpmqsHVrYC0NJp", "female"),
        "svea": ("Adoh4wA9tp5QXJi9", "female"), "anton": ("3ZKKapPOvuWFcw9f", "male"), "mirko": ("Xn9xDzqSSr4xGTNg", "male"),
        "mats": ("Kf5m22mROozoMWj3", "male"), "henrik": ("yyS1KYWs6mXoEw7D", "male"), "leon": ("20zdyYrQPzKlCwkk", "male"),
        "mika": ("R3uU1GTAZJotUhUs", "male")
    }},
    "spa": {"repo": "gradium/phonon-40m-es", "voices": {
        # es-es
        "noa": ("b6FvJAiokjdqIti4", "female"), "lucia_sol": ("3p0eIGbkmny71GlA", "female"), "candela": ("c9wqBDmQiBie5q6Y", "female"),
        "celia": ("rmLBOdHrfkFym9MM", "female"), "alba": ("u2UscyAnHilpiwmf", "female"), "alicia": ("4701YgRXjkBcg6sL", "female"),
        "nerea": ("EQcQFGkYfMn5YJgx", "female"), "marcos": ("jvPx8j8zLGQ3utZz", "male"), "borja": ("tIjCgP8v3RY8UpgM", "male"),
        "iker": ("t-_TS1e-0GzDAX02", "male"), "nuno": ("fghJGlv90qu8OJ36", "male"), "izan": ("Ejb29qHnSOK0cIHY", "male"),
        "guillermo": ("FaLVVqpFQcDOtq45", "male"),
        # es-mx
        "rebeca": ("Sx8m6WdXBG06zwZT", "female"), "regina": ("s58clrg2fe0MO7Y-", "female"), "danae": ("evfxKSxpDIhmsNoq", "female"),
        "azucena": ("KJpIQlbYrZPA4aLq", "female"), "jimena": ("qG5BXOJYrKEnXLIX", "female"), "ximena": ("VDwnGxAo68C8U8vC", "female"),
        "lalo": ("F05gqkzX7WhKVpSL", "male"), "aldo": ("ax7dW1XB0eiMfHgO", "male"), "yael": ("ALczEazoF4n6PmGl", "male"),
        "ulises": ("G5HLUsQd659UtRe7", "male"), "leonel": ("BkuASiOJRrJEB5qA", "male"), "nico": ("PwgPEaweQILZdGc4", "male")
    }},
    "por": {"repo": "gradium/phonon-40m-pt", "voices": {
        # pt-br
        "manuela_lu": ("KgC2Nqnjj48NUiyV", "female"), "isadora": ("CtNvKUUMrx1h56ih", "female"), "debora": ("K8mj96kYHMy8q3Hb", "female"),
        "rafaela": ("6k6cRt7QJfm5ChrH", "female"), "clarice": ("sGCMzFIA53ppIngM", "female"), "flavia": ("gOc90Rjmv5CobHCj", "female"),
        "davi": ("NuUr_x5V90hSHzCJ", "male"), "igor": ("l7520SIXi14iEamd", "male"), "kaua": ("6HftnVU1XqVBJS8t", "male"),
        "vitor": ("mWgyMRkFED70QxQv", "male"), "otavio": ("JYtmeaysoaR0Wybf", "male"), "marcelo": ("qDeAnE4L4bk0BRz1", "male")
    }}
}

models = {
    # each language's own checkpoint and its default voice; a voice file picks a same-gender catalog voice
    "internal": {
        "lang": "multi",
        "repo": checkpoints['eng']['repo'],
        "sub": "",
        "checkpoints": checkpoints,
        "speaker": None,
        "voice": default_engine_settings[TTS_ENGINES['PHONON']]['voice'],
        "files": default_engine_settings[TTS_ENGINES['PHONON']]['files'],
        "samplerate": default_engine_settings[TTS_ENGINES['PHONON']]['samplerate']
    },
    # one preset per catalog voice, listed for its language only: that voice, also as the source of a voice file
    **{
        name: {
            "lang": None,
            "languages": {lang: default_engine_settings[TTS_ENGINES['PHONON']]['languages'][lang]},
            "repo": checkpoint['repo'],
            "sub": "",
            "checkpoints": {lang: checkpoint},
            "speaker": name,
            "voice": default_engine_settings[TTS_ENGINES['PHONON']]['voice'],
            "files": default_engine_settings[TTS_ENGINES['PHONON']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['PHONON']]['samplerate']
        }
        for lang, checkpoint in checkpoints.items()
        for name in checkpoint['voices']
    }
}
