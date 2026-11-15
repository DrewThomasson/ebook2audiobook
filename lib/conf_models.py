import os, re
from lib.conf import tts_dir, voices_dir, devices

loaded_tts = {}
xtts_builtin_speakers_list = {}

# listed in any order: the end of this file sorts it by rating, with default_engine_settings
TTS_ENGINES = {
    "ZONOS": "zonos",
    "GPTSOVITS": "gptsovits",
    "OMNIVOICE": "omnivoice",
    "F5TTS": "f5tts",
    "ORPHEUS": "orpheus",
    "SPARKTTS": "sparktts",
    "CHATTTS": "chattts",
    "OPENVOICE": "openvoice",
    "MELOTTS": "melotts",
    "CSM": "csm",
    "PHONON": "phonon",
    "XTTS": "xtts",
    "BARK": "bark",
    "TORTOISE": "tortoise",
    "PIPER": "piper",
    "VITS": "vits",
    "FAIRSEQ": "fairseq",
    "GLOWTTS": "glowtts",
    "TACOTRON": "tacotron",
    "YOURTTS": "yourtts",
    # audio.cpp (0xShug0/audio.cpp) families:
    # one engine each, all run by the AudioCpp class (audiocpp.py)
    "BREEZE_TTS": "breeze_tts",
    "CHATTERBOX": "chatterbox",
    "CONFUCIUS4_TTS": "confucius4_tts",
    "COSYVOICE3": "cosyvoice3",
    "DOTS_TTS": "dots_tts",
    "DRAMABOX": "dramabox",
    "FIRERED_AUDIO": "firered_audio",
    "FIREREDTTS3": "fireredtts3",
    "FISH_AUDIO": "fish_audio",
    "HIGGS_AUDIO_TTS": "higgs_audio_tts",
    "INDEX_TTS2": "index_tts2",
    "IRODORI_TTS": "irodori_tts",
    "KOKORO_TTS": "kokoro_tts",
    "KUGELAUDIO": "kugelaudio",
    "MAGPIE_TTS": "magpie_tts",
    "MAYA1": "maya1",
    "MIOTTS": "miotts",
    "MOSS_TTS_LOCAL": "moss_tts_local",
    "MOSS_TTS_NANO": "moss_tts_nano",
    "NEUTTS": "neutts",
    "POCKET_TTS": "pocket_tts",
    "QWEN3_TTS": "qwen3_tts",
    "SUPERTONIC": "supertonic",
    "VIBEVOICE": "vibevoice",
    "VOXCPM2": "voxcpm2",
    "VOXTRAL_TTS": "voxtral_tts"
}

# voice conversion: a voice file picked for a built-in voice engine (piper, vits, fairseq, glowtts, tacotron, orpheus, melotts,
# phonon and the audio.cpp ones with clone False) turns its output into that voice, on audio.cpp's server (common/voice_conversion.py).
# default_vc_model below picks one; the last part of its path is the zero-shot engine's tts_zs_key (loaded_tts, model_zs_cache).
# task "vc": voice to voice. task "tts": the engine's voice clone speaks the sentence text again (no voice to voice).
# files: GGUF in audiocpp_repo; engine: the files of that engine's "internal" preset instead (one download for both).
# ref_max: the reference clip cut from the voice file, seconds (task "tts": the engine's own ref_min / ref_max)
#   seed_vc: Seed-VC V1 route, Whisper-small content + BigVGAN 22 kHz (the server default v2_vc reads content from
#     HuBERT-large, pretrained on English only). V1 shares a 30 s DiT window between the reference and each source
#     chunk: 15 s keeps a sentence in one window (no chunk crossfade)
#   chatterbox_vc: Chatterbox's S3Gen conditioned on the reference
#   qwen3_tts: Qwen3-TTS has no voice to voice: its Base clone speaks the text in the voice, in its own languages only
#     (fallback for the others); the built-in engine is not run for those sentences. The audio.cpp engines take the
#     fallback always (speaking their text again would only replace them)
TTS_VOICE_CONVERSION = {
    "seed_vc": {"path": "audiocpp/seed_vc", "task": "vc", "family": "seed_vc", "files": ["SeedVC-MLX-GGUF/seed-vc-mlx-q8_0.gguf"], "route": "v1_whisper_bigvgan_vc", "ref_max": 15.0},
    "chatterbox_vc": {"path": "audiocpp/chatterbox_vc", "task": "vc", "family": "chatterbox", "engine": TTS_ENGINES['CHATTERBOX'], "ref_max": 10.0},
    "qwen3_tts": {"path": "audiocpp/qwen3_tts", "task": "tts", "family": "qwen3_tts", "engine": TTS_ENGINES['QWEN3_TTS'], "fallback": "seed_vc"}
}

TTS_SML = {
    "break": {"static": "[break]", "paired": False},
    "pause": {"static": "[pause]", "paired": False},
    "voice": {"paired": True},
    # zonos only (ignored by the other engines): [emotion:sad]...[/emotion] or a mix [emotion:sad=0.7,angry=0.2].
    # ZONOS2 directions happy/sad/angry/surprised (0..1) and axes valence/arousal (-1..1); all at 0 is the plain
    # cloned voice. Zonos v0.1 names still work through aliases, fear/disgust through "map" (no direction of their own,
    # approximated on the two axes), neutral/other add nothing. A mix is scaled by 1/max(1, sum of |weights|).
    "emotion": {
        "paired": True,
        "values": ["happy", "sad", "angry", "surprised", "valence", "arousal"],
        "aliases": {"happiness": "happy", "joy": "happy", "sadness": "sad", "anger": "angry", "surprise": "surprised"},
        "map": {"fear": {"valence": -0.6, "arousal": 0.6}, "afraid": {"valence": -0.6, "arousal": 0.6}, "scared": {"valence": -0.6, "arousal": 0.6}, "disgust": {"valence": -0.6, "arousal": 0.2}, "disgusted": {"valence": -0.6, "arousal": 0.2}, "neutral": {}, "other": {}}
    }
}

sml_escape_tag = 0xE000
sml_tag_keys = '|'.join(map(re.escape, TTS_SML.keys()))

SML_TAG_PATTERN = re.compile(
    rf'''
    \[
        \s*
        (?P<close>/)?
        \s*
        (?P<tag>{sml_tag_keys})
        (?:\s*:\s*(?P<value>.*?))?
        \s*
    \]
    ''',
    re.VERBOSE | re.DOTALL
)

IPA_REMAINING_PATTERN = re.compile(
    r'['
    r'\u0250-\u02AF'  # IPA Extensions
    r'\u1D00-\u1D7F'  # Phonetic Extensions
    r'\u1D80-\u1DBF'  # Phonetic Extensions Supplement
    r'\u0300-\u036F'  # Combining Diacritical Marks
    r'\u02B0-\u02FF'  # Spacing Modifier Letters
    r'\u2070-\u209F'  # Superscripts (ⁿ etc.)
    r'\u0278\u0281'   # specific IPA symbols
    r'ʼ'
    r']+'
)

default_tts_engine = TTS_ENGINES['XTTS']
default_fine_tuned = 'internal'
default_vc_model = TTS_VOICE_CONVERSION['seed_vc']['path']
default_voice_detection_model = 'drewThomasson/segmentation'
# demucs voice separation checkpoint mirrored on HF (the official dl.fbaipublicfiles.com host is not reliable).
# file keeps its demucs name: <signature>-<sha256 prefix>.th, the prefix is checked again at load
default_voice_separation_model = dict(repo='drewThomasson/htdemucs', name='htdemucs', file='955717e8-8726e21a.th')
default_speaker = os.path.join(voices_dir, 'eng', 'adult', 'male', 'KumarDahl.wav')

tts_engines_from_coqui = [TTS_ENGINES['XTTS'], TTS_ENGINES['BARK'], TTS_ENGINES['TORTOISE'], TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['GLOWTTS'], TTS_ENGINES['TACOTRON'], TTS_ENGINES['YOURTTS']]
tts_engines_with_inner_speaker = [TTS_ENGINES['PIPER'], TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['GLOWTTS'], TTS_ENGINES['TACOTRON'], TTS_ENGINES['YOURTTS'], TTS_ENGINES['ORPHEUS'], TTS_ENGINES['OPENVOICE'], TTS_ENGINES['MELOTTS'], TTS_ENGINES['PHONON']]
tts_engines_with_custom_model = (TTS_ENGINES['PIPER'], TTS_ENGINES['XTTS'], TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['OMNIVOICE'], TTS_ENGINES['F5TTS'], TTS_ENGINES['ORPHEUS'], TTS_ENGINES['OPENVOICE'], TTS_ENGINES['MELOTTS'])

# audio.cpp engines (0xShug0/audio.cpp): one native audiocpp_server package per platform, shared by every audio.cpp
# engine, plus the GGUF weights of each engine's fine_tuned preset (presets/audiocpp_presets.py), driven by
# workers/audiocpp_worker.py. No torch, no venv (as ZONOS2).
# Release pinned for the official packages: asset names carry the tag and releases/latest points at side releases
# (v0.9.2-drama3-base-small). Bumping it re-downloads them once (a package whose install record names other urls)
audiocpp_version = '0.9.2'
audiocpp_release = f'https://github.com/0xShug0/audio.cpp/releases/download/v{audiocpp_version}/audio-v{audiocpp_version}'
audiocpp_packages = {
    # official release assets. Linux ones are built on Ubuntu 24.04: glibc 2.38 / GLIBCXX_3.4.32 / libgomp.so.1 floor
    # (a host missing the last two fails to start them and falls through to the next package); portable = runtime CPU
    # dispatch (libggml-cpu-<arch> picked at start, sse42 up to zen4 / sapphirerapids)
    "linux-x64-vulkan-acpp": {"urls": [f"{audiocpp_release}-bin-ubuntu-x64-vulkan-portable.tar.gz"], "gpu": True, "backend": "vulkan", "glibc_min": "2.38"},
    "linux-x64-cpu-acpp": {"urls": [f"{audiocpp_release}-bin-ubuntu-x64-cpu-portable.tar.gz"], "gpu": False, "glibc_min": "2.38"},
    "windows-x64-cuda13-acpp": {"urls": [f"{audiocpp_release}-bin-windows-x64-cuda13.3.zip", f"{audiocpp_release}-cudart-windows-x64-cuda13.3.zip"], "gpu": True, "backend": "cuda"},
    "windows-x64-cuda12-acpp": {"urls": [f"{audiocpp_release}-bin-windows-x64-cuda12.4.zip", f"{audiocpp_release}-cudart-windows-x64-cuda12.4.zip"], "gpu": True, "backend": "cuda"},
    "windows-x64-vulkan-acpp": {"urls": [f"{audiocpp_release}-bin-windows-x64-vulkan-portable.zip"], "gpu": True, "backend": "vulkan"},
    "windows-x64-cpu-acpp": {"urls": [f"{audiocpp_release}-bin-windows-x64-cpu-portable.zip"], "gpu": False},
    "macos-arm64-acpp": {"urls": [f"{audiocpp_release}-bin-macos-arm64-metal.tar.gz"], "gpu": True, "backend": "metal", "macos_min": "13.3"},
    "macos-arm64-cpu-acpp": {"urls": [f"{audiocpp_release}-bin-macos-arm64-metal.tar.gz"], "gpu": False, "macos_min": "13.3"},
    "macos-x86_64-acpp": {"urls": [f"{audiocpp_release}-bin-macos-x64-metal.tar.gz"], "gpu": False, "macos_min": "13.3"},
    # e2a's own builds (py-pkg release "audiocpp", made by py-pkg's audiocpp/build-audiocpp.sh, --tag
    # matching audiocpp_version): old glibc, no libgomp, CUDA runtime bundled, macOS 11. Off until published
    # published: linux-x64-cuda12 / -cuda13 with cudart, cuBLAS and cuFFT in lib/ (driver only), CPU part SSE4.2;
    # linux-x64-vulkan and -cpu-*: glibc 2.27, only libc/libm/libdl
    "linux-x64-cuda13": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-x64-cuda13.tar.gz"], "gpu": True, "backend": "cuda"},
    "linux-x64-cuda12": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-x64-cuda12.tar.gz"], "gpu": True, "backend": "cuda"},
    "linux-x64-vulkan": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-x64-vulkan.tar.gz"], "gpu": True, "backend": "vulkan", "cpu_flags": ["avx2", "fma", "f16c"]},
    "linux-x64-cpu-avx2": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-x64-cpu-avx2.tar.gz"], "gpu": False, "cpu_flags": ["avx2", "fma", "f16c", "bmi2"]},
    "linux-x64-cpu-sse42": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-x64-cpu-sse42.tar.gz"], "gpu": False, "cpu_flags": ["sse4_2"]},
    # published: Metal shaders embedded, macOS 11 on (audio.cpp's own macos-arm64-metal: 13.3)
    "macos-arm64": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-macos-arm64.tar.gz"], "gpu": True, "backend": "metal", "macos_min": "11.0"},
    "macos-arm64-cpu": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-macos-arm64.tar.gz"], "gpu": False, "macos_min": "11.0"},
    # published: the server and its Vulkan loader start on macOS 11, the bundled MoltenVK (the GPU path) needs macOS 12
    "macos-x86_64-vulkan": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-macos-x86_64-vulkan.tar.gz"], "gpu": True, "backend": "vulkan", "macos_min": "12.0"},
    "macos-x86_64": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-macos-x86_64.tar.gz"], "gpu": False, "macos_min": "11.0"},
    # no JetPack 5 (CUDA 11.4) package: audio.cpp needs CUDA 12 or newer, so Xavier and JetPack 5 Orin take the
    # linux-aarch64 CPU packages
    # published: JetPack's own CUDA libraries (6: CUDA 12.6, Ubuntu 22.04; 7: CUDA 13, Ubuntu 24.04), nothing bundled
    "jetson6-sm87": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-jetson6-sm87.tar.gz"], "gpu": True, "backend": "cuda", "jetpack": 6, "sm": [87]},
    "jetson7-sm87-sm110": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-jetson7-sm87-sm110.tar.gz"], "gpu": True, "backend": "cuda", "jetpack": 7, "sm": [87, 110]},
    # published (not linux-aarch64-cuda12, only built on request): ARM CUDA servers with cudart, cuBLAS and cuFFT in
    # lib/, CPU part ARMv8.2 + fp16; linux-aarch64(-v82, -vulkan): glibc 2.30, only libc/libm/libdl (+ libvulkan.so.1)
    "linux-aarch64-cuda13": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-aarch64-cuda13.tar.gz"], "gpu": True, "backend": "cuda", "cpu_flags": ["asimdhp"]},
    "linux-aarch64-cuda12": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-aarch64-cuda12.tar.gz"], "gpu": True, "backend": "cuda", "cpu_flags": ["asimdhp"], "enabled": False},
    # GPU through JetPack's own Vulkan driver where there is no CUDA package (Jetson Xavier, JetPack 5 Orin), and any
    # aarch64 Linux with a Vulkan driver; CPU part ARMv8.2 + fp16 (asimdhp), no dotprod (Xavier has none)
    "linux-aarch64-vulkan": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-aarch64-vulkan.tar.gz"], "gpu": True, "backend": "vulkan", "cpu_flags": ["asimdhp"]},
    "linux-aarch64-v82": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-aarch64-v82.tar.gz"], "gpu": False, "cpu_flags": ["asimddp", "asimdhp"]},
    "linux-aarch64": {"urls": ["https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/audiocpp/audiocpp-server-linux-aarch64.tar.gz"], "gpu": False}
}
# reference transcripts for the engines whose cloning takes one (ref_text below): transcribed once per voice clip by this
# ASR model, loaded in the same server only when needed and unloaded right after
audiocpp_asr = {"family": "qwen3_asr", "files": ["Qwen3-ASR-0.6B-GGUF/qwen3-asr-0.6b-q8_0.gguf"]}
audiocpp_repo = "audio-cpp/audio.cpp-gguf"

max_custom_model = 100
max_custom_voices = 1000

# devices each engine runs on ("devices" below): gradio's device list offers the ones found on this machine, convert_ebook()
# stops on any other. torch engines: every torch device, no Vulkan (torch has no Vulkan device). Native builds (zonos,
# audio.cpp): Vulkan too, their ROCm / XPU sessions run the Vulkan packages and MPS the Metal ones
torch_devices = [devices['CPU']['proc'], devices['CUDA']['proc'], devices['ROCM']['proc'], devices['XPU']['proc'], devices['MPS']['proc'], devices['JETSON']['proc']]
native_devices = torch_devices + [devices['VULKAN']['proc']]

default_engine_settings = {
    TTS_ENGINES['ZONOS']: {
        "version": "0.5.2",
        "packages": {
            "linux-x64-cuda13": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-x64-cuda13.tar.gz", "gpu": True},
            "linux-x64-cuda12": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-x64-cuda12.tar.gz", "gpu": True},
            "linux-x64-vulkan": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-x64-vulkan.tar.gz", "gpu": True, "cpu_flags": ["avx2", "fma", "f16c"]},
            "linux-x64-vulkan-zyphra": {"url": "https://github.com/Zyphra/zonos2.cpp/releases/latest/download/zonos2-linux-x64-vulkan.tar.gz", "gpu": True, "cpu_flags": ["avx2", "fma", "f16c"], "glibc_min": "2.34"},
            "linux-x64-cpu-avx2": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-x64-cpu-avx2.tar.gz", "gpu": False, "cpu_flags": ["avx2", "fma", "f16c", "bmi2"]},
            "linux-x64-cpu-sse42": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-x64-cpu-sse42.tar.gz", "gpu": False, "cpu_flags": ["sse4_2"]},
            "linux-x64-cpu-zyphra": {"url": "https://github.com/Zyphra/zonos2.cpp/releases/latest/download/zonos2-linux-x64-cpu.tar.gz", "gpu": False, "cpu_flags": ["avx512f", "avx512bw", "avx512vl", "avx512_vnni"], "glibc_min": "2.34"},
            "windows-x64-cuda13": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-windows-x64-cuda13.zip", "gpu": True},
            "windows-x64-cuda12": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-windows-x64-cuda12.zip", "gpu": True},
            "windows-x64-vulkan": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-windows-x64-vulkan.zip", "gpu": True, "cpu_flags": ["sse4_2"]},
            "windows-x64-vulkan-zyphra": {"url": "https://github.com/Zyphra/zonos2.cpp/releases/latest/download/zonos2-windows-x64-vulkan.zip", "gpu": True, "cpu_flags": ["avx2", "fma", "f16c"]},
            "windows-x64-cpu-avx2": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-windows-x64-cpu-avx2.zip", "gpu": False, "cpu_flags": ["avx2", "fma", "f16c", "bmi2"]},
            "windows-x64-cpu-sse42": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-windows-x64-cpu-sse42.zip", "gpu": False, "cpu_flags": ["sse4_2"]},
            "macos-arm64": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-macos-arm64.tar.gz", "gpu": True, "macos_min": 11},
            "macos-arm64-cpu": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-macos-arm64.tar.gz", "gpu": False, "macos_min": 11},
            "macos-arm64-metal": {"url": "https://github.com/Zyphra/zonos2.cpp/releases/latest/download/zonos2-macos-arm64-metal.tar.gz", "gpu": True, "macos_min": 15},
            "macos-x86_64-vulkan": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-macos-x86_64-vulkan.tar.gz", "gpu": True, "macos_min": 12},
            "macos-x86_64": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-macos-x86_64.tar.gz", "gpu": False, "macos_min": 11},
            "jetson5-sm72-sm87": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-jetson5-sm72-sm87.tar.gz", "gpu": True, "jetpack": 5, "sm": [72, 87]},
            "jetson6-sm87": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-jetson6-sm87.tar.gz", "gpu": True, "jetpack": 6, "sm": [87]},
            "jetson7-sm87-sm110": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-jetson7-sm87-sm110.tar.gz", "gpu": True, "jetpack": 7, "sm": [87, 110]},
            "linux-aarch64-cuda13": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-aarch64-cuda13.tar.gz", "gpu": True},
            "linux-aarch64-cuda12": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-aarch64-cuda12.tar.gz", "gpu": True},
            "linux-aarch64-v82": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-aarch64-v82.tar.gz", "gpu": False, "cpu_flags": ["asimddp", "asimdhp"]},
            "linux-aarch64": {"url": "https://github.com/ROBERT-MCDOWELL/py-pkg/releases/download/zonos2/zonos2-server-linux-aarch64.tar.gz", "gpu": False}
        },
        # GGUF weights (Hugging Face, e2a's tts_dir cache): the backbone file comes from the fine_tuned preset
        # (zonos_presets.py: Q4_K / Q6_K / Q8_0), the DAC decoder and the speaker encoder are shared
        "repo": "Zyphra/ZONOS2-GGUF",
        "dac": "dac.gguf",
        "spk": "spk-encoder.gguf",
        # official Tier 1 (en, Mandarin, ja) and Tier 2 languages. The model reads raw text, so the values are only
        # zonos2-server's own language codes (used by its optional text normalizer)
        "languages": {"eng": "en_us", "zho": "cmn", "jpn": "ja", "kor": "ko", "rus": "ru", "ita": "it", "por": "pt_br", "fra": "fr_fr", "spa": "es", "vie": "vi", "deu": "de", "heb": "he", "nld": "nl"},
        "samplerate": 44100,
        # emotion off by default; on, every slider at 0 is exactly the plain cloned voice (ZONOS2 adds the
        # sliders' directions to the speaker embedding), so users move away from it gradually
        "emotion_enabled": False,
        "emotion": {"happy": 0.0, "sad": 0.0, "angry": 0.0, "surprised": 0.0, "valence": 0.0, "arousal": 0.0},
        # multiplier on the server's per-speaker calibration of the emotion directions
        "emotion_strength": 1.0,
        # emotion guidance, 1.0 = off (the server runs with --batch 2 so any value is accepted)
        "emotion_cfg_scale": 1.0,
        # 0 = the model's own pace, else speaking-rate conditioning (about 10 slow, 15 natural, 30 fast)
        "speaking_rate": 0.0,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        "devices": native_devices,
        "rating": {"VRAM": 6, "CPU": 3, "RAM": 8, "Realism": 5}
    },
    TTS_ENGINES['GPTSOVITS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/gptsovits) behind a persistent
        # worker, from the pinned source tree: upstream is not a package, it runs from its repo root
        "repo": "lj1995/GPT-SoVITS",
        "source": "https://github.com/RVC-Boss/GPT-SoVITS/archive/e7cd61ec3dcc9a34089f50ed169e3103a16ad675.tar.gz",
        "python": "3.12",
        # package list = upstream's own requirements.txt (in the extracted tree), torch from the device's
        # PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback.
        # Left out: what inference never imports (webui, api, dataset / ASR tools, training) and the two
        # C builds: pyopenjtalk (pyopenjtalk-plus = same module, prebuilt wheels) and jieba_fast (the
        # worker aliases jieba). Names normalized as pip does (lowercase, - for _ and .).
        "requirements_exclude": ["gradio", "fastapi", "funasr", "modelscope", "tensorboard", "onnxruntime-gpu", "pyopenjtalk", "jieba-fast"],
        # torch is added by the install itself (torch_matrix 'last' for the device tag, or upstream's own
        # spec when it locks torch or caps it below that); onnxruntime replaces
        # the dropped onnxruntime-gpu; loguru / rich are hard imports upstream only gets through
        # fastapi[standard]; soundfile backs e2a's sitecustomize torchaudio.load shim (so no torchcodec);
        # nltk / matplotlib for the english frontend and utils; faster-whisper transcribes v5 references
        # hf_xet: huggingface_hub 0.36 only requires it when platform_machine is exactly x86_64 / amd64 /
        # arm64 / aarch64, and windows reports AMD64, so windows misses the fast Xet downloads; same range
        "requirements_extra": ["onnxruntime", "pyopenjtalk-plus", "loguru", "rich", "resampy", "soundfile", "nltk", "matplotlib", "faster-whisper", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler: the resolver takes the
        # newest release that has a wheel there (e.g. numba 0.68 / llvmlite 0.50 have no intel macOS
        # wheels, 0.62 / 0.45 do). These three only exist as pure-python sources.
        "packages_sdist": ["jieba", "g2p-en", "distance"],
        # weights every version loads; paths in the HF repo = paths under GPT_SoVITS/pretrained_models
        "weights": ["chinese-roberta-wwm-ext-large/*", "chinese-hubert-base/*", "s1v3.ckpt", "sv/pretrained_eres2netv2w24s4ep4.ckpt"],
        # upstream refuses references outside 3-10 s; the worker cuts a clip within this window
        "ref_min": 3.2,
        "ref_max": 9.5,
        "asr_model": "large-v3-turbo",
        "languages": {"eng": "en", "zho": "zh", "jpn": "ja", "kor": "ko"},
        "samplerate": 32000,
        "speed": 1.0,
        "top_k": 15,
        "top_p": 1.0,
        "temperature": 1.0,
        "repetition_penalty": 1.35,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 4, "CPU": 2, "RAM": 8, "Realism": 4}
    },
    TTS_ENGINES['OMNIVOICE']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/omnivoice) behind a persistent worker
        "repo": "k2-fsa/OmniVoice",
        "source": "https://github.com/k2-fsa/OmniVoice/archive/08be0b4ccbac3e13e374e86fbfead4b4cac343e2.tar.gz",
        "python": "3.12",
        # package list = upstream's own pyproject.toml dependencies (in the extracted tree), torch from the
        # device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback;
        # upstream's torch floor (torch>=2.4) stops devices that cannot reach it with a clear alert.
        # Left out: gradio (demo UI), tensorboardX / webdataset (training). Names normalized as pip does.
        "requirements_exclude": ["gradio", "tensorboardx", "webdataset"],
        "requirements_extra": [],
        # every package installs as a wheel, so no platform ever needs a compiler
        "packages_sdist": [],
        # reference transcription for the voice clone prompt (OmniVoice's own Whisper, run on cpu); one copy under
        # models/tts shared with the other engines using it
        "asr_model": "openai/whisper-large-v3-turbo",
        # the worker cuts a reference clip within this window (upstream asks for 3-10 s)
        "ref_min": 3.2,
        "ref_max": 9.5,
        # e2a's iso-639-3 codes -> OmniVoice language ids: all 646 of upstream's docs/lang_id_name_map.tsv
        "languages": {"aae": "aae", "aal": "aal", "aao": "aao", "abb": "abb", "abk": "ab", "abn": "abn", "abr": "abr", "abs": "abs", "abv": "abv", "acm": "acm", "acw": "acw", "acx": "acx", "adf": "adf", "adx": "adx", "ady": "ady", "aeb": "aeb", "aec": "aec", "afb": "afb", "afo": "afo", "afr": "af", "ahl": "ahl", "ahs": "ahs", "ajg": "ajg", "aju": "aju", "ala": "ala", "aln": "aln", "alo": "alo", "amh": "am", "amu": "amu", "anc": "anc", "ank": "ank", "anp": "anp", "anw": "anw", "aom": "aom", "apc": "apc", "apd": "apd", "ara": "arb", "arg": "an", "arq": "arq", "ars": "ars", "ary": "ary", "arz": "arz", "asm": "as", "ast": "ast", "avl": "avl", "awo": "awo", "ayl": "ayl", "ayp": "ayp", "aze": "az", "bag": "bag", "bak": "ba", "bas": "bas", "bax": "bax", "bba": "bba", "bbj": "bbj", "bbl": "bbl", "bbu": "bbu", "bce": "bce", "bci": "bci", "bcs": "bcs", "bcy": "bcy", "bda": "bda", "bde": "bde", "bdm": "bdm", "beb": "beb", "bel": "be", "ben": "bn", "bew": "bew", "bfd": "bfd", "bft": "bft", "bgp": "bgp", "bhb": "bhb", "bhh": "bhh", "bho": "bho", "bhp": "bhp", "bhr": "bhr", "bjj": "bjj", "bjk": "bjk", "bjn": "bjn", "bjt": "bjt", "bkh": "bkh", "bkm": "bkm", "bky": "bky", "bmm": "bmm", "bmq": "bmq", "bnm": "bnm", "bnn": "bnn", "bns": "bns", "bod": "bo", "bos": "bs", "bou": "bou", "bqg": "bqg", "bra": "bra", "bre": "br", "brh": "brh", "bri": "bri", "brx": "brx", "bsh": "bsh", "bsj": "bsj", "bsk": "bsk", "btm": "btm", "btv": "btv", "bug": "bug", "bul": "bg", "bum": "bum", "buo": "buo", "bux": "bux", "bwr": "bwr", "bxf": "bxf", "byc": "byc", "bys": "bys", "byv": "byv", "byx": "byx", "bzc": "bzc", "bzw": "bzw", "cat": "ca", "ccg": "ccg", "ceb": "ceb", "cen": "cen", "ces": "cs", "cfa": "cfa", "cgg": "cgg", "chq": "chq", "chv": "cv", "cjk": "cjk", "ckb": "ckb", "ckl": "ckl", "ckr": "ckr", "cky": "cky", "cnh": "cnh", "cor": "kw", "cpy": "cpy", "cte": "cte", "ctl": "ctl", "cut": "cut", "cux": "cux", "cym": "cy", "dag": "dag", "dan": "da", "dar": "dar", "dav": "dav", "dbd": "dbd", "dcc": "dcc", "deg": "deg", "deu": "de", "dgh": "dgh", "dgo": "dgo", "div": "dv", "dje": "dje", "dmk": "dmk", "dml": "dml", "dru": "dru", "dty": "dty", "dua": "dua", "dyu": "dyu", "dzg": "dzg", "ebr": "ebr", "ebu": "ebu", "ego": "ego", "eiv": "eiv", "eko": "eko", "ekr": "ekr", "ell": "el", "elm": "elm", "eng": "en", "epo": "eo", "est": "et", "esu": "esu", "eto": "eto", "ets": "ets", "etu": "etu", "eus": "eu", "ewo": "ewo", "ext": "ext", "eyo": "eyo", "fan": "fan", "fas": "fa", "fat": "fat", "ffm": "ffm", "fia": "fia", "fil": "fil", "fin": "fi", "fip": "fip", "fkk": "fkk", "fmp": "fmp", "fra": "fr", "fry": "fy", "fub": "fub", "fuc": "fuc", "fue": "fue", "fuf": "fuf", "fuh": "fuh", "fui": "fui", "ful": "ff", "fuq": "fuq", "fuv": "fuv", "gbm": "gbm", "gbr": "gbr", "gby": "gby", "gcc": "gcc", "gdf": "gdf", "gej": "gej", "ges": "ges", "ggg": "ggg", "gid": "gid", "gig": "gig", "giz": "giz", "gjk": "gjk", "gju": "gju", "gle": "ga", "glg": "gl", "glv": "gv", "glw": "glw", "gol": "gol", "gom": "gom", "grn": "gn", "gsl": "gsl", "gui": "gui", "guj": "gu", "gur": "gur", "guz": "guz", "gwc": "gwc", "gwe": "gwe", "gwt": "gwt", "gya": "gya", "gyz": "gyz", "hah": "hah", "hao": "hao", "hat": "ht", "hau": "ha", "haw": "haw", "haz": "haz", "hbb": "hbb", "heb": "he", "hem": "hem", "her": "hz", "hia": "hia", "hin": "hi", "hkk": "hkk", "hla": "hla", "hno": "hno", "hoj": "hoj", "hrv": "hr", "hsb": "hsb", "hue": "hue", "hul": "hul", "hun": "hu", "hux": "hux", "hwo": "hwo", "hye": "hy", "ibb": "ibb", "ibo": "ig", "ida": "ida", "idu": "idu", "ijc": "ijc", "ijn": "ijn", "ikw": "ikw", "ina": "ia", "ind": "id", "ipk": "ik", "ish": "ish", "isl": "is", "iso": "iso", "ita": "it", "its": "its", "itw": "itw", "itz": "itz", "jal": "jal", "jav": "jv", "jax": "jax", "jgo": "jgo", "jmx": "jmx", "jns": "jns", "jpn": "ja", "jqr": "jqr", "juk": "juk", "juo": "juo", "kab": "kab", "kai": "kai", "kaj": "kaj", "kam": "kam", "kan": "kn", "kas": "ks", "kat": "ka", "kaz": "kk", "kbd": "kbd", "kbl": "kbl", "kbt": "kbt", "kcq": "kcq", "kdh": "kdh", "kea": "kea", "keu": "keu", "kfe": "kfe", "kfk": "kfk", "kfp": "kfp", "khg": "khg", "khm": "km", "khw": "khw", "kin": "rw", "kir": "ky", "kjc": "kjc", "kjk": "kjk", "kln": "kln", "kls": "kls", "kmr": "kmr", "kmy": "kmy", "kna": "kna", "knn": "knn", "kol": "kol", "koo": "koo", "kor": "ko", "kpo": "kpo", "kqo": "kqo", "ksd": "ksd", "ksf": "ksf", "kto": "kto", "kua": "kj", "kuh": "kuh", "kvx": "kvx", "kwm": "kwm", "kxp": "kxp", "kyx": "kyx", "lag": "lag", "lao": "lo", "lav": "lv", "lcm": "lcm", "ldb": "ldb", "lij": "lij", "lin": "ln", "lir": "lir", "lit": "lt", "lkb": "lkb", "lla": "lla", "lnu": "lnu", "loa": "loa", "lrk": "lrk", "lss": "lss", "ltg": "ltg", "lto": "lto", "ltz": "lb", "lua": "lua", "lug": "lg", "luo": "luo", "lus": "lus", "lwg": "lwg", "mab": "mab", "maf": "maf", "mai": "mai", "mal": "ml", "mar": "mr", "mau": "mau", "max": "max", "mbo": "mbo", "mcf": "mcf", "mcn": "mcn", "mcx": "mcx", "mdd": "mdd", "mde": "mde", "mdf": "mdf", "mek": "mek", "mer": "mer", "meu": "meu", "mfm": "mfm", "mfn": "mfn", "mfo": "mfo", "mfv": "mfv", "mgg": "mgg", "mgi": "mgi", "mhk": "mhk", "mhr": "mhr", "mig": "mig", "miu": "miu", "mkd": "mk", "mkf": "mkf", "mki": "mki", "mlg": "plt", "mlq": "mlq", "mlt": "mt", "mne": "mne", "mni": "mni", "mon": "mn", "mqy": "mqy", "mri": "mi", "mrj": "mrj", "mrr": "mrr", "mrt": "mrt", "mse": "mse", "msh": "msh", "msw": "msw", "mtr": "mtr", "mtu": "mtu", "mtx": "mtx", "mua": "mua", "mug": "mug", "mui": "mui", "mve": "mve", "mvy": "mvy", "mxs": "mxs", "mxu": "mxu", "mxy": "mxy", "mya": "my", "myv": "myv", "mzl": "mzl", "nal": "nal", "nan": "nan", "nap": "nap", "nbh": "nbh", "ncf": "ncf", "nco": "nco", "ncx": "ncx", "ndi": "ndi", "ndo": "ng", "ngi": "ngi", "nhg": "nhg", "nhi": "nhi", "nhn": "nhn", "nhq": "nhq", "nja": "nja", "nla": "nla", "nld": "nl", "nlv": "nlv", "nmg": "nmg", "nmz": "nmz", "nnh": "nnh", "nno": "nn", "nob": "nb", "noe": "noe", "nor": "no", "npi": "npi", "nso": "nso", "nya": "ny", "nyu": "nyu", "oci": "oc", "odk": "odk", "odu": "odu", "ogo": "ogo", "orc": "orc", "orm": "om", "oru": "oru", "ory": "ory", "oss": "os", "pan": "pa", "pbs": "pbs", "pbt": "pbt", "pbu": "pbu", "pcm": "pcm", "pex": "pex", "phl": "phl", "phr": "phr", "pip": "pip", "piy": "piy", "pko": "pko", "plk": "plk", "pmq": "pmq", "pms": "pms", "pmy": "pmy", "pnb": "pnb", "poc": "poc", "poe": "poe", "pol": "pl", "por": "pt", "pow": "pow", "prq": "prq", "pst": "pst", "pua": "pua", "pus": "ps", "pwn": "pwn", "qug": "qug", "qum": "qum", "qup": "qup", "qur": "qur", "qus": "qus", "quv": "quv", "qux": "qux", "quy": "quy", "qva": "qva", "qvi": "qvi", "qvj": "qvj", "qvl": "qvl", "qwa": "qwa", "qws": "qws", "qxa": "qxa", "qxp": "qxp", "qxt": "qxt", "qxu": "qxu", "qxw": "qxw", "rag": "rag", "rob": "rob", "rof": "rof", "roh": "rm", "ron": "ro", "roo": "roo", "rth": "rth", "rup": "rup", "rus": "ru", "sah": "sah", "san": "sa", "sat": "sat", "sau": "sau", "say": "say", "sbn": "sbn", "scl": "scl", "scn": "scn", "sei": "sei", "shu": "shu", "sin": "si", "sip": "sip", "siw": "siw", "sjr": "sjr", "skg": "skg", "skr": "skr", "slk": "sk", "sln": "sl", "sna": "sn", "snc": "snc", "snd": "sd", "snk": "snk", "sol": "sol", "som": "so", "spa": "es", "sps": "sps", "sqi": "sq", "src": "src", "srd": "sc", "sro": "sro", "srp": "sr", "ssi": "ssi", "ste": "ste", "sua": "sua", "sva": "sva", "swe": "sv", "swh": "sw", "szy": "szy", "tam": "ta", "tan": "tan", "tar": "tar", "tat": "tt", "tay": "tay", "tbf": "tbf", "tcf": "tcf", "tcy": "tcy", "tdn": "tdn", "tdx": "tdx", "tel": "te", "tgc": "tgc", "tgk": "tg", "tha": "th", "the": "the", "thq": "thq", "thr": "thr", "thv": "thv", "tig": "tig", "tio": "tio", "tir": "ti", "tkg": "tkg", "tkt": "tkt", "tli": "tli", "tlp": "tlp", "tok": "tok", "tpl": "tpl", "tpz": "tpz", "tqp": "tqp", "trp": "trp", "trq": "trq", "trv": "trv", "trw": "trw", "tsn": "tn", "ttj": "ttj", "ttr": "ttr", "ttu": "ttu", "tui": "tui", "tuk": "tk", "tul": "tul", "tuq": "tuq", "tur": "tr", "tuv": "tuv", "tuy": "tuy", "tvo": "tvo", "tvu": "tvu", "twi": "tw", "twu": "twu", "txs": "txs", "txy": "txy", "udl": "udl", "uig": "ug", "uki": "uki", "ukr": "uk", "umb": "umb", "urd": "ur", "ush": "ush", "uzb": "uz", "uzn": "uzn", "vai": "vai", "var": "var", "ver": "ver", "vie": "vi", "vmc": "vmc", "vmj": "vmj", "vmm": "vmm", "vmp": "vmp", "vmz": "vmz", "vot": "vot", "vro": "vro", "wbl": "wbl", "wci": "wci", "weo": "weo", "wes": "wes", "wja": "wja", "wji": "wji", "wof": "wof", "wol": "wo", "xhe": "xhe", "xho": "xh", "xka": "xka", "xmf": "xmf", "xmv": "xmv", "xmw": "xmw", "xpe": "xpe", "xti": "xti", "xtu": "xtu", "yaq": "yaq", "yav": "yav", "yay": "yay", "ydd": "ydd", "ydg": "ydg", "yer": "yer", "yes": "yes", "yid": "yi", "yor": "yo", "yue": "yue", "zga": "zga", "zgh": "zgh", "zho": "zh", "zlm": "ms", "zoc": "zoc", "zoh": "zoh", "zor": "zor", "zpv": "zpv", "zpy": "zpy", "ztg": "ztg", "ztn": "ztn", "ztp": "ztp", "zts": "zts", "ztu": "ztu", "zul": "zu", "zza": "zza"},
        "samplerate": 24000,
        # upstream defaults: 32 unmasking steps (16 = faster), classifier-free guidance 2.0
        "num_step": 32,
        "guidance_scale": 2.0,
        "speed": 1.0,
        # custom model upload: a fine-tuned OmniVoice checkpoint (save_pretrained folder) + ref.wav; its
        # audio_tokenizer / chat_template come from the base model when the upload does not carry them
        "files": ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json", "ref.wav"],
        "voice": default_speaker,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 4, "CPU": 3, "RAM": 8, "Realism": 5}
    },
    TTS_ENGINES['F5TTS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/f5tts) behind a persistent worker
        "repo": "SWivid/F5-TTS",
        "source": "https://github.com/SWivid/F5-TTS/archive/2f866649b779881af8bd644e76b9a6d95053da29.tar.gz",
        "python": "3.12",
        # package list = upstream's own pyproject.toml dependencies (in the extracted tree), torch from the
        # device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback.
        # Left out: what inference never imports (gradio demo UI, bitsandbytes training optimizer, cached_path /
        # hydra-core used only by upstream's api / cli / socket server, transformers_stream_generator unused) and
        # torchcodec (the worker reads audio with soundfile). wandb / datasets / accelerate / ema_pytorch stay:
        # f5_tts.model imports its Trainer. Names normalized as pip does. onnxruntime (cpu) runs the Arabic
        # diacritizer below. transformers 5.0.0 left out: its ASR pipeline pops the num_frames its own Whisper feature
        # extractor no longer returns (KeyError on every reference transcription; 4.57 and 5.1+ are consistent), and
        # the <5.1 cap for torch < 2.4 (jetson5) lands exactly on it: those devices get 4.57 instead. datasets and
        # transformers get floors, upstream leaves them open and the resolver backtracks to releases that break:
        # datasets < 2.14.7 subclasses pa.PyExtensionType (gone since pyarrow 21), the pick on jetson where the fsspec
        # DeviceInstaller put in the venv rules out every newer datasets; with the <5.1 cap, datasets 5.2+
        # (huggingface-hub >= 1.31) drags transformers back to 2.x.
        "requirements_exclude": ["gradio", "bitsandbytes", "cached-path", "hydra-core", "transformers-stream-generator", "torchcodec"],
        "requirements_extra": ["onnxruntime", "datasets>=2.14.7", "transformers>=4.57,!=5.0.0"],
        # every package installs as a wheel, so no platform ever needs a compiler; encodec (vocos' dependency)
        # only exists as a pure-python source
        "packages_sdist": ["encodec"],
        # installed without their dependencies: catt-tashkeel declares onnxruntime-gpu (no macOS wheels, and the
        # cpu build is plenty for it)
        "packages_nodeps": ["catt-tashkeel==1.0.2"],
        "vocoder": "charactr/vocos-mel-24khz",
        # Arabic diacritization (SILMA's own choice, CATT encoder-only ONNX model), for checkpoints with tashkeel True
        "tashkeel": {"url": "https://github.com/abjadai/catt/releases/download/v2/eo_model_onnx.zip", "dir": "abjadai--catt-eo_model"},
        # reference transcription (F5-TTS clones from audio + its text), upstream's own Whisper, run on cpu; one
        # copy under models/tts shared with the other engines using it
        "asr_model": "openai/whisper-large-v3-turbo",
        # upstream clips references at 12 s (a checkpoint may set its own); no minimum: silence padding would slow
        # the speech, as F5-TTS derives the generated duration from the reference's seconds per character
        "ref_max": 12.0,
        # languages a checkpoint exists for (presets/f5tts_presets.py: v1 base for eng/zho, community models)
        "languages": {"eng": "en", "zho": "zh", "fra": "fr", "deu": "de", "ita": "it", "rus": "ru", "spa": "es", "fin": "fi", "hin": "hi", "lav": "lv", "jpn": "ja", "ara": "ar"},
        "samplerate": 24000,
        # upstream defaults (utils_infer.py)
        "nfe_step": 32,
        "cfg_strength": 2.0,
        "sway_sampling_coef": -1.0,
        "speed": 1.0,
        "cross_fade_duration": 0.15,
        "target_rms": 0.1,
        # custom model upload: a fine-tuned checkpoint (EMA weights as safetensors), its vocab, its DiT config
        # (SHARED.md "Config" line as json) + ref.wav; vocoder and ASR are the base ones
        "files": ["config.json", "model.safetensors", "vocab.txt", "ref.wav"],
        "voice": default_speaker,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 3, "CPU": 1, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['ORPHEUS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/orpheus) behind a persistent worker. Upstream's own
        # runtime is vllm (Linux CUDA only, its own torch pin): the worker runs upstream's transformers path instead
        # (its Colab notebooks), same prompt format and SNAC code layout, so every e2a torch device runs it
        # repo: ungated copy of the gated canopylabs/orpheus-3b-0.1-ft (English), also the tokenizer for checkpoints
        # shipped without one (the Llama 3 BPE every Orpheus model shares: only text tokens come from it)
        "repo": "unsloth/orpheus-3b-0.1-ft",
        "source": "https://github.com/canopyai/Orpheus-TTS/archive/e64661fe6d02c414fc77c53578c9d64082614861.tar.gz",
        "python": "3.12",
        # package list = upstream's own install_requires (orpheus_tts_pypi/setup.py in the extracted tree: snac,
        # vllm), torch from the device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller
        # as fallback. Left out: vllm. The orpheus_tts package is not installed either: it imports vllm and loads SNAC
        # onto cuda at import. transformers / accelerate run the model, soundfile writes the parts; hf_xet as for
        # GPT-SoVITS (windows reports AMD64, so huggingface_hub's own marker misses it: the checkpoints are on Xet)
        "requirements_file": "orpheus_tts_pypi/setup.py",
        "requirements_exclude": ["vllm"],
        "requirements_extra": ["transformers", "accelerate", "soundfile", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler
        "packages_sdist": [],
        # audio codec the model's tokens decode with (24 kHz, 7 tokens per frame)
        "snac": "hubertsiuzdak/snac_24khz",
        # languages a fine-tuned checkpoint exists for (presets/orpheus_presets.py): English, and the multilingual
        # research release (gated canopylabs repos: HF_TOKEN of an account that accepted their conditions)
        "languages": {"eng": "en", "fra": "fr", "deu": "de", "kor": "ko", "hin": "hi", "zho": "zh", "spa": "es", "ita": "it"},
        "samplerate": 24000,
        # upstream's realtime example (realtime_streaming_example/main.py): steadier than the package defaults for
        # narration. repetition_penalty >= 1.1 keeps generation stable, higher (with temperature) speaks faster
        "temperature": 0.4,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        # generation cap per sentence part: tokens_per_char x its length (~82 tokens per second of speech; 20 per
        # character is ~3x a latin letter's speech, a Han / kana / Hangul character counts as 3), at most
        # max_new_tokens (~50 s): a looping generation stops there instead of at upstream's 1200 (~14.6 s), which
        # cuts long sentences
        "tokens_per_char": 20,
        "max_new_tokens": 4096,
        # custom model upload: an Orpheus fine-tune (unsloth / upstream finetune/train.py save_pretrained folder),
        # its tokenizer + ref.wav. An optional "orpheus_speaker" key in its config.json is the speaker name it was
        # trained with (multi-speaker fine-tunes); without it the text is prompted bare (single-speaker fine-tunes)
        "files": ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json", "ref.wav"],
        # this required file may come sharded instead: <file>.index.json + every shard its weight_map names
        # (save_pretrained's default for a 3B model, e.g. model-00001-of-00002.safetensors)
        "files_sharded": "model.safetensors",
        # built-in speakers (as Piper): "default" speaks with the preset's speaker, a voice file converts a
        # same-gender built-in speaker with default_vc_model
        "voice": None,
        "voices": {},
        # 3.3B params: bf16 / fp16 on GPU, fp32 on CPU (~40x slower than real time there)
        "devices": torch_devices,
        "rating": {"VRAM": 7, "CPU": 1, "RAM": 14, "Realism": 5}
    },
    TTS_ENGINES['SPARKTTS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/sparktts) behind a persistent worker, from the pinned
        # source tree: upstream is not a package, the worker imports sparktts from the extracted repo root. Same
        # pipeline as Orpheus: a Qwen2.5-0.5B LLM (transformers) writes BiCodec tokens, BiCodec decodes them to 16 kHz.
        # repo: the LLM, BiCodec and the wav2vec2-large-xlsr-53 the references are tokenized with, in one folder
        "repo": "SparkAudio/Spark-TTS-0.5B",
        "source": "https://github.com/SparkAudio/Spark-TTS/archive/2f1ea9082400547242641f5271b6f941c9f439d1.tar.gz",
        "python": "3.12",
        # package list = upstream's own requirements.txt (in the extracted tree), torch from the device's PyTorch index
        # (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback. Left out: gradio (webui).
        # requirements_unpinned: upstream pins every package to its February 2025 release (torch 2.5.1 has no Blackwell
        # kernels nor torch_matrix's newer builds, transformers 4.46.2 no recent tokenizers wheels): names only, the
        # resolver takes what fits the device's torch. accelerate: the worker loads the LLM straight onto the GPU
        # (device_map, transformers needs it), upstream's list has none. transformers 5.0.0 left out: its Whisper
        # pipeline breaks the reference transcription (see F5-TTS). hf_xet as for GPT-SoVITS (windows reports AMD64,
        # so huggingface_hub's own marker misses it: the weights are on Xet)
        "requirements_file": "requirements.txt",
        "requirements_unpinned": True,
        "requirements_exclude": ["gradio"],
        "requirements_extra": ["accelerate", "transformers!=5.0.0", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler
        "packages_sdist": [],
        # reference transcription (the voice clone prompt is the reference's audio tokens + its text), Whisper run on
        # cpu; one copy under models/tts shared with the other engines using it
        "asr_model": "openai/whisper-large-v3-turbo",
        # the worker cuts a reference clip of at most ref_max seconds; no minimum: BiCodec repeats a short reference
        # itself for the speaker tokens (6 s window), silence padding would end up in the prompt
        "ref_max": 10.0,
        # upstream's languages (no language token: the text alone tells)
        "languages": {"eng": "en", "zho": "zh"},
        "samplerate": 16000,
        # upstream defaults (cli/SparkTTS.py inference)
        "temperature": 0.8,
        "top_k": 50,
        "top_p": 0.95,
        # generation cap per sentence part: tokens_per_char x its length (50 semantic tokens per second of speech; 10 per
        # character is ~3x a latin letter's speech, a Han character counts as 3), at most max_new_tokens (upstream's
        # 3000, 60 s): a looping generation stops there
        "tokens_per_char": 10,
        "max_new_tokens": 3000,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        # 0.5B LLM (bf16 from sm 8.0, fp32 below) + BiCodec + wav2vec2-large (fp32)
        "devices": torch_devices,
        "rating": {"VRAM": 3, "CPU": 2, "RAM": 6, "Realism": 4}
    },
    TTS_ENGINES['CHATTTS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/chattts) behind a persistent worker, from the pinned
        # source tree: the worker imports ChatTTS from the extracted repo root (the PyPI package is older: this commit's
        # tokenizer follows the latest transformers). A 20 layer Llama (transformers) writes DVAE codes, ChatTTS'
        # decoder and Vocos turn them into 24 kHz audio.
        # repo: GPT, DVAE (its encoder tokenizes the voice references), decoder, Vocos and tokenizer, under asset/
        "repo": "2Noise/ChatTTS",
        "source": "https://github.com/2noise/ChatTTS/archive/77b89ee281cd479f5b1a787ada330dc975ca1f2a.tar.gz",
        "python": "3.12",
        # package list = upstream's own install_requires (setup.py in the extracted tree, read as Orpheus' is: its
        # requirements.txt adds the webui, the IPython examples and the Linux-only pynini text normalizers), torch from
        # the device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback.
        # requests: ChatTTS.utils imports it, setup.py misses it (upstream fixed requirements.txt only); accelerate:
        # the worker loads the GPT straight onto the GPU (device_map, transformers needs it), no host copy first;
        # transformers 5.0.0 left out: its Whisper pipeline breaks the reference transcription (see F5-TTS);
        # soundfile / soxr cut and resample the voice references; hf_xet as for GPT-SoVITS (windows reports AMD64, so
        # huggingface_hub's own marker misses it)
        "requirements_file": "setup.py",
        "requirements_exclude": [],
        "requirements_extra": ["requests", "accelerate", "transformers!=5.0.0", "soundfile", "soxr", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler; encodec (vocos' dependency) only
        # exists as a pure-python source
        "packages_sdist": ["encodec"],
        # reference transcription (the voice clone prompt is the reference's DVAE codes + its text), Whisper run on
        # cpu; one copy under models/tts shared with the other engines using it
        "asr_model": "openai/whisper-large-v3-turbo",
        # the worker cuts a reference clip of at most ref_max seconds (its codes are part of every prompt)
        "ref_max": 10.0,
        # upstream's languages (no language token: lang only picks its text normalizer). The voice file must speak one
        # of them too: its transcript is part of the clone prompt, so the conversion stops on any other voice file
        "languages": {"eng": "en", "zho": "zh"},
        "samplerate": 24000,
        # upstream defaults (Chat.InferCodeParams)
        "temperature": 0.3,
        "top_k": 20,
        "top_p": 0.7,
        "repetition_penalty": 1.05,
        # upstream's [speed_N] prompt token: 0 (slowest) to 9, 5 by default
        "speed": 5,
        # generation cap per sentence part: tokens_per_char x its length (46.875 codes per second of speech; 10 per
        # character is ~3x a latin letter's speech, a Han character counts as 3), at most max_new_tokens (upstream's
        # 2048, ~43 s): a looping generation stops there
        "tokens_per_char": 10,
        "max_new_tokens": 2048,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        # 0.2B GPT + DVAE, decoder and Vocos (0.3B in all), all fp32: upstream asks 4 GB VRAM for 30 s of audio
        "devices": torch_devices,
        "rating": {"VRAM": 4, "CPU": 2, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['OPENVOICE']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/openvoice) behind a persistent worker. OpenVoice V2 as
        # upstream's demo_part3 runs it: MeloTTS speaks with its base speakers, OpenVoice's ToneColorConverter moves the base
        # speaker's tone color to the voice file's. repo: the converter and every base speaker's tone color embedding
        "repo": "myshell-ai/OpenVoiceV2",
        "source": "https://github.com/myshell-ai/OpenVoice/archive/74a1d147b17a8c3092dd5430504bd83ef6c7eb23.tar.gz",
        "source_melo": "https://github.com/myshell-ai/MeloTTS/archive/209145371cff8fc3bd60d7be902ea69cbdb7965a.tar.gz",
        "python": "3.12",
        # package list = OpenVoice's own install_requires (setup.py) + MeloTTS' requirements.txt (in the extracted trees),
        # torch from the device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback.
        # Left out: what inference never imports (faster-whisper / whisper-timestamped: se_extractor's VAD split, gradio:
        # demo UI, tensorboard: training, cached-path: melo's own downloads, done by the worker), the pins without py3.12
        # wheels (numpy 1.22.0, transformers 4.27.4 -> tokenizers 0.13, fugashi 1.3.0), unidic (770 MB
        # dictionary fetched by a post-install command: MeCab reads unidic-lite without it) and mecab-python3 (its MeCab
        # folder is python-mecab-ko's mecab folder on case-insensitive filesystems: the worker serves MeCab from fugashi,
        # same libmecab, same dictionary). Names normalized as pip does.
        "requirements_file": "setup.py",
        "requirements_file_melo": "requirements.txt",
        "requirements_exclude": ["faster-whisper", "whisper-timestamped", "gradio", "tensorboard", "cached-path", "numpy", "transformers", "fugashi", "unidic", "mecab-python3"],
        # transformers below 5: melo's BERT frontends are written for 4.x; soxr: transformers imports it whenever librosa
        # is there (librosa >= 0.10 brings it, upstream's 0.9.1 does not); setuptools below 82: librosa 0.9.1 imports
        # pkg_resources, gone from 82 on (torch 2.11 / 2.12 cap it there, 2.13 does not); fugashi unpinned: the japanese
        # BERT tokenizer and the MeCab stand-in; python-mecab-ko: g2pkk (korean) pip-installs it at runtime otherwise;
        # hf_xet as for GPT-SoVITS (windows reports AMD64, so huggingface_hub's own marker misses it: the weights are on Xet)
        "requirements_extra": ["transformers<5", "soxr", "setuptools<82", "fugashi", "python-mecab-ko", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler; these only exist as pure-python sources
        "packages_sdist": ["jieba", "eng-to-ipa", "langid", "txtsplit", "unidic-lite", "gruut", "gruut-ipa", "gruut-lang-de", "gruut-lang-en", "gruut-lang-es", "gruut-lang-fr", "docopt", "distance"],
        # MeloTTS' text frontend BERTs (melo/text/*_bert.py) by MeloTTS language: the worker fetches every tokenizer (melo
        # loads them all at import) and the language's weights, as plain folders under models/tts/openvoice
        "berts": {"EN": "bert-base-uncased", "ES": "dccuchile/bert-base-spanish-wwm-uncased", "FR": "dbmdz/bert-base-french-europeana-cased", "ZH": "bert-base-multilingual-uncased", "JP": "tohoku-nlp/bert-base-japanese-v3", "KR": "kykim/bert-kor-base"},
        # upstream's inaudible watermark on cloned audio (ToneColorConverter's default, wavmark): False builds the converter
        # without it (upstream's own enable_watermark switch cannot be used, OpenVoiceBaseClass refuses the kwarg)
        "watermark": True,
        "wavmark": {"repo": "M4869/WavMark", "file": "step59000_snr39.99_pesq4.35_BERP_none0.30_mean1.81_std1.81.model.pkl"},
        # upstream's reference split (se_extractor.split_audio_vad split_seconds): the voice file cut into pieces of about
        # that many seconds, their tone color embeddings averaged
        "ref_split": 10.0,
        # languages a MeloTTS checkpoint exists for (presets/openvoice_presets.py) -> MeloTTS' language codes
        "languages": {"eng": "EN", "spa": "ES", "fra": "FR", "zho": "ZH", "jpn": "JP", "kor": "KR"},
        "samplerate": 44100,
        # upstream defaults (melo tts_to_file, ToneColorConverter.convert); tau is the sampling temperature of the
        # converter's posterior encoder (0 = deterministic)
        "speed": 1.0,
        "sdp_ratio": 0.2,
        "noise_scale": 0.6,
        "noise_scale_w": 0.8,
        "tau": 0.3,
        # custom model upload: a MeloTTS fine-tune (its train.py config.json + a G_<step>.pth renamed checkpoint.pth) +
        # ref.wav, the voice it was trained on: the tone color a voice file is converted from
        "files": ["config.json", "checkpoint.pth", "ref.wav"],
        # built-in speakers (as Orpheus): "default" speaks with the preset's speaker, a voice file is cloned onto it
        "voice": None,
        "voices": {},
        # MeloTTS (~52M params) + its language's BERT + the converter (~33M): real time on CPU
        "devices": torch_devices,
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['MELOTTS']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/melotts) behind a persistent worker, from the pinned
        # source tree (the commit OpenVoice's base speakers run from). One VITS2 checkpoint per language with a BERT text
        # frontend, built-in speakers only (no cloning): a voice file converts the speaker's output with default_vc_model.
        # repo: the default English checkpoint (each language's own is in presets/melotts_presets.py)
        "repo": "myshell-ai/MeloTTS-English-v3",
        "source": "https://github.com/myshell-ai/MeloTTS/archive/209145371cff8fc3bd60d7be902ea69cbdb7965a.tar.gz",
        "python": "3.12",
        # package list = upstream's own requirements.txt (its setup.py reads it, in the extracted tree), torch from the
        # device's PyTorch index (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback. Left out, as
        # for OpenVoice: what inference never imports (gradio: demo UI, tensorboard: training, cached-path: melo's own
        # downloads, done by the worker), the pins without py3.12 wheels (transformers 4.27.4 -> tokenizers 0.13, fugashi
        # 1.3.0), unidic (770 MB dictionary fetched by a post-install command: MeCab reads unidic-lite without it) and
        # mecab-python3 (its MeCab folder is python-mecab-ko's mecab folder on case-insensitive filesystems: the worker
        # serves MeCab from fugashi, same libmecab, same dictionary). Names normalized as pip does.
        "requirements_file": "requirements.txt",
        "requirements_exclude": ["gradio", "tensorboard", "cached-path", "transformers", "fugashi", "unidic", "mecab-python3"],
        # transformers below 5: melo's BERT frontends are written for 4.x; soxr: transformers imports it whenever librosa
        # is there (librosa >= 0.10 brings it, upstream's 0.9.1 does not); setuptools below 82: librosa 0.9.1 imports
        # pkg_resources, gone from 82 on; fugashi unpinned: the japanese BERT tokenizer and the MeCab stand-in;
        # python-mecab-ko: g2pkk (korean) pip-installs it at runtime otherwise; hf_xet as for GPT-SoVITS (windows reports
        # AMD64, so huggingface_hub's own marker misses it: the weights are on Xet)
        "requirements_extra": ["transformers<5", "soxr", "setuptools<82", "fugashi", "python-mecab-ko", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler; these only exist as pure-python sources
        "packages_sdist": ["jieba", "eng-to-ipa", "langid", "txtsplit", "unidic-lite", "gruut", "gruut-ipa", "gruut-lang-de", "gruut-lang-en", "gruut-lang-es", "gruut-lang-fr", "docopt", "distance"],
        # MeloTTS' text frontend BERTs (melo/text/*_bert.py) by MeloTTS language: the worker fetches every tokenizer (melo
        # loads them all at import) and the language's weights, as plain folders under models/tts/melotts
        "berts": {"EN": "bert-base-uncased", "ES": "dccuchile/bert-base-spanish-wwm-uncased", "FR": "dbmdz/bert-base-french-europeana-cased", "ZH": "bert-base-multilingual-uncased", "JP": "tohoku-nlp/bert-base-japanese-v3", "KR": "kykim/bert-kor-base"},
        # languages a MeloTTS checkpoint exists for (presets/melotts_presets.py) -> MeloTTS' language codes (ZH reads
        # Chinese mixed with English)
        "languages": {"eng": "EN", "spa": "ES", "fra": "FR", "zho": "ZH", "jpn": "JP", "kor": "KR"},
        "samplerate": 44100,
        # upstream defaults (melo tts_to_file)
        "speed": 1.0,
        "sdp_ratio": 0.2,
        "noise_scale": 0.6,
        "noise_scale_w": 0.8,
        # custom model upload: a MeloTTS fine-tune (its train.py config.json + a G_<step>.pth renamed checkpoint.pth) +
        # ref.wav, the voice it was trained on: picking that voice speaks without conversion
        "files": ["config.json", "checkpoint.pth", "ref.wav"],
        # built-in speakers (as Orpheus): "default" speaks with the preset's speaker, a voice file converts it with
        # default_vc_model
        "voice": None,
        "voices": {},
        # MeloTTS (~52M params) + its language's BERT (base size): faster than real time on CPU
        "devices": torch_devices,
        "rating": {"VRAM": 1, "CPU": 4, "RAM": 2, "Realism": 4}
    },
    TTS_ENGINES['CSM']: {
        # runs in its own uv venv (lib/classes/tts_engines/venvs/csm) behind a persistent worker. Upstream's own code
        # (generator.py) needs torchtune / torchao / moshi pins and the gated meta-llama/Llama-3.2-1B tokenizer: the worker
        # runs CSM through transformers' native CsmForConditionalGeneration instead (upstream's README points there since
        # transformers 4.52.1), same prompt layout ([speaker]text segments, Mimi audio frames) and sampling, so every e2a
        # torch device runs it. The pinned source tree only serves upstream's watermarking.py (its silentcipher watermark).
        # repo: ungated copy of the gated sesame/csm-1b (transformers format: Llama-3.2-1B backbone, depth decoder, Mimi
        # codec and the Llama 3 tokenizer in one folder)
        "repo": "unsloth/csm-1b",
        "source": "https://github.com/SesameAILabs/csm/archive/daed31e6d42cf71873999075de204fa37d2acec3.tar.gz",
        # 3.12 at most: pydub (silentcipher) imports audioop, gone from python 3.13
        "python": "3.12",
        # package list = upstream's own requirements.txt (in the extracted tree), torch from the device's PyTorch index
        # (--torch-backend, e2a's detected tag) or e2a's DeviceInstaller as fallback. Left out: what only upstream's
        # generator.py imports (moshi, torchtune, torchao), its 2025 pins (torch / torchaudio 2.4.0, tokenizers 0.21.0,
        # transformers 4.49.0 without CSM, huggingface_hub 0.28.1) and silentcipher (a git requirement: packages_nodeps
        # below). Names normalized as pip does.
        "requirements_file": "requirements.txt",
        "requirements_exclude": ["torch", "torchaudio", "tokenizers", "transformers", "huggingface-hub", "moshi", "torchtune", "torchao", "silentcipher"],
        # transformers from 4.56 (CSM since 4.52.1, the dtype argument since 4.56), 5.0.0 left out: its Whisper pipeline
        # breaks the reference transcription (see F5-TTS); accelerate: the worker loads the model straight onto the GPU
        # (device_map, transformers needs it); torchaudio, librosa, scipy, pyaml, pydub: what silentcipher and upstream's
        # watermarking.py import; soundfile / soxr cut and resample the voice references; hf_xet as for GPT-SoVITS
        # (windows reports AMD64, so huggingface_hub's own marker misses it)
        "requirements_extra": ["transformers>=4.56,!=5.0.0", "accelerate", "torchaudio", "librosa", "scipy", "pyaml", "pydub", "soundfile", "soxr", "hf_xet>=1.1.3,<2.0.0; sys_platform == 'win32'"],
        # every package installs as a wheel, so no platform ever needs a compiler
        "packages_sdist": [],
        # installed without their dependencies: upstream's silentcipher fork (pure python, pinned at the master commit its
        # requirement points to) declares Flask for its demo server, its imports are in requirements_extra
        "packages_nodeps": ["silentcipher @ https://github.com/SesameAILabs/silentcipher/archive/d46d7d0893a583d8968ab3a6626e2289faec9152.tar.gz"],
        # upstream's imperceptible watermark on every generated part (generator.py: silentcipher, its public
        # CSM_1B_GH_WATERMARK key): False leaves the audio unmarked. The watermark model is fetched as a plain folder
        "watermark": True,
        "silentcipher": {"repo": "sony/silentcipher", "model_type": "44.1k", "ckpt": "44_1_khz/73999_iteration"},
        # reference transcription (the voice clone context is the reference's Mimi frames + its text), Whisper run on
        # cpu; one copy under models/tts shared with the other engines using it
        "asr_model": "openai/whisper-large-v3-turbo",
        # the worker cuts a reference clip of at most ref_max seconds (its frames are part of every prompt, within the
        # backbone's 2048 positions)
        "ref_max": 10.0,
        # upstream's language: English only ("some capacity for non-English languages ... likely won't do well")
        "languages": {"eng": "en"},
        "samplerate": 24000,
        # upstream defaults (generator.py generate), for the backbone and the depth decoder alike
        "temperature": 0.9,
        "top_k": 50,
        # generation cap per sentence part: tokens_per_char x its length (12.5 Mimi frames per second of speech; 3 per
        # character is ~3.5x a latin letter's speech), at least 5 s, at most max_new_tokens (upstream's 90 s
        # max_audio_length_ms): a looping generation stops there
        "tokens_per_char": 3,
        "max_new_tokens": 1125,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        # 1B backbone + 0.1B depth decoder (bf16 from sm 8.0, fp16 below, fp32 on Pascal / GTX 16xx and cpu) + Mimi (fp32)
        "devices": torch_devices,
        "rating": {"VRAM": 4, "CPU": 1, "RAM": 8, "Realism": 4}
    },
    TTS_ENGINES['PHONON']: {
        # Phonon (gradium-ai/xn-ptts): the ptts wheel lives in python_env like coqui-tts (one abi3 Rust extension,
        # numpy only, no torch). CPU only: ptts.available_devices() is ['cpu'] in the PyPI wheels. Linux / Windows x86_64
        # wheels are built for x86-64-v3: the engine checks these flags before importing ptts (a SIGILL otherwise)
        "cpu_flags": ["avx2", "fma", "f16c"],
        # voice catalog: embeddings only, the open checkpoints have no voice encoder (no local cloning)
        "voices_repo": "gradium/phonon-voices",
        # what ptts reads from a local checkpoint folder (q8 prefers model.q8.gguf)
        "checkpoint_files": ["config.json", "tokenizer.json", "model.q8.gguf", "default-voice.safetensors"],
        "quant": "q8",
        # e2a iso-639-3 -> ptts text normalization language
        "languages": {"eng": "en", "fra": "fr", "deu": "de", "spa": "es", "por": "pt"},
        "samplerate": 24000,
        # ptts defaults; duration_delta 0 = the checkpoint's own pace (negative faster, positive slower)
        "temperature": 0.3,
        "duration_delta": 0.0,
        "files": [],
        # built-in voices (as Orpheus): "default" speaks with the preset's voice, a voice file converts a
        # same-gender catalog voice with default_vc_model
        "voice": None,
        "voices": {},
        # 31M / 40M params, q8 weights ~65-75 MB, faster than real time on one CPU core
        # ptts' PyPI wheels build no GPU backend
        "devices": [devices['CPU']['proc']],
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 1, "Realism": 4}
    },
    TTS_ENGINES['XTTS']: {
        "repo": "coqui/XTTS-v2",
        "languages": {"ara": "ar", "ces": "cs", "deu": "de", "eng": "en", "fra": "fr", "hin": "hi", "hun": "hu", "ita": "it", "jpn": "ja", "kor": "ko", "nld": "nl", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tur": "tr", "zho": "zh-cn"},
        "samplerate": 24000,
        "temperature": 0.75,
        "codec_temperature": 0.3,
        "length_penalty": 1.0,
        "num_beams": 1,
        "repetition_penalty": 2.0,
        "cvvp_weight": 0.9,
        "top_k": 40,
        "top_p": 0.85,
        "speed": 1.0,
        "gpt_cond_len": 512,
        "gpt_batch_size": 1,
        "enable_text_splitting": False,
        "files": ['config.json', 'model.pth', 'vocab.json', 'ref.wav'],
        "voice": default_speaker,
        "voices": {
            "ClaribelDervla": "Claribel Dervla", "DaisyStudious": "Daisy Studious", "GracieWise": "Gracie Wise",
            "TammieEma": "Tammie Ema", "AlisonDietlinde": "Alison Dietlinde", "AnaFlorence": "Ana Florence",
            "AnnmarieNele": "Annmarie Nele", "AsyaAnara": "Asya Anara", "BrendaStern": "Brenda Stern",
            "GittaNikolina": "Gitta Nikolina", "HenrietteUsha": "Henriette Usha", "SofiaHellen": "Sofia Hellen",
            "TammyGrit": "Tammy Grit", "TanjaAdelina": "Tanja Adelina", "VjollcaJohnnie": "Vjollca Johnnie",
            "AndrewChipper": "Andrew Chipper", "BadrOdhiambo": "Badr Odhiambo", "DionisioSchuyler": "Dionisio Schuyler",
            "RoystonMin": "Royston Min", "ViktorEka": "Viktor Eka", "AbrahanMack": "Abrahan Mack",
            "AddeMichal": "Adde Michal", "BaldurSanjin": "Baldur Sanjin", "CraigGutsy": "Craig Gutsy",
            "DamienBlack": "Damien Black", "GilbertoMathias": "Gilberto Mathias", "IlkinUrbano": "Ilkin Urbano",
            "KazuhikoAtallah": "Kazuhiko Atallah", "LudvigMilivoj": "Ludvig Milivoj", "SuadQasim": "Suad Qasim",
            "TorcullDiarmuid": "Torcull Diarmuid", "ViktorMenelaos": "Viktor Menelaos", "ZacharieAimilios": "Zacharie Aimilios",
            "NovaHogarth": "Nova Hogarth", "MajaRuoho": "Maja Ruoho", "UtaObando": "Uta Obando",
            "LidiyaSzekeres": "Lidiya Szekeres", "ChandraMacFarland": "Chandra MacFarland", "SzofiGranger": "Szofi Granger",
            "CamillaHolmström": "Camilla Holmström", "LilyaStainthorpe": "Lilya Stainthorpe", "ZofijaKendrick": "Zofija Kendrick",
            "NarelleMoon": "Narelle Moon", "BarboraMacLean": "Barbora MacLean", "AlexandraHisakawa": "Alexandra Hisakawa",
            "AlmaMaría": "Alma María", "RosemaryOkafor": "Rosemary Okafor", "IgeBehringer": "Ige Behringer",
            "FilipTraverse": "Filip Traverse", "DamjanChapman": "Damjan Chapman", "WulfCarlevaro": "Wulf Carlevaro",
            "AaronDreschner": "Aaron Dreschner", "KumarDahl": "Kumar Dahl", "EugenioMataracı": "Eugenio Mataracı",
            "FerranSimen": "Ferran Simen", "XavierHayasaka": "Xavier Hayasaka", "LuisMoray": "Luis Moray",
            "MarcosRudaski": "Marcos Rudaski"
        },
        "devices": torch_devices,
        "rating": {"VRAM": 4, "CPU": 2, "RAM": 4, "Realism": 5}
    },
    TTS_ENGINES['BARK']: {
        "languages": {"deu": "de", "eng": "en", "fra": "fr", "hin": "hi", "ita": "it", "jpn": "ja", "kor": "ko", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tur": "tr", "zho": "zh-cn"},
        "samplerate": 24000,
        "text_temp": 0.22,
        "waveform_temp": 0.44,
        "files": [],
        "speakers_path": os.path.join(voices_dir, '__bark'),
        "voice": default_speaker,
        "voices": {
            "de_speaker_0": "Speaker 0", "de_speaker_1": "Speaker 1", "de_speaker_2": "Speaker 2",
            "de_speaker_3": "Speaker 3", "de_speaker_4": "Speaker 4", "de_speaker_5": "Speaker 5",
            "de_speaker_6": "Speaker 6", "de_speaker_7": "Speaker 7", "de_speaker_8": "Speaker 8",
            "de_speaker_9": "Speaker 9", "en_speaker_0": "Speaker 0", "en_speaker_1": "Speaker 1",
            "en_speaker_2": "Speaker 2", "en_speaker_3": "Speaker 3", "en_speaker_4": "Speaker 4",
            "en_speaker_5": "Speaker 5", "en_speaker_6": "Speaker 6", "en_speaker_7": "Speaker 7",
            "en_speaker_8": "Speaker 8", "en_speaker_9": "Speaker 9", "es_speaker_0": "Speaker 0",
            "es_speaker_1": "Speaker 1", "es_speaker_2": "Speaker 2", "es_speaker_3": "Speaker 3",
            "es_speaker_4": "Speaker 4", "es_speaker_5": "Speaker 5", "es_speaker_6": "Speaker 6",
            "es_speaker_7": "Speaker 7", "es_speaker_8": "Speaker 8", "es_speaker_9": "Speaker 9",
            "fr_speaker_0": "Speaker 0", "fr_speaker_1": "Speaker 1", "fr_speaker_2": "Speaker 2",
            "fr_speaker_3": "Speaker 3", "fr_speaker_4": "Speaker 4", "fr_speaker_5": "Speaker 5",
            "fr_speaker_6": "Speaker 6", "fr_speaker_7": "Speaker 7", "fr_speaker_8": "Speaker 8",
            "fr_speaker_9": "Speaker 9", "hi_speaker_0": "Speaker 0", "hi_speaker_1": "Speaker 1",
            "hi_speaker_2": "Speaker 2", "hi_speaker_3": "Speaker 3", "hi_speaker_4": "Speaker 4",
            "hi_speaker_5": "Speaker 5", "hi_speaker_6": "Speaker 6", "hi_speaker_7": "Speaker 7",
            "hi_speaker_8": "Speaker 8", "hi_speaker_9": "Speaker 9", "it_speaker_0": "Speaker 0",
            "it_speaker_1": "Speaker 1", "it_speaker_2": "Speaker 2", "it_speaker_3": "Speaker 3",
            "it_speaker_4": "Speaker 4", "it_speaker_5": "Speaker 5", "it_speaker_6": "Speaker 6",
            "it_speaker_7": "Speaker 7", "it_speaker_8": "Speaker 8", "it_speaker_9": "Speaker 9",
            "ja_speaker_0": "Speaker 0", "ja_speaker_1": "Speaker 1", "ja_speaker_2": "Speaker 2",
            "ja_speaker_3": "Speaker 3", "ja_speaker_4": "Speaker 4", "ja_speaker_5": "Speaker 5",
            "ja_speaker_6": "Speaker 6", "ja_speaker_7": "Speaker 7", "ja_speaker_8": "Speaker 8",
            "ja_speaker_9": "Speaker 9", "ko_speaker_0": "Speaker 0", "ko_speaker_1": "Speaker 1",
            "ko_speaker_2": "Speaker 2", "ko_speaker_3": "Speaker 3", "ko_speaker_4": "Speaker 4",
            "ko_speaker_5": "Speaker 5", "ko_speaker_6": "Speaker 6", "ko_speaker_7": "Speaker 7",
            "ko_speaker_8": "Speaker 8", "ko_speaker_9": "Speaker 9", "pl_speaker_0": "Speaker 0",
            "pl_speaker_1": "Speaker 1", "pl_speaker_2": "Speaker 2", "pl_speaker_3": "Speaker 3",
            "pl_speaker_4": "Speaker 4", "pl_speaker_5": "Speaker 5", "pl_speaker_6": "Speaker 6",
            "pl_speaker_7": "Speaker 7", "pl_speaker_8": "Speaker 8", "pl_speaker_9": "Speaker 9",
            "pt_speaker_0": "Speaker 0", "pt_speaker_1": "Speaker 1", "pt_speaker_2": "Speaker 2",
            "pt_speaker_3": "Speaker 3", "pt_speaker_4": "Speaker 4", "pt_speaker_5": "Speaker 5",
            "pt_speaker_6": "Speaker 6", "pt_speaker_7": "Speaker 7", "pt_speaker_8": "Speaker 8",
            "pt_speaker_9": "Speaker 9", "ru_speaker_0": "Speaker 0", "ru_speaker_1": "Speaker 1",
            "ru_speaker_2": "Speaker 2", "ru_speaker_3": "Speaker 3", "ru_speaker_4": "Speaker 4",
            "ru_speaker_5": "Speaker 5", "ru_speaker_6": "Speaker 6", "ru_speaker_7": "Speaker 7",
            "ru_speaker_8": "Speaker 8", "ru_speaker_9": "Speaker 9", "tr_speaker_0": "Speaker 0",
            "tr_speaker_1": "Speaker 1", "tr_speaker_2": "Speaker 2", "tr_speaker_3": "Speaker 3",
            "tr_speaker_4": "Speaker 4", "tr_speaker_5": "Speaker 5", "tr_speaker_6": "Speaker 6",
            "tr_speaker_7": "Speaker 7", "tr_speaker_8": "Speaker 8", "tr_speaker_9": "Speaker 9",
            "zh_speaker_0": "Speaker 0", "zh_speaker_1": "Speaker 1", "zh_speaker_2": "Speaker 2",
            "zh_speaker_3": "Speaker 3", "zh_speaker_4": "Speaker 4", "zh_speaker_5": "Speaker 5",
            "zh_speaker_6": "Speaker 6", "zh_speaker_7": "Speaker 7", "zh_speaker_8": "Speaker 8",
            "zh_speaker_9": "Speaker 9"
        },
        "devices": torch_devices,
        "rating": {"VRAM": 6, "CPU": 1, "RAM": 6, "Realism": 4}
    },
    TTS_ENGINES['TORTOISE']: {
        "languages": {"eng": "en"},
        "samplerate": 24000,
        "files": [],
        "voice": default_speaker,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 6, "CPU": 2, "RAM": 6, "Realism": 4}
    },
    TTS_ENGINES['PIPER']: {
        "languages": {
            "ara": "ar_JO", "cat": "ca_ES", "ces": "cs_CZ", "cym": "cy_GB", "dan": "da_DK",
            "deu": "de_DE", "ell": "el_GR", "eng": "en_GB", "spa": "es_ES", "fas": "fa_IR",
            "fin": "fi_FI", "fra": "fr_FR", "hun": "hu_HU", "isl": "is_IS", "ita": "it_IT",
            "kat": "ka_GE", "kaz": "kk_KZ", "ltz": "lb_LU", "lav": "lv_LV", "nep": "ne_NP",
            "nld": "nl_NL", "nob": "no_NO", "pol": "pl_PL", "por": "pt_PT", "ron": "ro_RO",
            "rus": "ru_RU", "slk": "sk_SK", "slv": "sl_SI", "srp": "sr_RS", "swe": "sv_SE",
            "swa": "sw_CD", "tur": "tr_TR", "ukr": "uk_UA", "urd": "ur_PK", "vie": "vi_VN",
            "zho": "zh_CN"
        },
        "samplerate": 22050,
        "files": ['config.onnx.json', 'model.onnx', 'ref.wav'],
        "speakers_path": os.path.join(voices_dir, '__piper'),
        "voice": None,
        "voices": {
            "ar_JO-kareem-medium":              "Kareem",
            "ca_ES-upc_ona-medium":             "Ona",
            "cs_CZ-jirka-medium":               "Jirka",
            "cy_GB-gwryw_gogleddol-medium":     "Gwryw Gogleddol",
            "cy_GB-bu_tts-medium":              "Bu",
            "da_DK-talesyntese-medium":         "Talesyntese",
            "de_DE-thorsten-medium":            "Thorsten",
            "de_DE-thorsten_emotional-medium":  "Thorsten Emotional",
            "de_DE-mls-medium":                 "Mls",
            "el_GR-rapunzelina-low":            "Rapunzelina",
            "en_GB-alan-medium":                "Alan",
            "en_GB-cori-high":                  "Cori",
            "es_ES-davefx-medium":              "DaveFX",
            "es_ES-sharvard-medium":            "Sharvard",
            "fa_IR-amir-medium":                "Amir",
            "fi_FI-harri-medium":               "Harri",
            "fr_FR-tom-medium":                 "Tom",
            "fr_FR-siwis-medium":               "Siwis",
            "hu_HU-anna-medium":                "Anna",
            "is_IS-bui-medium":                 "Bui",
            "is_IS-salka-medium":               "Salka",
            "it_IT-riccardo-x_low":             "Riccardo",
            "it_IT-paola-medium":               "Paola",
            "ka_GE-natia-medium":               "Natia",
            "kk_KZ-issai-high":                 "Issai",
            "kk_KZ-iseke-x_low":                "Iseke",
            "lb_LU-marylux-medium":             "MaryLux",
            "lv_LV-aivars-medium":              "Aivars",
            "ne_NP-google-medium":              "Google",
            "nl_NL-mls-medium":                 "Mls",
            "no_NO-talesyntese-medium":         "Talesyntese",
            "pl_PL-darkman-medium":             "Darkman",
            "pl_PL-gosia-medium":               "Gosia",
            "pt_PT-tug%C3%A3o-medium":          "Tugão",
            "ro_RO-mihai-medium":               "Mihai",
            "ru_RU-denis-medium":               "Denis",
            "ru_RU-irina-medium":               "Irina",
            "sk_SK-lili-medium":                "Lili",
            "sl_SI-artur-medium":               "Artur",
            "sr_RS-serbski_institut-medium":    "Serbski",
            "sv_SE-nst-medium":                 "Nst",
            "sw_CD-lanfrica-medium":            "Lanfrica",
            "tr_TR-dfki-medium":                "Dfki",
            "uk_UA-ukrainian_tts-medium":       "Ukrainian",
            "ur_PK-fasih-medium":               "Fasih",
            "vi_VN-vais1000-medium":            "Vais",
            "zh_CN-huayan-medium":              "Huayan"
        },
        # onnxruntime-gpu is its only GPU path: the CUDA build (x86_64 / win_amd64 wheels), no ROCm, OpenVINO nor Jetson one
        "devices": [devices['CPU']['proc'], devices['CUDA']['proc']],
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 4}
    },
    TTS_ENGINES['VITS']: {
        "languages": {"ben": "bn", "bul": "bg", "cat": "ca", "ces": "cs", "dan": "da", "deu": "de", "ell": "el", "eng": "en", "est": "et", "ewe": "ewe", "fas": "fa", "fin": "fi", "fra": "fr", "gle": "ga", "hau": "hau", "hrv": "hr", "hun": "hu", "ita": "it", "lav": "lv", "lin": "lin", "lit": "lt", "mlt": "mt", "nld": "nl", "pol": "pl", "por": "pt", "rom": "ro", "slk": "sk", "sln": "sl", "spa": "es", "srp": "sr", "swe": "sv", "tw_akuapem": "tw_akuapem", "tw_asante": "tw_asante", "ukr": "uk", "yor": "yor"},
        "samplerate": 22050,
        "files": ['config.json', 'best_model.pth', 'ref.wav'],
        "voice": None,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['FAIRSEQ']: {
        # "nob": "nb",
        "languages": {"ara": "ar", "ben": "bn", "eng": "en", "fas": "fa", "fra": "fr", "deu": "de", "hin": "hi", "hun": "hu", "ind": "id", "jav": "jv", "kor": "ko", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tam": "ta", "tel": "te", "tur": "tr", "yor": "yo", "abi": "abi", "ace": "ace", "aca": "aca", "acn": "acn", "acr": "acr", "ach": "ach", "acu": "acu", "guq": "guq", "ade": "ade", "adj": "adj", "agd": "agd", "agx": "agx", "agn": "agn", "aha": "aha", "aka": "ak", "knj": "knj", "ake": "ake", "aeu": "aeu", "ahk": "ahk", "bss": "bss", "alj": "alj", "sqi": "sq", "alt": "alt", "alp": "alp", "alz": "alz", "kab": "kab", "amk": "amk", "mmg": "mmg", "amh": "am", "ami": "ami", "azg": "azg", "agg": "agg", "boj": "boj", "cko": "cko", "any": "any", "arl": "arl", "atq": "atq", "luc": "luc", "hyw": "hyw", "apr": "apr", "aia": "aia", "msy": "msy", "cni": "cni", "cjo": "cjo", "cpu": "cpu", "cpb": "cpb", "asm": "as", "asa": "asa", "teo": "teo", "ati": "ati", "djk": "djk", "ava": "av", "avn": "avn", "avu": "avu", "awb": "awb", "kwi": "kwi", "awa": "awa", "agr": "agr", "agu": "agu", "ayr": "ayr", "ayo": "ayo", "abp": "abp", "blx": "blx", "sgb": "sgb", "azj-script_cyrillic": "azj-script_cyrillic", "azj-script_latin": "azj-script_latin", "azb": "azb", "bba": "bba", "bhz": "bhz", "bvc": "bvc", "bfy": "bfy", "bgq": "bgq", "bdq": "bdq", "bdh": "bdh", "bqi": "bqi", "bjw": "bjw", "blz": "blz", "ban": "ban", "bcc-script_latin": "bcc-script_latin", "bcc-script_arabic": "bcc-script_arabic", "bam": "bm", "ptu": "ptu", "bcw": "bcw", "bqj": "bqj", "bno": "bno", "bbb": "bbb", "bfa": "bfa", "bjz": "bjz", "bak": "ba", "eus": "eu", "bsq": "bsq", "akb": "akb", "btd": "btd", "btx": "btx", "bts": "bts", "bbc": "bbc", "bvz": "bvz", "bjv": "bjv", "bep": "bep", "bkv": "bkv", "bzj": "bzj", "bem": "bem", "bng": "bng", "bom": "bom", "btt": "btt", "bha": "bha", "bgw": "bgw", "bht": "bht", "beh": "beh", "sne": "sne", "ubl": "ubl", "bcl": "bcl", "bim": "bim", "bkd": "bkd", "bjr": "bjr", "bfo": "bfo", "biv": "biv", "bib": "bib", "bis": "bi", "bzi": "bzi", "bqp": "bqp", "bpr": "bpr", "bps": "bps", "bwq": "bwq", "bdv": "bdv", "bqc": "bqc", "bus": "bus", "bnp": "bnp", "bmq": "bmq", "bdg": "bdg", "boa": "boa", "ksr": "ksr", "bor": "bor", "bru": "bru", "box": "box", "bzh": "bzh", "bgt": "bgt", "sab": "sab", "bul": "bg", "bwu": "bwu", "bmv": "bmv", "mya": "my", "tte": "tte", "cjp": "cjp", "cbv": "cbv", "kaq": "kaq", "cot": "cot", "cbc": "cbc", "car": "car", "cat": "ca", "ceb": "ceb", "cme": "cme", "cbi": "cbi", "ceg": "ceg", "cly": "cly", "cya": "cya", "che": "ce", "hne": "hne", "nya": "ny", "dig": "dig", "dug": "dug", "bgr": "bgr", "cek": "cek", "cfm": "cfm", "cnh": "cnh", "hlt": "hlt", "mwq": "mwq", "ctd": "ctd", "tcz": "tcz", "zyp": "zyp", "cco": "cco", "cnl": "cnl", "cle": "cle", "chz": "chz", "cpa": "cpa", "cso": "cso", "cnt": "cnt", "cuc": "cuc", "hak": "hak", "nan": "nan", "xnj": "xnj", "cap": "cap", "cax": "cax", "ctg": "ctg", "ctu": "ctu", "chf": "chf", "cce": "cce", "crt": "crt", "crq": "crq", "cac-dialect_sansebasti\u00e1ncoat\u00e1n": "cac-dialect_sansebasti\u00e1ncoat\u00e1n", "cac-dialect_sanmateoixtat\u00e1n": "cac-dialect_sanmateoixtat\u00e1n", "ckt": "ckt", "ncu": "ncu", "cdj": "cdj", "chv": "cv", "caa": "caa", "asg": "asg", "con": "con", "crn": "crn", "cok": "cok", "crk-script_latin": "crk-script_latin", "crk-script_syllabics": "crk-script_syllabics", "crh": "crh", "cui": "cui", "ces": "cs", "dsh": "dsh", "dbq": "dbq", "dga": "dga", "dgi": "dgi", "dgk": "dgk", "dnj-dialect_gweetaawueast": "dnj-dialect_gweetaawueast", "dnj-dialect_blowowest": "dnj-dialect_blowowest", "daa": "daa", "dnt": "dnt", "dnw": "dnw", "dar": "dar", "tcc": "tcc", "dwr": "dwr", "ded": "ded", "mzw": "mzw", "ntr": "ntr", "ddn": "ddn", "des": "des", "dso": "dso", "nfa": "nfa", "dhi": "dhi", "gud": "gud", "did": "did", "mhu": "mhu", "dip": "dip", "dik": "dik", "tbz": "tbz", "dts": "dts", "dos": "dos", "dgo": "dgo", "mvp": "mvp", "jen": "jen", "dzo": "dz", "idd": "idd", "eka": "eka", "cto": "cto", "emp": "emp", "enx": "enx", "sja": "sja", "myv": "myv", "mcq": "mcq", "ese": "ese", "evn": "evn", "eza": "eza", "ewe": "ee", "fal": "fal", "fao": "fo", "far": "far", "fij": "fj", "fin": "fi", "fon": "fon", "frd": "frd", "ful": "ff", "flr": "flr", "gau": "gau", "gbk": "gbk", "gag-script_cyrillic": "gag-script_cyrillic", "gag-script_latin": "gag-script_latin", "gbi": "gbi", "gmv": "gmv", "lug": "lg", "pwg": "pwg", "gbm": "gbm", "cab": "cab", "grt": "grt", "krs": "krs", "gso": "gso", "nlg": "nlg", "gej": "gej", "gri": "gri", "kik": "ki", "acd": "acd", "glk": "glk", "gof-script_latin": "gof-script_latin", "gog": "gog", "gkn": "gkn", "wsg": "wsg", "gjn": "gjn", "gqr": "gqr", "gor": "gor", "gux": "gux", "gbo": "gbo", "ell": "el", "grc": "grc", "guh": "guh", "gub": "gub", "grn": "gn", "gyr": "gyr", "guo": "guo", "gde": "gde", "guj": "gu", "gvl": "gvl", "guk": "guk", "rub": "rub", "dah": "dah", "gwr": "gwr", "gwi": "gwi", "hat": "ht", "hlb": "hlb", "amf": "amf", "hag": "hag", "hnn": "hnn", "bgc": "bgc", "had": "had", "hau": "ha", "hwc": "hwc", "hvn": "hvn", "hay": "hay", "xed": "xed", "heb": "he", "heh": "heh", "hil": "hil", "hif": "hif", "hns": "hns", "hoc": "hoc", "hoy": "hoy", "hus-dialect_westernpotosino": "hus-dialect_westernpotosino", "hus-dialect_centralveracruz": "hus-dialect_centralveracruz", "huv": "huv", "hui": "hui", "hap": "hap", "iba": "iba", "isl": "is", "dbj": "dbj", "ifa": "ifa", "ifb": "ifb", "ifu": "ifu", "ifk": "ifk", "ife": "ife", "ign": "ign", "ikk": "ikk", "iqw": "iqw", "ilb": "ilb", "ilo": "ilo", "imo": "imo", "inb": "inb", "ipi": "ipi", "irk": "irk", "icr": "icr", "itv": "itv", "itl": "itl", "atg": "atg", "ixl-dialect_sanjuancotzal": "ixl-dialect_sanjuancotzal", "ixl-dialect_sangasparchajul": "ixl-dialect_sangasparchajul", "ixl-dialect_santamarianebaj": "ixl-dialect_santamarianebaj", "nca": "nca", "izr": "izr", "izz": "izz", "jac": "jac", "jam": "jam", "jvn": "jvn", "kac": "kac", "dyo": "dyo", "csk": "csk", "adh": "adh", "jun": "jun", "jbu": "jbu", "dyu": "dyu", "bex": "bex", "juy": "juy", "gna": "gna", "urb": "urb", "kbp": "kbp", "cwa": "cwa", "dtp": "dtp", "kbr": "kbr", "cgc": "cgc", "kki": "kki", "kzf": "kzf", "lew": "lew", "cbr": "cbr", "kkj": "kkj", "keo": "keo", "kqe": "kqe", "kak": "kak", "kyb": "kyb", "knb": "knb", "kmd": "kmd", "kml": "kml", "ify": "ify", "xal": "xal", "kbq": "kbq", "kay": "kay", "ktb": "ktb", "hig": "hig", "gam": "gam", "cbu": "cbu", "xnr": "xnr", "kmu": "kmu", "kne": "kne", "kan": "kn", "kby": "kby", "pam": "pam", "cak-dialect_santamar\u00edadejes\u00fas": "cak-dialect_santamar\u00edadejes\u00fas", "cak-dialect_southcentral": "cak-dialect_southcentral", "cak-dialect_yepocapa": "cak-dialect_yepocapa", "cak-dialect_western": "cak-dialect_western", "cak-dialect_santodomingoxenacoj": "cak-dialect_santodomingoxenacoj", "cak-dialect_central": "cak-dialect_central", "xrb": "xrb", "krc": "krc", "kaa": "kaa", "krl": "krl", "pww": "pww", "xsm": "xsm", "cbs": "cbs", "pss": "pss", "kxf": "kxf", "kyz": "kyz", "kyu": "kyu", "txu": "txu", "kaz": "kk", "ndp": "ndp", "kbo": "kbo", "kyq": "kyq", "ken": "ken", "ker": "ker", "xte": "xte", "kyg": "kyg", "kjh": "kjh", "kca": "kca", "khm": "km", "kxm": "kxm", "kjg": "kjg", "nyf": "nyf", "kij": "kij", "kia": "kia", "kqr": "kqr", "kqp": "kqp", "krj": "krj", "zga": "zga", "kin": "rw", "pkb": "pkb", "geb": "geb", "gil": "gil", "kje": "kje", "kss": "kss", "thk": "thk", "klu": "klu", "kyo": "kyo", "kog": "kog", "kfb": "kfb", "kpv": "kpv", "bbo": "bbo", "xon": "xon", "kma": "kma", "kno": "kno", "kxc": "kxc", "ozm": "ozm", "kqy": "kqy", "coe": "coe", "kpq": "kpq", "kpy": "kpy", "kyf": "kyf", "kff-script_telugu": "kff-script_telugu", "kri": "kri", "rop": "rop", "ktj": "ktj", "ted": "ted", "krr": "krr", "kdt": "kdt", "kez": "kez", "cul": "cul", "kle": "kle", "kdi": "kdi", "kue": "kue", "kum": "kum", "kvn": "kvn", "cuk": "cuk", "kdn": "kdn", "xuo": "xuo", "key": "key", "kpz": "kpz", "knk": "knk", "kmr-script_latin": "kmr-script_latin", "kmr-script_arabic": "kmr-script_arabic", "kmr-script_cyrillic": "kmr-script_cyrillic", "xua": "xua", "kru": "kru", "kus": "kus", "kub": "kub", "kdc": "kdc", "kxv": "kxv", "blh": "blh", "cwt": "cwt", "kwd": "kwd", "tnk": "tnk", "kwf": "kwf", "cwe": "cwe", "kyc": "kyc", "tye": "tye", "kir": "ky", "quc-dialect_north": "quc-dialect_north", "quc-dialect_east": "quc-dialect_east", "quc-dialect_central": "quc-dialect_central", "lac": "lac", "lsi": "lsi", "lbj": "lbj", "lhu": "lhu", "las": "las", "lam": "lam", "lns": "lns", "ljp": "ljp", "laj": "laj", "lao": "lo", "lat": "la", "lav": "lv", "law": "law", "lcp": "lcp", "lzz": "lzz", "lln": "lln", "lef": "lef", "acf": "acf", "lww": "lww", "mhx": "mhx", "eip": "eip", "lia": "lia", "lif": "lif", "onb": "onb", "lis": "lis", "loq": "loq", "lob": "lob", "yaz": "yaz", "lok": "lok", "llg": "llg", "ycl": "ycl", "lom": "lom", "ngl": "ngl", "lon": "lon", "lex": "lex", "lgg": "lgg", "ruf": "ruf", "dop": "dop", "lnd": "lnd", "ndy": "ndy", "lwo": "lwo", "lee": "lee", "mev": "mev", "mfz": "mfz", "jmc": "jmc", "myy": "myy", "mbc": "mbc", "mda": "mda", "mad": "mad", "mag": "mag", "ayz": "ayz", "mai": "mai", "mca": "mca", "mcp": "mcp", "mak": "mak", "vmw": "vmw", "mgh": "mgh", "kde": "kde", "mlg": "mg", "zlm": "zlm", "pse": "pse", "mkn": "mkn", "xmm": "xmm", "mal": "ml", "xdy": "xdy", "div": "dv", "mdy": "mdy", "mup": "mup", "mam-dialect_central": "mam-dialect_central", "mam-dialect_northern": "mam-dialect_northern", "mam-dialect_southern": "mam-dialect_southern", "mam-dialect_western": "mam-dialect_western", "mqj": "mqj", "mcu": "mcu", "mzk": "mzk", "maw": "maw", "mjl": "mjl", "mnk": "mnk", "mge": "mge", "mbh": "mbh", "knf": "knf", "mjv": "mjv", "mbt": "mbt", "obo": "obo", "mbb": "mbb", "mzj": "mzj", "nld": "nld", "sjm": "sjm", "mrw": "mrw", "mar": "mr", "mpg": "mpg", "mhr": "mhr", "enb": "enb", "mah": "mh", "myx": "myx", "klv": "klv", "mfh": "mfh", "met": "met", "mcb": "mcb", "mop": "mop", "yua": "yua", "mfy": "mfy", "maz": "maz", "vmy": "vmy", "maq": "maq", "mzi": "mzi", "maj": "maj", "maa-dialect_sanantonio": "maa-dialect_sanantonio", "maa-dialect_sanjer\u00f3nimo": "maa-dialect_sanjer\u00f3nimo", "mhy": "mhy", "mhi": "mhi", "zmz": "zmz", "myb": "myb", "gai": "gai", "mqb": "mqb", "mbu": "mbu", "med": "med", "men": "men", "mee": "mee", "mwv": "mwv", "meq": "meq", "zim": "zim", "mgo": "mgo", "mej": "mej", "mpp": "mpp", "min": "min", "gum": "gum", "mpx": "mpx", "mco": "mco", "mxq": "mxq", "pxm": "pxm", "mto": "mto", "mim": "mim", "xta": "xta", "mbz": "mbz", "mip": "mip", "mib": "mib", "miy": "miy", "mih": "mih", "miz": "miz", "xtd": "xtd", "mxt": "mxt", "xtm": "xtm", "mxv": "mxv", "xtn": "xtn", "mie": "mie", "mil": "mil", "mio": "mio", "mdv": "mdv", "mza": "mza", "mit": "mit", "mxb": "mxb", "mpm": "mpm", "soy": "soy", "cmo-script_latin": "cmo-script_latin", "cmo-script_khmer": "cmo-script_khmer", "mfq": "mfq", "old": "old", "mfk": "mfk", "mif": "mif", "mkl": "mkl", "mox": "mox", "myl": "myl", "mqf": "mqf", "mnw": "mnw", "mon": "mn", "mog": "mog", "mfe": "mfe", "mor": "mor", "mqn": "mqn", "mgd": "mgd", "mtj": "mtj", "cmr": "cmr", "mtd": "mtd", "bmr": "bmr", "moz": "moz", "mzm": "mzm", "mnb": "mnb", "mnf": "mnf", "unr": "unr", "fmu": "fmu", "mur": "mur", "tih": "tih", "muv": "muv", "muy": "muy", "sur": "sur", "moa": "moa", "wmw": "wmw", "tnr": "tnr", "miq": "miq", "mos": "mos", "muh": "muh", "nas": "nas", "mbj": "mbj", "nfr": "nfr", "kfw": "kfw", "nst": "nst", "nag": "nag", "nch": "nch", "nhe": "nhe", "ngu": "ngu", "azz": "azz", "nhx": "nhx", "ncl": "ncl", "nhy": "nhy", "ncj": "ncj", "nsu": "nsu", "npl": "npl", "nuz": "nuz", "nhw": "nhw", "nhi": "nhi", "nlc": "nlc", "nab": "nab", "gld": "gld", "nnb": "nnb", "npy": "npy", "pbb": "pbb", "ntm": "ntm", "nmz": "nmz", "naw": "naw", "nxq": "nxq", "ndj": "ndj", "ndz": "ndz", "ndv": "ndv", "new": "new", "nij": "nij", "sba": "sba", "gng": "gng", "nga": "nga", "nnq": "nnq", "ngp": "ngp", "gym": "gym", "kdj": "kdj", "nia": "nia", "nim": "nim", "nin": "nin", "nko": "nko", "nog": "nog", "lem": "lem", "not": "not", "nhu": "nhu", "bud": "bud", "nus": "nus", "yas": "yas", "nnw": "nnw", "nwb": "nwb", "nyy": "nyy", "nyn": "nyn", "rim": "rim", "lid": "lid", "nuj": "nuj", "nyo": "nyo", "nzi": "nzi", "ann": "ann", "ory": "ory", "ojb-script_latin": "ojb-script_latin", "ojb-script_syllabics": "ojb-script_syllabics", "oku": "oku", "bsc": "bsc", "bdu": "bdu", "orm": "om", "ury": "ury", "oss": "os", "ote": "ote", "otq": "otq", "stn": "stn", "sig": "sig", "kfx": "kfx", "bfz": "bfz", "sey": "sey", "pao": "pao", "pau": "pau", "pce": "pce", "plw": "plw", "pmf": "pmf", "pag": "pag", "pap": "pap", "prf": "prf", "pab": "pab", "pbi": "pbi", "pbc": "pbc", "pad": "pad", "ata": "ata", "pez": "pez", "peg": "peg", "pcm": "pcm", "pis": "pis", "pny": "pny", "pir": "pir", "pjt": "pjt", "poy": "poy", "pps": "pps", "pls": "pls", "poi": "poi", "poh-dialect_eastern": "poh-dialect_eastern", "poh-dialect_western": "poh-dialect_western", "prt": "prt", "pui": "pui", "pan": "pa", "tsz": "tsz", "suv": "suv", "lme": "lme", "quy": "quy", "qvc": "qvc", "quz": "quz", "qve": "qve", "qub": "qub", "qvh": "qvh", "qwh": "qwh", "qvw": "qvw", "quf": "quf", "qvm": "qvm", "qul": "qul", "qvn": "qvn", "qxn": "qxn", "qxh": "qxh", "qvs": "qvs", "quh": "quh", "qxo": "qxo", "qxr": "qxr", "qvo": "qvo", "qvz": "qvz", "qxl": "qxl", "quw": "quw", "kjb": "kjb", "kek": "kek", "rah": "rah", "rjs": "rjs", "rai": "rai", "lje": "lje", "rnl": "rnl", "rkt": "rkt", "rap": "rap", "yea": "yea", "raw": "raw", "rej": "rej", "rel": "rel", "ril": "ril", "iri": "iri", "rgu": "rgu", "rhg": "rhg", "rmc-script_latin": "rmc-script_latin", "rmc-script_cyrillic": "rmc-script_cyrillic", "rmo": "rmo", "rmy-script_latin": "rmy-script_latin", "rmy-script_cyrillic": "rmy-script_cyrillic", "ron": "ro", "rol": "rol", "cla": "cla", "rng": "rng", "rug": "rug", "run": "rn", "lsm": "lsm", "spy": "spy", "sck": "sck", "saj": "saj", "sch": "sch", "sml": "sml", "xsb": "xsb", "sbl": "sbl", "saq": "saq", "sbd": "sbd", "smo": "sm", "rav": "rav", "sxn": "sxn", "sag": "sg", "sbp": "sbp", "xsu": "xsu", "srm": "srm", "sas": "sas", "apb": "apb", "sgw": "sgw", "tvw": "tvw", "lip": "lip", "slu": "slu", "snw": "snw", "sea": "sea", "sza": "sza", "seh": "seh", "crs": "crs", "ksb": "ksb", "shn": "shn", "sho": "sho", "mcd": "mcd", "cbt": "cbt", "xsr": "xsr", "shk": "shk", "shp": "shp", "sna": "sn", "cjs": "cjs", "jiv": "jiv", "snp": "snp", "sya": "sya", "sid": "sid", "snn": "snn", "sri": "sri", "srx": "srx", "sil": "sil", "sld": "sld", "akp": "akp", "xog": "xog", "som": "so", "bmu": "bmu", "khq": "khq", "ses": "ses", "mnx": "mnx", "srn": "srn", "sxb": "sxb", "suc": "suc", "tgo": "tgo", "suk": "suk", "sun": "su", "suz": "suz", "sgj": "sgj", "sus": "sus", "swh": "swh", "swe": "sv", "syl": "syl", "dyi": "dyi", "myk": "myk", "spp": "spp", "tap": "tap", "tby": "tby", "tna": "tna", "shi": "shi", "klw": "klw", "tgl": "tl", "tbk": "tbk", "tgj": "tgj", "blt": "blt", "tbg": "tbg", "omw": "omw", "tgk": "tg", "tdj": "tdj", "tbc": "tbc", "tlj": "tlj", "tly": "tly", "ttq-script_tifinagh": "ttq-script_tifinagh", "taj": "taj", "taq": "taq", "tpm": "tpm", "tgp": "tgp", "tnn": "tnn", "tac": "tac", "rif-script_latin": "rif-script_latin", "rif-script_arabic": "rif-script_arabic", "tat": "tt", "tav": "tav", "twb": "twb", "tbl": "tbl", "kps": "kps", "twe": "twe", "ttc": "ttc", "kdh": "kdh", "tes": "tes", "tex": "tex", "tee": "tee", "tpp": "tpp", "tpt": "tpt", "stp": "stp", "tfr": "tfr", "twu": "twu", "ter": "ter", "tew": "tew", "tha": "th", "nod": "nod", "thl": "thl", "tem": "tem", "adx": "adx", "bod": "bo", "khg": "khg", "tca": "tca", "tir": "ti", "txq": "txq", "tik": "tik", "dgr": "dgr", "tob": "tob", "tmf": "tmf", "tng": "tng", "tlb": "tlb", "ood": "ood", "tpi": "tpi", "jic": "jic", "lbw": "lbw", "txa": "txa", "tom": "tom", "toh": "toh", "tnt": "tnt", "sda": "sda", "tcs": "tcs", "toc": "toc", "tos": "tos", "neb": "neb", "trn": "trn", "trs": "trs", "trc": "trc", "tri": "tri", "cof": "cof", "tkr": "tkr", "kdl": "kdl", "cas": "cas", "tso": "ts", "tuo": "tuo", "iou": "iou", "tmc": "tmc", "tuf": "tuf", "tuk-script_latin": "tk", "tuk-script_arabic": "tk", "bov": "bov", "tue": "tue", "kcg": "kcg", "tzh-dialect_bachaj\u00f3n": "tzh-dialect_bachaj\u00f3n", "tzh-dialect_tenejapa": "tzh-dialect_tenejapa", "tzo-dialect_chenalh\u00f3": "tzo-dialect_chenalh\u00f3", "tzo-dialect_chamula": "tzo-dialect_chamula", "tzj-dialect_western": "tzj-dialect_western", "tzj-dialect_eastern": "tzj-dialect_eastern", "aoz": "aoz", "udm": "udm", "udu": "udu", "ukr": "uk", "ppk": "ppk", "ubu": "ubu", "urk": "urk", "ura": "ura", "urt": "urt", "urd-script_devanagari": "ur", "urd-script_arabic": "ur", "urd-script_latin": "ur", "upv": "upv", "usp": "usp", "uig-script_arabic": "ug", "uig-script_cyrillic": "ug", "uzb-script_cyrillic": "uz", "vag": "vag", "bav": "bav", "vid": "vid", "vie": "vi", "vif": "vif", "vun": "vun", "vut": "vut", "prk": "prk", "wwa": "wwa", "rro": "rro", "bao": "bao", "waw": "waw", "lgl": "lgl", "wlx": "wlx", "cou": "cou", "hub": "hub", "gvc": "gvc", "mfi": "mfi", "wap": "wap", "wba": "wba", "war": "war", "way": "way", "guc": "guc", "cym": "cy", "kvw": "kvw", "tnp": "tnp", "hto": "hto", "huu": "huu", "wal-script_latin": "wal-script_latin", "wal-script_ethiopic": "wal-script_ethiopic", "wlo": "wlo", "noa": "noa", "wob": "wob", "kao": "kao", "xer": "xer", "yad": "yad", "yka": "yka", "sah": "sah", "yba": "yba", "yli": "yli", "nlk": "nlk", "yal": "yal", "yam": "yam", "yat": "yat", "jmd": "jmd", "tao": "tao", "yaa": "yaa", "ame": "ame", "guu": "guu", "yao": "yao", "yre": "yre", "yva": "yva", "ybb": "ybb", "pib": "pib", "byr": "byr", "pil": "pil", "ycn": "ycn", "ess": "ess", "yuz": "yuz", "atb": "atb", "zne": "zne", "zaq": "zaq", "zpo": "zpo", "zad": "zad", "zpc": "zpc", "zca": "zca", "zpg": "zpg", "zai": "zai", "zpl": "zpl", "zam": "zam", "zaw": "zaw", "zpm": "zpm", "zac": "zac", "zao": "zao", "ztq": "ztq", "zar": "zar", "zpt": "zpt", "zpi": "zpi", "zas": "zas", "zaa": "zaa", "zpz": "zpz", "zab": "zab", "zpu": "zpu", "zae": "zae", "zty": "zty", "zav": "zav", "zza": "zza", "zyb": "zyb", "ziw": "ziw", "zos": "zos", "gnd": "gnd"},
        "samplerate": 16000,
        "files": ['config.json', 'G_100000.pth', 'vocab.txt', 'ref.wav'],
        "voice": None,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['GLOWTTS']: {
        "languages": {"eng": "en", "ukr": "uk", "tur": "tr", "ita": "it", "fas": "fa", "bel": "be"},
        "samplerate": 22050,
        "files": [],
        "voice": None,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 1, "CPU": 4, "RAM": 2, "Realism": 3}
    },
    TTS_ENGINES['TACOTRON']: {
        "languages": {"deu": "de", "eng": "en", "fra": "fr", "spa": "es"},
        "samplerate": 22050,
        "files": [],
        "voice": None,
        "voices": {},
        "devices": torch_devices,
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 3}
    },
    TTS_ENGINES['YOURTTS']: {
        "languages": {"eng": "en", "fra": "fr", "por": "pt"},
        "samplerate": 16000,
        "files": [],
        "voice": None,
        "voices": {"Machinella-5": "female-en-5", "ElectroMale-2": "male-en-2", 'Machinella-4': 'female-pt-4\n', 'ElectroMale-3': 'male-pt-3\n'},
        "devices": torch_devices,
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 1, "Realism": 2}
    }
}
# audio.cpp engines, values from audio.cpp v0.9.2 (model_specs/<family>.json and the family's session code).
# languages: e2a iso-639-3 -> what the family reads as the text language ("" = the model detects it);
# language_option: also sent as the "language" request option (the family ignores the text language);
# clone: True = clones the voice file picked in e2a, False = built-in voice (voice_ids) converted by Seed-VC when a
# voice file is picked; voice_ids: built-in voice per language ("*" = any); ref_min / ref_max: reference clip window (s);
# ref_text: None, "optional" (sent when the ASR finds one) or "required" (the clone needs it); ref_fallback: request
# options sent instead when a required transcript is empty; load / session / request: the server config's load_options /
# session_options / default_request_options; load_by_language: load options per language (one package per language);
# speaker_label: VibeVoice reads only "Speaker N:" script lines; espeak: Kokoro phonemizes through e2a's eSpeak-ng;
# samplerate: initial value only, the first reply sets the real one; rating: estimates from the model sizes
audiocpp_families = {
    TTS_ENGINES['BREEZE_TTS']: {"family": "breeze_tts", "languages": {"zho": "zh", "eng": "en"}, "clone": True, "ref_text": "required", "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 4}},
    TTS_ENGINES['CHATTERBOX']: {"family": "chatterbox", "languages": {"ara": "ar", "dan": "da", "deu": "de", "ell": "el", "eng": "en", "spa": "es", "fin": "fi", "fra": "fr", "hin": "hi", "ita": "it", "kor": "ko", "zlm": "ms", "nld": "nl", "nob": "no", "nor": "no", "pol": "pl", "por": "pt", "swe": "sv", "swh": "sw", "tur": "tr"}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 3, "CPU": 3, "RAM": 4, "Realism": 5}},
    # F32 package only: the heaviest of the small models
    TTS_ENGINES['CONFUCIUS4_TTS']: {"family": "confucius4_tts", "languages": {"zho": "zh", "eng": "en", "jpn": "ja", "kor": "ko", "deu": "de", "fra": "fr", "spa": "es", "ind": "id", "ita": "it", "tha": "th", "por": "pt", "rus": "ru", "zlm": "ms", "vie": "vi"}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 22050, "rating": {"VRAM": 6, "CPU": 2, "RAM": 8, "Realism": 4}},
    # zero_shot needs the transcript; without one, cross_lingual clones from the audio alone
    TTS_ENGINES['COSYVOICE3']: {"family": "cosyvoice3", "languages": {"zho": "zh", "eng": "en", "jpn": "ja", "kor": "ko", "deu": "de", "spa": "es", "fra": "fr", "ita": "it", "rus": "ru", "yue": "yue"}, "clone": True, "ref_text": "required", "ref_fallback": {"template_name": "cross_lingual"}, "samplerate": 24000, "rating": {"VRAM": 3, "CPU": 3, "RAM": 4, "Realism": 5}},
    # the language becomes an [EN]-style tag; audio.cpp documents only "multilingual" (en, zh in its examples)
    TTS_ENGINES['DOTS_TTS']: {"family": "dots_tts", "languages": {"eng": "en", "zho": "zh"}, "clone": True, "ref_text": "optional", "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 4}},
    # 48 kHz stereo, mixed down to mono by convert()
    TTS_ENGINES['DRAMABOX']: {"family": "dramabox", "languages": {"eng": "en"}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 48000, "rating": {"VRAM": 8, "CPU": 1, "RAM": 10, "Realism": 5}},
    TTS_ENGINES['FIRERED_AUDIO']: {"family": "firered_audio", "languages": {"zho": "zh", "eng": "en"}, "clone": True, "ref_text": "required", "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 6, "CPU": 1, "RAM": 8, "Realism": 4}},
    # language tags are names, not codes (<|English|>)
    TTS_ENGINES['FIREREDTTS3']: {"family": "fireredtts3", "languages": {"zho": "Chinese", "eng": "English", "yue": "Cantonese", "jpn": "Japanese", "kor": "Korean", "spa": "Spanish", "fra": "French", "rus": "Russian", "ara": "Arabic", "tur": "Turkish", "ind": "Indonesian", "por": "Portuguese", "ita": "Italian", "nld": "Dutch", "vie": "Vietnamese", "deu": "German", "ukr": "Ukrainian", "tha": "Thai", "pol": "Polish", "ron": "Romanian", "ell": "Greek", "ces": "Czech", "fin": "Finnish", "hin": "Hindi"}, "clone": True, "ref_text": "required", "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 6, "CPU": 1, "RAM": 8, "Realism": 5}},
    # Fish Audio's tier 1 and 2 languages (the model detects them); audio.cpp tested English and Chinese
    TTS_ENGINES['FISH_AUDIO']: {"family": "fish_audio", "languages": {"eng": "en", "zho": "zh", "jpn": "ja", "kor": "ko", "spa": "es", "por": "pt", "ara": "ar", "rus": "ru", "fra": "fr", "deu": "de"}, "clone": True, "ref_text": "required", "ref_fallback": {}, "samplerate": 44100, "rating": {"VRAM": 8, "CPU": 1, "RAM": 10, "Realism": 5}},
    # Higgs v3 claims 100+ languages, detected by the model: the major ones first
    TTS_ENGINES['HIGGS_AUDIO_TTS']: {"family": "higgs_audio_tts", "languages": {"eng": "en", "zho": "zh", "jpn": "ja", "kor": "ko", "deu": "de", "fra": "fr", "spa": "es", "ita": "it", "por": "pt", "rus": "ru"}, "clone": True, "ref_text": "optional", "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 8, "CPU": 1, "RAM": 10, "Realism": 5}},
    # reads its language from the request options only (else zh on Han text, en otherwise); v2 presets: zh, en
    TTS_ENGINES['INDEX_TTS2']: {"family": "index_tts2", "languages": {"zho": "zh", "eng": "en", "jpn": "ja", "spa": "es", "ara": "ar"}, "language_option": True, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 22050, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 5}},
    TTS_ENGINES['IRODORI_TTS']: {"family": "irodori_tts", "languages": {"jpn": "ja"}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 48000, "rating": {"VRAM": 2, "CPU": 3, "RAM": 4, "Realism": 4}},
    # the voice prefix decides the language; Japanese needs UniDic, missing from the release GGUF
    TTS_ENGINES['KOKORO_TTS']: {"family": "kokoro_tts", "languages": {"eng": "en-us", "spa": "es", "fra": "fr-fr", "hin": "hi", "ita": "it", "por": "pt-br", "zho": "zh"}, "clone": False, "voice_ids": {"eng": "af_heart", "spa": "ef_dora", "fra": "ff_siwis", "hin": "hf_alpha", "ita": "if_sara", "por": "pf_dora", "zho": "zf_xiaobei"}, "espeak": True, "samplerate": 24000, "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 4}},
    # the model reads the language from the text; "default" is a German voice, english_female a British one
    TTS_ENGINES['KUGELAUDIO']: {"family": "kugelaudio", "languages": {"eng": "", "deu": "", "fra": "", "spa": "", "ita": "", "por": "", "nld": "", "pol": "", "rus": "", "ukr": "", "ces": "", "ron": "", "hun": "", "swe": "", "dan": "", "fin": "", "nob": "", "nor": "", "ell": "", "bul": "", "slk": "", "hrv": "", "srp": "", "tur": ""}, "clone": False, "voice_ids": {"eng": "english_female", "*": "default"}, "samplerate": 24000, "rating": {"VRAM": 6, "CPU": 1, "RAM": 8, "Realism": 4}},
    TTS_ENGINES['MAGPIE_TTS']: {"family": "magpie_tts", "languages": {"ara": "ar-MSA", "deu": "de", "eng": "en", "spa": "es", "fra": "fr", "hin": "hi", "ita": "it", "kor": "ko", "por": "pt-BR", "vie": "vi", "zho": "zh"}, "clone": False, "voice_ids": {"*": "Aria"}, "samplerate": 22050, "rating": {"VRAM": 2, "CPU": 3, "RAM": 4, "Realism": 4}},
    # voice designed from a description (required by the model), converted by Seed-VC when a voice file is picked
    TTS_ENGINES['MAYA1']: {"family": "maya1", "languages": {"eng": "en"}, "clone": False, "request": {"instruct": "Calm adult narrator with a neutral American accent, warm timbre and steady audiobook pacing."}, "samplerate": 24000, "rating": {"VRAM": 6, "CPU": 1, "RAM": 8, "Realism": 5}},
    TTS_ENGINES['MIOTTS']: {"family": "miotts", "languages": {"eng": "", "jpn": ""}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 44100, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 4}},
    # the language goes verbatim into the prompt template: "" lets the model detect it
    TTS_ENGINES['MOSS_TTS_LOCAL']: {"family": "moss_tts_local", "languages": {"ara": "", "ces": "", "dan": "", "deu": "", "ell": "", "eng": "", "spa": "", "fas": "", "fin": "", "fra": "", "heb": "", "hin": "", "hun": "", "ita": "", "jpn": "", "kor": "", "mkd": "", "zlm": "", "nld": "", "pol": "", "por": "", "ron": "", "rus": "", "swe": "", "swh": "", "tha": "", "tgl": "", "fil": "", "tur": "", "vie": "", "yue": "", "zho": ""}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 24000, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 4}},
    TTS_ENGINES['MOSS_TTS_NANO']: {"family": "moss_tts_nano", "languages": {"ara": "", "ces": "", "dan": "", "deu": "", "ell": "", "eng": "", "spa": "", "fas": "", "fra": "", "hun": "", "ita": "", "jpn": "", "kor": "", "pol": "", "por": "", "rus": "", "swe": "", "tur": "", "zho": ""}, "clone": True, "ref_text": "optional", "ref_fallback": {}, "samplerate": 48000, "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 3}},
    TTS_ENGINES['NEUTTS']: {"family": "neutts", "languages": {"eng": "en"}, "clone": False, "voice_ids": {"*": "emily"}, "samplerate": 24000, "rating": {"VRAM": 2, "CPU": 3, "RAM": 4, "Realism": 4}},
    # one package per language (the preset's files_by_language)
    TTS_ENGINES['POCKET_TTS']: {"family": "pocket_tts", "languages": {"eng": "en", "fra": "fr", "deu": "de", "ita": "it", "por": "pt", "spa": "es"}, "clone": True, "ref_text": None, "ref_fallback": {}, "load_by_language": {"eng": {"language": "english"}, "fra": {"language": "french"}, "deu": {"language": "german"}, "ita": {"language": "italian"}, "por": {"language": "portuguese"}, "spa": {"language": "spanish"}}, "samplerate": 24000, "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 4}},
    TTS_ENGINES['QWEN3_TTS']: {"family": "qwen3_tts", "languages": {"zho": "zh", "eng": "en", "jpn": "ja", "kor": "ko", "deu": "de", "fra": "fr", "rus": "ru", "por": "pt", "spa": "es", "ita": "it"}, "clone": True, "ref_text": "required", "ref_fallback": {"x_vector_only_mode": True}, "samplerate": 24000, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 5}},
    TTS_ENGINES['SUPERTONIC']: {"family": "supertonic", "languages": {"eng": "en", "kor": "ko", "jpn": "ja", "ara": "ar", "bul": "bg", "ces": "cs", "dan": "da", "deu": "de", "ell": "el", "spa": "es", "est": "et", "fin": "fi", "fra": "fr", "hin": "hi", "hrv": "hr", "hun": "hu", "ind": "id", "ita": "it", "lit": "lt", "lav": "lv", "nld": "nl", "pol": "pl", "por": "pt", "ron": "ro", "rus": "ru", "slk": "sk", "sln": "sl", "swe": "sv", "tur": "tr", "ukr": "uk", "vie": "vi"}, "clone": False, "voice_ids": {"*": "M1"}, "samplerate": 44100, "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 4}},
    TTS_ENGINES['VIBEVOICE']: {"family": "vibevoice", "languages": {"eng": "", "zho": ""}, "clone": True, "ref_text": None, "ref_fallback": {}, "speaker_label": True, "samplerate": 24000, "rating": {"VRAM": 4, "CPU": 1, "RAM": 8, "Realism": 5}},
    TTS_ENGINES['VOXCPM2']: {"family": "voxcpm2", "languages": {"ara": "ar", "mya": "my", "zho": "zh", "dan": "da", "nld": "nl", "eng": "en", "fin": "fi", "fra": "fr", "deu": "de", "ell": "el", "heb": "he", "hin": "hi", "ind": "id", "ita": "it", "jpn": "ja", "khm": "km", "kor": "ko", "lao": "lo", "zlm": "ms", "nob": "no", "nor": "no", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "swh": "sw", "swe": "sv", "tgl": "tl", "fil": "tl", "tha": "th", "tur": "tr", "vie": "vi"}, "clone": True, "ref_text": None, "ref_fallback": {}, "samplerate": 48000, "rating": {"VRAM": 4, "CPU": 2, "RAM": 6, "Realism": 5}},
    TTS_ENGINES['VOXTRAL_TTS']: {"family": "voxtral_tts", "languages": {"eng": "en", "fra": "fr", "spa": "es", "deu": "de", "ita": "it", "por": "pt", "nld": "nl", "ara": "ar", "hin": "hi"}, "clone": False, "voice_ids": {"eng": "casual_male", "fra": "fr_male", "spa": "es_male", "deu": "de_male", "ita": "it_male", "por": "pt_male", "nld": "nl_male", "ara": "ar_male", "hin": "hi_male"}, "samplerate": 24000, "rating": {"VRAM": 8, "CPU": 1, "RAM": 10, "Realism": 5}}
}
audiocpp_engines = list(audiocpp_families)
for _acpp_engine, _acpp_cfg in audiocpp_families.items():
    _acpp_cfg = {"language_option": False, "voice_ids": {}, "ref_text": None, "ref_fallback": {}, "ref_min": 3.2, "ref_max": 10.0, "load": {}, "session": {}, "request": {}, "load_by_language": {}, "speaker_label": False, "espeak": False, **_acpp_cfg}
    audiocpp_families[_acpp_engine] = _acpp_cfg
    default_engine_settings[_acpp_engine] = {
        "devices": native_devices,
        "audiocpp": _acpp_cfg,
        "languages": _acpp_cfg['languages'],
        "samplerate": _acpp_cfg['samplerate'],
        "files": [],
        "voice": default_speaker if _acpp_cfg['clone'] else None,
        "voices": {},
        "rating": _acpp_cfg['rating']
    }
# built-in voice engines: e2a offers their own voice as "default" (voice None), as for Piper
tts_engines_with_inner_speaker += [_acpp_engine for _acpp_engine, _acpp_cfg in audiocpp_families.items() if not _acpp_cfg['clone']]
# engine order (gradio's engine list follows default_engine_settings, the CLI help TTS_ENGINES): most realistic first,
# then the fastest on CPU, then the smallest VRAM, then the smallest RAM; ties by name. When a language change rules
# out the current engine, gradio picks the first compatible one, so the best rated
_acpp_order = sorted(default_engine_settings, key=lambda engine: (-default_engine_settings[engine]['rating']['Realism'], -default_engine_settings[engine]['rating']['CPU'], default_engine_settings[engine]['rating']['VRAM'], default_engine_settings[engine]['rating']['RAM'], engine))
_acpp_keys = {value: key for key, value in TTS_ENGINES.items()}
_acpp_settings = {engine: default_engine_settings[engine] for engine in _acpp_order}
default_engine_settings.clear()
default_engine_settings.update(_acpp_settings)
TTS_ENGINES.clear()
TTS_ENGINES.update({_acpp_keys[engine]: engine for engine in _acpp_order})