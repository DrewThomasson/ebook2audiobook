import os
from lib.conf import voices_dir
from lib.lang import default_voice_file

XTTSv2 = 'xtts'
FAIRSEQ = 'fairseq'

tts_engines = [XTTSv2, FAIRSEQ]

default_tts_engine = 'xtts'
default_fine_tuned = 'std'

# config file must always on first row
default_xtts_files = ['config.json', 'model.pth', 'vocab.json', 'ref.wav']
default_fairseq_files = ['config.json', 'G_100000.pth', 'vocab.json']
default_yourtts_files = ['config.json', 'model_file.pth']
default_bark_files = ['coarse_2.pt']
default_libri_files = ['config.json', 'model_file.pth']
default_openvoice2_files = ['config.json', 'checkpoint.pth']
default_freevc24_files = ['config.json', 'model.pth']

default_xtts_samplerate = 24000
default_fairseq_samplerate = 24000
default_yourtts_samplerate = 22050
default_bark_samplerate = 24000
default_libri_samplerate = 24000
default_openvoice2_samplerate = 24000
default_freevc24_samplerate = 24000

builtin_xtts_voices = [
    'Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 'Alison Dietlinde', 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 
    'Brenda Stern', 'Gitta Nikolina', 'Henriette Usha', 'Sofia Hellen', 'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 'Andrew Chipper', 
    'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 
    'Damien Black', 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 'Ludvig Milivoj', 'Suad Qasim', 'Torcull Diarmuid', 
    'Viktor Menelaos', 'Zacharie Aimilios', 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 'Lidiya Szekeres', 'Chandra MacFarland', 
    'Szofi Granger', 'Camilla Holmström', 'Lilya Stainthorpe', 'Zofija Kendrick', 'Narelle Moon', 'Barbora MacLean', 
    'Alexandra Hisakawa', 'Alma María', 'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 
    'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Eugenio Mataracı', 'Ferran Simen', 'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski'
]
builtin_yourtts_voices = ['female-en-5', 'female-en-5\n', 'female-pt-4\n', 'male-en-2', 'male-en-2\n', 'male-pt-3\n']

models = {
    "xtts": {
        "std": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/xtts_v2",
            "sub": "",
            "voice": default_voice_file,
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"AiExplained_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobOdenkirk_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BobRoss_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"BryanCranston_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"DavidAttenborough_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "DeathPussInBoots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPussInBoots",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"DeathPussInBoots_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"GhostMW2_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "JhonButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonButlerASMR",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"JhonButlerASMR_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "JhonMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonMulaney",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"JhonMulaney_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"MorganFreeman_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", f"RainyDayHeadSpace_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", f"WhisperSalemASMR_{default_xtts_samplerate}.wav"),
            "files": default_xtts_files,
            "samplerate": default_xtts_samplerate
        }
    },
    "fairseq": {
        "std": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": default_voice_file,
            "files": default_fairseq_files,
            "samplerate": default_fairseq_samplerate
        }
    }
}