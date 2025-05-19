import os

from lib.classes.tts_engines.coqui import Coqui
from lib.models import *

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.active = False
        self.tts = None
        self._build()
 
    def _build(self):
        if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
            from lib.classes.tts_engines.coqui import Coqui
            self.tts = Coqui(self.session)
        else:
            print('Other TTS engines coming soon!')
        if self.tts is not None:
            self.active = True
        else:
            error = 'TTS engine could not be created!'
            print(error)

    def convert_sentence2audio(self, sentence_number, sentence):
        try:
            if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
                return self.tts.convert(sentence_number, sentence)
            else:
                print('Other TTS engines coming soon!')    
                return False
        except Exception as e:
            error = f'convert_sentence2audio(): {e}'
            raise ValueError(e)
            return False