"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use this for lightweight, idempotent environment patches.

This version is guaranteed build-safe for:
• PyTorch source builds
• CMake / pip toolchains
• Deep NLP toolchains (stanza, transformers, etc.)
• Jetson CUDA environments

It patches transformers.check_torch_load_is_safe ONLY if/when transformers is imported.

Compatible with Python 3.10 → 3.14.
"""

import sys, os, importlib
from types import ModuleType, FunctionType
from typing import Any

# Enable debug logging via:
#   export DEBUG_SITECUSTOMIZE=1
debug = os.environ.get('DEBUG_SITECUSTOMIZE') == '1'
def warn(msg: str) -> None:
    if debug:
        print(f'[sitecustomize] {msg}')

# ─────────────────────────────────────────────────────
# SAFETY MODE → skip entirely during PyTorch/CMake builds
# (but DO NOT exit Python — just skip logic)
# ─────────────────────────────────────────────────────
inactive = any(os.environ.get(v) == '1' for v in [
    'TORCH_BUILD', 'PYTORCH_BUILD', 'DISABLE_SITECUSTOMIZE'
])

if inactive:
    warn('inactive (torch build or manual disable)')
    patch_enabled = False
else:
    patch_enabled = True


# ─────────────────────────────────────────────────────
# Patch definition (lazy applied only after modules load)
# ─────────────────────────────────────────────────────
def wrapped_check_torch_load_is_safe(*args: Any, **kwargs: Any) -> None:
    warn('patched transformers check_torch_load_is_safe')
    return None

def patch_module(mod: ModuleType, attr='check_torch_load_is_safe') -> None:
    if hasattr(mod, attr):
        setattr(mod, attr, wrapped_check_torch_load_is_safe)
        warn(f'patched {mod.__name__}.{attr}')

    # Patch missing isin_mps_friendly for newer transformers
    if mod.__name__ == 'transformers.pytorch_utils' and not hasattr(mod, 'isin_mps_friendly'):
        import torch
        mod.isin_mps_friendly = torch.isin
        warn(f'patched {mod.__name__}.isin_mps_friendly')

    # Rewrite use_auth_token → token for newer huggingface_hub
    if mod.__name__ == 'huggingface_hub':
        for fn_name in dir(mod):
            fn = getattr(mod, fn_name, None)
            if not isinstance(fn, FunctionType) or fn_name.startswith('_'):
                continue

            def _make_wrapper(fn):

                def wrapper(*args, **kwargs):
                    if 'use_auth_token' in kwargs:
                        kwargs['token'] = kwargs.pop('use_auth_token')
                        warn(f'rewrote use_auth_token → token in {fn.__name__}()')
                    return fn(*args, **kwargs)
                return wrapper

            setattr(mod, fn_name, _make_wrapper(fn))
        warn(f'patched all callables in {mod.__name__} (use_auth_token compat)')


# ─────────────────────────────────────────────────────
# IMPORT HOOK (activates only when modules load)
# ─────────────────────────────────────────────────────
if patch_enabled:

    class WrappedLoader:
        """Composition-based loader wrapper.
        Delegates to the original loader regardless of its type,
        avoiding constructor signature mismatches across loader classes.
        Compatible with all loader types (source, extension, frozen, namespace).
        """

        def __init__(self, orig):
            self._orig = orig

        def create_module(self, spec):
            if hasattr(self._orig, 'create_module'):
                return self._orig.create_module(spec)
            return None

        def exec_module(self, module):
            self._orig.exec_module(module)
            if module.__name__.startswith(('transformers', 'huggingface_hub')):
                patch_module(module)

    class TransformersHook:
        def find_spec(self, fullname, path, target=None):
            if not fullname.startswith(('transformers', 'huggingface_hub')):
                return None

            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            if not spec or not spec.loader:
                return spec

            spec.loader = WrappedLoader(spec.loader)
            return spec

    sys.meta_path.insert(0, TransformersHook())
    warn('active (lazy transformers patch mode)')

else:
    warn('loaded but inactive (no patches applied)')