import os, tempfile, sys, re

debug_mode = False

DEVICE_SYSTEM = sys.platform

systems = {
    "LINUX": "linux",
    "MACOS": "darwin",
    "WINDOWS": "win32"
}

cli_options = [
    '--script_mode', '--docker_mode', '--session', '--share', '--headless', 
    '--ebook', '--ebooks_dir', '--text', '--language', '--voice', '--device', '--tts_engine', 
    '--custom_model', '--fine_tuned', '--output_format', '--output_channel',
    '--temperature', '--length_penalty', '--num_beams', '--repetition_penalty', 
    '--top_k', '--top_p', '--speed', '--enable_text_splitting', '--text_temp',
    '--waveform_temp', '--output_dir', '--version', '--docker_device', '--workflow', '--help'
]

workflow_id = 'ba800d22-ee51-11ef-ac34-d4ae52cfd9ce'
fernet_key = '0TkxI0iP0jmhT0vJ-AUpM2U4SAX3urVtrx1q8lwTynI='
fernet_data = b'gAAAAABptJuHZS_rMQRTmqzy-i5UFTh6HqcbklSV6oZsRpZXa7uSEveAMv1daIFzzeeWZW0wDV-frFlzk_gJPc5tr_YVKW-Eg8evw9Wll1rWrvIAfT0YQywaUe188qP1dg-GOJDM7Ul1'

# ---------------------------------------------------------------------
# Version and runtime config
# ---------------------------------------------------------------------
prog_version = (lambda: open('VERSION.txt').read().strip())()

NATIVE = 'native'
FULL_DOCKER = 'full_docker'
BUILD_DOCKER = 'build_docker'

# ---------------------------------------------------------------------
# Python environment references
# ---------------------------------------------------------------------
min_python_version = (3,10)
max_python_version = (3,12)
python_env_dir = os.path.abspath(os.path.join('.','python_env'))
requirements_file = os.path.abspath(os.path.join('.','requirements.txt'))

# ---------------------------------------------------------------------
# Hardware mappings
# ---------------------------------------------------------------------
devices = {
    "CPU": {"proc": "cpu", "found": True},
    "CUDA": {"proc": "cuda", "found": False},
    "MPS": {"proc": "mps", "found": False},
    "ROCM": {"proc": "rocm", "found": False},
    "XPU": {"proc": "xpu", "found": False},
    "JETSON": {"proc": "jetson", "found": False},
}

default_device = devices['CPU']['proc']

default_gpu_wiki = '<a href="https://github.com/DrewThomasson/ebook2audiobook/wiki/GPU-ISSUES">GPU howto wiki</a>'

default_py_major = sys.version_info.major
default_py_minor = sys.version_info.minor

default_pytorch_url = 'https://download.pytorch.org/whl'
default_pytorch_amd_url = 'https://repo.radeon.com/rocm/windows'
default_jetson_url = 'https://www.e-blokos.com/whl/jetson' # TODO: find a permanent website where to upload the jetpack torch

torch_matrix = {
    # CPU
    "cpu":       {"compat": list(systems.values()), "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    # CUDA
    "cu118":     {"compat": list(systems.values()), "base": "2.7.1", "last": "2.7.1", "extra_tag": ""},
    "cu121":     {"compat": list(systems.values()), "base": "2.5.1", "last": "2.5.1", "extra_tag": ""},
    "cu124":     {"compat": list(systems.values()), "base": "2.6.0", "last": "2.6.0", "extra_tag": ""},
    "cu126":     {"compat": list(systems.values()), "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    "cu128":     {"compat": list(systems.values()), "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    "cu129":     {"compat": list(systems.values()), "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    "cu130":     {"compat": list(systems.values()), "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    # ROCm
    "rocm5.7":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.3.1", "last": "2.3.1", "extra_tag": ""},
    "rocm6.0":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.4.1", "last": "2.4.1", "extra_tag": ""},
    "rocm6.1":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.6.0", "last": "2.6.0", "extra_tag": ""},
    "rocm6.2":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.5.1", "last": "2.5.1", "extra_tag": ""},
    "rocm6.2.4": {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    "rocm6.3":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.7.1", "last": "2.9.1", "extra_tag": ""},
    "rocm7.0":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.10.0", "last": "2.10.0", "extra_tag": ""},
    "rocm7.1":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.11.0", "last": "2.11.0", "extra_tag": ""},
    "rocm7.2":   {"compat": [systems['LINUX'], systems['MACOS']], "base": "2.11.0", "last": "2.11.0", "extra_tag": ""},
    "rocm-rel-7.2.1": {"compat": [systems['WINDOWS']], "base": "2.9.1", "last": "2.9.1", "extra_tag": "+rocm7.2.1"},
    # MPS
    "mps":       {"compat": [systems['MACOS']], "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    # XPU
    "xpu":       {"compat": [systems['LINUX'], systems['WINDOWS']], "base": "2.7.1", "last": "2.11.0", "extra_tag": ""},
    # JETSON
    "jetson51":  {"compat": [systems['LINUX']], "base": "2.4.1", "last": "2.4.1", "extra_tag": ""},
    "jetson60":  {"compat": [systems['LINUX']], "base": "2.4.0", "last": "2.4.0", "extra_tag": ""},
    "jetson61":  {"compat": [systems['LINUX']], "base": "2.5.0", "last": "2.5.0", "extra_tag": ""}
}

cuda_version_range = {"min": (11,8), "max": (13,0)}
rocm_version_range = {"min": (5,7), "max": (7,2)}
mps_version_range = {"min": (0,0), "max": (0,0)}
xpu_version_range = {"min": (0,0), "max": (0,0)}
jetson_version_range = {"min": (5,1), "max": (6,1)}

############### SETTINGS BELOW CAN BE MODIFIED ###############

# ---------------------------------------------------------------------
# Global paths
# ---------------------------------------------------------------------
root_dir = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.abspath('tmp')
run_dir = os.path.abspath('run')
gradio_cache_dir = os.path.normpath(os.path.join(run_dir, 'gradio'))
models_dir = os.path.abspath('models')
ebooks_dir = os.path.abspath('ebooks')
voices_dir = os.path.abspath('voices')
tts_dir = os.path.join(models_dir, 'tts')
components_dir = os.path.abspath('components')
tempfile.tempdir = run_dir

# ---------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['CALIBRE_NO_NATIVE_FILEDIALOGS'] = '1'
os.environ['CALIBRE_TEMP_DIR'] = run_dir
os.environ['CALIBRE_CACHE_DIRECTORY'] = run_dir
os.environ['CALIBRE_CONFIG_DIRECTORY'] = run_dir
os.environ['TMPDIR'] = run_dir
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
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
os.environ['CUDA_MODULE_LOADING'] = 'LAZY'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_CACHE_MAXSIZE'] = '2147483648'
os.environ['SUNO_OFFLOAD_CPU'] = 'False'
os.environ['SUNO_USE_SMALL_MODELS'] = 'False'
os.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'
os.environ['MIOPEN_FIND_MODE'] = 'FAST'
os.environ['MIOPEN_FIND_ENFORCE'] = 'SEARCH_DB_UPDATE'
if DEVICE_SYSTEM == systems['WINDOWS']:
    os.environ['ESPEAK_DATA_PATH'] = os.path.expandvars(r"%USERPROFILE%\scoop\apps\espeak-ng\current\espeak-ng-data")

# ---------------------------------------------------------------------
# Global settings
# ---------------------------------------------------------------------
max_upload_size = '6GB' # MB or GB
tmp_expire = 60 # days
max_ebook_textarea_length = 1024 # chars

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
    ".png", ".jpg", ".jpeg", ".bmp", ".pptx"
]
voice_formats = [
    ".mp4", ".m4b", ".m4a", ".mp3", ".wav", ".aac", ".flac", ".alac", ".ogg",
    ".aiff", ".aif", ".wma", ".dsd", ".opus", ".pcmu", ".pcma", ".gsm"
]
output_formats = [
    "aac", "flac", "mp3", "m4b", "m4a", "mp4", "mov", "ogg", "wav", "webm"
]
default_audio_proc_samplerate = 24000
default_audio_proc_format = 'flac' # or 'ogg', 'wav' (wav format is ok but limited to process files < 4GB)
default_output_format = 'm4b'
default_output_channel = 'mono' # mono or stereo
default_output_split = False
default_output_split_hours = '6' # if the final ouput esceed outpout_split_hours * 2 hours the final file will be splitted by outpout_split_hours + the end if any.