import os
from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

models = {
    TTS_ENGINES['XTTSv2']: {
        "internal": {
            "lang": "multi",
            "repo": "coqui/XTTS-v2",
            "sub": "tts_models/multilingual/multi-dataset/xtts_v2/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'KumarDahl.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'AiExplained.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "AsmrRacoon": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AsmrRacoon/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'AsmrRacoon.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "Awkwafina": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/Awkwafina/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'Awkwafina.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'BobOdenkirk.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'BobRoss.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BrinaPalencia": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BrinaPalencia/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'BrinaPalencia.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'BryanCranston.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough/",
            "voice": os.path.join(voices_dir, 'eng', 'elder', 'male', 'DavidAttenborough.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DeathPussInBoots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPussInBoots/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'DeathPussInBoots.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "DermotCrowley": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DermotCrowley/",
            "voice": os.path.join(voices_dir, 'eng', 'elder', 'male', 'DermotCrowley.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "EvaSeymour": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/EvaSeymour/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'EvaSeymour.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "GideonOfnirEldenRing": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GideonOfnirEldenRing/",
            "voice": os.path.join(voices_dir, 'eng', 'elder', 'male', 'GideonOfnirEldenRing.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'GhostMW2.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JohnButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JohnButlerASMR/",
            "voice": os.path.join(voices_dir, 'eng', 'elder', 'male', 'JohnButlerASMR.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JohnMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JohnMulaney/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'JohnMulaney.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JillRedfield": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JillRedfield/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'JillRedfield.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "JuliaWhenlan": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JuliaWhenlan/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'JuliaWhenlan.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "LeeHorsley": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/LeeHorsley/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'LeeHorsley.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "MelinaEldenRing": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MelinaEldenRing/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'MelinaEldenRing.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'MorganFreeman.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "NeilGaiman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/NeilGaiman/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'NeilGaiman.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "PeterGriffinFamilyGuy": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/PeterGriffinFamilyGuy/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'PeterGriffinFamilyGuy.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RafeBeckley": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RafeBeckley/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'RafeBeckley.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace/",
            "voice": os.path.join(voices_dir, 'eng', 'elder', 'male', 'RainyDayHeadSpace.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RayPorter": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RayPorter/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'RayPorter.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RelaxForAWhile": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RelaxForAWhile/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'RelaxForAWhile.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "RosamundPike": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RosamundPike/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'RosamundPike.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "ScarlettJohansson": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/ScarlettJohansson/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'female', 'ScarlettJohansson.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "SladeTeenTitans": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/SladeTeenTitans/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'SladeTeenTitans.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "StanleyParable": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/StanleyParable/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'StanleyParable.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "Top15s": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/Top15s/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'Top15s.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR/",
            "voice": os.path.join(voices_dir, 'eng', 'adult', 'male', 'WhisperSalemASMR.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        },
        "Konishev": {
            "lang": "rus",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/rus/Konishev/",
            "voice": os.path.join(voices_dir, 'rus', 'adult', 'male', 'Konishev.wav'),
            "files": default_engine_settings[TTS_ENGINES['XTTSv2']]['files'],
            "samplerate": default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate']
        }
    }
}