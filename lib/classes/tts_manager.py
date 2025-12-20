from typing import Any
from lib.classes.tts_registry import TTSRegistry

import lib.classes.tts_engines

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

    def convert_sentence2audio(self, sentence_number:int, sentence:str)->bool:
        return self.engine.convert(sentence_number, sentence)