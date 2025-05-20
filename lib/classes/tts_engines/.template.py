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

class myTTS:
    def __init__(self, session):   
        self.session = session
        self.cache_dir = os.path.join(models_dir,'tts')  
        self.tts = None
        self.sentences_total_time = 0.0
        self.sentence_idx = 1
        self.params = {}
        self.vtt_path = None
        self._build()
 
    def _build(self):
        model_path = None
        config_path = None
        tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
        settings = self.params[self.session['tts_engine']]
        settings['sample_rate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
        self.vtt_path = os.path.splitext(self.session['final_name'])[0] + '.vtt'
        if self.session['tts_engine'] == XXXX:
            if self.session['custom_model'] is not None:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                model_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'model.pth')
                config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'config.json')
                tts_custom_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                if tts_custom_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_custom_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory:
                        self._unload_tts(self.session['device'])
                    self.tts = self._load_checkpoint(model_path, config_path, vocab_path, self.session['device'])
            else:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = f"{models[self.session['tts_engine']][self.session['fine_tuned']]['sub']}/" if self.session['fine_tuned'] != 'internal' else ''
                model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}model.pth", cache_dir=self.cache_dir)
                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}config.json", cache_dir=self.cache_dir)
                if tts_key in loaded_tts.keys():
                    self.tts = loaded_tts[tts_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory:
                        self._unload_tts(self.session['device'])
                    self.tts = self._load_checkpoint(model_path, config_path, vocab_path, self.session['device'])
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

    def _load_checkpoint(self, model_path, config_path, vocab_path, device):
        global lock
        try:
            config = self.XttsConfig()
            config.models_dir = os.path.join("models", "tts")
            config.load_json(config_path)
            tts = self.Xtts.init_from_config(config)
            with lock:
                tts.load_checkpoint(
                    config,
                    checkpoint_path=model_path,
                    vocab_path=vocab_path,
                    use_deepspeed=default_xtts_settings['use_deepspeed'],
                    eval=True
                )
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
          
    def _wav2npz(self, wav_path, npz_path, sample_rate):
        audio, sr = sf.read(wav_path)
        np.savez(npz_path, audio=audio, sample_rate=sample_rate)
        msg = f"Saved NPZ file: {npz_path}"
        print(msg)
        
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
            sample_rate = settings['sample_rate']
            silence_tensor = torch.zeros(1, sample_rate * 2)
            audio_segments = []
            if self.tts:
                for text_part in sentence_parts:
                    text_part = text_part.strip()
                    if not text_part:
                        audio_segments.append(silence_tensor.clone())
                        continue
                    audio_part = None
                    if self.session['tts_engine'] == XXXX:
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
                            result = self.tts.XXXX()
                        audio_part = result.get('wav')
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