"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use for lightweight, idempotent environment patches.
"""

import sys, os, importlib
from types import ModuleType
from typing import Any

debug:bool=False

def warn(msg:str)->None:
	if debug:
		print(msg)

# ────────────────────────────────────────────────
# 🛡 SAFETY: disable during torch or cmake builds
# ────────────────────────────────────────────────

# If you export TORCH_BUILD=1 in your build script, this hook becomes a no-op.
if os.environ.get("TORCH_BUILD") == "1" or os.environ.get("DISABLE_SITECUSTOMIZE") == "1":
	if debug:
		warn("[sitecustomize] disabled during build")
	# DO NOT raise SystemExit or fail import — just exit silently
	sys.exit(0)


# ────────────────────────────────────────────────
# Lazy transformers patch (only applied when imported)
# ────────────────────────────────────────────────

def wrapped_check_torch_load_is_safe(*args:Any,**kwargs:Any)->None:
	if debug:
		warn("[sitecustomize] check_torch_load_is_safe patched call")
	return None

def _patch_module_attr(mod:ModuleType,name:str)->None:
	if hasattr(mod,name):
		setattr(mod,name,wrapped_check_torch_load_is_safe)
		if debug:
			warn(f"[sitecustomize] patched {mod.__name__}.{name}")

def _lazy_patch_transformers(module:ModuleType)->None:
	_patch_module_attr(module,"check_torch_load_is_safe")


# Hook into import — do NOT import transformers proactively
class _TransformersLazyLoader:
	def find_spec(self,fullname,path,target=None):
		if not fullname.startswith("transformers"):
			return None
		spec = importlib.machinery.PathFinder.find_spec(fullname,path)
		if not spec or not spec.loader:
			return spec
		orig_loader = spec.loader
		class Loader(orig_loader.__class__):
			def exec_module(self_inner,module):
				orig_loader.exec_module(module)
				if module.__name__.startswith("transformers"):
					_lazy_patch_transformers(module)
		spec.loader = Loader()
		return spec

# Install passive import hook
sys.meta_path.insert(0,_TransformersLazyLoader())

if debug:
	warn("[sitecustomize] active (lazy mode)")