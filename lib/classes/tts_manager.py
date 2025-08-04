import os

from lib.models import TTS_ENGINES

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.tts = None
        self._build()
 
    def _build(self):
        if self.session['tts_engine'] in TTS_ENGINES.values():
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

    def convert_sentence2audio(self, sentence_number, sentence, character_name=None):
        try:
            if self.session['tts_engine'] in TTS_ENGINES.values():
                return self.tts.convert(sentence_number, sentence, character_name)
            else:
                print('Other TTS engines coming soon!')    
        except Exception as e:
            error = f'convert_sentence2audio(): {e}'
            raise ValueError(e)
        return False