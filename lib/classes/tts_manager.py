import os, shutil, hashlib

from typing import Any
from lib.classes.tts_registry import TTSRegistry
from lib.lang import legends

class TTSManager:

    def __init__(self, session:Any, verify:bool=False)->None:
        self.session = session
        self.verifier = None
        self.deterministic = False
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
        # a failed take is generated again, its text by levels (conf_models.py): new draws first (the engines draw a
        # new take on each call), then less punctuation, then none. The best take is kept when all of them fail
        best_file = os.path.join(os.path.dirname(sentence_file), f'__verify_best_{os.path.basename(sentence_file)}')
        # a deterministic engine gives the same audio for the same text: no new draws, no level with nothing to strip
        plan = []
        for level in self.verifier.levels:
            text = self.verifier.text_variant(sentence, level)
            if plan and self.deterministic and (level == plan[-1][0] or text == plan[-1][1]):
                continue
            plan.append((level, text))
        retries = len(plan) - 1
        stats = self.verifier.stats
        best = None
        result = None
        last_text = None
        last_digest = None
        for attempt, (level, text) in enumerate(plan):
            if attempt > 0:
                # found deterministic during this sentence
                if self.deterministic and text == last_text:
                    continue
                msg = legends[('msg_verify_retry', 'msg_verify_retry_light', 'msg_verify_retry_bare')[level]].format(reason=result['reason'], attempt=attempt, retries=retries)
                print(msg)
            run, error = self.engine.convert(sentence_file, text, **kwargs)
            if not run or not os.path.exists(sentence_file):
                self._drop_file(best_file)
                return run, error
            result = self.verifier.check(sentence_file, sentence, attempt == 0)
            if attempt == 0:
                stats['checked'] += 1
            if result['ok']:
                if attempt > 0:
                    stats[('fixed_redraw', 'fixed_light', 'fixed_bare')[level]] += 1
                self._drop_file(best_file)
                return True, None
            if attempt == 0:
                stats['failed'] += 1
            if best is None or result['badness'] < best['badness']:
                shutil.copyfile(sentence_file, best_file)
                best = result
            # the same audio again for the same text: no new draw from this engine, its next sentences go to the
            # punctuation levels straight away
            digest = self._file_digest(sentence_file)
            if not self.deterministic and text == last_text and digest == last_digest:
                self.deterministic = True
                msg = legends['msg_verify_deterministic'].format(engine=self.session.get('tts_engine'))
                print(msg)
            last_text = text
            last_digest = digest
        os.replace(best_file, sentence_file)
        self.verifier.flag(sentence_file, sentence, best)
        return True, None

    def close_verifier(self)->None:
        if self.verifier is not None:
            self.verifier.close()
            self.verifier = None
