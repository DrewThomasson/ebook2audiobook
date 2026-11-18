"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use this for lightweight, idempotent environment patches.

This version is guaranteed build-safe for:
- PyTorch source builds
- CMake / pip toolchains
- Jetson CUDA environments

It replaces torchaudio.load ONLY if/when torchaudio is imported (avoids torchcodec
DLL load failures on PyTorch ROCm/Windows builds).
It configures PyTorch safe globals for Coqui-TTS compatibility.
It makes torch.xpu report no device when E2A_XPU_UNUSABLE=1 (Intel GPU torch xpu
cannot run on: its device count is a Windows access violation).
"""

import sys, os, importlib
import importlib.machinery
from types import ModuleType

# Enable debug logging via:
#   export DEBUG_SITECUSTOMIZE=1
debug = os.environ.get('DEBUG_SITECUSTOMIZE') == '1'
def warn(msg: str)->None:
    if debug:
        print(f'[sitecustomize] {msg}')

# ────────────────────────────────────────────────────────
# SAFETY MODE → skip entirely during PyTorch/CMake builds
# (but DO NOT exit Python — just skip logic)
# ────────────────────────────────────────────────────────
inactive = any(os.environ.get(v) == '1' for v in [
    'TORCH_BUILD', 'PYTORCH_BUILD', 'DISABLE_SITECUSTOMIZE'
])

if inactive:
    warn('inactive (torch build or manual disable)')
    patch_enabled = False
else:
    patch_enabled = True

# ─────────────────────────────────────────────────────
# Patch definitions (lazy applied only after modules load)
# ─────────────────────────────────────────────────────
def patch_torchaudio(mod: ModuleType)->None:
    """Replace torchaudio.load with a soundfile-backed shim."""
    if getattr(getattr(mod, 'load', None), '__name__', '') == '_load_via_soundfile':
        return
    try:
        import soundfile as sf
        import torch
    except ImportError as e:
        warn(f'torchaudio.load patch skipped: {e!r}')
        return

    def _load_via_soundfile(uri, frame_offset:int=0, num_frames:int=-1,
                            normalize:bool=True, channels_first:bool=True,
                            **_ignored):
        start = int(frame_offset) if frame_offset else 0
        frames = -1 if (num_frames is None or num_frames<0) else int(num_frames)
        dtype = 'float32' if normalize else 'int16'
        data, sr = sf.read(uri, start=start, frames=frames,
                           dtype=dtype, always_2d=True)
        tensor = torch.from_numpy(data)
        if channels_first:
            tensor = tensor.T.contiguous()
        return tensor, sr

    mod.load = _load_via_soundfile
    warn('patched torchaudio.load → soundfile (bypass torchcodec)')

def patch_torch_xpu(mod: ModuleType)->None:
    """No XPU device, without asking the SYCL runtime, once DeviceInstaller set E2A_XPU_UNUSABLE=1.

    It does when detect_gpu.py, in its own process, found torch xpu cannot run on the Intel GPU (unsupported iGPU,
    driver too old). There torch.xpu.device_count() falls back to torch._C._xpu_getDeviceCount() when Level Zero
    Sysman fails, and the SYCL runtime dies enumerating the GPU: a Windows access violation no except catches.
    Third-party code asks it on its own, CPU sessions included: transformers at import (masking_utils ->
    is_torch_xpu_available). torch.xpu.is_available() and torch.accelerator.device_count()/is_available() read
    these attributes of the module, so they answer from here too."""
    if os.environ.get('E2A_XPU_UNUSABLE') != '1':
        return
    xpu = getattr(mod, 'xpu', None)
    if xpu is None or getattr(xpu.device_count, '__name__', '') == '_no_xpu_device_count':
        return

    def _no_xpu_device_count()->int:
        return 0

    def _no_xpu_is_available()->bool:
        return False

    xpu.device_count = _no_xpu_device_count
    xpu.is_available = _no_xpu_is_available
    warn('torch.xpu reports no device (E2A_XPU_UNUSABLE=1)')

def patch_torch(mod: ModuleType)->None:
    """Allowlist Coqui-TTS classes for PyTorch 2.6+ weights_only=True loading."""
    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        if hasattr(mod.serialization, 'add_safe_globals'):
            mod.serialization.add_safe_globals([XttsConfig])
            warn('added XttsConfig to torch safe globals')
    except Exception as e:
        warn(f'failed to add torch safe globals: {e!r}')


# ─────────────────────────────────────────────────────
# IMPORT HOOK (activates only when modules load)
# ─────────────────────────────────────────────────────
if patch_enabled:

    class WrappedLoader:
        """Composition-based loader wrapper."""

        def __init__(self, orig):
            self._orig = orig

        def create_module(self, spec):
            if hasattr(self._orig, 'create_module'):
                return self._orig.create_module(spec)
            return None

        def exec_module(self, module):
            self._orig.exec_module(module)
            name = module.__name__
            if name == 'torchaudio':
                patch_torchaudio(module)
            elif name == 'torch':
                # first, before patch_torch() runs any third-party import
                patch_torch_xpu(module)
                patch_torch(module)

    class LazyPatchHook:

        def find_spec(self, fullname, path, target=None):
            if fullname not in ('torchaudio', 'torch'):
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            if not spec or not spec.loader:
                return spec
            spec.loader = WrappedLoader(spec.loader)
            return spec

    sys.meta_path.insert(0, LazyPatchHook())
else:
    warn('loaded but inactive (no patches applied)')