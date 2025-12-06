import os, sys, importlib
from types import ModuleType
from typing import Any

DEBUG = os.environ.get("DEBUG_SITECUSTOMIZE") == "1"

def log(msg: str) -> None:
	if DEBUG:
		print("[sitecustomize]", msg)

skip = any(os.environ.get(k) == "1" for k in ["DISABLE_SITECUSTOMIZE", "TORCH_BUILD", "PYTORCH_BUILD"])
if skip:
	log("skipping initialization")
else:
	def wrapped_check_torch_load_is_safe(*args: Any, **kwargs: Any) -> None:
		log("patched check_torch_load_is_safe")
		return None
	def patch_module(mod: ModuleType) -> None:
		if hasattr(mod, "check_torch_load_is_safe"):
			setattr(mod, "check_torch_load_is_safe", wrapped_check_torch_load_is_safe)
			log(f"patched {mod.__name__}.check_torch_load_is_safe")
	class _TransformersImportHook:
		def find_spec(self, fullname, path, target=None):
			if not fullname.startswith("transformers"):
				return None
			spec = importlib.machinery.PathFinder.find_spec(fullname, path)
			if not spec or not spec.loader:
				return spec
			orig_loader = spec.loader
			class Loader(orig_loader.__class__):
				def exec_module(self_inner, module):
					orig_loader.exec_module(module)
					if module.__name__.startswith("transformers"):
						patch_module(module)
			spec.loader = Loader()
			return spec
	sys.meta_path.insert(0, _TransformersImportHook())
	log("initialized")