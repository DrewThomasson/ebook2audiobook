import os
import gc
import hashlib
import numpy as np
import regex as re
import shutil
import soundfile as sf
import subprocess
import tempfile
import torch
import torchaudio
import threading
import uuid

from huggingface_hub import hf_hub_download
from pathlib import Path
from scipy.io import wavfile as wav
from scipy.signal import find_peaks

from lib.models import loaded_tts, default_vc_model, XTTSv2, BARK, VITS, FAIRSEQ, TACOTRON2, YOURTTS, models, default_xtts_settings, default_bark_settings, default_vits_settings, default_fairseq_settings, default_yourtts_settings
from lib.conf import voices_dir, models_dir, tts_dir, default_audio_proc_format
from lib.lang import language_tts, abbreviations_mapping

torch.backends.cudnn.benchmark = True
#torch.serialization.add_safe_globals(["numpy.core.multiarray.scalar"])

lock = threading.Lock()
xtts_builtin_speakers_list = None

class Coqui:
    def __init__(self, session):   
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
        self.params = {XTTSv2: {"latent_embedding":{}}, BARK: {}, TACOTRON2: {"semitones": {}}, VITS: {"semitones": {}}, FAIRSEQ: {"semitones": {}}, YOURTTS: {}}  
        self.vtt_path = None
        self._build()
 
    def _build(self):
        global xtts_builtin_speakers_list
        self.vtt_path = os.path.join(self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt')
        if xtts_builtin_speakers_list is None:
            self.speakers_path = hf_hub_download(repo_id=models[XTTSv2]['internal']['repo'], filename=default_xtts_settings['files'][4], cache_dir=self.cache_dir)
            xtts_builtin_speakers_list = torch.load(self.speakers_path)
        if self.session['tts_engine'] == XTTSv2:
            self.params[XTTSv2]['sample_rate'] = models[XTTSv2][self.session['fine_tuned']]['samplerate']
            msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
            print(msg)
            if self.session['custom_model'] is not None:
                config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_xtts_settings['files'][0])
                checkpoint_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], default_xtts_settings['files'][1])
                vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],default_xtts_settings['files'][2])
                self.tts_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.session['device'])
            else:
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                if self.session['fine_tuned'] == 'internal':
                    hf_sub = ''
                    if self.speakers_path is None:
                        self.speakers_path = hf_hub_download(repo_id=hf_repo, filename=default_xtts_settings['files'][4], cache_dir=self.cache_dir)
                else:
                    hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=self.session['device'])
        elif self.session['tts_engine'] == BARK:      
            if self.session['custom_model'] is not None:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return False
            else:
                self.params[BARK]['sample_rate'] = models[BARK][self.session['fine_tuned']]['samplerate']
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                checkpoint_dir = os.path.dirname(text_model_path)
                tts = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_dir=checkpoint_dir, device=self.session['device'])
        elif self.session['tts_engine'] == VITS:
            if self.session['custom_model'] is not None:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)     
                return False
            else:
                iso_dir = language_tts[self.session['tts_engine']][self.session['language']]
                sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)  
                if sub is not None:
                    self.params[VITS]['sample_rate'] = models[VITS][self.session['fine_tuned']]['samplerate'][sub]
                    model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                    msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                    print(msg)
                    self.tts_key = model_path
                    tts = self._load_api(self.tts_key, model_path, self.session['device'])
                    if self.session['voice'] is not None:
                        msg = f"Loading vocoder {self.tts_vc_key} zeroshot model, it takes a while, please be patient..."
                        print(msg)
                        tts_vc = self._load_api(self.tts_vc_key, default_vc_model, self.session['device'])
                else:
                    msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                    print(msg)
                    return False
        elif self.session['tts_engine'] == FAIRSEQ:
            if self.session['custom_model'] is not None:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return False
            else:
                self.params[FAIRSEQ]['sample_rate'] = models[FAIRSEQ][self.session['fine_tuned']]['samplerate']
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                self.tts_key = model_path
                tts = self._load_api(self.tts_key, model_path, self.session['device'])
                if self.session['voice'] is not None:
                    msg = f"Loading TTS {self.tts_vc_key} zeroshot model, it takes a while, please be patient..."
                    print(msg)
                    tts_vc = self._load_api(self.tts_vc_key, default_vc_model, self.session['device'])
        elif self.session['tts_engine'] == TACOTRON2:
            if self.session['custom_model'] is not None:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)     
                return False
            else:
                iso_dir = language_tts[self.session['tts_engine']][self.session['language']]
                sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                self.params[TACOTRON2]['sample_rate'] = models[TACOTRON2][self.session['fine_tuned']]['samplerate'][sub]
                if sub is None:
                    iso_dir = self.session['language']
                    sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                if sub is not None:
                    model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                    msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                    print(msg)
                    self.tts_key = model_path
                    tts = self._load_api(self.tts_key, model_path, self.session['device'])
                    if self.session['voice'] is not None:
                        msg = f"Loading vocoder {self.tts_vc_key} zeroshot model, it takes a while, please be patient..."
                        print(msg)
                        tts_vc = self._load_api(self.tts_vc_key, default_vc_model, self.session['device'])
                else:
                    msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                    print(msg)
                    return False
        elif self.session['tts_engine'] == YOURTTS:
            if self.session['custom_model'] is not None:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return False
            else:
                self.params[YOURTTS]['sample_rate'] = models[YOURTTS][self.session['fine_tuned']]['samplerate']
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                tts = self._load_api(self.tts_key, model_path, self.session['device'])
        return (loaded_tts.get(self.tts_key) or {}).get('engine', False)

    def _load_api(self, key, model_path, device):
        from TTS.api import TTS as coquiAPI
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            self._unload_tts(self.session['device'])
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
                    gc.collect()
                    error = 'TTS engine could not be created!'
                    print(error)
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
        return False

    def _md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _load_checkpoint(self, **kwargs):
        global lock
        try:
            key = kwargs.get('key')
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            tts_engine = kwargs.get('tts_engine')
            device = kwargs.get('device')
            self._unload_tts(device)
            with lock:
                if tts_engine == XTTSv2:
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
                        use_deepspeed=default_xtts_settings['use_deepspeed'],
                        eval=True
                    )
                elif tts_engine == BARK:
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
                gc.collect()
                error = 'TTS engine could not be created!'
                print(error)
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
        return False

    def _check_xtts_builtin_speakers(self, voice_path, speaker, device):
        try:
            voice_parts = Path(voice_path).parts
            if self.session['language'] not in voice_parts and self.session['language'] != 'en':               
                if self.session['language'] in language_tts[XTTSv2].keys():
                    lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                    new_voice_path = voice_path.replace('/eng/',f'/{lang_dir}/').replace('\\eng\\',f'\\{lang_dir}\\')
                    default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                    if os.path.exists(default_text_file):
                        msg = f"Converting builtin eng voice to {self.session['language']}..."
                        print(msg)
                        tts_internal_key = f"{XTTSv2}-internal"
                        default_text = Path(default_text_file).read_text(encoding="utf-8")
                        hf_repo = models[XTTSv2]['internal']['repo']
                        hf_sub = ''
                        tts = (loaded_tts.get(tts_internal_key) or {}).get('engine', False)
                        if not tts:
                            config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[XTTSv2]['internal']['files'][0]}", cache_dir=self.cache_dir)
                            checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[XTTSv2]['internal']['files'][1]}", cache_dir=self.cache_dir)
                            vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[XTTSv2]['internal']['files'][2]}", cache_dir=self.cache_dir)
                            tts = self._load_checkpoint(tts_engine=XTTSv2, key=tts_internal_key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path, device=device)
                        if tts:
                            file_path = new_voice_path.replace('_24000.wav', '.wav')
                            if speaker in default_xtts_settings['voices'].keys():
                                gpt_cond_latent, speaker_embedding = xtts_builtin_speakers_list[default_xtts_settings['voices'][speaker]].values()
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
                                torchaudio.save(file_path, audio_tensor, default_xtts_settings['samplerate'], format='wav')
                                for samplerate in [16000, 24000]:
                                    output_file = file_path.replace('.wav', f'_{samplerate}.wav')
                                    if not self._normalize_audio(file_path, output_file, samplerate):
                                        break
                                del audio_data, sourceTensor, audio_tensor  
                                if self.session['tts_engine'] != XTTSv2:
                                    del tts
                                    self._unload_tts(device, tts_internal_key)
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    return new_voice_path
                            else:
                                error = f'No audio waveform found in _check_xtts_builtin_speakers() result: {result}'
                                print(error)
                        else:
                            error = f"_check_xtts_builtin_speakers() error: {XTTSv2} is False"
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
            if self.session['language'] in language_tts[BARK].keys():
                npz_dir = os.path.join(bark_dir, speaker)
                npz_file = os.path.join(npz_dir, f'{speaker}.npz')
                if os.path.exists(npz_file):
                    return True
                else:
                    os.makedirs(npz_dir, exist_ok=True)
                    tts_internal_key = f"{BARK}-internal"
                    hf_repo = models[BARK]['internal']['repo']
                    hf_sub =models[BARK]['internal']['sub']
                    tts = (loaded_tts.get(tts_internal_key) or {}).get('engine', False)
                    if not tts:
                        text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[BARK]['internal']['files'][0]}", cache_dir=self.cache_dir)
                        coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[BARK]['internal']['files'][1]}", cache_dir=self.cache_dir)
                        fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[BARK]['internal']['files'][2]}", cache_dir=self.cache_dir)
                        checkpoint_dir = os.path.dirname(text_model_path)
                        tts = self._load_checkpoint(tts_engine=BARK, key=tts_internal_key, checkpoint_dir=checkpoint_dir, device=device)
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
                                speaker_id=speaker,
                                voice_dirs=bark_dir,
                                silent=True,
                                **fine_tuned_params
                            )
                        os.remove(voice_temp)
                        del audio_data
                        if self.session['tts_engine'] != BARK:
                            del tts
                            self._unload_tts(device, tts_internal_key)
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
   
    def _detect_gender(self, voice_path):
        try:
            sample_rate, signal = wav.read(voice_path)
            # Convert stereo to mono if needed
            if len(signal.shape) > 1:
                signal = np.mean(signal, axis=1)
            # Compute FFT
            fft_spectrum = np.abs(np.fft.fft(signal))
            freqs = np.fft.fftfreq(len(fft_spectrum), d=1/sample_rate)
            # Consider only positive frequencies
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = fft_spectrum[:len(fft_spectrum)//2]
            # Find peaks in frequency spectrum
            peaks, _ = find_peaks(positive_magnitude, height=np.max(positive_magnitude) * 0.2)
            if len(peaks) == 0:
                return None 
            # Find the first strong peak within the human voice range (75Hz - 300Hz)
            for peak in peaks:
                if 75 <= positive_freqs[peak] <= 300:
                    pitch = positive_freqs[peak]
                    gender = "female" if pitch > 135 else "male"
                    return gender
                    break     
            return None
        except Exception as e:
            error = f"_detect_gender() error: {voice_path}: {e}"
            print(error)
            return None

    def _unload_tts(self, device, tts_key=None):
        if len(loaded_tts) >= max_tts_in_memory:
            if tts_key is not None:
                if tts_key in loaded_tts.keys():
                    del loaded_tts[tts_key]
            else:
                for key in list(loaded_tts.keys()):
                    if key != self.tts_vc_key and key != self.tts_key:
                        del loaded_tts[key]
                if device != 'cpu':
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()

    def _tensor_type(self, audio_data):
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data, np.ndarray):  
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data, list):  
            return torch.tensor(audio_data, dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")

    def _trim_audio(self, audio_data, sample_rate, silence_threshold=0.001, buffer_sec=0.007):
        # Ensure audio_data is a PyTorch tensor
        if isinstance(audio_data, list):  
            audio_data = torch.tensor(audio_data)
        if isinstance(audio_data, torch.Tensor):
            if audio_data.is_cuda:
                audio_data = audio_data.cpu()           
            # Detect non-silent indices
            non_silent_indices = torch.where(audio_data.abs() > silence_threshold)[0]

            if len(non_silent_indices) == 0:
                return torch.tensor([], device=audio_data.device)
            # Calculate start and end trimming indices with buffer
            start_index = max(non_silent_indices[0] - int(buffer_sec * sample_rate), 0)
            end_index = non_silent_indices[-1] + int(buffer_sec * sample_rate)
            # Trim the audio
            trimmed_audio = audio_data[start_index:end_index]
            return trimmed_audio       
        raise TypeError("audio_data must be a PyTorch tensor or a list of numerical values.")

    def _normalize_audio(self, input_file, output_file, samplerate):
        filter_complex = (
            'agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
            'afftdn=nf=-70,'
            'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
            'loudnorm=I=-14:TP=-3:LRA=7:linear=true,'
            'equalizer=f=150:t=q:w=2:g=1,'
            'equalizer=f=250:t=q:w=2:g=-3,'
            'equalizer=f=3000:t=q:w=2:g=2,'
            'equalizer=f=5500:t=q:w=2:g=-4,'
            'equalizer=f=9000:t=q:w=2:g=-2,'
            'highpass=f=63[audio]'
        )
        ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', input_file]
        ffmpeg_cmd += [
            '-filter_complex', filter_complex,
            '-map', '[audio]',
            '-ar', str(samplerate),
            '-y', output_file
        ]
        try:
            subprocess.run(
                ffmpeg_cmd,
                env={},
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='ignore'
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"_normalize_audio() error: {input_file}: {e}")
            return False

    def _append_sentence2vtt(self, sentence_obj, path):
        def format_timestamp(seconds):
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return f"{int(h):02}:{int(m):02}:{s:06.3f}"

        index = 1
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if "-->" in line:
                        index += 1
        if index > 1 and "resume_check" in sentence_obj and sentence_obj["resume_check"] < index:
            return index  # Already written
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(sentence_obj["start"])
            end = format_timestamp(sentence_obj["end"])
            text = re.sub(r'[\r\n]+', ' ', sentence_obj["text"]).strip()
            f.write(f"{start} --> {end}\n{text}\n\n")
        return index + 1

    def _is_valid(self, audio_data):
        if audio_data is None:
            return False
        if isinstance(audio_data, torch.Tensor):
            return audio_data.numel() > 0
        if isinstance(audio_data, (list, tuple)):
            return len(audio_data) > 0
        try:
            import numpy as np
            if isinstance(audio_data, np.ndarray):
                return audio_data.size > 0
        except ImportError:
            pass
        return False

    def convert(self, sentence_number, sentence):
        global xtts_builtin_speakers_list
        try:
            speaker = None
            audio_data = False
            audio2trim = False
            trim_audio_buffer = 0.001
            settings = self.params[self.session['tts_engine']]
            final_sentence = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            if sentence.endswith('-'):
                sentence = sentence[:-1]
                audio2trim = True
            settings['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'ref.wav') if self.session['custom_model'] is not None
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )          
            if settings['voice_path'] is not None:
                speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(settings['voice_path']))
                self.session['voice'] = settings['voice_path'] = self._check_xtts_builtin_speakers(settings['voice_path'], speaker, self.session['device'])
                if not settings['voice_path']:
                    msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                    print(msg)
                    return False
            sentence_parts = sentence.split('‡pause‡')
            if self.session['tts_engine'] == XTTSv2 or self.session['tts_engine'] == FAIRSEQ:
                sentence_parts = [p.replace('.', '— ') for p in sentence_parts]
            sample_rate = 16000 if self.session['tts_engine'] in [TACOTRON2, VITS] and self.session['voice'] is not None else settings['sample_rate']
            silence_tensor = torch.zeros(1, int(sample_rate * 1.4)) # 1.4 seconds
            audio_segments = []
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
            if tts:
                for text_part in sentence_parts:
                    text_part = text_part.strip()
                    if not text_part:
                        audio_segments.append(silence_tensor.clone())
                        continue
                    audio_part = None
                    if self.session['tts_engine'] == XTTSv2:
                        trim_audio_buffer = 0.07 
                        if settings['voice_path'] is not None and settings['voice_path'] in settings['latent_embedding'].keys():
                            settings['gpt_cond_latent'], settings['speaker_embedding'] = settings['latent_embedding'][settings['voice_path']]
                        else:
                            msg = 'Computing speaker latents...'
                            print(msg)
                            if speaker in default_xtts_settings['voices'].keys():
                                settings['gpt_cond_latent'], settings['speaker_embedding'] = xtts_builtin_speakers_list[default_xtts_settings['voices'][speaker]].values()
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
                        if self._is_valid(audio_part):
                            audio_part = audio_part.tolist()
                    elif self.session['tts_engine'] == BARK:
                        trim_audio_buffer = 0.004
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
                        bark_dir = os.path.join(os.path.dirname(settings['voice_path']), 'bark')                       
                        if self._check_bark_npz(settings['voice_path'], bark_dir, speaker, self.session['device']):                                 
                            fine_tuned_params = {
                                key: cast_type(self.session[key])
                                for key, cast_type in {
                                    "text_temp": float,
                                    "waveform_temp": float
                                }.items()
                                if self.session.get(key) is not None
                            }
                            npz = os.path.join(bark_dir, speaker, f'{speaker}.npz')
                            if self.npz_path is None or self.npz_path != npz:
                                self.npz_path = npz
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
                            if self._is_valid(audio_part):
                                audio_part = audio_part.tolist()
                        else:
                            error = 'Could not create npz file!'
                            print(error)
                            return False
                    elif self.session['tts_engine'] == VITS:
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
                                voice_path_gender = self._detect_gender(settings['voice_path'])
                                voice_builtin_gender = self._detect_gender(tmp_in_wav)
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
                                        "-r", str(settings['sample_rate']), tmp_out_wav,
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
                            if tts_vc:
                                audio_part = tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            else:
                                error = f'Engine {self.tts_vc_key} is None'
                                print(error)
                                return False
                            settings['sample_rate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = tts.tts(
                                text=text_part,
                                **speaker_argument
                            )
                    elif self.session['tts_engine'] == FAIRSEQ:
                        if settings['voice_path'] is not None:
                            settings['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', settings['voice_path'])
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tts.tts_to_file(
                                text=text_part,
                                file_path=tmp_in_wav
                            )
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = self._detect_gender(settings['voice_path'])
                                voice_builtin_gender = self._detect_gender(tmp_in_wav)
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
                                        "-r", str(settings['sample_rate']), tmp_out_wav,
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
                                text=text_part
                            )
                    elif self.session['tts_engine'] == TACOTRON2:
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
                                voice_path_gender = self._detect_gender(settings['voice_path'])
                                voice_builtin_gender = self._detect_gender(tmp_in_wav)
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
                                        "-r", str(settings['sample_rate']), tmp_out_wav,
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
                            if tts_vc:
                                audio_part = tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            else:
                                error = f'Engine {self.tts_vc_key} is None'
                                print(error)
                                return False
                            settings['sample_rate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = tts.tts(
                                text=text_part,
                                **speaker_argument
                            )
                    elif self.session['tts_engine'] == YOURTTS:
                        trim_audio_buffer = 0.005
                        speaker_argument = {}
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        if settings['voice_path'] is not None:
                            settings['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', settings['voice_path'])
                            speaker_argument = {"speaker_wav": settings['voice_path']}
                        else:
                            voice_key = default_yourtts_settings['voices']['ElectroMale-2']
                            speaker_argument = {"speaker": voice_key}
                        with torch.no_grad():
                            audio_part = tts.tts(
                                text=text_part,
                                language=language,
                                **speaker_argument
                            )
                    if self._is_valid(audio_part):
                        sourceTensor = self._tensor_type(audio_part)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        audio_segments.append(audio_tensor)
                        audio_segments.append(silence_tensor.clone())
                if audio_segments and torch.equal(audio_segments[-1], silence_tensor):
                    audio_segments = audio_segments[:-1]
                if audio_segments:
                    audio_tensor = torch.cat(audio_segments, dim=-1)
                    if audio2trim:
                        audio_tensor = self._trim_audio(audio_tensor.squeeze(), sample_rate, 0.001, trim_audio_buffer).unsqueeze(0)
                    start_time = self.sentences_total_time
                    duration = audio_tensor.shape[-1] / sample_rate
                    end_time = start_time + duration
                    self.sentences_total_time = end_time
                    sentence_obj = {
                        "start": start_time,
                        "end": end_time,
                        "text": sentence,
                        "resume_check": self.sentence_idx
                    }
                    self.sentence_idx = self._append_sentence2vtt(sentence_obj, self.vtt_path)
                    torchaudio.save(final_sentence, audio_tensor, sample_rate, format=default_audio_proc_format)
                    del audio_tensor
                if self.session['device'] == 'cuda':
                    torch.cuda.empty_cache()
                if os.path.exists(final_sentence):
                    return True
                else:
                    error = f"Cannot create {final_sentence}"
                    print(error)
            else:
                error = f"convert() error: {self.session['tts_engine']} is None"
                print(error)
        except Exception as e:
            error = f'Coquit.convert(): {e}'
            raise ValueError(e)
        return False
