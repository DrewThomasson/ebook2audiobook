from typing import Any
from lib.classes.tts_registry import TTSRegistry

class TTSManager:

    def __init__(self, session:Any)->None:
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
        # a native crash while loading (no Python exception, no session in the report) then says what loaded and the RAM left
        from lib.classes.bug_reporter import bug_reporter
        bug_reporter.note(f"loading {engine_name} ({session.get('fine_tuned')}) on {session.get('device')}", ram=True)
        self.engine = engine_cls(session)
        bug_reporter.note(f'{engine_name} loaded')
    
    def set_voice(self, block_voice:str|None)->tuple:
        return self.engine._set_voice(block_voice)

    def convert_sentence2audio(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        return self.engine.convert(sentence_file, sentence, **kwargs)