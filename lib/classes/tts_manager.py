import os

from lib.models import TTS_ENGINES

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.tts = None
        self._build()
 
    def _build(self):
        if self.session['tts_engine'] in TTS_ENGINES.values():
            if self.session['tts_engine'] == TTS_ENGINES['KOKORO']:
                from lib.classes.tts_engines.kokoro import Coqui
                self.tts = Coqui(self.session)
            else:
                from lib.classes.tts_engines.coqui import Coqui
                self.tts = Coqui(self.session)
            if self.tts:
                return True
            else:
                error = 'TTS engine could not be created!'
                print(error)
        else:
            print('Other TTS engines coming soon!')
        return False

    def convert_sentence2audio(self, sentence_number, sentence):
        try:
            if self.session['tts_engine'] in TTS_ENGINES.values():
                return self.tts.convert(sentence_number, sentence)
            else:
                print('Other TTS engines coming soon!')    
        except Exception as e:
            error = f'convert_sentence2audio(): {e}'
            raise ValueError(e)
        return False