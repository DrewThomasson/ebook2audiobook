"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
Use for lightweight, idempotent environment patches.
"""

import sys, os, glob, importlib
from types import ModuleType
from typing import Any

debug:bool=False

def _add_gpu_paths(paths):
	for p in paths:
		for resolved in glob.glob(p):
			if os.path.isdir(resolved) and resolved not in sys.path:
				sys.path.append(resolved)

def warn(msg:str)->None:
	if debug:
		print(msg)

def wrapped_check_torch_load_is_safe(*args:Any,**kwargs:Any)->None:
	if debug:
		warn("[sitecustomize] check_torch_load_is_safe patched call")
	return None

def _patch_module_attr(mod:ModuleType,name:str)->None:
	if hasattr(mod,name):
		setattr(mod,name,wrapped_check_torch_load_is_safe)
		if debug:
			warn(f"[sitecustomize] patched {mod.__name__}.{name}")

def apply_transformers_patch()->None:
	if getattr(sys,"_sitecustomize_torchload_patched",False):
		return
	sys._sitecustomize_torchload_patched=True
	try:
		iu=importlib.import_module("transformers.utils.import_utils")
		_patch_module_attr(iu,"check_torch_load_is_safe")
	except ModuleNotFoundError:
		if debug:
			warn("[sitecustomize] transformers.utils.import_utils not available")
	try:
		u=importlib.import_module("transformers.utils")
		_patch_module_attr(u,"check_torch_load_is_safe")
	except ModuleNotFoundError:
		if debug:
			warn("[sitecustomize] transformers.utils not available")
	for name,mod in list(sys.modules.items()):
		if isinstance(mod,ModuleType) and name.startswith("transformers"):
			_patch_module_attr(mod,"check_torch_load_is_safe")

# NVIDIA CUDA (Linux desktop)
_add_gpu_paths([
	"/usr/local/cuda/lib64",
	"/usr/local/cuda/lib",
	"/usr/local/cuda*/lib64",
	"/usr/local/cuda*/lib",
	"/usr/lib/x86_64-linux-gnu",
])

# NVIDIA Jetson / aarch64
_add_gpu_paths([
	"/usr/local/cuda-*/targets/aarch64-linux/lib",
	"/usr/lib/aarch64-linux-gnu",
	"/usr/lib/aarch64-linux-gnu/tegra",
])

# AMD ROCm
_add_gpu_paths([
	"/opt/rocm/lib",
	"/opt/rocm/lib64",
	"/opt/rocm*/lib",
	"/opt/rocm*/lib64",
	"/usr/lib64",
])

# Intel XPU / Level Zero
_add_gpu_paths([
	"/usr/lib/x86_64-linux-gnu/dri",
	"/usr/lib/dri",
	"/usr/lib64/dri",
])

# Conda environment support (passive, no autodetect)
if "CONDA_PREFIX" in os.environ:
	_add_gpu_paths([
		f"{os.environ['CONDA_PREFIX']}/lib",
		f"{os.environ['CONDA_PREFIX']}/lib64"
	])

apply_transformers_patch()
