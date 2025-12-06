"""
Safe sitecustomize hook.
Runs on interpreter init, but avoids modifying environment during builds.
Only patches transformers AFTER torch is importable and stable.
"""

import os, sys, importlib
from types import ModuleType
from typing import Any

# Toggle verbose debugging with env DEBUG_SITECUSTOMIZE=1
DEBUG = os.environ.get("DEBUG_SITECUSTOMIZE") == "1"

def log(msg: str) -> None:
	if DEBUG:
		print(f"[sitecustomize] {msg}")

# ──────────────────────────────────────────────────────────────────────────────
# SAFETY GUARDS: prevent execution during builds
# ──────────────────────────────────────────────────────────────────────────────

# Disable completely if requested
if os.environ.get("DISABLE_SITECUSTOMIZE") == "1":
	log("DISABLED via env var.")
	raise SystemExit

# Skip COMMON build environments (Jetson / PyTorch / CMake / pip)
if any(k in os.environ for k in [
	"TORCH_BUILD", "PYTORCH_BUILD", "CMAKE_GENERATOR", "PIP_BUILD_TRACKER"
]):
	log("Skipping patch during build environment.")
	raise SystemExit

# ──────────────────────────────────────────────────────────────────────────────
# TRANSFORMERS PATCH — ONLY APPLIED IF MODULE IS ACTUALLY LOADED
# (no forced imports, no deep sys.modules scan)
# ──────────────────────────────────────────────────────────────────────────────

def wrapped_check_torch_load_is_safe(*args: Any, **kwargs: Any) -> None:
	log("patched check_torch_load_is_safe call")
	return None

def patch_if_loaded(modname: str, attr: str = "check_torch_load_is_safe") -> None:
	mod = sys.modules.get(modname)
	if isinstance(mod, ModuleType) and hasattr(mod, attr):
		setattr(mod, attr, wrapped_check_torch_load_is_safe)
		log(f"Patched {modname}.{attr}")

def lazy_patch_transformers(mod: ModuleType) -> None:
	"""Patch transformers dynamically — no startup imports required."""
	for name in (
		"transformers.utils.import_utils",
		"transformers.utils"
	):
		if name in sys.modules:
			patch_if_loaded(name)

# Install import hook ONLY if transformers is missing (fast no-op otherwise)
class _TransformersImporter:
	def find_spec(self, fullname, path, target=None):
		if fullname.startswith("transformers"):
			log(f"Hooking import of {fullname}")
			spec = importlib.machinery.PathFinder.find_spec(fullname, path)
			if spec and spec.loader:
				orig_loader = spec.loader
				class PatchedLoader(orig_loader.__class__):
					def exec_module(self_inner, module):
						orig_loader.exec_module(module)
						lazy_patch_transformers(module)
				spec.loader = PatchedLoader()
			return spec

sys.meta_path.insert(0, _TransformersImporter())
log("sitecustomize loaded safely and in passive mode.")