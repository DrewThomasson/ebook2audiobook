import os
from lib.conf import voices_dir

XTTSv2 = 'xtts'
BARK = 'bark'
VITS = 'vits'
FAIRSEQ = 'fairseq'
YOURTTS = 'yourtts'

default_tts_engine = 'xtts'
default_fine_tuned = 'internal'

default_xtts_settings = {
    "samplerate": 24000,
    "temperature": 0.75,
    "length_penalty": 1.0,
    "num_beams": 1,
    "repetition_penalty": 5.0,
    "top_k": 50,
    "top_p": 0.85,
    "speed": 1.0,
    "enable_text_splitting": False,
    # to enable_deepspeed, it must be installed manually.
    # conda activate [./python_env | .\python_env]
    # pip install deepspeed
    # conda deactivate
    "use_deepspeed": False
    "files": ['config.json', 'model.pth', 'vocab.json', 'ref.wav']
    "voices": {
        'ClaribelDervla': 'Claribel Dervla', 'DaisyStudious': 'Daisy Studious', 'GracieWise': 'Gracie Wise',
        'TammieEma': 'Tammie Ema', 'AlisonDietlinde': 'Alison Dietlinde', 'AnaFlorence': 'Ana Florence',
        'AnnmarieNele': 'Annmarie Nele', 'AsyaAnara': 'Asya Anara', 'BrendaStern': 'Brenda Stern',
        'GittaNikolina': 'Gitta Nikolina', 'HenrietteUsha': 'Henriette Usha', 'SofiaHellen': 'Sofia Hellen',
        'TammyGrit': 'Tammy Grit', 'TanjaAdelina': 'Tanja Adelina', 'VjollcaJohnnie': 'Vjollca Johnnie',
        'AndrewChipper': 'Andrew Chipper', 'BadrOdhiambo': 'Badr Odhiambo', 'DionisioSchuyler': 'Dionisio Schuyler',
        'RoystonMin': 'Royston Min', 'ViktorEka': 'Viktor Eka', 'AbrahanMack': 'Abrahan Mack',
        'AddeMichal': 'Adde Michal', 'BaldurSanjin': 'Baldur Sanjin', 'CraigGutsy': 'Craig Gutsy',
        'DamienBlack': 'Damien Black', 'GilbertoMathias': 'Gilberto Mathias', 'IlkinUrbano': 'Ilkin Urbano',
        'KazuhikoAtallah': 'Kazuhiko Atallah', 'LudvigMilivoj': 'Ludvig Milivoj', 'SuadQasim': 'Suad Qasim',
        'TorcullDiarmuid': 'Torcull Diarmuid', 'ViktorMenelaos': 'Viktor Menelaos', 'ZacharieAimilios': 'Zacharie Aimilios',
        'NovaHogarth': 'Nova Hogarth', 'MajaRuoho': 'Maja Ruoho', 'UtaObando': 'Uta Obando',
        'LidiyaSzekeres': 'Lidiya Szekeres', 'ChandraMacFarland': 'Chandra MacFarland', 'SzofiGranger': 'Szofi Granger',
        'CamillaHolmström': 'Camilla Holmström', 'LilyaStainthorpe': 'Lilya Stainthorpe', 'ZofijaKendrick': 'Zofija Kendrick',
        'NarelleMoon': 'Narelle Moon', 'BarboraMacLean': 'Barbora MacLean', 'AlexandraHisakawa': 'Alexandra Hisakawa',
        'AlmaMaría': 'Alma María', 'RosemaryOkafor': 'Rosemary Okafor', 'IgeBehringer': 'Ige Behringer',
        'FilipTraverse': 'Filip Traverse', 'DamjanChapman': 'Damjan Chapman', 'WulfCarlevaro': 'Wulf Carlevaro',
        'AaronDreschner': 'Aaron Dreschner', 'KumarDahl': 'Kumar Dahl', 'EugenioMataracı': 'Eugenio Mataracı',
        'FerranSimen': 'Ferran Simen', 'XavierHayasaka': 'Xavier Hayasaka', 'LuisMoray': 'Luis Moray',
        'MarcosRudaski': 'Marcos Rudaski'
    }
}
default_bark_settings = {
    "samplerate": 24000,
    "files": ['coarse_2.pt']
}
default_fairseq_settings = {
    "samplerate": 24000,
    "files": ['config.json', 'G_100000.pth', 'vocab.json']
}
default_vits_settings = {
    "samplerate": 24000,
    "files": ['config.json', 'model_file.pth', 'language_ids.json']
}
default_yourtts_settings = {
    "samplerate": 24000,
    "files": ['config.json', 'model_file.pth']
    "voices": {"MachinElla": "female-en-5", "ElectroMale": "male-en-2"}
}

models = {
    XTTSv2: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/xtts_v2",
            "sub": "",
            "voice": default_xtts_settings['voices']['KumarDahl'],
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"AiExplained_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobOdenkirk_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobRoss_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BryanCranston_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"DavidAttenborough_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "DeathPussInBoots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPussInBoots",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"DeathPussInBoots_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"GhostMW2_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "JhonButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonButlerASMR",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"JhonButlerASMR_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "JhonMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonMulaney",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"JhonMulaney_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"MorganFreeman_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"RainyDayHeadSpace_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"WhisperSalemASMR_{default_xtts_settings['samplerate']}.wav"),
            "files": default_xtts_settings['files'],
            "samplerate": default_xtts_settings['samplerate']
        }
    },
    BARK: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/bark",
            "sub": "",
            "voice": None,
            "files": default_bark_settings['files'],
            "samplerate": default_bark_settings['samplerate']
        }
    },
    VITS: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang_iso1]/[xxx]",
            "sub": {"cv/vits":["bg","cs","da","et","ga","hr","lt","lv","mt","pt","ro","sk","sl","sv"], "css10/vits":["es","fr","nl","hu","fi","ru","el","ja","zh"], "ljspeech/vits": ["en"], "thorsten/tacotron2-DDC": ["de"]},
            "voice": None,
            "files": default_vits_settings['files'],
            "samplerate": default_vits_settings['samplerate']
        }
    },
    FAIRSEQ: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": None,
            "files": default_fairseq_settings['files'],
            "samplerate": default_fairseq_settings['samplerate']
        }
    },
    YOURTTS: {
        "internal": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/your_tts",
            "sub": "",
            "voice": default_yourtts_settings['voices']['ElectroMale'],
            "files": default_yourtts_settings['files'],
            "samplerate": default_yourtts_settings['samplerate']
        }
    }
}