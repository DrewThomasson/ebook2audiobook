import os
from lib.conf import voices_dir
from lib.lang import default_voice_file


default_tts_engine = 'xtts'
default_fine_tuned = 'std'
default_xtts_files = ['config.json', 'vocab.json', 'model.pth', 'ref.wav']
default_fairseq_files = ['config.json', 'vocab.json', 'G_100000.pth']
default_yourtts_files = ['config.json', 'model_file.pth']
default_bark_files = ['coarse_2.pt']
default_libri_files = ['config.json', 'model_file.pth']
default_openvoice2_files = ['config.json', 'checkpoint.pth']
default_freevc24_files = ['config.json', 'model.pth']

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
            "files": default_xtts_files
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "AiExplained_24khz.wav"),
            "files": default_xtts_files
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "BobOdenkirk_24khz.wav"),
            "files": default_xtts_files
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "BobRoss_24khz.wav"),
            "files": default_xtts_files
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "BryanCranston_24khz.wav"),
            "files": default_xtts_files
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", "DavidAttenborough_24khz.wav"),
            "files": default_xtts_files
        },
        "DeathPussInBoots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPussInBoots",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "DeathPussInBoots_24khz.wav"),
            "files": default_xtts_files
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "GhostMW2_24khz.wav"),
            "files": default_xtts_files
        },
        "JhonButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonButlerASMR",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", "JhonButlerASMR_24khz.wav"),
            "files": default_xtts_files
        },
        "JhonMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonMulaney",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "JhonMulaney_24khz.wav"),
            "files": default_xtts_files
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "MorganFreeman_24khz.wav"),
            "files": default_xtts_files
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace",
            "voice": os.path.join(voices_dir, "eng", "elder", "male", "RainyDayHeadSpace_24khz.wav"),
            "files": default_xtts_files
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR",
            "voice": os.path.join(voices_dir, "eng", "adult", "male", "WhisperSalemASMR_24khz.wav"),
            "files": default_xtts_files
        }
    },
    "fairseq": {
        "std": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": default_voice_file,
            "files": default_fairseq_files
        }
    }
}