import os, torch, random, regex as re, numpy as np

from multiprocessing.managers import DictProxy
from typing import Any
from pathlib import Path

from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.utils import TTSUtils
from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
from lib.conf import tts_dir, devices
from lib.conf_models import loaded_tts, TTS_ENGINES, default_vc_model, models
from lib.conf_lang import language_tts

class Tacotron2(TTSUtils, TTSRegistry, name='tacotron'):

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
            self.params = {"semitones":{}}
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

    def _load_engine(self)->Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient..."
            print(msg)
            self._cleanup_memory()
            engine = loaded_tts.get(self.tts_key, False)
            if not engine:
                if self.session['custom_model'] is not None:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    iso_dir = language_tts[self.session['tts_engine']][self.session['language']]
                    sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                    sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                    self.params['samplerate'] = models[TTS_ENGINES['TACOTRON2']][self.session['fine_tuned']]['samplerate'][sub]
                    if sub is None:
                        iso_dir = self.session['language']
                        sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                    if sub is not None:
                        model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                        self.tts_key = model_path
                        engine = self._load_api(self.tts_key, model_path)
                        m = engine.synthesizer.tts_model
                        d = m.decoder
                        # Stability
                        d.prenet_dropout = 0.0
                        d.attention_dropout = 0.0
                        d.decoder_dropout = 0.0
                        # Stop-gate tuning
                        d.gate_threshold = 0.5
                        d.force_gate = True
                        d.gate_delay = 10
                        # Long-sentence fix
                        d.max_decoder_steps = 1000
                        # Prevent attention drift
                        d.attention_keeplast = True
                    else:
                        msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                        print(msg)
            if engine and engine is not None:
                msg = f'TTS {self.tts_key} Loaded!'
                return engine
        except Exception as e:
            error = f'_load_engine() error: {e}'
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
                    trim_audio_buffer = 0.004
                    sentence += '...' if sentence[-1].isalnum() else ''
                    speaker_argument = {}
                    if self.session['language'] in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
                        not_supported_punc_pattern = re.compile(r'\p{P}+')
                    else:
                        not_supported_punc_pattern = re.compile(r'["—…¡¿]')
                    if self.params['voice_path'] is not None:
                        proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                        os.makedirs(proc_dir, exist_ok=True)
                        tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                        tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                        with torch.no_grad():
                            self.engine.tts_to_file(
                                text=re.sub(not_supported_punc_pattern, ' ', sentence),
                                file_path=tmp_in_wav,
                                **speaker_argument
                            )
                        if self.params['voice_path'] in self.params['semitones'].keys():
                            semitones = self.params['semitones'][self.params['voice_path']]
                        else:
                            voice_path_gender = detect_gender(self.params['voice_path'])
                            voice_builtin_gender = detect_gender(tmp_in_wav)
                            msg = f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                            print(msg)
                            if voice_builtin_gender != voice_path_gender:
                                semitones = -4 if voice_path_gender == 'male' else 4
                                msg = f"Adapting builtin voice frequencies from the clone voice..."
                                print(msg)
                            else:
                                semitones = 0
                            self.params['semitones'][self.params['voice_path']] = semitones
                        if semitones > 0:
                            try:
                                cmd = [
                                    shutil.which('sox'), tmp_in_wav,
                                    "-r", str(self.params['samplerate']), tmp_out_wav,
                                    "pitch", str(semitones * 100)
                                ]
                                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            except subprocess.CalledProcessError as e:
                                error = f"Subprocess error: {e.stderr}"
                                print(error)
                                DependencyError(e)
                                return False
                            except FileNotFoundError as e:
                                error = f"File not found: {e}"
                                print(error)
                                DependencyError(e)
                                return False
                        else:
                            tmp_out_wav = tmp_in_wav
                        if self.engine_zs:
                            self.params['samplerate'] = TTS_VOICE_CONVERSION[self.tts_zs_key]['samplerate']
                            source_wav = self._resample_wav(tmp_out_wav, self.params['samplerate'])
                            target_wav = self._resample_wav(self.params['voice_path'], self.params['samplerate'])
                            audio_sentence = self.engine_zs.voice_conversion(
                                source_wav=source_wav,
                                target_wav=target_wav
                            )
                        else:
                            error = f'Engine {self.tts_zs_key} is None'
                            print(error)
                            return False
                        if os.path.exists(tmp_in_wav):
                            os.remove(tmp_in_wav)
                        if os.path.exists(tmp_out_wav):
                            os.remove(tmp_out_wav)
                        if os.path.exists(source_wav):
                            os.remove(source_wav)
                    else:
                        with torch.no_grad():
                            audio_sentence = self.engine.tts(
                                text=re.sub(not_supported_punc_pattern, ' ', sentence),
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
            error = f'Tacotron2.convert(): {e}'
            raise ValueError(e)
            return False