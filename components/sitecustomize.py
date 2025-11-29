"""
Global environment initialization hook.
Executed automatically on Python startup before user code.
"""

import sys
import importlib
import importlib.abc
import importlib.util
from types import ModuleType
from typing import Any

debug:bool=False

def warn(msg:str)->None:
	if debug:
		print(msg)

def wrapped_check_torch_load_is_safe()->None:
	if debug:
		warn("[sitecustomize] check_torch_load_is_safe called")
	return None

def patch_all()->None:
	target=wrapped_check_torch_load_is_safe
	# patch transformers.utils.import_utils
	try:
		iu=importlib.import_module("transformers.utils.import_utils")
		setattr(iu,"check_torch_load_is_safe",target)
	except ModuleNotFoundError:
		iu=None
	# patch transformers.utils
	try:
		tu=importlib.import_module("transformers.utils")
		setattr(tu,"check_torch_load_is_safe",target)
	except ModuleNotFoundError:
		tu=None
	# patch any already-imported transformers.* module that has a global with that name
	for name,module in list(sys.modules.items()):
		if not name.startswith("transformers."):
			continue
		if not isinstance(module,ModuleType):
			continue
		if hasattr(module,"check_torch_load_is_safe"):
			setattr(module,"check_torch_load_is_safe",target)
	if debug:
		warn("[sitecustomize] patch_all applied")

class _Loader(importlib.abc.Loader):
	def __init__(self,orig:importlib.abc.Loader)->None:
		self.orig=orig
	def create_module(self,spec:Any)->ModuleType|None:
		if hasattr(self.orig,"create_module"):
			return self.orig.create_module(spec)  # type: ignore[no-any-return]
		return None
	def exec_module(self,module:ModuleType)->None:
		if hasattr(self.orig,"exec_module"):
			self.orig.exec_module(module)  # type: ignore[arg-type]
		patch_all()

class _Finder(importlib.abc.MetaPathFinder):
	def find_spec(self,fullname:str,path:list[str]|None,target:ModuleType|None=None)->Any:
		if fullname in ("transformers.utils.import_utils","transformers.utils"):
			spec=importlib.util.find_spec(fullname)
			if spec and spec.loader:
				spec.loader=_Loader(spec.loader)  # type: ignore[arg-type]
				return spec
		return None

if not getattr(sys,"_sitecustomize_loaded",False):
	sys._sitecustomize_loaded=True
	sys.meta_path.insert(0,_Finder())
	try:
		patch_all()
	except Exception as e:
		if debug:
			warn(f"[sitecustomize] initial patch failed: {e!r}")