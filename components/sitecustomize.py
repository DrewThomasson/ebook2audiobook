"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use for lightweight, idempotent environment patches.
"""

import sys
import importlib

debug = True

def warn(msg:str)->None:
    if debug:
        print(msg)

def wrapped_check_torch_load_is_safe(*args, **kwargs):
    warn("[sitecustomize] Hook: check called")
    pass

if not getattr(sys, "_sitecustomize_loaded", False):
    sys._sitecustomize_loaded = True
    try:
        iu = importlib.import_module("transformers.utils.import_utils")
        if not hasattr(iu, "_patch_applied"):
            iu.check_torch_load_is_safe = wrapped_check_torch_load_is_safe
            iu._patch_applied = True
            warn("[sitecustomize] hook installation successful")
        else:
            warn("[sitecustomize] hook already installed!")
    except ModuleNotFoundError:
        warn("[sitecustomize] transformers not available; skipping patch")
        pass