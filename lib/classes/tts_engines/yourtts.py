import threading, torch, random

import regex as re
import numpy as np 

from multiprocessing.managers import DictProxy
from typing import Any
from pathlib import Path

from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.utils import TTSUtils
from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
from lib import *

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

class YourTTS(TTSUtils, TTSRegistry, name='yourtts'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.tts_zs_key = default_vc_model.rsplit('/',1)[-1]
            self.pth_voice_file = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.params = {}
            self.params['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
            self.resampler_cache = {}
            self.audio_segments = []
            using_gpu = self.session['device'] != devices['CPU']['proc']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 123456
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            has_cuda = (torch.version.cuda is not None and torch.cuda.is_available())
            if has_cuda:
                self._apply_cuda_policy(using_gpu=using_gpu, enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self._load_engine()
            self.engine_zs = self._load_engine_zs()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            speaker = None
            audio_sentence = False
            self.params['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            if self.params['voice_path'] is not None:
                speaker = re.sub(r'\.wav$', '', os.path.basename(self.params['voice_path']))
                if self.params['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in self.params['voice_path']:
                    self.session['voice'] = self.params['voice_path'] = self._check_xtts_builtin_speakers(self.params['voice_path'], speaker)
                    if not self.params['voice_path']:
                        msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                        print(msg)
                        return False
            if self.engine:
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                self.engine.to(device)
                final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_index}.{default_audio_proc_format}')
                if sentence == TTS_SML['break']:
                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 0.4 to 0.7 seconds
                    self.audio_segments.append(break_tensor.clone())
                    return True
                elif not sentence.replace('—', '').strip() or sentence == TTS_SML['pause']:
                    silence_time = int(np.random.uniform(1.0, 1.8) * 100) / 100
                    pause_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 1.0 to 1.8 seconds
                    self.audio_segments.append(pause_tensor.clone())
                    return True
                else:
                    if sentence.endswith("'"):
                        sentence = sentence[:-1]
                    trim_audio_buffer = 0.002
                    sentence += '...' if sentence[-1].isalnum() else ''
                    speaker_argument = {}
                    not_supported_punc_pattern = re.compile(r'[—]')
                    language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                    if self.params['voice_path'] is not None:
                        speaker_wav = self.params['voice_path']
                        speaker_argument = {"speaker_wav": speaker_wav}
                    else:
                        voice_key = default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2']
                        speaker_argument = {"speaker": voice_key}
                    with torch.no_grad():
                        audio_sentence = self.engine.tts(
                            text=re.sub(not_supported_punc_pattern, ' ', sentence),
                            language=language,
                            **speaker_argument
                        )
                    if is_audio_data_valid(audio_sentence):
                        sourceTensor = self._tensor_type(audio_sentence)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        if sentence[-1].isalnum() or sentence[-1] == '—':
                            audio_tensor = trim_audio(audio_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                        if audio_tensor is not None and audio_tensor.numel() > 0:
                            self.audio_segments.append(audio_tensor)
                            if not re.search(r'\w$', sentence, flags=re.UNICODE) and sentence[-1] != '—':
                                silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                self.audio_segments.append(break_tensor.clone())
                            if self.audio_segments:
                                audio_tensor = torch.cat(self.audio_segments, dim=-1)
                                start_time = self.sentences_total_time
                                duration = round((audio_tensor.shape[-1] / self.params['samplerate']), 2)
                                end_time = start_time + duration
                                self.sentences_total_time = end_time
                                sentence_obj = {
                                    "start": start_time,
                                    "end": end_time,
                                    "text": sentence,
                                    "resume_check": self.sentence_idx
                                }
                                self.sentence_idx = self._append_sentence2vtt(sentence_obj, self.vtt_path)
                                if self.sentence_idx:
                                    torchaudio.save(final_sentence_file, audio_tensor, self.params['samplerate'], format=default_audio_proc_format)
                                    del audio_tensor
                                    self._cleanup_memory()
                            self.audio_segments = []
                            if os.path.exists(final_sentence_file):
                                return True
                            else:
                                error = f"Cannot create {final_sentence_file}"
                                print(error)
                                return False
                    else:
                        error = f"audio_sentence not valid"
                        print(error)
                        return False
            else:
                error = f"TTS engine {self.session['tts_engine']} could not be loaded!\nPossible reason can be not enough VRAM/RAM memory"
                print(error)
                return False
        except Exception as e:
            error = f'YourTTS.convert(): {e}'
            raise ValueError(e)
            return False