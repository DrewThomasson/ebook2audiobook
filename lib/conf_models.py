import os
from lib.conf import tts_dir, voices_dir

loaded_tts = {}
xtts_builtin_speakers_list = {}

TTS_ENGINES = {
    "XTTSv2": "xtts", 
    "BARK": "bark", 
    "VITS": "vits", 
    "FAIRSEQ": "fairseq", 
    "TACOTRON2": "tacotron", 
    "YOURTTS": "yourtts"
}

TTS_VOICE_CONVERSION = {
    "freevc24": {"path": "voice_conversion_models/multilingual/vctk/freevc24", "samplerate": 24000},
    "knnvc": {"path": "voice_conversion_models/multilingual/multi-dataset/knnvc", "samplerate": 16000},
    "openvoice_v1": {"path": "voice_conversion_models/multilingual/multi-dataset/openvoice_v1", "samplerate": 22050},
    "openvoice_v2": {"path": "voice_conversion_models/multilingual/multi-dataset/openvoice_v2", "samplerate": 22050}
}

TTS_SML = {
    "break": "‡break‡",
    "pause": "‡pause‡",
    "###": "‡pause‡"
}

default_tts_engine = TTS_ENGINES['XTTSv2']
default_fine_tuned = 'internal'
default_vc_model = TTS_VOICE_CONVERSION['knnvc']['path']
default_voice_detection_model = 'drewThomasson/segmentation'

max_custom_model = 100
max_custom_voices = 1000

default_engine_settings = {
    TTS_ENGINES['XTTSv2']: {
        "samplerate": 24000,
        "temperature": 0.75,
        #"codec_temperature": 0.3,
        "length_penalty": 1.0,
        "num_beams": 1,
        "repetition_penalty": 2.0,
        #"cvvp_weight": 0.3,
        "top_k": 50,
        "top_p": 0.85,
        "speed": 1.0,
        #"gpt_cond_len": 512,
        #"gpt_batch_size": 1,
        "enable_text_splitting": False,
        "files": ['config.json', 'model.pth', 'vocab.json', 'ref.wav'],
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
        "rating": {"VRAM": 4, "CPU": 2, "RAM": 4, "Realism": 5}
    },
    TTS_ENGINES['BARK']: {
        "samplerate": 24000,
        "text_temp": 0.22,
        "waveform_temp": 0.44,
        "files": ["text_2.pt", "coarse_2.pt", "fine_2.pt"],
        "speakers_path": os.path.join(voices_dir, '__bark'),
        "voices": {
            "de_speaker_0": "Speaker 0", "de_speaker_1": "Speaker 1", "de_speaker_2": "Speaker 2",
            "de_speaker_3": "Speaker 3", "de_speaker_4": "Speaker 4", "de_speaker_5": "Speaker 5",
            "de_speaker_6": "Speaker 6", "de_speaker_7": "Speaker 7", "de_speaker_8": "Speaker 8",
            "de_speaker_9": "Speaker 9", "en_speaker_0": "Speaker 0", "en_speaker_1": "Speaker 1",
            "en_speaker_2": "Speaker 2", "en_speaker_3": "Speaker 3", "en_speaker_4": "Speaker 4",
            "en_speaker_5": "Speaker 5", "en_speaker_6": "Speaker 6", "en_speaker_7": "Speaker 7",
            "en_speaker_8": "Speaker 8", "en_speaker_9": "Speaker 9", "es_speaker_0": "Speaker 0",
            "es_speaker_1": "Speaker 1", "es_speaker_2": "Speaker 2", "es_speaker_3": "Speaker 3",
            "es_speaker_4": "Speaker 4", "es_speaker_5": "Speaker 5", "es_speaker_6": "Speaker 6",
            "es_speaker_7": "Speaker 7", "es_speaker_8": "Speaker 8", "es_speaker_9": "Speaker 9",
            "fr_speaker_0": "Speaker 0", "fr_speaker_1": "Speaker 1", "fr_speaker_2": "Speaker 2",
            "fr_speaker_3": "Speaker 3", "fr_speaker_4": "Speaker 4", "fr_speaker_5": "Speaker 5",
            "fr_speaker_6": "Speaker 6", "fr_speaker_7": "Speaker 7", "fr_speaker_8": "Speaker 8",
            "fr_speaker_9": "Speaker 9", "hi_speaker_0": "Speaker 0", "hi_speaker_1": "Speaker 1",
            "hi_speaker_2": "Speaker 2", "hi_speaker_3": "Speaker 3", "hi_speaker_4": "Speaker 4",
            "hi_speaker_5": "Speaker 5", "hi_speaker_6": "Speaker 6", "hi_speaker_7": "Speaker 7",
            "hi_speaker_8": "Speaker 8", "hi_speaker_9": "Speaker 9", "it_speaker_0": "Speaker 0",
            "it_speaker_1": "Speaker 1", "it_speaker_2": "Speaker 2", "it_speaker_3": "Speaker 3",
            "it_speaker_4": "Speaker 4", "it_speaker_5": "Speaker 5", "it_speaker_6": "Speaker 6",
            "it_speaker_7": "Speaker 7", "it_speaker_8": "Speaker 8", "it_speaker_9": "Speaker 9",
            "ja_speaker_0": "Speaker 0", "ja_speaker_1": "Speaker 1", "ja_speaker_2": "Speaker 2",
            "ja_speaker_3": "Speaker 3", "ja_speaker_4": "Speaker 4", "ja_speaker_5": "Speaker 5",
            "ja_speaker_6": "Speaker 6", "ja_speaker_7": "Speaker 7", "ja_speaker_8": "Speaker 8",
            "ja_speaker_9": "Speaker 9", "ko_speaker_0": "Speaker 0", "ko_speaker_1": "Speaker 1",
            "ko_speaker_2": "Speaker 2", "ko_speaker_3": "Speaker 3", "ko_speaker_4": "Speaker 4",
            "ko_speaker_5": "Speaker 5", "ko_speaker_6": "Speaker 6", "ko_speaker_7": "Speaker 7",
            "ko_speaker_8": "Speaker 8", "ko_speaker_9": "Speaker 9", "pl_speaker_0": "Speaker 0",
            "pl_speaker_1": "Speaker 1", "pl_speaker_2": "Speaker 2", "pl_speaker_3": "Speaker 3",
            "pl_speaker_4": "Speaker 4", "pl_speaker_5": "Speaker 5", "pl_speaker_6": "Speaker 6",
            "pl_speaker_7": "Speaker 7", "pl_speaker_8": "Speaker 8", "pl_speaker_9": "Speaker 9",
            "pt_speaker_0": "Speaker 0", "pt_speaker_1": "Speaker 1", "pt_speaker_2": "Speaker 2",
            "pt_speaker_3": "Speaker 3", "pt_speaker_4": "Speaker 4", "pt_speaker_5": "Speaker 5",
            "pt_speaker_6": "Speaker 6", "pt_speaker_7": "Speaker 7", "pt_speaker_8": "Speaker 8",
            "pt_speaker_9": "Speaker 9", "ru_speaker_0": "Speaker 0", "ru_speaker_1": "Speaker 1",
            "ru_speaker_2": "Speaker 2", "ru_speaker_3": "Speaker 3", "ru_speaker_4": "Speaker 4",
            "ru_speaker_5": "Speaker 5", "ru_speaker_6": "Speaker 6", "ru_speaker_7": "Speaker 7",
            "ru_speaker_8": "Speaker 8", "ru_speaker_9": "Speaker 9", "tr_speaker_0": "Speaker 0",
            "tr_speaker_1": "Speaker 1", "tr_speaker_2": "Speaker 2", "tr_speaker_3": "Speaker 3",
            "tr_speaker_4": "Speaker 4", "tr_speaker_5": "Speaker 5", "tr_speaker_6": "Speaker 6",
            "tr_speaker_7": "Speaker 7", "tr_speaker_8": "Speaker 8", "tr_speaker_9": "Speaker 9",
            "zh_speaker_0": "Speaker 0", "zh_speaker_1": "Speaker 1", "zh_speaker_2": "Speaker 2",
            "zh_speaker_3": "Speaker 3", "zh_speaker_4": "Speaker 4", "zh_speaker_5": "Speaker 5",
            "zh_speaker_6": "Speaker 6", "zh_speaker_7": "Speaker 7", "zh_speaker_8": "Speaker 8",
            "zh_speaker_9": "Speaker 9"
        },
        "rating": {"VRAM": 6, "CPU": 1, "RAM": 6, "Realism": 5}
    },
    TTS_ENGINES['VITS']: {
        "samplerate": 22050,
        "files": ['config.json', 'model_file.pth', 'language_ids.json'],
        "voices": {},
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['FAIRSEQ']: {
        "samplerate": 16000,
        "files": ['config.json', 'G_100000.pth', 'vocab.json'],
        "voices": {},
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['TACOTRON2']: {
        "samplerate": 22050,
        "files": ['config.json', 'best_model.pth', 'vocoder_config.json', 'vocoder_model.pth'],
        "voices": {},
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 3}
    },
    TTS_ENGINES['YOURTTS']: {
        "samplerate": 16000,
        "files": ['config.json', 'model_file.pth'],
        "voices": {"Machinella-5": "female-en-5", "ElectroMale-2": "male-en-2", 'Machinella-4': 'female-pt-4\n', 'ElectroMale-3': 'male-pt-3\n'},
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 1, "Realism": 2}
    }
}