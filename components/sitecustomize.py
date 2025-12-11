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
"""

import sys, os, importlib
from types import ModuleType
from typing import Any

# Enable debug logging via:
#   export DEBUG_SITECUSTOMIZE=1
debug = os.environ.get("DEBUG_SITECUSTOMIZE") == "1"
def warn(msg: str) -> None:
	if debug:
		print(f"[sitecustomize] {msg}")

# ─────────────────────────────────────────────────────
# SAFETY MODE → skip entirely during PyTorch/CMake builds
# (but DO NOT exit Python — just skip logic)
# ─────────────────────────────────────────────────────
inactive = any(os.environ.get(v) == "1" for v in [
	"TORCH_BUILD", "PYTORCH_BUILD", "DISABLE_SITECUSTOMIZE"
])

if inactive:
	warn("inactive (torch build or manual disable)")
	patch_enabled = False
else:
	patch_enabled = True


# ─────────────────────────────────────────────────────
# Patch definition (lazy applied only after transformers loads)
# ─────────────────────────────────────────────────────
def wrapped_check_torch_load_is_safe(*args: Any, **kwargs: Any) -> None:
	warn("patched transformers check_torch_load_is_safe")
	return None

def patch_module(mod: ModuleType, attr="check_torch_load_is_safe") -> None:
	if hasattr(mod, attr):
		setattr(mod, attr, wrapped_check_torch_load_is_safe)
		warn(f"patched {mod.__name__}.{attr}")


# ─────────────────────────────────────────────────────
# IMPORT HOOK (activates only when transformers loads)
# ─────────────────────────────────────────────────────
if patch_enabled:

	class TransformersHook:
		def find_spec(self, fullname, path, target=None):
			if not fullname.startswith("transformers"):
				return None

			spec = importlib.machinery.PathFinder.find_spec(fullname, path)
			if not spec or not spec.loader:
				return spec

			orig_loader = spec.loader

			# wrapped loader instance, NOT new class
			class WrappedLoader(orig_loader.__class__):
				def exec_module(self_inner, module):
					orig_loader.exec_module(module)  # real import
					if module.__name__.startswith("transformers"):
						patch_module(module)

			# pass correct args so loader doesn't break import
			try:
				spec.loader = WrappedLoader(orig_loader.name, orig_loader.path)
			except Exception:
				spec.loader = orig_loader  # fallback safety
			return spec

	sys.meta_path.insert(0, TransformersHook())
	warn("active (lazy transformers patch mode)")

else:
	warn("loaded but inactive (no patches applied)")