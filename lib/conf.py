import os
import platform

version = '25.2.0'
min_python_version = (3,12)
max_python_version = (3,12)

NATIVE = 'native'
FULL_DOCKER = 'full_docker'

debug_mode = True

device_list = ['cpu', 'gpu', 'mps']
default_device = "cuda"

python_env_dir = os.path.abspath(os.path.join('.','python_env'))
requirements_file = os.path.abspath(os.path.join('.','requirements.txt'))

interface_host = '0.0.0.0'
interface_port = 7860
interface_shared_tmp_expire = 3 # in days
interface_concurrency_limit = 1 # or None for unlimited

interface_component_options = {
    "gr_tab_preferences": True,
    "gr_group_voice_file": True,
    "gr_group_custom_model": True
}

models_dir = os.path.abspath('models')
ebooks_dir = os.path.abspath('ebooks')
voices_dir = os.path.abspath('voices')

tmp_dir = os.path.abspath('tmp')
tmp_expire = 7 # days

max_tts_in_memory = 4 # TTS engines to keep in memory
max_custom_model = 10
max_custom_voices = 100
max_upload_size = '6GB'

audiobooks_gradio_dir = os.path.abspath(os.path.join('audiobooks','gui','gradio'))
audiobooks_host_dir = os.path.abspath(os.path.join('audiobooks','gui','host'))
audiobooks_cli_dir = os.path.abspath(os.path.join('audiobooks','cli'))

ebook_formats = ['.epub', '.mobi', '.azw3', '.fb2', '.lrf', '.rb', '.snb', '.tcr', '.pdf', '.txt', '.rtf', '.doc', '.docx', '.html', '.odt', '.azw']
voice_formats = ['.mp4', '.m4b', '.mp3', '.wav', '.aac', '.flac', '.alac', '.ogg', '.aiff', '.aif', '.wma', '.dsd', '.opus', '.pcmu', '.pcma', '.gsm'] # Add or remove the format you wish
output_formats = ['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']
default_audio_proc_format = 'flac' # or 'wav', 'pcm', 'ieee', 'ogg', 'nist', 'mp3', 'aiff', 'aac', 'wma', 'mp4', 'm4a', 'm4b', 'amr', '3gp', 'webm', 'alac'
default_output_format = 'm4b' # or 'wav', 'pcm', 'ieee', 'ogg', 'nist', 'mp3', 'aiff', 'aac', 'wma', 'mp4', 'm4a', 'flac', 'amr', '3gp', 'webm', 'alac'


# to enable_deepspeed, it must be installed manually.
# conda activate [./python_env | .\python_env]
# pip install deepspeed
# conda deactivate
tts_default_settings = {
    "temperature": 0.6,  # Natural variation without sounding robotic
    "length_penalty": 1.2,  # Encourages slightly longer phrases
    "num_beams": 4,  # More beams improve long-term coherence
    "repetition_penalty": 2.0,  # Helps prevent redundant phrasing
    "top_k": 45,  # Balanced word diversity
    "top_p": 0.85,  # Good tradeoff between diversity and coherence
    "speed": 1.0,  # Normal pace
    "enable_text_splitting": True,  # Helps with better pacing for long content
    "enable_deepspeed": False,
    "length_scale": 1.0,
    "noise_scale": 0.3
}

os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
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
os.environ["SUNO_OFFLOAD_CPU"] = "True" # BARK option: "False" needs A GPU
os.environ["SUNO_USE_SMALL_MODELS"] = "True" # "False" needs a GPU with VRAM > 4GB
if platform.system() == "Windows":
    os.environ["ESPEAK_DATA_PATH"] = os.path.expandvars(r"%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data")