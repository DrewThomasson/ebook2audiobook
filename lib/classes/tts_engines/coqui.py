import hashlib
import math
import os
import shutil
import subprocess
import tempfile
import threading
import uuid

import numpy as np
import regex as re
import soundfile as sf
import torch
import torchaudio

from huggingface_hub import hf_hub_download
from pathlib import Path
from pprint import pprint

from lib import *
from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()
xtts_builtin_speakers_list = None

class Coqui:

    def __init__(self, session):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
            self.tts_vc_key = default_vc_model.rsplit('/', 1)[-1]
            self.is_bf16 = True if self.session['device'] == 'cuda' and torch.cuda.is_bf16_supported() == True else False
            self.npz_path = None
            self.npz_data = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.params = {TTS_ENGINES['XTTSv2']: {"latent_embedding":{}}, TTS_ENGINES['BARK']: {},TTS_ENGINES['VITS']: {"semitones": {}}, TTS_ENGINES['FAIRSEQ']: {"semitones": {}}, TTS_ENGINES['TACOTRON2']: {"semitones": {}}, TTS_ENGINES['YOURTTS']: {}}  
            self.params[self.session['tts_engine']]['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt')       
            self.max_chars = language_mapping.get(self.session['language'], {}).get("max_chars") + 2
            list_split = [
                # Western
                '.', ',',
                # Arabic-Persian
                '،',
                # CJK
                '。', '，', '、', '·', '…',
                # Indic
                '।', '॥',
                # Thai
                'ฯ',
                # Ethiopic
                '፡', '።', '፣', '፤', '፥', '፦', '፧',
                # Hebrew
                '״',
                # Tibetan
                '།', '༎',
                # Khmer
                '។', '៕',
                # Lao
                '໌', 'ໍ',
                # Misc (global)
                '—', '!', '?', ':', ';'
            ]
            punctuation_class = "[" + "".join(re.escape(ch) for ch in list_split) + "]"
            self.punc_re = re.compile(punctuation_class)
            self._build()
        except Exception as e:
            error = f'__init__() error: {e}'
            print(error)
            return None

    def _build(self):
        try:
            global xtts_builtin_speakers_list
            load_zeroshot = True if self.session['tts_engine'] in [TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2']] else False
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                if xtts_builtin_speakers_list is None:
                    self.speakers_path = hf_hub_download(repo_id=models[TTS_ENGINES['XTTSv2']]['internal']['repo'], filename=default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][4], cache_dir=self.cache_dir)
                    xtts_builtin_speakers_list = torch.load(self.speakers_path)
                if self.session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                    msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                    print(msg)
                    if self.session['custom_model'] is not None:
                        config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][0])
                        checkpoint_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][1])
                        vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][2])
                        self.tts_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                        tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.session['device'])
                    else:
                        hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                        if self.session['fine_tuned'] == 'internal':
                            hf_sub = ''
                            if self.speakers_path is None:
                                self.speakers_path = hf_hub_download(repo_id=hf_repo, filename=default_engine_settings[TTS_ENGINES['XTTSv2']]['files'][4], cache_dir=self.cache_dir)
                        else:
                            hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                        config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                        checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                        vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                        tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.session['device'])
                elif self.session['tts_engine'] == TTS_ENGINES['BARK']:      
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                        hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                        text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                        coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                        fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                        checkpoint_dir = os.path.dirname(text_model_path)
                        tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_dir=checkpoint_dir, device=self.session['device'])
                elif self.session['tts_engine'] == TTS_ENGINES['VITS']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)     
                        return False
                    else:
                        iso_dir = language_tts[self.session['tts_engine']][self.session['language']]
                        sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                        sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)  
                        if sub is not None:
                            self.params[self.session['tts_engine']]['samplerate'] = models[TTS_ENGINES['VITS']][self.session['fine_tuned']]['samplerate'][sub]
                            model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                            msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                            print(msg)
                            self.tts_key = model_path
                            tts = self._load_api(self.tts_key, model_path, self.session['device'])
                        else:
                            msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                            print(msg)
                            return False
                elif self.session['tts_engine'] == TTS_ENGINES['FAIRSEQ']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                        self.tts_key = model_path
                        tts = self._load_api(self.tts_key, model_path, self.session['device'])
                elif self.session['tts_engine'] == TTS_ENGINES['TACOTRON2']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)     
                        return False
                    else:
                        iso_dir = language_tts[self.session['tts_engine']][self.session['language']]
                        sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                        sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                        self.params[self.session['tts_engine']]['samplerate'] = models[TTS_ENGINES['TACOTRON2']][self.session['fine_tuned']]['samplerate'][sub]
                        if sub is None:
                            iso_dir = self.session['language']
                            sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                        if sub is not None:
                            model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                            msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                            print(msg)
                            self.tts_key = model_path
                            tts = self._load_api(self.tts_key, model_path, self.session['device'])
                        else:
                            msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                            print(msg)
                            return False
                elif self.session['tts_engine'] == TTS_ENGINES['YOURTTS']:
                    if self.session['custom_model'] is not None:
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                        return False
                    else:
                        model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                        tts = self._load_api(self.tts_key, model_path, self.session['device'])
            if load_zeroshot:
                tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                if not tts_vc:
                    if self.session['voice'] is not None:
                        msg = f"Loading TTS {self.tts_vc_key} zeroshot model, it takes a while, please be patient..."
                        print(msg)
                        tts_vc = self._load_api(self.tts_vc_key, default_vc_model, self.session['device'])
            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            error = f'build() error: {e}'
            print(error)
            return False

    def _load_api(self, key, model_path, device):
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_key, self.tts_vc_key])
            from TTS.api import TTS as coquiAPI
            with lock:
                tts = coquiAPI(model_path)
                if tts:
                    if device == 'cuda':
                        tts.cuda()
                    else:
                        tts.to(device)
                    loaded_tts[key] = {"engine": tts, "config": None} 
                    msg = f'{model_path} Loaded!'
                    print(msg)
                    return tts
                else:
                    error = 'TTS engine could not be created!'
                    print(error)
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
        return False

    def _load_checkpoint(self, **kwargs):
        global lock
        try:
            key = kwargs.get('key')
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            tts_engine = kwargs.get('tts_engine')
            device = kwargs.get('device')
            unload_tts(device, [self.tts_key, self.tts_vc_key])
            with lock:
                if tts_engine == TTS_ENGINES['XTTSv2']:
                    from TTS.tts.configs.xtts_config import XttsConfig
                    from TTS.tts.models.xtts import Xtts
                    checkpoint_path = kwargs.get('checkpoint_path')
                    config_path = kwargs.get('config_path', None)
                    vocab_path = kwargs.get('vocab_path', None)
                    config = XttsConfig()
                    config.models_dir = os.path.join("models", "tts")
                    config.load_json(config_path)
                    tts = Xtts.init_from_config(config)
                    tts.load_checkpoint(
                        config,
                        checkpoint_path=checkpoint_path,
                        vocab_path=vocab_path,
                        use_deepspeed=default_engine_settings[TTS_ENGINES['XTTSv2']]['use_deepspeed'],
                        eval=True
                    )
                elif tts_engine == TTS_ENGINES['BARK']:
                    from TTS.tts.configs.bark_config import BarkConfig
                    from TTS.tts.models.bark import Bark
                    checkpoint_dir = kwargs.get('checkpoint_dir')
                    config = BarkConfig()
                    config.CACHE_DIR = self.cache_dir
                    config.USE_SMALLER_MODELS = os.environ.get('SUNO_USE_SMALL_MODELS', '').lower() == 'true'
                    tts = Bark.init_from_config(config)
                    tts.load_checkpoint(
                        config,
                        checkpoint_dir=checkpoint_dir,
                        eval=True
                    )                    
            if tts:
                if device == 'cuda':
                    tts.cuda()
                else:
                    tts.to(device)
                loaded_tts[key] = {"engine": tts, "config": config}
                msg = f'{tts_engine} Loaded!'
                print(msg)
                return tts
            else:
                error = 'TTS engine could not be created!'
                print(error)
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
        return False

    def _check_xtts_builtin_speakers(self, voice_path, speaker, device):
        try:
            voice_parts = Path(voice_path).parts
            if self.session['language'] not in voice_parts and speaker not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['language'] != 'eng':
                if self.session['language'] in language_tts[TTS_ENGINES['XTTSv2']].keys():
                    lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                    new_voice_path = re.sub(r'([\\/])eng([\\/])', rf'\1{lang_dir}\2', voice_path)
                    default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                    if os.path.exists(default_text_file):
                        msg = f"Converting builtin eng voice to {self.session['language']}..."
                        print(msg)
                        tts_internal_key = f"{TTS_ENGINES['XTTSv2']}-internal"
                        default_text = Path(default_text_file).read_text(encoding="utf-8")
                        hf_repo = models[TTS_ENGINES['XTTSv2']]['internal']['repo']
                        hf_sub = ''
                        tts = (loaded_tts.get(tts_internal_key) or {}).get('engine', False)
                        if not tts:
                            for key in list(loaded_tts.keys()): unload_tts(device, None, key)
                            config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][0]}", cache_dir=self.cache_dir)
                            checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][1]}", cache_dir=self.cache_dir)
                            vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][2]}", cache_dir=self.cache_dir)
                            tts = self._load_checkpoint(tts_engine=TTS_ENGINES['XTTSv2'], key=tts_internal_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=device)
                        if tts:
                            file_path = new_voice_path.replace('_24000.wav', '.wav')
                            if speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys():
                                gpt_cond_latent, speaker_embedding = xtts_builtin_speakers_list[default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'][speaker]].values()
                            else:
                                gpt_cond_latent, speaker_embedding = tts.get_conditioning_latents(audio_path=[voice_path])
                            fine_tuned_params = {
                                key: cast_type(self.session[key])
                                for key, cast_type in {
                                    "temperature": float,
                                    "length_penalty": float,
                                    "num_beams": int,
                                    "repetition_penalty": float,
                                    "top_k": int,
                                    "top_p": float,
                                    "speed": float,
                                    "enable_text_splitting": bool
                                }.items()
                                if self.session.get(key) is not None
                            }
                            with torch.no_grad():
                                result = tts.inference(
                                    text=default_text,
                                    language=self.session['language_iso1'],
                                    gpt_cond_latent=gpt_cond_latent,
                                    speaker_embedding=speaker_embedding,
                                    **fine_tuned_params
                                )
                            audio_data = result.get('wav')
                            if audio_data is not None:
                                audio_data = audio_data.tolist()
                                sourceTensor = self._tensor_type(audio_data)
                                audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                                torchaudio.save(file_path, audio_tensor, default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate'], format='wav')
                                for samplerate in [16000, 24000]:
                                    output_file = file_path.replace('.wav', f'_{samplerate}.wav')
                                    if not normalize_audio(file_path, output_file, samplerate):
                                        break
                                del audio_data, sourceTensor, audio_tensor  
                                if self.session['tts_engine'] != TTS_ENGINES['XTTSv2']:
                                    del tts
                                    unload_tts(device, None, tts_internal_key)
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    return new_voice_path
                            else:
                                error = f'No audio waveform found in _check_xtts_builtin_speakers() result: {result}'
                                print(error)
                        else:
                            error = f"_check_xtts_builtin_speakers() error: {TTS_ENGINES['XTTSv2']} is False"
                            print(error)
                    else:
                        error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                        print(error)
                else:
                    return voice_path
            else:
                return voice_path
        except Exception as e:
            error = f'_check_xtts_builtin_speakers() error: {e}'
            print(error)
        return False

    def _check_bark_npz(self, voice_path, bark_dir, speaker, device):
        try:
            if self.session['language'] in language_tts[TTS_ENGINES['BARK']].keys():
                npz_dir = os.path.join(bark_dir, speaker)
                npz_file = os.path.join(npz_dir, f'{speaker}.npz')
                if os.path.exists(npz_file):
                    return True
                else:
                    os.makedirs(npz_dir, exist_ok=True)
                    tts_internal_key = f"{TTS_ENGINES['BARK']}-internal"
                    hf_repo = models[TTS_ENGINES['BARK']]['internal']['repo']
                    hf_sub = models[TTS_ENGINES['BARK']]['internal']['sub']
                    tts = (loaded_tts.get(tts_internal_key) or {}).get('engine', False)
                    if not tts:
                        for key in list(loaded_tts.keys()): unload_tts(device, None, key)
                        text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][0]}", cache_dir=self.cache_dir)
                        coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][1]}", cache_dir=self.cache_dir)
                        fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['BARK']]['internal']['files'][2]}", cache_dir=self.cache_dir)
                        checkpoint_dir = os.path.dirname(text_model_path)
                        tts = self._load_checkpoint(tts_engine=TTS_ENGINES['BARK'], key=tts_internal_key, checkpoint_dir=checkpoint_dir, device=device)
                    if tts:
                        voice_temp = os.path.splitext(npz_file)[0]+'.wav'
                        shutil.copy(voice_path, voice_temp)
                        default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                        default_text = Path(default_text_file).read_text(encoding="utf-8")
                        fine_tuned_params = {
                            key: cast_type(self.session[key])
                            for key, cast_type in {
                                "text_temp": float,
                                "waveform_temp": float
                            }.items()
                            if self.session.get(key) is not None
                        }
                        with torch.no_grad():
                            torch.manual_seed(67878789)
                            audio_data = tts.synthesize(
                                default_text,
                                loaded_tts[tts_internal_key]['config'],
                                speaker=speaker,
                                voice_dirs=bark_dir,
                                silent=True,
                                **fine_tuned_params
                            )
                        os.remove(voice_temp)
                        del audio_data
                        if self.session['tts_engine'] != TTS_ENGINES['BARK']:
                            del tts
                            unload_tts(device, None, tts_internal_key)
                        msg = f"Saved NPZ file: {npz_file}"
                        print(msg)
                        return True
                    else:
                        error = f'_check_bark_npz() error: {tts_internal_key} is False'
                        print(error)
            else:
                return True
        except Exception as e:
            error = f'_check_bark_npz() error: {e}'
            print(error)
        return False
        
    def _tensor_type(self, audio_data):
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data, np.ndarray):  
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data, list):  
            return torch.tensor(audio_data, dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")

    def convert(self, sentence_number, sentence):
        global xtts_builtin_speakers_list
        try:
            speaker = None
            audio_data = False
            trim_audio_buffer = 0.004
            settings = self.params[self.session['tts_engine']]
            final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            sentence = sentence.rstrip()
            settings['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'ref.wav') if self.session['custom_model'] is not None
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            if settings['voice_path'] is not None:
                speaker = re.sub(r'_(24000|16000)\.wav$|\.wav$', '', os.path.basename(settings['voice_path']))
                if settings['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and os.path.basename(settings['voice_path']) != 'ref.wav':
                    self.session['voice'] = settings['voice_path'] = self._check_xtts_builtin_speakers(settings['voice_path'], speaker, self.session['device'])
                    if not settings['voice_path']:
                        msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                        print(msg)
                        return False
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if tts:
                sentence_parts = sentence.split('‡pause‡')
                if self.session['tts_engine'] in [TTS_ENGINES['XTTSv2'], TTS_ENGINES['FAIRSEQ']]:
                    sentence_parts = [p.replace('.', ' — ') for p in sentence_parts]
                silence_tensor = torch.zeros(1, int(settings['samplerate'] * 1.4)) # 1.4 seconds
                extra_audio_buffer = 0
                audio_segments = []
                for text_part in sentence_parts:
                    text_part = text_part.strip()
                    if not text_part:
                        audio_segments.append(silence_tensor.clone())
                        continue
                    if self.session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                        trim_audio_buffer = 0.06
                        if settings['voice_path'] is not None and settings['voice_path'] in settings['latent_embedding'].keys():
                            settings['gpt_cond_latent'], settings['speaker_embedding'] = settings['latent_embedding'][settings['voice_path']]
                        else:
                            msg = 'Computing speaker latents...'
                            print(msg)
                            if speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys():
                                settings['gpt_cond_latent'], settings['speaker_embedding'] = xtts_builtin_speakers_list[default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'][speaker]].values()
                            else:
                                settings['gpt_cond_latent'], settings['speaker_embedding'] = tts.get_conditioning_latents(audio_path=[settings['voice_path']])  
                            settings['latent_embedding'][settings['voice_path']] = settings['gpt_cond_latent'], settings['speaker_embedding']
                        fine_tuned_params = {
                            key: cast_type(self.session[key])
                            for key, cast_type in {
                                "temperature": float,
                                "length_penalty": float,
                                "num_beams": int,
                                "repetition_penalty": float,
                                "top_k": int,
                                "top_p": float,
                                "speed": float,
                                "enable_text_splitting": bool
                            }.items()
                            if self.session.get(key) is not None
                        }
                        with torch.no_grad():
                            result = tts.inference(
                                text=text_part,
                                language=self.session['language_iso1'],
                                gpt_cond_latent=settings['gpt_cond_latent'],
                                speaker_embedding=settings['speaker_embedding'],
                                **fine_tuned_params
                            )
                        audio_part = result.get('wav')
                        if is_audio_data_valid(audio_part):
                            audio_part = audio_part.tolist()
                    elif self.session['tts_engine'] == TTS_ENGINES['BARK']:
                        trim_audio_buffer = 0.002
                        '''
                            [laughter]
                            [laughs]
                            [sighs]
                            [music]
                            [gasps]
                            [clears throat]
                            — or ... for hesitations
                            ♪ for song lyrics
                            CAPITALIZATION for emphasis of a word
                            [MAN] and [WOMAN] to bias Bark toward male and female speakers, respectively
                        '''
                        if speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                            bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                        else:
                            bark_dir = os.path.join(os.path.dirname(settings['voice_path']), 'bark')       
                            if not self._check_bark_npz(settings['voice_path'], bark_dir, speaker, self.session['device']):
                                error = 'Could not create npz file!'
                                print(error)
                                return False
                        npz_file = os.path.join(bark_dir, speaker, f'{speaker}.npz')
                        fine_tuned_params = {
                            key: cast_type(self.session[key])
                            for key, cast_type in {
                                "text_temp": float,
                                "waveform_temp": float
                            }.items()
                            if self.session.get(key) is not None
                        }
                        if self.npz_path is None or self.npz_path != npz_file:
                            self.npz_path = npz_file
                            self.npz_data = np.load(self.npz_path, allow_pickle=True)
                        history_prompt = [
                                self.npz_data["semantic_prompt"],
                                self.npz_data["coarse_prompt"],
                                self.npz_data["fine_prompt"]
                        ]
                        with torch.no_grad():
                            torch.manual_seed(67878789)
                            audio_part, _ = tts.generate_audio(
                                text_part,
                                history_prompt=history_prompt,
                                silent=True,
                                **fine_tuned_params
                            )                                
                        if is_audio_data_valid(audio_part):
                            audio_part = audio_part.tolist()
                    elif self.session['tts_engine'] == TTS_ENGINES['VITS']:
                        speaker_argument = {}
                        if self.session['language'] == 'eng' and 'vctk/vits' in models[self.session['tts_engine']]['internal']['sub']:
                            if self.session['language'] in models[self.session['tts_engine']]['internal']['sub']['vctk/vits'] or self.session['language_iso1'] in models[self.session['tts_engine']]['internal']['sub']['vctk/vits']:
                                speaker_argument = {"speaker": 'p262'}
                        elif self.session['language'] == 'cat' and 'custom/vits' in models[self.session['tts_engine']]['internal']['sub']:
                            if self.session['language'] in models[self.session['tts_engine']]['internal']['sub']['custom/vits'] or self.session['language_iso1'] in models[self.session['tts_engine']]['internal']['sub']['custom/vits']:
                                speaker_argument = {"speaker": '09901'}
                        if settings['voice_path'] is not None:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tts.tts_to_file(
                                text=text_part,
                                file_path=tmp_in_wav,
                                **speaker_argument
                            )
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = detect_gender(settings['voice_path'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                                print(msg)
                                if voice_builtin_gender != voice_path_gender:
                                    semitones = -4 if voice_path_gender == 'male' else 4
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    semitones = 0
                                settings['semitones'][settings['voice_path']] = semitones
                            if semitones > 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(settings['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                except subprocess.CalledProcessError as e:
                                    print(f"Subprocess error: {e.stderr}")
                                    DependencyError(e)
                                    return False
                                except FileNotFoundError as e:
                                    print(f"File not found: {e}")
                                    DependencyError(e)
                                    return False
                            else:
                                tmp_out_wav = tmp_in_wav
                            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                            if tts_vc:
                                audio_part = tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            else:
                                error = f'Engine {self.tts_vc_key} is None'
                                print(error)
                                return False
                            settings['samplerate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = tts.tts(
                                text=text_part,
                                **speaker_argument
                            )
                    elif self.session['tts_engine'] == TTS_ENGINES['FAIRSEQ']:
                        speaker_argument = {}
                        if settings['voice_path'] is not None:
                            settings['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', settings['voice_path'])
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tts.tts_to_file(
                                text=text_part,
                                file_path=tmp_in_wav,
                                **speaker_argument
                            )
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = detect_gender(settings['voice_path'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                                print(msg)
                                if voice_builtin_gender != voice_path_gender:
                                    semitones = -4 if voice_path_gender == 'male' else 4
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    semitones = 0
                                settings['semitones'][settings['voice_path']] = semitones
                            if semitones > 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(settings['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                except subprocess.CalledProcessError as e:
                                    print(f"Subprocess error: {e.stderr}")
                                    DependencyError(e)
                                    return False
                                except FileNotFoundError as e:
                                    print(f"File not found: {e}")
                                    DependencyError(e)
                                    return False
                            else:
                                tmp_out_wav = tmp_in_wav
                            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                            if tts_vc:
                                audio_part = tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            else:
                                error = f'Engine {self.tts_vc_key} is None'
                                print(error)
                                return False
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = tts.tts(
                                text=text_part,
                                **speaker_argument
                            )
                    elif self.session['tts_engine'] == TTS_ENGINES['TACOTRON2']:
                        speaker_argument = {}
                        if settings['voice_path'] is not None:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tts.tts_to_file(
                                text=text_part,
                                file_path=tmp_in_wav,
                                **speaker_argument
                            )
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = detect_gender(settings['voice_path'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}"
                                print(msg)
                                if voice_builtin_gender != voice_path_gender:
                                    semitones = -4 if voice_path_gender == 'male' else 4
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    semitones = 0
                                settings['semitones'][settings['voice_path']] = semitones
                            if semitones > 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(settings['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                except subprocess.CalledProcessError as e:
                                    print(f"Subprocess error: {e.stderr}")
                                    DependencyError(e)
                                    return False
                                except FileNotFoundError as e:
                                    print(f"File not found: {e}")
                                    DependencyError(e)
                                    return False
                            else:
                                tmp_out_wav = tmp_in_wav
                            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                            if tts_vc:
                                audio_part = tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            else:
                                error = f'Engine {self.tts_vc_key} is None'
                                print(error)
                                return False
                            settings['samplerate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = tts.tts(
                                text=text_part,
                                **speaker_argument
                            )
                    elif self.session['tts_engine'] == TTS_ENGINES['YOURTTS']:
                        trim_audio_buffer = 0.004
                        speaker_argument = {}
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        if settings['voice_path'] is not None:
                            settings['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', settings['voice_path'])
                            speaker_argument = {"speaker_wav": settings['voice_path']}
                        else:
                            voice_key = default_engine_settings[TTS_ENGINES['YOURTTS']]['voices']['ElectroMale-2']
                            speaker_argument = {"speaker": voice_key}
                        with torch.no_grad():
                            audio_part = tts.tts(
                                text=text_part,
                                language=language,
                                **speaker_argument
                            )
                    if is_audio_data_valid(audio_part):
                        sourceTensor = self._tensor_type(audio_part)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        audio_segments.append(audio_tensor)
                        audio_segments.append(silence_tensor.clone())
                if audio_segments and torch.equal(audio_segments[-1], silence_tensor):
                    audio_segments = audio_segments[:-1]
                if audio_segments:
                    audio_tensor = torch.cat(audio_segments, dim=-1)
                    if not text_part.endswith('-') and not text_part[-1].isalnum():
                        extra_audio_buffer = np.random.uniform(0.8, 1.6)
                    audio_tensor = trim_audio(audio_tensor.squeeze(), settings['samplerate'], 0.001, trim_audio_buffer + extra_audio_buffer).unsqueeze(0)
                    start_time = self.sentences_total_time
                    duration = audio_tensor.shape[-1] / settings['samplerate']
                    end_time = start_time + duration
                    self.sentences_total_time = end_time
                    sentence_obj = {
                        "start": start_time,
                        "end": end_time,
                        "text": sentence.replace('‡pause‡', '. '),
                        "resume_check": self.sentence_idx
                    }
                    self.sentence_idx = append_sentence2vtt(sentence_obj, self.vtt_path)
                    if self.sentence_idx:
                        torchaudio.save(final_sentence_file, audio_tensor, settings['samplerate'], format=default_audio_proc_format)
                        del audio_tensor
                if os.path.exists(final_sentence_file):
                    return True
                else:
                    error = f"Cannot create {final_sentence_file}"
                    print(error)
            else:
                error = f"convert() error: {self.session['tts_engine']} is None"
                print(error)
        except Exception as e:
            error = f'Coquit.convert(): {e}'
            raise ValueError(e)
        return False