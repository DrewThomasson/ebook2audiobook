import importlib
import threading
import lib.classes.tts_engines

from typing import Dict, Any
from functools import lru_cache
from lib.classes.tts_registry import TTSRegistry

_lock = threading.Lock()
_models_cache:Dict[str, Dict[str, Any]] = {}

def load_engine_presets(engine:str)->Dict[str, Any]:
    with _lock:
        if engine in _models_cache:
            return _models_cache[engine]
        module = importlib.import_module(
            f"lib.classes.tts_engines.presets.{engine}_presets"
        )
        if not hasattr(module, "models"):
            raise RuntimeError(
                f"'models' not found in {engine}_presets"
            )
        _models_cache[engine] = module.models
        return module.models

class TTSManager:

    def __init__(self, session: Any) -> None:
        self.session = session
        engine_name = session.get("tts_engine")
        if engine_name is None:
            raise ValueError("session['tts_engine'] is missing")
        try:
            engine_cls = TTSRegistry.ENGINES[engine_name]
        except KeyError:
            raise ValueError(
                f"Invalid tts_engine '{engine_name}'. "
                f"Expected one of: {', '.join(TTSRegistry.ENGINES)}"
            )
        self.engine = engine_cls(session)
        self.engine.models = load_engine_presets(engine_name)

    def convert_sentence2audio(self, sentence_number: int, sentence: str) -> bool:
        return self.engine.convert(sentence_number, sentence)