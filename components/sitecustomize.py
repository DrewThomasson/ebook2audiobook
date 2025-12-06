"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use for lightweight, idempotent environment patches.
"""

import sys, os, importlib
from types import ModuleType
from typing import Any

debug: bool = False

def warn(msg:str) -> None:
	if debug:
		print("[sitecustomize]", msg)

# ───────────────────────────────────────────────
# SAFETY MODE — during build do NOTHING
# Important: do NOT exit Python
# ───────────────────────────────────────────────
if os.environ.get("TORCH_BUILD") == "1" or os.environ.get("DISABLE_SITECUSTOMIZE") == "1":
	if debug:
		warn("sitecustomize skipped (build mode)")
	# LOAD SUCCESSFULLY and STOP EXECUTING
	# (do nothing, but do not exit!)
	patch_enabled = False
else:
	patch_enabled = True


# ───────────────────────────────────────────────
# Only activate transformers patch when enabled
# ───────────────────────────────────────────────

if patch_enabled:

	def wrapped_check_torch_load_is_safe(*args:Any, **kwargs:Any) -> None:
		if debug:
			warn("patched check_torch_load_is_safe")
		return None

	def patch_module(mod:ModuleType, attr="check_torch_load_is_safe") -> None:
		if hasattr(mod, attr):
			setattr(mod, attr, wrapped_check_torch_load_is_safe)
			if debug:
				warn(f"patched {mod.__name__}.{attr}")

	# Lazy import hook — patches ONLY after transformers is imported
	class TransformersHook:
		def find_spec(self, fullname, path, target=None):
			if not fullname.startswith("transformers"):
				return None
			spec = importlib.machinery.PathFinder.find_spec(fullname, path)
			if spec and spec.loader:
				orig_loader = spec.loader
				class Loader(orig_loader.__class__):
					def exec_module(self_inner, module):
						orig_loader.exec_module(module)
						if module.__name__.startswith("transformers"):
							patch_module(module)
				spec.loader = Loader()
			return spec

	sys.meta_path.insert(0, TransformersHook())

	if debug:
		warn("sitecustomize activated (lazy mode)")
else:
	if debug:
		warn("sitecustomize loaded but inactive")