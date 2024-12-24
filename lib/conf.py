import os
from lib.lang import default_voice_file

NATIVE = 'native'
DOCKER_UTILS = 'docker_utils'
FULL_DOCKER = 'full_docker'

version = '2.0.0'
min_python_version = (3,10)
max_python_version = (3,12)

requirements_file = os.path.abspath(os.path.join('.','requirements.txt'))

docker_utils_image = 'utils'

interface_host = '0.0.0.0'
interface_port = 7860
interface_shared_expire = 72 # hours
interface_concurrency_limit = 8 # or None for unlimited
interface_component_options = {
    "gr_tab_preferences": True,
    "gr_voice_file": True,
    "gr_group_custom_model": True
}

python_env_dir = os.path.abspath(os.path.join('.','python_env'))

models_dir = os.path.abspath(os.path.join('.','models'))
ebooks_dir = os.path.abspath(os.path.join('.','ebooks'))
processes_dir = os.path.abspath(os.path.join('.','tmp'))

audiobooks_gradio_dir = os.path.abspath(os.path.join('.','audiobooks','gui','gradio'))
audiobooks_host_dir = os.path.abspath(os.path.join('.','audiobooks','gui','host'))
audiobooks_cli_dir = os.path.abspath(os.path.join('.','audiobooks','cli'))

# <<<<<<< HEAD
# Automatically accept the non-commercial license
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['CALIBRE_TEMP_DIR'] = processes_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = processes_dir
os.environ['CALIBRE_NO_NATIVE_FILEDIALOGS'] = '1'
os.environ['DO_NOT_TRACK'] = 'true'
os.environ['HUGGINGFACE_HUB_CACHE'] = models_dir
os.environ['TTS_HOME'] = models_dir
os.environ['HF_HOME'] = models_dir
os.environ['HF_DATASETS_CACHE'] = models_dir
os.environ['HF_TOKEN_PATH'] = os.path.join(os.path.expanduser('~'), '.huggingface_token')
os.environ['TTS_CACHE'] = models_dir
os.environ['TORCH_HOME'] = models_dir
os.environ['XDG_CACHE_HOME'] = models_dir

ebook_formats = ['.epub', '.mobi', '.azw3', 'fb2', 'lrf', 'rb', 'snb', 'tcr', '.pdf', '.txt', '.rtf', 'doc', '.docx', '.html', '.odt', '.azw']
audiobook_format = 'm4b' # or 'mp3'
audioproc_format = 'wav' # only 'wav' is valid for now

default_tts_engine = 'xtts'
default_fine_tuned = 'std'
default_model_files = ['config.json', 'vocab.json', 'model.pth', 'ref.wav']

models = {
    "xtts": {
        "std": {
            "lang": "multi",
            "repo": "tts_models/multilingual/multi-dataset/xtts_v2",
            "sub": "",
            "voice": default_voice_file
        },
        "AiExplained": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/AiExplained",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "AiExplained_24khz.wav"))
        },
        "BobOdenkirk": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobOdenkirk",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "BobOdenkirk_24khz.wav"))
        },
        "BobRoss": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BobRoss",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "BobRoss_24khz.wav"))
        },
        "BryanCranston": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/BryanCranston",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "BryanCranston_24khz.wav"))
        },
        "DavidAttenborough": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DavidAttenborough",
            "voice": os.path.abspath(os.path.join("voices", "eng", "elder", "male", "DavidAttenborough_24khz.wav"))
        },
        "DeathPuss&Boots": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/DeathPuss&Boots",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "DeathPuss&Boots_24khz.wav"))
        },
        "GhostMW2": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/GhostMW2",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "GhostMW2_24khz.wav"))
        },
        "JhonButlerASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonButlerASMR",
            "voice": os.path.abspath(os.path.join("voices", "eng", "elder", "male", "JhonButlerASMR_24khz.wav"))
        },
        "JhonMulaney": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/JhonMulaney",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "JhonMulaney_24khz.wav"))
        },
        "MorganFreeman": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/MorganFreeman",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "MorganFreeman_24khz.wav"))
        },
        "RainyDayHeadSpace": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/RainyDayHeadSpace",
            "voice": os.path.abspath(os.path.join("voices", "eng", "elder", "male", "RainyDayHeadSpace_24khz.wav"))
        },
        "WhisperSalemASMR": {
            "lang": "eng",
            "repo": "drewThomasson/fineTunedTTSModels",
            "sub": "xtts-v2/eng/WhisperSalemASMR",
            "voice": os.path.abspath(os.path.join("voices", "eng", "adult", "male", "WhisperSalemASMR_24khz.wav"))
        }
    },
    "fairseq": {
        "std": {
            "lang": "multi",
            "repo": "tts_models/[lang]/fairseq/vits",
            "sub": "",
            "voice": default_voice_file
        }
    }
}