import os, shutil, hashlib

from typing import Any
from lib.classes.tts_registry import TTSRegistry
from lib.lang import legends

class TTSManager:

    def __init__(self, session:Any, verify:bool=False)->None:
        self.session = session
        self.verifier = None
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
        # the conversion only (core.py): an edit preview is listened to right away
        if verify:
            from lib.classes.sentence_verifier import SentenceVerifier
            self.verifier = SentenceVerifier(session)

    def set_voice(self, block_voice:str|None)->tuple:
        return self.engine._set_voice(block_voice)

    def _file_digest(self, path:str)->str:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _drop_file(self, path:str)->None:
        if os.path.exists(path):
            os.unlink(path)

    def convert_sentence2audio(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        if self.verifier is None:
            return self.engine.convert(sentence_file, sentence, **kwargs)
        # each failed take is generated again (the engines draw a new one on each call), the best take is kept when
        # all of them fail. Two identical takes in a row: the engine gives the same audio each time, no use going on
        best_file = os.path.join(os.path.dirname(sentence_file), f'__verify_best_{os.path.basename(sentence_file)}')
        best = None
        last_digest = None
        for attempt in range(self.verifier.retries + 1):
            run, error = self.engine.convert(sentence_file, sentence, **kwargs)
            if not run or not os.path.exists(sentence_file):
                self._drop_file(best_file)
                return run, error
            result = self.verifier.check(sentence_file, sentence, attempt == 0)
            if result['ok']:
                self._drop_file(best_file)
                return True, None
            if best is None or result['badness'] < best['badness']:
                shutil.copyfile(sentence_file, best_file)
                best = result
            digest = self._file_digest(sentence_file)
            if digest == last_digest:
                break
            last_digest = digest
            if attempt < self.verifier.retries:
                msg = legends['msg_verify_retry'].format(reason=result['reason'], attempt=attempt + 1, retries=self.verifier.retries)
                print(msg)
        os.replace(best_file, sentence_file)
        self.verifier.flag(sentence_file, sentence, best)
        return True, None

    def close_verifier(self)->None:
        if self.verifier is not None:
            self.verifier.close()
            self.verifier = None
