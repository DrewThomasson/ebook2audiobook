import os
import gc
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
from TTS.api import TTS as coquiAPI
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.configs.bark_config import BarkConfig
from TTS.tts.models.xtts import Xtts
from TTS.tts.models.bark import Bark

from lib.models import *
from lib.conf import voices_dir, models_dir, default_audio_proc_format
from lib.lang import language_tts

torch.backends.cudnn.benchmark = True
#torch.serialization.add_safe_globals(["numpy.core.multiarray.scalar"])

_original_multinomial = torch.multinomial

def _safe_multinomial(input, num_samples, replacement=False, *, generator=None, out=None):
	with torch.no_grad():
		input = torch.nan_to_num(input, nan=0.0, posinf=0.0, neginf=0.0)
		input = torch.clamp(input, min=0.0)
		sum_input = input.sum(dim=-1, keepdim=True)
		# Handle degenerate cases: fallback to uniform
		mask = (sum_input <= 0)
		if mask.any():
			input[mask.expand_as(input)] = 1.0  # fallback to uniform distribution
			sum_input = input.sum(dim=-1, keepdim=True)
		input = input / sum_input
	return _original_multinomial(input, num_samples, replacement=replacement, generator=generator, out=out)

torch.multinomial = _safe_multinomial

lock = threading.Lock()
xtts_builtin_speakers_list = None

class Coqui:
    def __init__(self, session):   
        self.session = session
        self.cache_dir = os.path.join(models_dir,'tts')  
        self.coquiAPI = coquiAPI
        self.XttsConfig = XttsConfig
        self.Xtts = Xtts
        self.tts = None
        self.tts_vc = None
        self.fine_tuned_params = {
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
        self.sentences_total_time = 0.0
        self.sentence_idx = 1
        self.params = {XTTSv2: {"latent_embedding":{}}, BARK: {}, VITS: {"semitones": {}}, FAIRSEQ: {"semitones": {}}, YOURTTS: {}}  
        self.vtt_path = None
        self._build()
 
    def _build(self):
        global xtts_builtin_speakers_list
        model_path = None
        config_path = None
        tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
        self.vtt_path = os.path.splitext(self.session['final_name'])[0] + '.vtt'
        if self.session['voice'] is not None:
            if not self._check_builtin_speakers(self.session['voice']):
                msg = f"Could not create the builtin XTTSv2 speaker example in {self.session['language']}"
                print(msg)
                return None
        if self.session['tts_engine'] == XTTSv2:
            if xtts_builtin_speakers_list is None:
                speakers_path = hf_hub_download(repo_id=models['xtts']['internal']['repo'], filename="speakers_xtts.pth", cache_dir=self.cache_dir)
                xtts_builtin_speakers_list = torch.load(speakers_path)
            if self.session['custom_model'] is not None:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                model_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'model.pth')
                config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'config.json')
                vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'vocab.json')
                tts_custom_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                if tts_custom_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_custom_key]
                else:
                    self.tts = self._load_checkpoint(XTTSv2, model_path, config_path, vocab_path, self.session['device'])
            else:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = f"{models[self.session['tts_engine']][self.session['fine_tuned']]['sub']}/" if self.session['fine_tuned'] != 'internal' else ''
                if self.session['fine_tuned'] == 'internal':
                    speakers_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}speakers_xtts.pth", cache_dir=self.cache_dir)
                model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}model.pth", cache_dir=self.cache_dir)
                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}config.json", cache_dir=self.cache_dir)
                vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}vocab.json", cache_dir=self.cache_dir)
                if tts_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_key]
                else:
                    self.tts = self._load_checkpoint(XTTSv2, model_path, config_path, vocab_path, self.session['device'])
        elif self.session['tts_engine'] == BARK:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_key]
                else:
                    self.tts = self._load_checkpoint(BARK, model_path, None, None, self.session['device'])
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return None
        elif self.session['tts_engine'] == VITS:
            if self.session['custom_model'] is None:
                iso_dir = self.session['language_iso1']
                sub_dict = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                if sub is None:
                    iso_dir = self.session['language']
                    sub = next((key for key, lang_list in sub_dict.items() if iso_dir in lang_list), None)
                if sub is not None:
                    model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang_iso1]", iso_dir).replace("[xxx]", sub)
                    msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                    print(msg)
                    if tts_key in loaded_tts.keys():
                        self.tts = loaded_tts[tts_key]
                    else:
                        self.tts = self._load_api(model_path, self.session['device'])
                    if not self.tts:
                        return None
                    if self.session['voice'] is not None:
                        tts_vc_key = default_vc_model
                        msg = f"Loading vocoder {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                        print(msg)
                        if tts_vc_key in loaded_tts.keys():
                            self.tts_vc = loaded_tts[tts_vc_key]
                        else:
                            self.tts_vc = self._load_api_vc(self.session['device'])
                            if self.tts_vc:
                                loaded_tts[tts_vc_key] = self.tts_vc
                            else:
                                error = 'TTS VC engine could not be created!'
                                print(error)
                                return None
                else:
                    msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                    print(msg)
                    return None
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)     
                return None
        elif self.session['tts_engine'] == FAIRSEQ:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                msg = f"Loading TTS {tts_key} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_key]
                else:
                    self.tts = self._load_api(model_path, self.session['device'])
                if self.session['voice'] is not None:
                    tts_vc_key = default_vc_model
                    msg = f"Loading TTS {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                    print(msg)
                    if tts_vc_key in loaded_tts.keys():
                        self.tts_vc = loaded_tts[tts_vc_key]
                    else:
                        self.tts_vc = self._load_api_vc(self.session['device'])
                        if self.tts_vc:
                            loaded_tts[tts_vc_key] = self.tts_vc
                        else:
                            error = 'TTS VC engine could not be created!'
                            print(error)
                            return None
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return None
        elif self.session['tts_engine'] == YOURTTS:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_key]
                else:
                    self.tts = self._load_api(model_path, self.session['device'])
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
                return None
        if self.tts:
            loaded_tts[tts_key] = self.tts
            return self.tts
        else:
            self._unload_tts(self.session['device'])
            gc.collect()
            error = 'TTS engine could not be created!'
            print(error)
            return None
       
    def _load_api(self, model_path, device):
        global lock
        try:
            if len(loaded_tts) == max_tts_in_memory:
                self._unload_tts(self.session['device'])
            with lock:
                tts = self.coquiAPI(model_path)
                if tts:
                    if device == 'cuda':
                        tts.cuda()
                    else:
                        tts.to(device)
                    return tts
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
        return 0

    def _load_checkpoint(self, tts_engine, model_path, config_path, vocab_path, device):
        global lock
        try:
            with lock:
                if tts_engine == XTTSv2:
                    if len(loaded_tts) == max_tts_in_memory:
                        self._unload_tts(self.session['device'])
                    config = self.XttsConfig()
                    config.models_dir = os.path.join("models", "tts")
                    config.load_json(config_path)
                    tts = self.Xtts.init_from_config(config)                   
                    tts.load_checkpoint(
                        config,
                        checkpoint_path=model_path,
                        vocab_path=vocab_path,
                        use_deepspeed=default_xtts_settings['use_deepspeed'],
                        eval=True
                    )
                elif tts_engine == BARK:
                    self._unload_tts(self.session['device'])
                    config = BarkConfig()
                    config.USE_SMALLER_MODELS = os.environ.get('SUNO_USE_SMALL_MODELS', '').lower() == 'true'
                    config.CACHE_DIR = os.path.join(models_dir, 'tts', 'suno', 'bark')
                    tts = Bark.init_from_config(config)
                    tts.load_checkpoint(
                        config,
                        checkpoint_dir=model_path,
                        eval=True
                    )
                else:
                    if len(loaded_tts) == max_tts_in_memory:
                        self._unload_tts(self.session['device'])
                if tts:
                    if device == 'cuda':
                        tts.cuda()
                    else:
                        tts.to(device)
                    return tts
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
            print(error)
        return 0

    def _load_api_vc(self, device):
        global lock
        try:
            with lock:
                tts = self.coquiAPI(default_vc_model).to(device)
                if tts:
                    return tts
        except Exception as e:
            error = f'_load_api_vc() error: {e}'
            print(error)
        return 0
    def _check_builtin_speakers(self, voice_path):
        try:
            if f"/{self.session['language']}/" in voice_path:
                return True
            else:
                speaker = re.sub(r'_(24000|16000)\.wav$', '', os.path.basename(voice_path))
                if speaker not in default_xtts_settings['voices']:
                    return True
                else:
                    if self.session['language'] in language_tts[XTTSv2].keys():
                        default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                        default_text = Path(default_text_file).read_text(encoding="utf-8")
                        if os.path.exists(default_text_file):
                            msg = f"Converting xttsv2 builtin english voice to {self.session['language']}..."
                            print(msg)
                            model_path = models[XTTSv2]['internal']['repo']
                            tts_internal_key = f"{self.session['tts_engine']}-internal"
                            if tts_internal_key in loaded_tts.keys():
                                self.tts = loaded_tts[tts_internal_key]
                            else:
                                if len(loaded_tts) == max_tts_in_memory:
                                    self._unload_tts(self.session['device'])
                                hf_repo = models[self.session['tts_engine']]['internal']['repo']
                                hf_sub = ''
                                model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}model.pth", cache_dir=self.cache_dir)
                                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}config.json", cache_dir=self.cache_dir)
                                vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}vocab.json", cache_dir=self.cache_dir)
                                self.tts = self._load_checkpoint(XTTSv2, model_path, config_path, vocab_path, self.session['device'])
                                loaded_tts[tts_internal_key] = self.tts
                            if not self.tts:
                                return False
                            lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                            file_path = voice_path.replace('_24000.wav', '.wav').replace('/eng/', f'/{lang_dir}/').replace('\\eng\\', f'\\{lang_dir}\\')

                            gpt_cond_latent, speaker_embedding = xtts_builtin_speakers_list[default_xtts_settings['voices'][speaker]].values()
                            with torch.no_grad():
                                result = self.tts.inference(
                                    text=default_text,
                                    language=self.session['language_iso1'],
                                    gpt_cond_latent=gpt_cond_latent,
                                    speaker_embedding=speaker_embedding,
                                    **self.fine_tuned_params
                                )
                            audio_data = result.get('wav')
                            if audio_data is not None:
                                audio_data = audio_data.tolist()
                            else:
                                error = f'No audio waveform found in convert_sentence2audio() result: {result}'
                                print(error)
                                return False
                            sourceTensor = self._tensor_type(audio_data)
                            audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                            torchaudio.save(file_path, audio_tensor, 24000, format='wav')
                            del audio_data, sourceTensor, audio_tensor  
                            for samplerate in [16000, 24000]:
                                output_file = file_path.replace('.wav', f'_{samplerate}.wav')
                                if self._normalize_audio(file_path, output_file, samplerate):
                                    break
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            bark_dir = os.path.join(os.path.dirname(voice_path), 'bark')
                            speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(voice_path)) 
                            if self._check_bark_npz(voice_path, bark_dir, speaker, default_text):
                                return True
                            else:
                                return False
                        else:
                            error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                            print(error)
                            return False
        except Exception as e:
            error = f'_check_builtin_speakers() error: {e}'
            print(error)
            return False

    def _check_bark_npz(self, voice_path, bark_dir, speaker, default_text=None):
        try:
            if self.session['language'] in language_tts[BARK].keys():
                npz_dir = os.path.join(bark_dir, speaker)
                npz_file = os.path.join(npz_dir, f'{speaker}.npz')
                if os.path.exists(npz_file):
                    return True
                else:
                    os.makedirs(npz_dir, exist_ok=True)     
                    if self.session['tts_engine'] != BARK:
                        self._unload_tts(self.session['device'])
                        self.tts = self._load_checkpoint(BARK, models[BARK]['internal']['repo'], None, None, self.session['device'])
                    voice_path_temp = os.path.splitext(npz_file)[0]+'.wav'
                    shutil.copy(os.path.dirname(voice_path, voice_path_temp))
                    if default_text is None:
                        default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                        default_text = Path(default_text_file).read_text(encoding="utf-8")
                    default_text = default_text
                    output_dict = self.tts.synthesize(
                        default_text,
                        config,
                        speaker_id=speaker,
                        voice_dirs=bark_dir,
                        temperature=0.85
                    )
                    os.remove(voice_path_temp)
                    msg = f"Saved NPZ file: {npz_file}"
                    print(msg)
                    return True
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

    def _unload_tts(self, device):
        for key in list(loaded_tts.keys()):
            del loaded_tts[key]
        if self.tts:
            del self.tts
        if self.tts_vc:
            del self.tts_vc
        self.tts = self.tts_vc = None
        if device == 'cuda':
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
            audio_data = False
            audio2trim = False
            trim_audio_buffer = 0.001
            settings = self.params[self.session['tts_engine']]
            settings['sample_rate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            final_sentence = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            if sentence.endswith('-'):
                sentence = sentence[:-1]
                audio2trim = True
            settings['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'ref.wav') if self.session['custom_model'] is not None
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            sentence_parts = sentence.split('‡pause‡')
            if self.session['tts_engine'] == XTTSv2 or self.session['tts_engine'] == FAIRSEQ:
                sentence_parts = [p.replace('.', '— ') for p in sentence_parts]
            sample_rate = 16000 if self.session['tts_engine'] == VITS and self.session['voice'] is not None else settings['sample_rate']
            silence_tensor = torch.zeros(1, sample_rate * 2)
            audio_segments = []
            if self.tts:
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
                            if settings['voice_path'] in default_xtts_settings['voices'].values():
                                settings['gpt_cond_latent'], settings['speaker_embedding'] = xtts_builtin_speakers_list[settings['voice_path']].values()
                            else:
                                settings['gpt_cond_latent'], settings['speaker_embedding'] = self.tts.get_conditioning_latents(audio_path=[settings['voice_path']])  
                            settings['latent_embedding'][settings['voice_path']] = settings['gpt_cond_latent'], settings['speaker_embedding']
                        with torch.no_grad():
                            result = self.tts.inference(
                                text=text_part,
                                language=self.session['language_iso1'],
                                gpt_cond_latent=settings['gpt_cond_latent'],
                                speaker_embedding=settings['speaker_embedding'],
                                **self.fine_tuned_params
                            )
                        audio_part = result.get('wav')
                        if self._is_valid(audio_part):
                            audio_part = audio_part.tolist()
                    elif self.session['tts_engine'] == BARK:
                        trim_audio_buffer = 0.001
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
                        if voice_path is not None:
                            bark_dir = os.path.join(os.path.dirname(voice_path), 'bark')
                            speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(voice_path))                               
                        else:
                            bark_dir = os.path.join(os.path.dirname(default_bark_settings['voices']['Jamie']), 'bark')
                            speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(default_bark_settings['voices']['Jamie']))
                        if self._check_bark_npz(settings['voice_path'], bark_dir, speaker, None):
                            speaker_argument = {
                                "voice_dir": bark_dir,
                                "speaker": speaker,
                                "text_temp": 0.85
                            }                      
                            with torch.no_grad():
                                audio_part = self.tts.tts(
                                    text=text_part,
                                    **speaker_argument
                                )
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
                            self.tts.tts_to_file(
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
                            with torch.no_grad():
                                audio_part = self.tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            settings['sample_rate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = self.tts.tts(
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
                            self.tts.tts_to_file(
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
                            with torch.no_grad():
                                audio_part = self.tts_vc.voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=settings['voice_path']
                                )
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_part = self.tts.tts(
                                text=text_part
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
                            audio_part = self.tts.tts(
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
                    return False
            else:
                error = f"TTS engine failed to load!"
                print(error)
                return False               
        except Exception as e:
            error = f'convert_sentence2audio(): {e}'
            raise ValueError(e)
            return False