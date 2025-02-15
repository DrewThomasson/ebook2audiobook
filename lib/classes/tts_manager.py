import gc
import os
import torch
import torchaudio
import threading

from fastapi import FastAPI
from huggingface_hub import hf_hub_download
from TTS.api import TTS as TtsXTTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from lib.models import XTTSv2, FAIRSEQ, VITS, YOURTTS, BARK, models, default_fine_tuned, builtin_xtts_voices, builtin_yourtts_voices
from lib.conf import models_dir, tts_default_settings, default_audio_proc_format

app = FastAPI()
lock = threading.Lock()
loaded_tts = {}

@app.post("/coqui_tts_load_api/")
def coqui_tts_load_api(model_path: str, device: str):
    try:
        with lock:
            tts = TtsXTTS(model_path, gpu=True if device == "cuda" else False).to(device)
        return tts
    except Exception as e:
        error = f'coqui_tts_load_api() error: {e}'
        print(error)
        return None

@app.post("/coqui_tts_load_custom/")
def coqui_tts_load_custom(model_path: str, config_path: str, vocab_path: str, device: str):
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
                enable_deepspeed=True,
                eval=True,
            ).to(device)
        return tts
    except Exception as e:
        error = f'coqui_tts_load_custom() error: {e}'
        print(error)
        return None

class TTSManager:
    def __init__(self, session):   
        self.session = session
        self.params = {}
        self.model_name = None
        self.model_path = None
        self.config_path = None
        self.vocab_path = None      
        if self.session['tts_engine'] == XTTSv2:
            if self.session['custom_model'] is not None:
                self.model_name = os.path.basename(self.session['custom_model'])
                msg = f"Loading TTS {self.session['tts_engine']} model from {self.session['custom_model']}, it takes a while, please be patient..."
                print(msg)
                self.model_path = os.path.join(self.session['custom_model'], 'model.pth')
                self.config_path = os.path.join(self.session['custom_model'],'config.json')
                self.vocab_path = os.path.join(self.session['custom_model'],'vocab.json')
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = self.coqui_tts_load_custom(self.model_path, self.config_path, self.vocab_path, self.session['device'])
            elif self.session['fine_tuned'] != default_fine_tuned:
                self.model_name = self.session['fine_tuned']
                msg = f"Loading TTS {self.session['tts_engine']} model from {self.session['fine_tuned']}, it takes a while, please be patient..."
                print(msg)
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                cache_dir = os.path.join(models_dir,'tts')
                self.model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/model.pth", cache_dir=cache_dir)
                self.config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/config.json", cache_dir=cache_dir)
                self.vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/vocab.json", cache_dir=cache_dir)    
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = self.coqui_tts_load_custom(self.model_path, self.config_path, self.vocab_path, self.session['device'])
            else:
                self.model_name = self.session['fine_tuned']
                msg = f"Loading TTS {self.session['tts_engine']} model from {models[self.session['tts_engine']][self.session['fine_tuned']]['repo']}, it takes a while, please be patient..."
                print(msg)
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = coqui_tts_load_api(self.model_path, self.session['device'])
        elif self.session['tts_engine'] == BARK:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_name = self.session['fine_tuned']
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {self.model_path} model from {self.model_path}, it takes a while, please be patient..."
                print(msg)
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = coqui_tts_load_api(self.model_path, self.session['device'])
        elif self.session['tts_engine'] == VITS:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_name = self.session['fine_tuned']
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", self.session['language_iso1']).replace("[xxx]", sub)
                sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                sub = next((key for key, lang_list in sub_dict.items() if self.session['language_iso1'] in lang_list), None)
                msg = f"Loading TTS {self.model_path} model from {self.model_path}, it takes a while, please be patient..."
                print(msg)
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = coqui_tts_load_api(self.model_path, self.session['device'])                    
        elif self.session['tts_engine'] == FAIRSEQ:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_name = self.session['fine_tuned']
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                msg = f"Loading TTS {self.model_path} model from {self.model_path}, it takes a while, please be patient..."
                print(msg)
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = coqui_tts_load_api(self.model_path, self.session['device'])
        elif self.session['tts_engine'] == YOURTTS:
            if self.session['custom_model'] is not None:
                print(f"{self.session['tts_engine']} custom model not implemented yet!")
            else:
                self.model_name = self.session['fine_tuned']
                self.model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {self.model_path} model from {self.model_path}, it takes a while, please be patient..."
                print(msg)
                if self.model_name in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[self.model_name]
                else:
                    self.params['tts'] = coqui_tts_load_api(self.model_path, self.session['device'])
        if self.params['tts'] is None:
            return None
        loaded_tts[self.model_name] = self.params['tts']

    def convert_sentence_to_audio(self):
        try:
            audio_data = None
            fine_tuned_params = {
                "temperature": float(self.session['temperature']),
                "length_penalty": float(self.session["length_penalty"]),
                "num_beams": int(self.session["num_beams"]),
                "repetition_penalty": float(self.session['repetition_penalty']),
                "top_k": int(self.session['top_k']),
                "top_p": float(self.session['top_p']),
                "speed": float(self.session['speed']),
                "enable_text_splitting": bool(self.session['enable_text_splitting'])
            }  
            if self.session['tts_engine'] == XTTSv2:
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != default_fine_tuned:
                    msg = 'Computing speaker latents...'
                    print(msg)
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else os.path.join(self.session['custom_model'],'ref.wav')
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
                    voice_name = os.path.basename(self.params['voice_path']).replace('_24000.wav','').replace('_16000.wav','')
                    if voice_name in builtin_xtts_voices.values():
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
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != default_fine_tuned:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                    with torch.no_grad():
                        audio_data = self.params['tts'].tts(
                            text=self.params['sentence'],
                            language=self.session['language_iso1'],
                            speaker_wav=self.params['voice_path'],
                            emotion='neutral'  # Available options: "neutral", "angry", "happy", "sad"
                        )
            elif self.session['tts_engine'] == VITS:
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != default_fine_tuned:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                    with torch.no_grad():
                        if self.params['voice_path'] is not None:
                            audio_data = self.params['tts'].tts_with_vc(
                                text=self.params['sentence'],
                                speaker_wav=self.params['voice_path']
                            )
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                            )
            elif self.session['tts_engine'] == FAIRSEQ:
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != default_fine_tuned:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                    with torch.no_grad():
                        if self.params['voice_path'] is not None:
                            audio_data = self.params['tts'].tts_with_vc(
                                text=self.params['sentence'],
                                speaker_wav=self.params['voice_path']
                            )
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                            )
            elif self.session['tts_engine'] == YOURTTS:
                if self.session['custom_model'] is not None or self.session['fine_tuned'] != default_fine_tuned:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    with torch.no_grad():
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        self.params['voice_path'] = self.session['voice'] if self.session['voice'] is not None else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                        self.params['voice_path'] = self.params['voice_path'].replace('_24000.wav','_16000.wav')
                        voice_name = os.path.basename(self.params['voice_path']).replace('_16000.wav','')
                        if voice_name in builtin_yourtts_voices.values():
                            speaker_argument = {"speaker": voice_name}
                        else:
                            speaker_argument = {"speaker_wav": self.params['voice_path']}
                        audio_data = self.params['tts'].tts(
                            text=self.params['sentence'],
                            language=language,
                            **speaker_argument
                        )
            if audio_data is not None:
                sample_rate = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
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