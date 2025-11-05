import os

from typing import Any
from lib.models import TTS_ENGINES

class TTSManager:
    def __init__(self, session:Any):   
        self.session = session
        self.engine = False
        self._build()
 
    def _build(self)->None:
        if self.session['tts_engine'] in TTS_ENGINES.values():
            try:
                if self.session['tts_engine'] in [TTS_ENGINES['XTTSv2'],TTS_ENGINES['BARK'],TTS_ENGINES['VITS'],TTS_ENGINES['FAIRSEQ'],TTS_ENGINES['TACOTRON2'],TTS_ENGINES['YOURTTS']]:
                    from lib.classes.tts_engines.coqui import Coqui
                    self.engine = Coqui(self.session)
                elif self.session['tts_engine'] in [TTS_ENGINES['PIPER']]:
                    from lib.classes.tts_engines.piper import Coqui as PiperCoqui
                    self.engine = PiperCoqui(self.session)
                #elif self.session['tts_engine'] in [TTS_ENGINES['NEW_TTS']]:
                #    from lib.classes.tts_engines.new_tts import NewTts
                #    self.engine = NewTts(self.session)
                
                # Check if engine was created successfully (not False)
                if self.engine is False:
                    error='TTS engine could not be created!'
                    print(error)
            except Exception as e:
                error = f'_build() error: {e}'
                print(error)
                self.engine = False
        else:
            print('Other TTS engines coming soon!')

    def convert_sentence2audio(self,sentence_number:int,sentence:str)->bool:
        try:
            if self.session['tts_engine'] in TTS_ENGINES.values():
                return self.engine.convert(sentence_number,sentence)
            else:
                print('Other TTS engines coming soon!')
        except Exception as e:
            error=f'convert_sentence2audio(): {e}'
            raise ValueError(e)
        return False