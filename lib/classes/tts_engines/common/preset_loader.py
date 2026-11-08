import importlib
import threading
from typing import Dict, Any
from lib.conf_models import audiocpp_engines

_lock = threading.Lock()
_presets_cache:Dict[str, Dict[str, Any]] = {}

def load_engine_presets(engine:str)->Dict[str, Any]:
    with _lock:
        if engine in _presets_cache:
            return _presets_cache[engine]
        # audio.cpp engines share one presets module, keyed by engine
        module_name = 'audiocpp' if engine in audiocpp_engines else engine
        try:
            module = importlib.import_module(f"lib.classes.tts_engines.presets.{module_name}_presets")
        except Exception as e:
            raise ImportError(f"Failed to import presets for engine '{engine}'") from e
        if not hasattr(module, "models"):
            raise RuntimeError(f"'models' not found in {module_name}_presets")
        _presets_cache[engine] = module.models[engine] if module_name != engine else module.models
        return _presets_cache[engine]