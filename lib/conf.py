import os
import platform

models_dir = os.path.abspath('models')
ebooks_dir = os.path.abspath('ebooks')
voices_dir = os.path.abspath('voices')

tmp_dir = os.path.abspath('tmp')
tmp_expire = 7 # days

os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['CALIBRE_NO_NATIVE_FILEDIALOGS'] = '1'
os.environ['DO_NOT_TRACK'] = 'true'
os.environ['CALIBRE_TEMP_DIR'] = tmp_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = tmp_dir
os.environ['HUGGINGFACE_HUB_CACHE'] = models_dir
os.environ['TTS_HOME'] = models_dir
os.environ['HF_HOME'] = models_dir
os.environ['HF_DATASETS_CACHE'] = models_dir
os.environ['TTS_CACHE'] = models_dir
os.environ['TORCH_HOME'] = models_dir
os.environ['XDG_CACHE_HOME'] = models_dir
os.environ["ARGOS_TRANSLATE_PACKAGE_PATH"] = os.path.join(models_dir, 'argostranslate')
os.environ['HF_TOKEN_PATH'] = os.path.join(os.path.expanduser('~'), '.huggingface_token')
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
os.environ["SUNO_OFFLOAD_CPU"] = 'False' # BARK option: False needs A GPU
os.environ["SUNO_USE_SMALL_MODELS"] = 'False' # BARK option: False needs a GPU with VRAM > 4GB
if platform.system() == 'Windows':
    os.environ['ESPEAK_DATA_PATH'] = os.path.expandvars(r"%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data")

prog_version = (lambda: open('VERSION.txt').read().strip())()

min_python_version = (3,10)
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

audiobooks_gradio_dir = os.path.abspath(os.path.join('audiobooks','gui','gradio'))
audiobooks_host_dir = os.path.abspath(os.path.join('audiobooks','gui','host'))
audiobooks_cli_dir = os.path.abspath(os.path.join('audiobooks','cli'))

ebook_formats = ['.epub', '.mobi', '.azw3', '.fb2', '.lrf', '.rb', '.snb', '.tcr', '.pdf', '.txt', '.rtf', '.doc', '.docx', '.html', '.odt', '.azw']
voice_formats = ['.mp4', '.m4b', '.m4a', '.mp3', '.wav', '.aac', '.flac', '.alac', '.ogg', '.aiff', '.aif', '.wma', '.dsd', '.opus', '.pcmu', '.pcma', '.gsm'] # Add or remove the format you wish
output_formats = ['m4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac']
default_audio_proc_format = 'flac' # or 'wav', 'mp3', 'aac', 'm4a', 'm4b', 'amr', '3gp', 'alac'
default_output_format = 'm4b' # or 'm4b', 'm4a', 'mp4', 'webm', 'mov', 'mp3', 'flac', 'wav', 'ogg', 'aac'