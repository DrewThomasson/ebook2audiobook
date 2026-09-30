import os
import logging
import numpy as np
import soundfile as sf
import torch

from math import gcd
from typing import Optional, Callable
from scipy.signal import resample_poly
from transformers import pipeline, AutoProcessor, MusicgenForConditionalGeneration, StoppingCriteriaList

class AudiocraftPrompter:

    def __init__(self, device:str='cpu')->None:
        self.device = str(device or 'cpu').lower()
        self.torch_device = None
        self.classifier = None
        self.processor = None
        self.model = None
        self.prompt_map = {
            'action and suspense': 'fast tempo, cinematic percussion, tense strings, dramatic trailer music',
            'melancholic and emotional': 'slow piano, melancholic cello, ambient reverb, emotional cinematic score',
            'peaceful and ambient': 'lo-fi beats, soft acoustic guitar, relaxing nature sounds, calm background music',
            'epic and orchestral': 'massive brass, epic choir, soaring strings, hans zimmer style, 120 bpm',
            'sci-fi and electronic': 'synthwave, pulsing bass, atmospheric synth pads, futuristic, blade runner vibe'
        }
        self.candidate_labels = list(self.prompt_map.keys())

    def load_model(self)->None:
        if self.classifier is None:
            # the checkpoint carries a legacy position_ids buffer that transformers 5 reports as UNEXPECTED, harmless: mute that report for this load only
            report_logger = logging.getLogger('transformers.utils.loading_report')
            report_level = report_logger.level
            report_logger.setLevel(logging.ERROR)
            try:
                self.classifier = pipeline(
                    'zero-shot-classification',
                    model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
                    device=-1,
                    dtype=torch.float32,
                    trust_remote_code=True
                )
            finally:
                report_logger.setLevel(report_level)

    def generate_prompt(self, text:str)->str:
        self.load_model()
        truncated_text = text[:1000]
        result = self.classifier(truncated_text, self.candidate_labels)
        best_vibe = result['labels'][0]
        return self.prompt_map.get(best_vibe, 'neutral ambient background music, seamless loop')

    def generate_interlude(self, prompt:str, output_path:str, duration:int=30, samplerate:int=24000, channels:int=2, on_progress:Optional[Callable[[float], None]]=None)->Optional[str]:
        try:
            if self.model is None:
                # e2a device -> torch device, checked against what the installed torch can really use
                if self.device in ('cuda', 'rocm', 'jetson') and torch.cuda.is_available():
                    self.torch_device = 'cuda'
                elif self.device == 'mps' and torch.backends.mps.is_available():
                    self.torch_device = 'mps'
                elif self.device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
                    self.torch_device = 'xpu'
                else:
                    self.torch_device = 'cpu'
                # generation settings per device: fp16 on CUDA/ROCm/XPU, medium only when the GPU has the room, small fp32 on MPS/CPU
                size = 'small'
                dtype = torch.float32
                if self.torch_device == 'cuda':
                    dtype = torch.float16
                    if torch.cuda.mem_get_info()[0] >= 8 * 1024 ** 3:
                        size = 'medium'
                elif self.torch_device == 'xpu':
                    dtype = torch.float16
                model_name = f"facebook/musicgen-{'stereo-' if channels == 2 else ''}{size}"
                msg = f"Loading {model_name} on {self.torch_device} ({str(dtype).replace('torch.', '')})..."
                print(msg)
                # MusicGen's pad/bos ids sit one past its vocabulary by design (extra embedding row): newer transformers warn about it, mute that check for this load only
                config_logger = logging.getLogger('transformers.configuration_utils')
                config_level = config_logger.level
                config_logger.setLevel(logging.ERROR)
                try:
                    try:
                        self.processor = AutoProcessor.from_pretrained(model_name)
                        self.model = MusicgenForConditionalGeneration.from_pretrained(model_name, dtype=dtype).to(self.torch_device)
                    except Exception as e:
                        if size == 'small':
                            raise
                        print(f'{model_name} failed ({e}), falling back to small...')
                        model_name = model_name.replace('-medium', '-small')
                        self.processor = AutoProcessor.from_pretrained(model_name)
                        self.model = MusicgenForConditionalGeneration.from_pretrained(model_name, dtype=dtype).to(self.torch_device)
                finally:
                    config_logger.setLevel(config_level)
                self.model.eval()
            # MusicGen is trained on 30 s windows: transformers hard-caps generation there
            max_new_tokens = int(max(1, min(duration, 30)) * self.model.config.audio_encoder.frame_rate)
            inputs = self.processor(text=[prompt], padding=True, return_tensors='pt')
            step = [0]
            def _progress(input_ids:torch.LongTensor, scores:torch.FloatTensor, **kwargs)->torch.BoolTensor:
                # never stops generation, only reports the step counter
                step[0] += 1
                done = min(step[0], max_new_tokens)
                print(f'{done: 6d} / {max_new_tokens: 6d}', end='\r', flush=True)
                if on_progress is not None:
                    on_progress(done / max_new_tokens)
                return torch.zeros(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
            threads = torch.get_num_threads()
            try:
                if self.torch_device == 'cpu':
                    # the e2a process runs torch on one thread (OMP_NUM_THREADS=1): MusicGen gets every core for this call only
                    torch.set_num_threads(os.cpu_count() or 1)
                try:
                    with torch.inference_mode():
                        audio = self.model.generate(**inputs.to(self.torch_device), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, stopping_criteria=StoppingCriteriaList([_progress]))
                except Exception as e:
                    if self.torch_device == 'cpu':
                        raise
                    print(f'\nGeneration on {self.torch_device} failed ({e}), retrying on cpu...')
                    self.torch_device = 'cpu'
                    self.model = self.model.to('cpu', dtype=torch.float32)
                    step[0] = 0
                    torch.set_num_threads(os.cpu_count() or 1)
                    with torch.inference_mode():
                        audio = self.model.generate(**inputs.to('cpu'), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, stopping_criteria=StoppingCriteriaList([_progress]))
            finally:
                torch.set_num_threads(threads)
            print()
            sample_rate = self.model.config.audio_encoder.sampling_rate
            audio = audio[0].float().cpu().numpy()
            if audio.shape[0] != channels:
                audio = audio.mean(axis=0, keepdims=True) if channels == 1 else np.repeat(audio, 2, axis=0)
            # match the chapters' sample rate: the final merge expects one uniform rate
            if sample_rate != samplerate:
                g = gcd(sample_rate, samplerate)
                audio = resample_poly(audio, samplerate // g, sample_rate // g, axis=1)
            # MusicGen levels vary a lot between prompts: peak-normalize to -1 dBFS
            peak = float(np.abs(audio).max())
            if peak > 0:
                audio = audio * (0.89 / peak)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sf.write(output_path, np.clip(audio.T, -1.0, 1.0), samplerate, subtype='PCM_16')
            msg = f'Saved interlude to {output_path}'
            print(msg)
            return output_path
        except Exception as e:
            error = f'Audiocraft error: {e}'
            print(error)
            return None
