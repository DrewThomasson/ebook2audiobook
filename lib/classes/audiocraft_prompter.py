import io
import os
import sys
import importlib
import logging
import numpy as np
import soundfile as sf
import torch

from math import gcd
from typing import Optional, Callable
from scipy.signal import resample_poly
from tqdm import tqdm
from huggingface_hub import snapshot_download
from transformers import pipeline, AutoProcessor, MusicgenForConditionalGeneration, StoppingCriteriaList

class AudiocraftPrompter:

    def __init__(self, device:str='cpu', channels:int=2, progress_bar:Optional[Callable]=None)->None:
        self.device = str(device or 'cpu').lower()
        self.channels = channels
        # gradio progress_bar in GUI mode, None in headless mode: downloads and generation show in both the terminal and the GUI,
        # transformers' "Loading weights" goes to the terminal in headless mode and to the GUI only in GUI mode
        self.progress_bar = progress_bar
        self.classifier_repo = 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'
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
        if self.classifier is not None and self.model is not None:
            return
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
        model_name = f"facebook/musicgen-{'stereo-' if self.channels == 2 else ''}{size}"
        report = self.progress_bar
        state = {'desc': '', 'bars': [], 'shown': 0.0}
        class _GuiTqdm(tqdm):
            # huggingface_hub download bars: drawn in the terminal as usual, byte progress also forwarded to gradio
            def __init__(self, *args, **kwargs):
                kwargs.pop('name', None)
                kwargs['disable'] = False
                super().__init__(*args, **kwargs)
                if self.unit == 'B':
                    state['bars'].append(self)
            def update(self, n=1):
                shown = super().update(n)
                if self.unit == 'B':
                    # xet transfers count bytes on a bar with no total, while the bar that knows the size (reconstruction)
                    # only moves at the end: the furthest byte count is measured against the largest total known so far
                    total = max((b.total or 0) for b in state['bars'])
                    if total > 0:
                        done = max(b.n for b in state['bars'])
                        # totals grow as each file registers: never let the bar step back
                        state['shown'] = max(state['shown'], min(1.0, done / total))
                        report(state['shown'], desc=f"{state['desc']} ({min(done, total) / 1e6:.0f}/{total / 1e6:.0f} MB)")
                return shown
        class _LoadTqdm(tqdm):
            # transformers' "Loading weights" bar in GUI mode: not drawn in the terminal, progress sent to gradio instead
            def __init__(self, *args, **kwargs):
                kwargs['file'] = io.StringIO()
                super().__init__(*args, **kwargs)
            def update(self, n=1):
                shown = super().update(n)
                if self.total:
                    report(min(1.0, self.n / self.total), desc=state['desc'])
                return shown
        def _fetch(repo_id:str)->None:
            # GUI only: pre-download exactly what transformers loads. The repos also hold weights it never reads:
            # MusicGen's model.fp32.safetensors (2.4 GB) and pytorch_model.bin, audiocraft-format .bin files, DeBERTa's onnx/ folder
            state['desc'] = f'Downloading {repo_id}'
            state['bars'] = []
            state['shown'] = 0.0
            report(0.0, desc=state['desc'])
            try:
                snapshot_download(repo_id, allow_patterns=['*.json', '*.model', '*.txt', 'model.safetensors', 'model-*-of-*.safetensors'], ignore_patterns=['*/*'], tqdm_class=_GuiTqdm)
            except Exception as e:
                # offline or an older huggingface_hub: from_pretrained still resolves the files itself
                print(f'Pre-download of {repo_id} skipped ({str(e).splitlines()[0] if str(e) else type(e).__name__})')
        if report is not None:
            if self.classifier is None:
                _fetch(self.classifier_repo)
            if self.model is None:
                _fetch(model_name)
        modeling_logger = logging.getLogger('transformers.modeling_utils')
        config_logger = logging.getLogger('transformers.configuration_utils')
        config_level = config_logger.level
        # a load report listing only UNEXPECTED keys (tensors the checkpoint stores but the model rebuilds itself) is noise:
        # drop it, keep any report that flags MISSING, MISMATCH or CONVERSION problems
        def _report_filter(record:logging.LogRecord)->bool:
            msg = record.getMessage()
            return 'LOAD REPORT' not in msg or any(s in msg for s in ('MISSING', 'MISMATCH', 'CONVERSION'))
        modeling_logger.addFilter(_report_filter)
        # MusicGen's pad/bos ids sit one past its vocabulary by design (extra embedding row): newer transformers warn about it
        config_logger.setLevel(logging.ERROR)
        # "Loading weights": terminal bar in headless mode, gradio progress_bar in GUI mode
        # (transformers 5.0 calls logging.tqdm, newer versions a tqdm imported into core_model_loading: both are swapped)
        loading_bars = []
        for name in ('transformers.utils.logging', 'transformers.core_model_loading'):
            try:
                module = importlib.import_module(name)
                if hasattr(module, 'tqdm'):
                    loading_bars.append((module, module.tqdm))
            except ImportError:
                pass
        if report is not None:
            for module, _ in loading_bars:
                module.tqdm = _LoadTqdm
        try:
            if self.classifier is None:
                state['desc'] = 'Loading the text classifier'
                if report is not None:
                    report(0.0, desc=state['desc'])
                self.classifier = pipeline(
                    'zero-shot-classification',
                    model=self.classifier_repo,
                    device=-1,
                    dtype=torch.float32,
                    trust_remote_code=True
                )
                if report is not None:
                    report(1.0, desc=state['desc'])
            if self.model is None:
                msg = f"Loading {model_name} on {self.torch_device} ({str(dtype).replace('torch.', '')})..."
                print(msg)
                state['desc'] = msg
                if report is not None:
                    report(0.0, desc=msg)
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
                self.model.eval()
                if report is not None:
                    report(1.0, desc=msg)
        finally:
            for module, original in loading_bars:
                module.tqdm = original
            modeling_logger.removeFilter(_report_filter)
            config_logger.setLevel(config_level)

    def generate_prompt(self, text:str)->str:
        self.load_model()
        truncated_text = text[:1000]
        result = self.classifier(truncated_text, self.candidate_labels)
        best_vibe = result['labels'][0]
        return self.prompt_map.get(best_vibe, 'neutral ambient background music, seamless loop')

    def generate_interlude(self, prompt:str, output_path:str, duration:int=30, samplerate:int=24000, desc:str='Interlude', is_cancelled:Optional[Callable[[], bool]]=None)->Optional[str]:
        bar = None
        try:
            self.load_model()
            # MusicGen is trained on 30 s windows: transformers hard-caps generation there
            max_new_tokens = int(max(1, min(duration, 30)) * self.model.config.audio_encoder.frame_rate)
            inputs = self.processor(text=[prompt], padding=True, return_tensors='pt')
            bar = tqdm(total=max_new_tokens, desc=desc, unit='step', file=sys.stdout, dynamic_ncols=True, leave=False)
            step = [0]
            cancelled = [False]
            def _progress(input_ids:torch.LongTensor, scores:torch.FloatTensor, **kwargs)->torch.BoolTensor:
                # reports the step counter (terminal bar, plus progress_bar in GUI) and stops generation only on a cancel request
                if is_cancelled is not None and is_cancelled():
                    cancelled[0] = True
                    return torch.ones(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
                step[0] += 1
                bar.update(1)
                if self.progress_bar is not None:
                    self.progress_bar(min(step[0], max_new_tokens) / max_new_tokens, desc=desc)
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
                    # a cancel stops generation mid-way and MusicGen may fail decoding the partial codes: that is not an error
                    if not cancelled[0]:
                        if self.torch_device == 'cpu':
                            raise
                        print(f'Generation on {self.torch_device} failed ({e}), retrying on cpu...')
                        self.torch_device = 'cpu'
                        self.model = self.model.to('cpu', dtype=torch.float32)
                        step[0] = 0
                        if bar is not None:
                            bar.reset()
                        torch.set_num_threads(os.cpu_count() or 1)
                        with torch.inference_mode():
                            audio = self.model.generate(**inputs.to('cpu'), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, stopping_criteria=StoppingCriteriaList([_progress]))
            finally:
                torch.set_num_threads(threads)
            if cancelled[0]:
                msg = f'{desc} cancelled, nothing saved'
                print(msg)
                return None
            sample_rate = self.model.config.audio_encoder.sampling_rate
            audio = audio[0].float().cpu().numpy()
            if audio.shape[0] != self.channels:
                audio = audio.mean(axis=0, keepdims=True) if self.channels == 1 else np.repeat(audio, 2, axis=0)
            # match the chapters' sample rate: the final merge expects one uniform rate
            if sample_rate != samplerate:
                g = gcd(sample_rate, samplerate)
                audio = resample_poly(audio, samplerate // g, sample_rate // g, axis=1)
            # MusicGen levels vary a lot between prompts: peak-normalize to -1 dBFS
            peak = float(np.abs(audio).max())
            if peak > 0:
                audio = audio * (0.89 / peak)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            # written next to the target then renamed: a crash or kill mid-write never leaves a truncated interlude for the next run to reuse
            root, ext = os.path.splitext(output_path)
            tmp_path = f'{root}.part{ext}'
            sf.write(tmp_path, np.clip(audio.T, -1.0, 1.0), samplerate, subtype='PCM_16' if ext.lower() in ('.flac', '.wav') else None)
            os.replace(tmp_path, output_path)
            if bar is not None:
                bar.close()
                bar = None
            msg = f'Saved interlude to {output_path}'
            print(msg)
            return output_path
        except Exception as e:
            error = f'Audiocraft error: {e}'
            print(error)
            return None
        finally:
            if bar is not None:
                bar.close()
