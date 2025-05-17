import numpy as np
import os
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

lock = threading.Lock()
loaded_tts = {}
loaded_builtin_speakers = {}
loaded_processed_voices = {}

class TTSManager:
    def __init__(self, session, is_gui_process):   
        self.session = session
        self.is_gui_process = is_gui_process
        self.cache_dir = os.path.join(models_dir,'tts')
        self.params = {}
        self.sentences_total_time = 0.0
        self.sentence_idx = 1
        self.vtt_path = os.path.splitext(session['epub_path'])[0] + '.vtt'
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
        self.coquiAPI = None
        self.XttsConfig = None
        self.Xtts = None
        self._build()
 
    def _build(self):
        model_path = None
        config_path = None
        vocab_path = None
        if self.session['tts_engine'] in (XTTSv2, BARK, VITS, FAIRSEQ, YOURTTS):
            from TTS.api import TTS as coquiAPI
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
            self.coquiAPI = coquiAPI
            self.XttsConfig = XttsConfig
            self.Xtts = Xtts
        tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
        self.params['sample_rate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
        if self.session['language'] in language_tts[XTTSv2].keys():
            if self.session['voice'] is not None and self.session['language'] != 'eng':
                speaker = re.sub(r'_(24000|16000)\.wav$', '', os.path.basename(self.session['voice']))
                if speaker in default_xtts_settings['voices']:
                    if not f"/{self.session['language']}/" in self.session['voice']:
                        try:
                            default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                            if os.path.exists(default_text_file):
                                msg = f"Converting xttsv2 builtin english voice to {self.session['language']}..."
                                print(msg)
                                model_path = models[XTTSv2]['internal']['repo']
                                tts_internal_key = f"{self.session['tts_engine']}-internal"
                                if tts_internal_key in loaded_tts.keys():
                                    self.params['tts'] = loaded_tts[tts_internal_key]
                                else:
                                    if len(loaded_tts) == max_tts_in_memory::
                                        self._unload_tts()
                                    hf_repo = models[self.session['tts_engine']]['internal']['repo']
                                    hf_sub = ''
                                    model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}model.pth", cache_dir=self.cache_dir)
                                    config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}config.json", cache_dir=self.cache_dir)
                                    vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}vocab.json", cache_dir=self.cache_dir)
                                    self.params['tts'] = self._load_coqui_tts_checkpoint(model_path, config_path, vocab_path, self.session['device'])
                                    loaded_tts[tts_internal_key] = self.params['tts']
                                lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                                file_path = self.session['voice'].replace('_24000.wav', '.wav').replace('/eng/', f'/{lang_dir}/').replace('\\eng\\', f'\\{lang_dir}\\')
                                base_dir = os.path.dirname(file_path)
                                default_text = Path(default_text_file).read_text(encoding="utf-8")
                                if self.session['tts_engine'] not in loaded_builtin_speakers.keys():
                                    speakers_path = hf_hub_download(repo_id=models[self.session['tts_engine']]['internal']['repo'], filename="speakers_xtts.pth", cache_dir=self.cache_dir)
                                    loaded_builtin_speakers[self.session['tts_engine']] = torch.load(speakers_path)
                                speakers_list = loaded_builtin_speakers[self.session['tts_engine']]
                                self.params['gpt_cond_latent'], self.params['speaker_embedding'] = speakers_list[default_xtts_settings['voices'][speaker]].values()
                                with torch.no_grad():
                                    result = self.params['tts'].inference(
                                        text=default_text,
                                        language=self.session['language_iso1'],
                                        gpt_cond_latent=self.params['gpt_cond_latent'],
                                        speaker_embedding=self.params['speaker_embedding'],
                                        **self.fine_tuned_params
                                    )
                                audio_data = result.get('wav')
                                if audio_data is not None:
                                    audio_data = audio_data.tolist()
                                else:
                                    error = f'No audio waveform found in convert_sentence_to_audio() result: {result}'
                                    print(error)
                                    return False
                                sourceTensor = self._tensor_type(audio_data)
                                audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                                torchaudio.save(file_path, audio_tensor, 24000, format='wav')
                                del audio_data, sourceTensor, audio_tensor  
                                for samplerate in [16000, 24000]:
                                    output_file = file_path.replace('.wav', f'_{samplerate}.wav')
                                    if self._normalize_audio(file_path, output_file, samplerate):
                                        # for Bark
                                        if samplerate == 24000:
                                            bark_dir = os.path.join(os.path.dirname(os.path.dirname(file_path)), 'bark')
                                            npz_dir = os.path.join(bark_dir, speaker)
                                            os.makedirs(npz_dir, exist_ok=True)
                                            npz_file = os.path.join(npz_dir, f'{speaker}.npz')
                                            self._wav_to_npz(output_file, npz_file)
                                    else:
                                        break
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                            else:
                                error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                                print(error)
                        except Exception as e:
                            error = f'_build() builtin voice conversion error: {e}'
                            print(error)
        if self.session['tts_engine'] == XTTSv2:
            if self.session['custom_model'] is not None:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                model_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'], 'model.pth')
                config_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'config.json')
                vocab_path = os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'vocab.json')
                tts_custom_key = f"{self.session['tts_engine']}-{self.session['custom_model']}"
                if tts_custom_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_custom_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory::
                        self._unload_tts()
                    self.params['tts'] = self._load_coqui_tts_checkpoint(model_path, config_path, vocab_path, self.session['device'])
                    loaded_tts[tts_custom_key] = self.params['tts']
            else:
                msg = f"Loading TTS {self.session['tts_engine']} model, it takes a while, please be patient..."
                print(msg)
                hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                hf_sub = f"{models[self.session['tts_engine']][self.session['fine_tuned']]['sub']}/" if self.session['fine_tuned'] != 'internal' else ''
                speakers_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}speakers_xtts.pth", cache_dir=self.cache_dir)
                model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}model.pth", cache_dir=self.cache_dir)
                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}config.json", cache_dir=self.cache_dir)
                vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}vocab.json", cache_dir=self.cache_dir)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory::
                        self._unload_tts()
                    self.params['tts'] = self._load_coqui_tts_checkpoint(model_path, config_path, vocab_path, self.session['device'])
        elif self.session['tts_engine'] == BARK:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    self._unload_tts()
                    self.params['tts'] = self._load_coqui_tts_api(model_path, self.session['device'])
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
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
                        self.params['tts'] = loaded_tts[tts_key]
                    else:
                        if len(loaded_tts) == max_tts_in_memory:
                            self._unload_tts()
                        self.params['tts'] = self._load_coqui_tts_api(model_path, self.session['device'])
                    if self.session['voice'] is not None:
                        tts_vc_key = default_vc_model
                        msg = f"Loading vocoder {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                        print(msg)
                        if tts_vc_key in loaded_tts.keys():
                            self.params['tts_vc'] = loaded_tts[tts_vc_key]
                        else:
                            self.params['tts_vc'] = self._load_coqui_tts_vc(self.session['device'])
                            loaded_tts[tts_vc_key] = self.params['tts_vc']
                else:
                    msg = f"{self.session['tts_engine']} checkpoint for {self.session['language']} not found!"
                    print(msg)
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)                 
        elif self.session['tts_engine'] == FAIRSEQ:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo'].replace("[lang]", self.session['language'])
                msg = f"Loading TTS {tts_key} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory::
                        self._unload_tts()
                    self.params['tts'] = self._load_coqui_tts_api(model_path, self.session['device'])
                if self.session['voice'] is not None:
                    tts_vc_key = default_vc_model
                    msg = f"Loading TTS {tts_vc_key} zeroshot model, it takes a while, please be patient..."
                    print(msg)
                    if tts_vc_key in loaded_tts.keys():
                        self.params['tts_vc'] = loaded_tts[tts_vc_key]
                    else:
                        if len(loaded_tts) == max_tts_in_memory:
                            self._unload_tts()
                        self.params['tts_vc'] = self._load_coqui_tts_vc(self.session['device'])
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
        elif self.session['tts_engine'] == YOURTTS:
            if self.session['custom_model'] is None:
                model_path = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                msg = f"Loading TTS {model_path} model, it takes a while, please be patient..."
                print(msg)
                if tts_key in loaded_tts.keys():
                    self.params['tts'] = loaded_tts[tts_key]
                else:
                    if len(loaded_tts) == max_tts_in_memory:
                        self._unload_tts()
                    self.params['tts'] = self._load_coqui_tts_api(model_path, self.session['device'])
            else:
                msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                print(msg)
        if 'tts' in self.params.keys():
            loaded_tts[tts_key] = self.params['tts']
        else:
            error = 'TTS engine could not be created!'
            print(error)
          
    def _load_coqui_tts_api(self, model_path, device):
        try:
            with lock:
                tts = self.coquiAPI(model_path)
                if device == 'cuda':
                    tts.cuda()
                else:
                    tts.to(device)
            return tts
        except Exception as e:
            error = f'_load_coqui_tts_api() error: {e}'
            print(error)
            return None

    def _load_coqui_tts_checkpoint(self, model_path, config_path, vocab_path, device):
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
                if device == 'cuda':
                    tts.cuda()
                else:
                    tts.to(device)
            return tts
        except Exception as e:
            error = f'_load_coqui_tts_checkpoint() error: {e}'
            print(error)
            return None

    def _load_coqui_tts_vc(self, device):
        try:
            with lock:
                tts = self.coquiAPI(default_vc_model).to(device)
            return tts
        except Exception as e:
            error = f'_load_coqui_tts_vc() error: {e}'
            print(error)
            return None
          
    def _wav_to_npz(self, wav_path, npz_path):
        audio, sr = sf.read(wav_path)
        np.savez(npz_path, audio=audio, sample_rate=24000)
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

    def _unload_tts(self):
        for key in list(loaded_tts.keys()):
            del loaded_tts[key]
        if 'tts' in self.params.keys():
            del self.params['tts']
        if torch.cuda:
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

    def _append_sentence_to_vtt(self, sentence_obj, path):
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
                f.write("WEBVTT\r\n\r\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(sentence_obj["start"])
            end = format_timestamp(sentence_obj["end"])
            text = sentence_obj["text"].replace("\n", " ").strip()
            f.write(f"{start} --> {end}\n{text}\r\n\r\n")
        return index + 1

    def convert_sentence_to_audio(self):
        try:
            audio_data = None
            audio_to_trim = False
            trim_audio_buffer = 0.001
            if self.params['sentence'].endswith('‡pause‡'):
                sample_rate = 16000 if self.session['tts_engine'] == VITS else self.params['sample_rate']
                 # 2 seconds of silence = sample_rate * 2 samples
                num_samples = sample_rate * 2
                # Generate mono silent tensor (1 channel)
                audio_tensor = torch.zeros(1, num_samples)
                torchaudio.save(
                    self.params['sentence_audio_file'],
                    audio_tensor,
                    sample_rate,
                    format=default_audio_proc_format
                )               
            else:
                self.params['voice_path'] = (
                    self.session['voice'] if self.session['voice'] is not None 
                    else os.path.join(self.session['custom_model_dir'], self.session['tts_engine'], self.session['custom_model'],'ref.wav') if self.session['custom_model'] is not None
                    else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
                )
                if self.params['sentence'].endswith('-'):
                    self.params['sentence'] = self.params['sentence'][:-1]
                    audio_to_trim = True
                processed_voice_key = f"{self.session['tts_engine']}-{self.params['voice_path'].replace(' ','')}" if self.params['voice_path'] is not None else None
                if self.session['tts_engine'] == XTTSv2:
                    trim_audio_buffer = 0.07
                    if self.session['tts_engine'] not in loaded_builtin_speakers.keys():
                        speakers_path = hf_hub_download(repo_id=models[self.session['tts_engine']]['internal']['repo'], filename="speakers_xtts.pth", cache_dir=self.cache_dir)
                        loaded_builtin_speakers[self.session['tts_engine']] = torch.load(speakers_path)
                    speakers_list = loaded_builtin_speakers[self.session['tts_engine']]
                    if processed_voice_key is not None and processed_voice_key in loaded_processed_voices.keys():
                        self.params['gpt_cond_latent'], self.params['speaker_embedding'] = loaded_processed_voices[processed_voice_key]
                    else:
                        msg = 'Computing speaker latents...'
                        print(msg)
                        if self.params['voice_path'] in default_xtts_settings['voices'].values():
                            self.params['gpt_cond_latent'], self.params['speaker_embedding'] = speakers_list[self.params['voice_path']].values()
                        else:
                            self.params['gpt_cond_latent'], self.params['speaker_embedding'] = self.params['tts'].get_conditioning_latents(audio_path=[self.params['voice_path']])  
                        loaded_processed_voices[processed_voice_key] = self.params['gpt_cond_latent'], self.params['speaker_embedding']
                    with torch.no_grad():
                        result = self.params['tts'].inference(
                            text=self.params['sentence'],
                            language=self.session['language_iso1'],
                            gpt_cond_latent=self.params['gpt_cond_latent'],
                            speaker_embedding=self.params['speaker_embedding'],
                            **self.fine_tuned_params
                        )
                    audio_data = result.get('wav')
                    if audio_data is not None:
                        audio_data = audio_data.tolist()
                    else:
                        error = f'No audio waveform found in convert_sentence_to_audio() result: {result}'
                        print(error)
                        return False
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
                    if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                    else:
                        if processed_voice_key is not None and processed_voice_key in loaded_processed_voices.keys():
                            bark_dir, speaker = loaded_processed_voices[processed_voice_key]
                        else:
                            if self.params['voice_path'] is not None:
                                bark_dir = os.path.join(os.path.dirname(self.params['voice_path']), 'bark')
                                speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(self.params['voice_path']))
                            else:
                                bark_dir = os.path.join(os.path.dirname(default_bark_settings['voices']['Jamie']), 'bark')
                                speaker = re.sub(r'(_16000|_24000).wav$', '', os.path.basename(default_bark_settings['voices']['Jamie']))
                            loaded_processed_voices[processed_voice_key] = bark_dir, speaker
                        speaker_argument = {
                            "voice_dir": bark_dir,
                            "speaker": speaker,
                            "text_temp": 0.2
                        }                      
                        with torch.no_grad():
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                                **speaker_argument
                            )
                elif self.session['tts_engine'] == VITS:
                    if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                    else:
                        speaker_argument = {}
                        if self.session['language'] == 'eng' and 'vctk/vits' in models[self.session['tts_engine']]['internal']['sub']:
                            if self.session['language'] in models[self.session['tts_engine']]['internal']['sub']['vctk/vits'] or self.session['language_iso1'] in models[self.session['tts_engine']]['internal']['sub']['vctk/vits']:
                                speaker_argument = {"speaker": 'p262'}
                        elif self.session['language'] == 'cat' and 'custom/vits' in models[self.session['tts_engine']]['internal']['sub']:
                            if self.session['language'] in models[self.session['tts_engine']]['internal']['sub']['custom/vits'] or self.session['language_iso1'] in models[self.session['tts_engine']]['internal']['sub']['custom/vits']:
                                speaker_argument = {"speaker": '09901'}
                        if self.params['voice_path'] is not None:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            self.params['tts'].tts_to_file(
                                text=self.params['sentence'],
                                file_path=tmp_in_wav,
                                **speaker_argument
                            )
                            if processed_voice_key is not None and processed_voice_key in loaded_processed_voices.keys():
                                self.params['semitones'] = loaded_processed_voices[processed_voice_key]
                            else:
                                self.params['voice_path_gender'] = self._detect_gender(self.params['voice_path'])
                                self.params['voice_builtin_gender'] = self._detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {self.params['voice_path_gender']}\nBuiltin voice seems to be {self.params['voice_builtin_gender']}"
                                print(msg)
                                if self.params['voice_builtin_gender'] != self.params['voice_path_gender']:
                                    self.params['semitones'] = -4 if self.params['voice_path_gender'] == 'male' else 4
                                    loaded_processed_voices[processed_voice_key] = self.params['semitones']
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    loaded_processed_voices[processed_voice_key] = self.params['semitones'] = None
                            if self.params['semitones'] is not None:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(self.params['sample_rate']), tmp_out_wav,
                                        "pitch", str(self.params['semitones'] * 100)
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
                                audio_data = self.params['tts_vc'].voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=self.params['voice_path']
                                )
                            self.params['sample_rate'] = 16000
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                                **speaker_argument
                            )
                elif self.session['tts_engine'] == FAIRSEQ:
                    if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                    else:
                        if self.params['voice_path'] is not None:
                            self.params['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', self.params['voice_path'])
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            self.params['tts'].tts_to_file(
                                text=self.params['sentence'],
                                file_path=tmp_in_wav
                            )
                            if processed_voice_key is not None and processed_voice_key in loaded_processed_voices.keys():
                                self.params['semitones'] = loaded_processed_voices[processed_voice_key]
                            else:
                                self.params['voice_path_gender'] = self._detect_gender(self.params['voice_path'])
                                self.params['voice_builtin_gender'] = self._detect_gender(tmp_in_wav)
                                msg = f"Cloned voice seems to be {self.params['voice_path_gender']}\nBuiltin voice seems to be {self.params['voice_builtin_gender']}"
                                print(msg)
                                if self.params['voice_builtin_gender'] != self.params['voice_path_gender']:
                                    self.params['semitones'] = -4 if self.params['voice_path_gender'] == 'male' else 4
                                    loaded_processed_voices[processed_voice_key] = self.params['semitones']
                                    msg = f"Adapting builtin voice frequencies from the clone voice..."
                                    print(msg)
                                else:
                                    loaded_processed_voices[processed_voice_key] = self.params['semitones'] = None
                            if self.params['semitones'] is not None:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(self.params['sample_rate']), tmp_out_wav,
                                        "pitch", str(self.params['semitones'] * 100)
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
                                audio_data = self.params['tts_vc'].voice_conversion(
                                    source_wav=tmp_out_wav,
                                    target_wav=self.params['voice_path']
                                )
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav):
                                os.remove(tmp_out_wav)
                        else:
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence']
                            )
                elif self.session['tts_engine'] == YOURTTS:
                    trim_audio_buffer = 0.004
                    if self.session['custom_model'] is not None or self.session['fine_tuned'] != 'internal':
                        msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                        print(msg)
                    else:
                        speaker_argument = {}
                        language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
                        if processed_voice_key is not None and processed_voice_key in loaded_processed_voices.keys():
                            speaker_argument = loaded_processed_voices[processed_voice_key]
                        else:
                            if self.params['voice_path'] is not None:
                                self.params['voice_path'] = re.sub(r'_24000\.wav$', '_16000.wav', self.params['voice_path'])
                                speaker_argument = {"speaker_wav": self.params['voice_path']}
                                voice_key = self.params['voice_path']
                            else:
                                voice_key = default_yourtts_settings['voices']['ElectroMale-2']
                                speaker_argument = {"speaker": voice_key}
                        with torch.no_grad():
                            audio_data = self.params['tts'].tts(
                                text=self.params['sentence'],
                                language=language,
                                **speaker_argument
                            )
                if audio_data is not None:
                    if audio_to_trim:
                        audio_data = self._trim_audio(audio_data, self.params['sample_rate'],0.001,trim_audio_buffer) 
                    sourceTensor = self._tensor_type(audio_data)
                    audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                    start_time = self.sentences_total_time
                    duration = audio_tensor.shape[-1] / self.params['sample_rate']
                    end_time = start_time + duration
                    self.sentences_total_time = end_time
                    sentence_obj = {
                        "start": start_time,
                        "end": end_time,
                        "text": self.params['sentence'],
                        "resume_check": self.sentence_idx
                    }
                    self.sentence_idx = self._append_sentence_to_vtt(sentence_obj, self.vtt_path)
                    torchaudio.save(self.params['sentence_audio_file'], audio_tensor, self.params['sample_rate'], format=default_audio_proc_format)
                    del audio_data, sourceTensor, audio_tensor
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