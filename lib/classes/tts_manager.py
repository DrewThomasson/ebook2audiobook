import gc
import os
import regex as re
import subprocess
import tempfile
import torch
import torchaudio
import threading
import uuid

from fastapi import FastAPI
from huggingface_hub import hf_hub_download
from TTS.api import TTS as TtsXTTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from lib.models import *
from lib.conf import models_dir, default_audio_proc_format

app = FastAPI()
lock = threading.Lock()
loaded_tts = {}

@app.post("/load_coqui_tts_api/")
def load_coqui_tts_api(model_path, device):
    try:
        with lock:
            tts = TtsXTTS(model_path, gpu=True if device == "cuda" else False).to(device)
        return tts
    except Exception as e:
        error = f'load_coqui_tts_api() error: {e}'
        print(error)
        return None

@app.post("/load_coqui_tts_checkpoint/")
def load_coqui_tts_checkpoint(model_path, config_path, vocab_path, device):
    try:
        config = XttsConfig()
        config.models_dir = os.path.join("models", "tts")
        config.load_json(config_path)
        tts = Xtts.init_from_config(config)
        with lock:
            tts.load_checkpoint(
                config,
                checkpoint_path=model_path,
                vocab_path=vocab_path,
                use_deepspeed=default_xtts_settings['use_deepspeed'],
                eval=True
            )
        if device == 'cuda':
            tts.cuda()
        return tts
    except Exception as e:
        error = f'load_coqui_tts_checkpoint() error: {e}'
        print(error)
        return None

@app.post("/load_coqui_tts_vc/")
def load_coqui_tts_vc(device):
    try:
        with lock:
            tts = TtsXTTS(default_vc_model).to(device)
        return tts
    except Exception as e:
        error = f'load_coqui_tts_vc() error: {e}'
        print(error)
        return None

class TTSManager:
    def __init__(self, session, is_gui_process):   
        self.session = session
        self.is_gui_process = is_gui_process
        self.params = {}
        self.model_path = None
        self.config_path = None
        self.vocab_path = None      
        self._build()
 
    def _build(self):
        tts_key = None
        self.params['current_voice_path'] = None
        if self.session['tts_engine'] == XTTSv2:
            if self.session['custom_model'] is not None:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                self.model_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'model.pth')
                self.config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'config.json')
                self.vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'vocab.json')
                tts_key = self.session['custom_model']
                if self.session['custom_model'] in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.session['custom_model']]
                else:
                    if len(loaded_tts) == max_tts_in_memory:
                        self.unload_tts()
                    self.params['tts'] = load_coqui_tts_checkpoint(self.model_path, self.config_path, self.vocab_path, self.session['device'])
            elif self.session['fine_tuned'] != 'internal':
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                cache_dir = os.path.join(models_dir,'tts')
                self.model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/model.pth", cache_dir=cache_dir)
                self.config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/config.json", cache_dir=cache_dir)
                self.vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/vocab.json", cache_dir=cache_dir)    
                tts_key = hf_sub
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[hf_sub]
                else:
                    self.params['tts'] = load_coqui_tts_checkpoint(self.model_path, self.config_path, self.vocab_path, self.session['device'])
            else:
                msg = f"Loading TTS {models[self.session['tts_engine']][self.session['fine_tuned']]['repo']} model, it takes a while, please be patient..."
                print(msg)
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                tts_key = self.model_path
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_path]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])
        elif self.session['tts_engine'] == BARK:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {self.model_path} model, it takes a while, please be patient..."
                print(msg)
                tts_key = self.model_path
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])
        elif self.session['tts_engine'] == VITS:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                sub = next((key for key, lang_list in sub_dict.items() if self.session['language_iso1'] in lang_list), None)
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", self.session['language_iso1']).replace("[xxx]", sub)
                r"""
                msg = f"Loading TTS {self.model_path} model, it takes a while, please be patient..."
                print(msg)
                tts_key = self.model_path
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])  
                """
                tts_key = self.model_path
                msg = f"Loading TTS {tts_key} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])
                tts_vc_key = default_vc_model
                msg = f"Loading TTS {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                print(msg)
                if tts_vc_key in loaded_tts.keys():
                    self.params['tts_vc'] = loaded_tts[tts_vc_key]
                else:
                    self.params['tts_vc'] = load_coqui_tts_vc(self.session['device'])
        elif self.session['tts_engine'] == FAIRSEQ:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                tts_key = self.model_path
                msg = f"Loading TTS {tts_key} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])
                tts_vc_key = default_vc_model
                msg = f"Loading TTS {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                print(msg)
                if tts_vc_key in loaded_tts.keys():
                    self.params['tts_vc'] = loaded_tts[tts_vc_key]
                else:
                    self.params['tts_vc'] = load_coqui_tts_vc(self.session['device'])
        elif self.session['tts_engine'] == YOURTTS:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {self.model_path} model, it takes a while, please be patient..."
                print(msg)
                tts_key = self.model_path
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_path]
                else:
                    self.params['tts'] = load_coqui_tts_api(self.model_path, self.session['device'])
        if self.params['tts'] is not None:
            loaded_tts[tts_key] = self.params['tts']

    def _unload_tts():
         for key in list(loaded_tts.keys()):
            if key != default_vc_model:
                del loaded_tts[key]
                gc.collect()
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                break

    def convert_sentence_to_audio(self):
        try:
            audio_data = None
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
            if self.session['tts_engine'] == XTTSv2:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                    self.params['voice_path'] = (
                        self.session['voice'] if self.session['voice'] is not None 
                        else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'ref.wav') if self.session['custom_model']
                        else models[self.session['tts_engine']][self.session['fine_tuned']]['voice'] if self.session['fine_tuned']
                        else models[self.session['tts_engine']]['internal']['voice']
                    )
                    if self.params['current_voice_path'] != self.params['voice_path']:
                        msg = 'Computing speaker latents...'
                        print(msg)
                        self.params['current_voice_path'] = self.params['voice_path']
                        self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.params['tts'].get_conditioning_latents(audio_path=[self.params['voice_path']])
                    with torch.no_grad():
                        result = self.params['tts'].inference(
                            text=self.params['sentence'],
                            language=self.session['language_iso1'],
                            gpt_cond_latent=self.params['gpt_cond_latent'],
                            speaker_embedding=self.params['speaker_embedding'],
                            **fine_tuned_params
                        )
                    audio_data = result.get('wav')
                    if audio_data is None:
                        error = f'No audio waveform found in convert_sentence_to_audio() result: {result}'
                        print(error)
                        return False
                else:
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                    voice_name = re.sub(r'_(24000|16000)\.wav$', '', os.path.basename(os.path.basename(self.params['voice_path'])))
                    if voice_name in default_xtts_settings['voices'].values():
                        speaker_argument = {"speaker": voice_name}
                    else:
                        speaker_argument = {"speaker_wav": self.params['voice_path']}
                    with torch.no_grad():
                        audio_data = self.params['tts'].tts(
                            text=self.params['sentence'],
                            language=self.session['language_iso1'],
                            **speaker_argument,
                            **fine_tuned_params
                        )
            elif self.session['tts_engine'] == BARK:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
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
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                    with torch.no_grad():
                        audio_data = self.params['tts'].tts(
                            text=self.params['sentence'],
                            #language=self.session['language_iso1'],
                            #speaker_wav=self.params['voice_path'],
                            #emotion='neutral'  # Available options: "neutral", "angry", "happy", "sad"
                        )
            elif self.session['tts_engine'] == VITS:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    self.params['voice_path'] = self.session['voice']
                    with torch.no_grad():
                        if self.params['voice_path'] is not None:
                            tmp_in_wav = os.path.join(self.session['voice_dir'], f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(self.session['voice_dir'], f"{uuid.uuid4()}.wav")
                            self.params['tts'].tts_to_file(text=self.params['sentence'], file_path=tmp_in_wav)
                            cmd = ["sox", tmp_in_wav, tmp_out_wav, "pitch", str(-8 * 100)]
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            audio_data = self.params['tts_vc'].voice_conversion(
                                source_wav=tmp_out_wav,
                                target_wav=self.params['voice_path']
                            )
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                            )
            elif self.session['tts_engine'] == FAIRSEQ:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:     
                    self.params['voice_path'] = self.session['voice']
                    with torch.no_grad():
                        if self.params['voice_path'] is not None:
                            tmp_wav = os.path.join(self.session['voice_dir'], f"{uuid.uuid4()}.wav")
                            self.params['tts'].tts_to_file(text=self.params['sentence'], file_path=tmp_wav)
                            audio_data = self.params['tts_vc'].voice_conversion(
                                source_wav=tmp_wav,
                                target_wav=self.params['voice_path']
                            )
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                            )
            elif self.session['tts_engine'] == YOURTTS:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    with torch.no_grad():
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                        voice_name = re.sub(r'_(24000|16000)\.wav$', '', os.path.basename(os.path.basename(self.params['voice_path'])))
                        if voice_name in default_yourtts_settings['voices'].values():
                            speaker_argument = {"speaker": voice_name}
                        else:
                            self.params['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', self.params['voice_path'])
                            speaker_argument = {"speaker_wav": self.params['voice_path']}
                        audio_data = self.params['tts'].tts(
                            text=self.params['sentence'],
                            language=language,
                            **speaker_argument
                        )
            if audio_data is not None:
                audio_tensor  = torch.tensor(audio_data, dtype=torch.float32).unsqueeze(0)
                torchaudio.save(self.params['sentence_audio_file'], audio_tensor, sample_rate, format=default_audio_proc_format)
                del audio_data
            collected = gc.collect()
            if self.session['device'] == 'cuda':
                torch.cuda.empty_cache()         
            if os.path.exists(self.params['sentence_audio_file']):
                return True
            error = f"Cannot create {self.params['sentence_audio_file']}"
            print(error)
            return False
        except Exception as e:
            error = f'convert_sentence_to_audio(): {e}'
            raise ValueError(e)
            return False