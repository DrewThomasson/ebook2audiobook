import os
import torch

from lib.models import *

_original_multinomial = torch.multinomial
def _safe_multinomial(input, num_samples, replacement=False, *, generator=None, out=None):
	with torch.no_grad():
		input = torch.nan_to_num(input, nan=0.0, posinf=0.0, neginf=0.0)
		input = torch.clamp(input, min=0.0)
		sum_input = input.sum(dim=-1, keepdim=True)
		input = input / (sum_input + 1e-9)  # Normalize
	return _original_multinomial(input, num_samples, replacement=replacement, generator=generator, out=out)
torch.multinomial = _safe_multinomial

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.params = {}
        self.sentences_total_time = 0.0
        self.sentence_idx = 1
        self.vtt_path = os.path.splitext(session['epub_path'])[0] + '.vtt'
        self._build()
 
    def _build(self):
        model_path = None
        config_path = None
        vocab_path = None
        if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
            from lib.classes.tts_engines.coqui import Coqui
            self.params['tts'] = Coqui(self.session)
        else:
            print('Other TTS engines coming soon!')
        if self.params['tts'] is None:
            error = 'TTS engine could not be created!'
            print(error)

    def convert_sentence_to_audio(self):
        try:
            audio_data = None
            if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
                return Coqui.convert()
            else:
                print('Other TTS engines coming soon!')    
                return False
        except Exception as e:
            error = f'convert_sentence_to_audio(): {e}'
            raise ValueError(e)
            return False