import os

from lib.models import TTS_ENGINES

class TTSManager:
    def __init__(self, session, force_device=None):   
        self.session = session
        self.tts = None
        self.force_device = force_device
        self._build()
 
    def _build(self):
        # Temporarily override device if force_device is specified
        original_device = None
        if self.force_device:
            original_device = self.session['device']
            self.session['device'] = self.force_device
        
        try:
            if self.session['tts_engine'] in TTS_ENGINES.values():
                if self.session['tts_engine'] in [TTS_ENGINES['XTTSv2'], TTS_ENGINES['BARK'], TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2'], TTS_ENGINES['YOURTTS']]:
                    from lib.classes.tts_engines.coqui import Coqui
                    self.tts = Coqui(self.session)
                #elif self.session['tts_engine'] in [TTS_ENGINES['NEW_TTS']]:
                #    from lib.classes.tts_engines.new_tts import NewTts
                #    self.tts = NewTts(self.session)
                if self.tts:
                    return True
                else:
                    error = 'TTS engine could not be created!'
                    print(error)
            else:
                print('Other TTS engines coming soon!')
            return False
        finally:
            # Restore original device
            if original_device is not None:
                self.session['device'] = original_device

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