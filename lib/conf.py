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
gradio_interface_port = 7860
gradio_shared_expire = 72 # hours
concurrency_limit = 8 # or None for unlimited

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
audio_proc_format = 'wav' # only 'wav' is valid for now

default_tts_engine = 'xtts'
default_fine_tuned = 'std'

models = {
    "xtts": {
        "std": {
            "folder": "tts_models--multilingual--multi-dataset--xtts_v2",
            "api": "tts_models/multilingual/multi-dataset/xtts_v2",
            "voice": default_voice_file
        },
        "DavidAttenborough": {
            "folder": "tts_models--multilingual--multi-dataset--",
            "api": "drewThomasson/fineTunedTTSModels/xtts-v2/eng/DavidAttenborough",
            "voice": os.path.abspath(os.path.join("voices", "eng", "elder", "male", "DavidAttenborough_24khz.wav"))
        }
    },
    "mms": {
        "std": {
            "folder": "tts_models--[lang]--fairseq--vits",
            "api": "tts_models/[lang]/fairseq/vits",
            "voice": default_voice_file
        }
    }
}