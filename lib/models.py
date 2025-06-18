import os

from lib.conf import voices_dir
loaded_tts = {}

TTS_ENGINES = {
    "XTTSv2": "xtts", 
    "BARK": "bark", 
    "VITS": "vits", 
    "FAIRSEQ": "fairseq", 
    "TACOTRON2": "tacotron", 
    "YOURTTS": "yourtts"
}

default_tts_engine = TTS_ENGINES['XTTSv2']
default_fine_tuned = 'internal'

r"""
voice_conversion_models/multilingual/vctk/freevc24
voice_conversion_models/multilingual/multi-dataset/knnvc
voice_conversion_models/multilingual/multi-dataset/openvoice_v1
voice_conversion_models/multilingual/multi-dataset/openvoice_v2
"""
default_vc_model = "voice_conversion_models/multilingual/multi-dataset/knnvc"

max_tts_in_memory = 2 # TTS engines to keep in memory (1 tts engine ~= 4GB to 8GB RAM).
max_custom_model = 10
max_custom_voices = 100
max_upload_size = '6GB'

default_engine_settings = {
    TTS_ENGINES['XTTSv2']: {
        "samplerate": 24000,
        "temperature": 0.75,
        "length_penalty": 1.0,
        "num_beams": 1,
        "repetition_penalty": 3.0,
        "top_k": 50,
        "top_p": 0.85,
        "speed": 1.0,
        "enable_text_splitting": False,
        # to enable deepspeed, you must install it first:
        # conda activate ./python_env (linux/mac) or .\python_env (windows)
        # pip install deepspeed
        # conda deactivate
        "use_deepspeed": False,
        "files": ['config.json', 'model.pth', 'vocab.json', 'ref.wav', 'speakers_xtts.pth'],
        "voices": {
            "ClaribelDervla": "Claribel Dervla", "DaisyStudious": "Daisy Studious", "GracieWise": "Gracie Wise",
            "TammieEma": "Tammie Ema", "AlisonDietlinde": "Alison Dietlinde", "AnaFlorence": "Ana Florence",
            "AnnmarieNele": "Annmarie Nele", "AsyaAnara": "Asya Anara", "BrendaStern": "Brenda Stern",
            "GittaNikolina": "Gitta Nikolina", "HenrietteUsha": "Henriette Usha", "SofiaHellen": "Sofia Hellen",
            "TammyGrit": "Tammy Grit", "TanjaAdelina": "Tanja Adelina", "VjollcaJohnnie": "Vjollca Johnnie",
            "AndrewChipper": "Andrew Chipper", "BadrOdhiambo": "Badr Odhiambo", "DionisioSchuyler": "Dionisio Schuyler",
            "RoystonMin": "Royston Min", "ViktorEka": "Viktor Eka", "AbrahanMack": "Abrahan Mack",
            "AddeMichal": "Adde Michal", "BaldurSanjin": "Baldur Sanjin", "CraigGutsy": "Craig Gutsy",
            "DamienBlack": "Damien Black", "GilbertoMathias": "Gilberto Mathias", "IlkinUrbano": "Ilkin Urbano",
            "KazuhikoAtallah": "Kazuhiko Atallah", "LudvigMilivoj": "Ludvig Milivoj", "SuadQasim": "Suad Qasim",
            "TorcullDiarmuid": "Torcull Diarmuid", "ViktorMenelaos": "Viktor Menelaos", "ZacharieAimilios": "Zacharie Aimilios",
            "NovaHogarth": "Nova Hogarth", "MajaRuoho": "Maja Ruoho", "UtaObando": "Uta Obando",
            "LidiyaSzekeres": "Lidiya Szekeres", "ChandraMacFarland": "Chandra MacFarland", "SzofiGranger": "Szofi Granger",
            "CamillaHolmström": "Camilla Holmström", "LilyaStainthorpe": "Lilya Stainthorpe", "ZofijaKendrick": "Zofija Kendrick",
            "NarelleMoon": "Narelle Moon", "BarboraMacLean": "Barbora MacLean", "AlexandraHisakawa": "Alexandra Hisakawa",
            "AlmaMaría": "Alma María", "RosemaryOkafor": "Rosemary Okafor", "IgeBehringer": "Ige Behringer",
            "FilipTraverse": "Filip Traverse", "DamjanChapman": "Damjan Chapman", "WulfCarlevaro": "Wulf Carlevaro",
            "AaronDreschner": "Aaron Dreschner", "KumarDahl": "Kumar Dahl", "EugenioMataracı": "Eugenio Mataracı",
            "FerranSimen": "Ferran Simen", "XavierHayasaka": "Xavier Hayasaka", "LuisMoray": "Luis Moray",
            "MarcosRudaski": "Marcos Rudaski"
        },
        "rating": {"GPU VRAM": 4, "CPU": 3, "RAM": 8, "Emotions": 3}
    },
    TTS_ENGINES['BARK']: {
        "samplerate": 24000,
        "text_temp": 0.40,
        "waveform_temp": 0.40,
        "files": ["text_2.pt", "coarse_2.pt", "fine_2.pt"],
        "voices": {
            "ClaribelDervla": "Claribel Dervla", "DaisyStudious": "Daisy Studious", "GracieWise": "Gracie Wise",
            "TammieEma": "Tammie Ema", "AlisonDietlinde": "Alison Dietlinde", "AnaFlorence": "Ana Florence",
            "AnnmarieNele": "Annmarie Nele", "AsyaAnara": "Asya Anara", "BrendaStern": "Brenda Stern",
            "GittaNikolina": "Gitta Nikolina", "HenrietteUsha": "Henriette Usha", "SofiaHellen": "Sofia Hellen",
            "TammyGrit": "Tammy Grit", "TanjaAdelina": "Tanja Adelina", "VjollcaJohnnie": "Vjollca Johnnie",
            "AndrewChipper": "Andrew Chipper", "BadrOdhiambo": "Badr Odhiambo", "DionisioSchuyler": "Dionisio Schuyler",
            "RoystonMin": "Royston Min", "ViktorEka": "Viktor Eka", "AbrahanMack": "Abrahan Mack",
            "AddeMichal": "Adde Michal", "BaldurSanjin": "Baldur Sanjin", "CraigGutsy": "Craig Gutsy",
            "DamienBlack": "Damien Black", "GilbertoMathias": "Gilberto Mathias", "IlkinUrbano": "Ilkin Urbano",
            "KazuhikoAtallah": "Kazuhiko Atallah", "LudvigMilivoj": "Ludvig Milivoj", "SuadQasim": "Suad Qasim",
            "TorcullDiarmuid": "Torcull Diarmuid", "ViktorMenelaos": "Viktor Menelaos", "ZacharieAimilios": "Zacharie Aimilios",
            "NovaHogarth": "Nova Hogarth", "MajaRuoho": "Maja Ruoho", "UtaObando": "Uta Obando",
            "LidiyaSzekeres": "Lidiya Szekeres", "ChandraMacFarland": "Chandra MacFarland", "SzofiGranger": "Szofi Granger",
            "CamillaHolmström": "Camilla Holmström", "LilyaStainthorpe": "Lilya Stainthorpe", "ZofijaKendrick": "Zofija Kendrick",
            "NarelleMoon": "Narelle Moon", "BarboraMacLean": "Barbora MacLean", "AlexandraHisakawa": "Alexandra Hisakawa",
            "AlmaMaría": "Alma María", "RosemaryOkafor": "Rosemary Okafor", "IgeBehringer": "Ige Behringer",
            "FilipTraverse": "Filip Traverse", "DamjanChapman": "Damjan Chapman", "WulfCarlevaro": "Wulf Carlevaro",
            "AaronDreschner": "Aaron Dreschner", "KumarDahl": "Kumar Dahl", "EugenioMataracı": "Eugenio Mataracı",
            "FerranSimen": "Ferran Simen", "XavierHayasaka": "Xavier Hayasaka", "LuisMoray": "Luis Moray",
            "MarcosRudaski": "Marcos Rudaski"
        },
        "rating": {"GPU VRAM": 4, "CPU": 1, "RAM": 16, "Emotions": 4}
    },
    TTS_ENGINES['VITS']: {
        "samplerate": 22050,
        "files": ['config.json', 'model_file.pth', 'language_ids.json'],
        "voices": {},
        "rating": {"GPU VRAM": 2, "CPU": 3, "RAM": 4, "Emotions": 2}
    },
    TTS_ENGINES['FAIRSEQ']: {
        "samplerate": 16000,
        "files": ['config.json', 'G_100000.pth', 'vocab.json'],
        "voices": {},
        "rating": {"GPU VRAM": 2, "CPU": 3, "RAM": 4, "Emotions": 2}
    },
    TTS_ENGINES['TACOTRON2']: {
        "samplerate": 22050,
        "files": ['config.json', 'best_model.pth', 'vocoder_config.json', 'vocoder_model.pth'],
        "voices": {},
        "rating": {"GPU VRAM": 2, "CPU": 3, "RAM": 4, "Emotions": 2}
    },
    TTS_ENGINES['YOURTTS']: {
        "samplerate": 16000,
        "files": ['config.json', 'model_file.pth'],
        "voices": {"Machinella-5": "female-en-5", "ElectroMale-2": "male-en-2", 'Machinella-4': 'female-pt-4\n', 'ElectroMale-3': 'male-pt-3\n'},
        "rating": {"GPU VRAM": 1, "CPU": 5, "RAM": 4, "Emotions": 1}
    }
}
models = {
    TTS_ENGINES['XTTSv2']: {
        "internal": {
            "lang": "multi",
            "repo": "coqui/XTTS-v2",
            "sub": "tts_models/multilingual/multi-dataset/xtts_v2/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"KumarDahl_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"AiExplained_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "AsmrRacoon": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AsmrRacoon",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"AsmrRacoon_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobOdenkirk_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobRoss_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BrinaPalencia": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BrinaPalencia/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"BrinaPalencia_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BryanCranston_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"DavidAttenborough_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DeathPussInBoots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPussInBoots/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"DeathPussInBoots_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DermotCrowley": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DermotCrowley/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"DermotCrowley_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "EvaSeymour": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/EvaSeymour/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"EvaSeymour_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "GideonOfnirEldenRing": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GideonOfnirEldenRing/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"GideonOfnirEldenRing_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"GhostMW2_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JhonButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonButlerASMR/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"JhonButlerASMR_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JhonMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonMulaney/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"JhonMulaney_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JillRedfield": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JillRedfield/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"JillRedfield_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JuliaWhenlan": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JuliaWhenlan/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"JuliaWhenlan_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "LeeHorsley": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/LeeHorsley/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"LeeHorsley_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "MelinaEldenRing": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MelinaEldenRing/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"MelinaEldenRing_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"MorganFreeman_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "NeilGaiman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/NeilGaiman/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"NeilGaiman_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace/",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"RainyDayHeadSpace_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RayPorter": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RayPorter/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"RayPorter_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RelaxForAWhile": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RelaxForAWhile/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"RelaxForAWhile_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RosamundPike": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RosamundPike/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"RosamundPike_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "ScarlettJohansson": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/ScarlettJohansson/",
            "voice": os.path.join(voices_dir, "eng", "adult", "female", f"ScarlettJohansson_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "SladeTeenTitans": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/SladeTeenTitans/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"SladeTeenTitans_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "StanleyParable": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/StanleyParable/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"StanleyParable_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR/",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"WhisperSalemASMR_{default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        }
    },
    TTS_ENGINES['BARK']: {
        "internal": {
            "lang": "multi",
            "repo": "suno/bark", # rsxdalv/suno, tts_models/multilingual/multi-dataset/bark
            "sub": "", # {"big-bf16": "big-bf16/", "small-bf16": "small-bf16/", "big": "big/", "small": "small/"}
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"KumarDahl_{default_engine_settings[TTS_ENGINES['BARK']]['samplerate']}.wav"),
            "files": default_engine_settings[TTS_ENGINES['BARK']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['BARK']]['samplerate']
        }
    },
    TTS_ENGINES['VITS']: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang_iso1]/[xxx]",
            "sub": {
                "css10/vits": ['es','hu','fi','fr','nl','ru','el'],
                "custom/vits": ['ca'],
                "custom/vits-female": ['bn', 'fa'],
                "cv/vits": ['bg','cs','da','et','ga','hr','lt','lv','mt','pt','ro','sk','sl','sv'],
                "mai/vits": ['uk'],
                "mai_female/vits": ['pl'],
                "mai_male/vits": ['it'],
                "openbible/vits": ['ewe','hau','lin','tw_akuapem','tw_asante','yor'],
                "vctk/vits": ['en'],
                "thorsten/vits": ['de']
            },
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['VITS']]['files'],
            "samplerate": {
                "css10/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "custom/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "custom/vits-female": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "cv/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "mai/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "mai_female/vits": 24000,
                "mai_male/vits": 16000,
                "openbible/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "vctk/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate'],
                "thorsten/vits": default_engine_settings[TTS_ENGINES['VITS']]['samplerate']
            }
        }
    },
    TTS_ENGINES['FAIRSEQ']: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['FAIRSEQ']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['FAIRSEQ']]['samplerate']
        }
    },
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
    },
    TTS_ENGINES['YOURTTS']: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/your_tts",
            "sub": "",
            "voice": None,
            "files": default_engine_settings[TTS_ENGINES['YOURTTS']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['YOURTTS']]['samplerate']
        }
    }
}
