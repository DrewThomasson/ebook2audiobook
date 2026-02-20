import os, tempfile, sys, re

# ---------------------------------------------------------------------
# Global configuration
# ---------------------------------------------------------------------
min_python_version = (3,10)
max_python_version = (3,12)

root_dir = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.abspath('tmp')
tempfile.tempdir = tmp_dir
tmp_expire = 7 # days

models_dir = os.path.abspath('models')
ebooks_dir = os.path.abspath('ebooks')
voices_dir = os.path.abspath('voices')
tts_dir = os.path.join(models_dir, 'tts')
components_dir = os.path.abspath('components')

# ---------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['CALIBRE_NO_NATIVE_FILEDIALOGS'] = '1'
os.environ['CALIBRE_TEMP_DIR'] = tmp_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = tmp_dir
os.environ['CALIBRE_CONFIG_DIRECTORY'] = tmp_dir
os.environ['TMPDIR'] = tmp_dir
os.environ['GRADIO_DEBUG'] = '0'
os.environ['DO_NOT_TRACK'] = 'True'
os.environ['HUGGINGFACE_HUB_CACHE'] = tts_dir
os.environ['HF_HOME'] = tts_dir
os.environ['HF_DATASETS_CACHE'] = tts_dir
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['BARK_CACHE_DIR'] = tts_dir
os.environ['TTS_CACHE'] = tts_dir
os.environ['TORCH_HOME'] = tts_dir
os.environ['TTS_HOME'] = models_dir
os.environ['XDG_CACHE_HOME'] = models_dir
os.environ['MPLCONFIGDIR'] = f'{models_dir}/matplotlib'
os.environ['TESSDATA_PREFIX'] = f'{models_dir}/tessdata'
os.environ['STANZA_RESOURCES_DIR'] = os.path.join(models_dir, 'stanza')
os.environ['ARGOS_TRANSLATE_PACKAGE_PATH'] = os.path.join(models_dir, 'argostranslate')
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['PYTORCH_NO_CUDA_MEMORY_CACHING'] = '1'
os.environ['TORCH_CUDA_ENABLE_CUDA_GRAPH'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128,garbage_collection_threshold:0.6,expandable_segments:True'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
os.environ['CUDA_CACHE_MAXSIZE'] = '2147483648'
os.environ['SUNO_OFFLOAD_CPU'] = 'False'
os.environ['SUNO_USE_SMALL_MODELS'] = 'False'
if sys.platform == 'win32':
    os.environ['ESPEAK_DATA_PATH'] = os.path.expandvars(r"%USERPROFILE%\scoop\apps\espeak-ng\current\espeak-ng-data")

# ---------------------------------------------------------------------
# Version and runtime config
# ---------------------------------------------------------------------
prog_version = (lambda: open('VERSION.txt').read().strip())()
max_upload_size = '6GB'

NATIVE = 'native'
FULL_DOCKER = 'full_docker'
BUILD_DOCKER = 'build_docker'

debug_mode = False

# ---------------------------------------------------------------------
# Python environment references
# ---------------------------------------------------------------------

python_env_dir = os.path.abspath(os.path.join('.','python_env'))
requirements_file = os.path.abspath(os.path.join('.','requirements.txt'))

# ---------------------------------------------------------------------
# Hardware mappings
# ---------------------------------------------------------------------

systems = {
    "LINUX": "linux",
    "MACOS": "darwin",
    "WINDOWS": "win32"
}

devices = {
    "CPU": {"proc": "cpu", "found": True},
    "CUDA": {"proc": "cuda", "found": False},
    "MPS": {"proc": "mps", "found": False},
    "ROCM": {"proc": "rocm", "found": False},
    "XPU": {"proc": "xpu", "found": False},
    "JETSON": {"proc": "jetson", "found": False},
}

default_device = devices['CPU']['proc']
default_chapters_preview = False

default_gpu_wiki = '<a href="https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES">GPU howto wiki</a>'

default_py_major = sys.version_info.major
default_py_minor = sys.version_info.minor

default_pytorch_url = 'https://download.pytorch.org/whl'
default_jetson_url = 'https://www.e-blokos.com/whl/jetson' # TODO: find a permanent website where to upload the jetpack torch

torch_matrix = {
    # CPU
    "cpu":       {"url": None, "base": ((lambda m:m.group(1) if m else '')(re.search(r'(?m)^\s*torch\s*==\s*([0-9]+\.[0-9]+\.[0-9]+)',open(requirements_file).read())))},
    # CUDA
    "cu118":     {"url": default_pytorch_url, "base": "2.7.1"},
    "cu121":     {"url": default_pytorch_url, "base": "2.5.1"},
    "cu124":     {"url": default_pytorch_url, "base": "2.6.0"},
    "cu126":     {"url": default_pytorch_url, "base": "2.7.1"},
    "cu128":     {"url": default_pytorch_url, "base": "2.7.1"},
    # ROCm
    "rocm5.7":   {"url": default_pytorch_url, "base": "2.3.1"},
    "rocm6.0":   {"url": default_pytorch_url, "base": "2.4.1"},
    "rocm6.1":   {"url": default_pytorch_url, "base": "2.6.0"},
    "rocm6.2":   {"url": default_pytorch_url, "base": "2.5.1"},
    "rocm6.2.4": {"url": default_pytorch_url, "base": "2.7.1"},
    "rocm6.3":   {"url": default_pytorch_url, "base": "2.7.1"},
    # MPS
    "mps":       {"url": default_pytorch_url, "base": "2.7.1"},
    # XPU
    "xpu":       {"url": default_pytorch_url, "base": "2.7.1"},
    # JETSON
    "jetson60":  {"url": default_jetson_url, "base": "2.4.0"},
    "jetson61":  {"url": default_jetson_url, "base": "2.5.0"}
}

cuda_version_range = {"min": (11,8), "max": (12,8)}
rocm_version_range = {"min": (5,7), "max": (6,3)}
mps_version_range = {"min": (0,0), "max": (0,0)}
xpu_version_range = {"min": (0,0), "max": (0,0)}
jetson_version_range = {"min": (6,0), "max": (6,1)}

# ---------------------------------------------------------------------
# Interface configuration
# ---------------------------------------------------------------------

interface_host = '0.0.0.0'
interface_port = 7860
interface_shared_tmp_expire = 3 # in days
interface_concurrency_limit = 1 # or None for unlimited multiple parallele user conversion

interface_component_options = {
    "gr_tab_xtts_params": True,
    "gr_tab_bark_params": True,
    "gr_group_voice_file": True,
    "gr_group_custom_model": True
}

# ---------------------------------------------------------------------
# UI directories
# ---------------------------------------------------------------------

audiobooks_gradio_dir = os.path.abspath(os.path.join('audiobooks','gui','gradio'))
audiobooks_host_dir = os.path.abspath(os.path.join('audiobooks','gui','host'))
audiobooks_cli_dir = os.path.abspath(os.path.join('audiobooks','cli'))

# ---------------------------------------------------------------------
# files and audio supported formats
# ---------------------------------------------------------------------

ebook_formats = [
    ".epub", ".mobi", ".azw3", ".fb2", ".lrf", ".rb", ".snb", ".tcr", ".pdf",
    ".txt", ".rtf", ".doc", ".docx", ".html", ".odt", ".azw", ".tiff", ".tif",
    ".png", ".jpg", ".jpeg", ".bmp",
]
voice_formats = [
    ".mp4", ".m4b", ".m4a", ".mp3", ".wav", ".aac", ".flac", ".alac", ".ogg",
    ".aiff", ".aif", ".wma", ".dsd", ".opus", ".pcmu", ".pcma", ".gsm",
]
output_formats = [
    "aac", "flac", "mp3", "m4b", "m4a", "mp4", "mov", "ogg", "wav", "webm",
]
default_audio_proc_samplerate = 24000
default_audio_proc_format = 'flac' # or 'mp3', 'aac', 'm4a', 'm4b', 'amr', '3gp', 'alac'. 'wav' format is ok but limited to process files < 4GB
default_output_format = 'm4b'
default_output_channel = 'mono' # mono or stereo
default_output_split = False
default_output_split_hours = '6' # if the final ouput esceed outpout_split_hours * 2 hours the final file will be splitted by outpout_split_hours + the end if any.