import os

version = '2.1.0'
min_python_version = (3,12)
max_python_version = (3,12)

NATIVE = 'native'
DOCKER_UTILS = 'docker_utils'
FULL_DOCKER = 'full_docker'

device_list = ['cpu', 'gpu', 'mps']
default_device = "cuda"

python_env_dir = os.path.abspath(os.path.join('.','python_env'))
requirements_file = os.path.abspath(os.path.join('.','requirements.txt'))
docker_utils_image = 'utils'

interface_host = '0.0.0.0'
interface_port = 7860
interface_shared_tmp_expire = 3 # days
interface_concurrency_limit = 8 # or None for unlimited
interface_component_options = {
    "gr_tab_preferences": True,
    "gr_voice_file": True,
    "gr_group_custom_model": True
}

models_dir = os.path.abspath(os.path.join('.','models'))
ebooks_dir = os.path.abspath(os.path.join('.','ebooks'))
voices_dir = os.path.abspath(os.path.join('.','voices'))

tmp_dir = os.path.abspath(os.path.join('.','tmp'))
tmp_expire = 7 # days

max_custom_model = 10
max_custom_voices = 100

audiobooks_gradio_dir = os.path.abspath(os.path.join('.','audiobooks','gui','gradio'))
audiobooks_host_dir = os.path.abspath(os.path.join('.','audiobooks','gui','host'))
audiobooks_cli_dir = os.path.abspath(os.path.join('.','audiobooks','cli'))

ebook_formats = ['.epub', '.mobi', '.azw3', 'fb2', 'lrf', 'rb', 'snb', 'tcr', '.pdf', '.txt', '.rtf', 'doc', '.docx', '.html', '.odt', '.azw']
voice_formats = ['.mp4', '.m4b', '.mp3', '.wav', '.aac', '.flac', '.alac', '.ogg', '.aiff', '.aif', '.wma', '.dsd', '.opus', '.pcmu', '.pcma', '.gsm']
output_formats = ['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']
default_audioproc_format = 'wav' # only 'wav' is valid for now
default_output_format = 'm4b' # or 'mp3' 'opus' or any you wish

tts_default_settings = {
    "temperature": 0.65,
    "length_penalty": 1.0,
    "repetition_penalty": 2.5,
    "top_k": 50,
    "top_p": 0.8,
    "speed": 1.0,
    "enable_text_splitting": False
}

os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['CALIBRE_TEMP_DIR'] = tmp_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = tmp_dir
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