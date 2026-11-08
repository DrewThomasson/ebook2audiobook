import io
import os
import json
import sys
import time
import ctypes
import importlib
import contextvars
import logging
import numpy as np
import soundfile as sf
import torch

from math import gcd
from typing import Optional, Callable
from scipy.signal import resample_poly
from tqdm import tqdm
from huggingface_hub import snapshot_download
from transformers import pipeline, AutoProcessor, MusicgenForConditionalGeneration, StoppingCriteriaList, LogitsProcessorList
from lib.lang import legends
from lib.conf_interlude import interlude_classifier_repo, interlude_genre_min_score, interlude_templates, interlude_moods, interlude_genre_styles, interlude_classifier_languages, interlude_neutral_style, interlude_neutral_moods

class InterludeGenerator:

    # level of safe settings that last made generation work in this process (see generate_interlude), so the next
    # interludes and books start there instead of rediscovering it: 0 normal, 1 eager attention, 2 eager + no thread boost
    safe_level = 0

    def __init__(self, device:str='cpu', channels:int=2, progress_bar:Optional[Callable]=None)->None:
        self.device = str(device or 'cpu').lower()
        self.channels = channels
        # gradio progress_bar in GUI mode, None in headless mode: downloads and generation show in both the terminal and the GUI,
        # transformers' "Loading weights" goes to the terminal in headless mode and to the GUI only in GUI mode
        self.progress_bar = progress_bar
        self.classifier_repo = interlude_classifier_repo
        self.torch_device = None
        # torch's intra-op threads call BLAS concurrently: fine with MKL, Accelerate or an OpenMP OpenBLAS (PyPI wheels),
        # not with a pthreads or sequential OpenBLAS, which is what the Jetson torch builds link (the system libopenblas.so.0,
        # 0.3.8 pthreads on JetPack 5): there concurrent GEMMs return NaN/garbage now and then. On such builds torch keeps
        # its single thread and a pthreads OpenBLAS gets the cores instead, inside each GEMM (its safe way to go parallel)
        self.raise_threads = True
        self.openblas = None
        if sys.platform.startswith('linux'):
            try:
                with open('/proc/self/maps', 'r') as f:
                    blas = next((line.split()[-1] for line in f if 'libopenblas' in line), None)
                if blas:
                    openblas = ctypes.CDLL(blas)
                    parallel = openblas.openblas_get_parallel()
                    if parallel != 2:
                        self.raise_threads = False
                    if parallel == 1:
                        self.openblas = openblas
            except Exception:
                pass
        self.classifier = None
        self.processor = None
        self.model = None
        # every map (moods, genres, languages...) lives in lib/conf_interlude.py
        self.moods = interlude_moods
        self.genre_styles = interlude_genre_styles
        self.classifier_languages = interlude_classifier_languages
        self.neutral_style = interlude_neutral_style
        self.neutral_moods = interlude_neutral_moods
        self.neutral_turn = 0
        # set by generate_prompt() on its first call, or beforehand by the caller (e.g. a genre stored for the book);
        # genre_scores: the averaged classifier score of every genre when it was detected here
        self.genre = None
        self.genre_scores = None
        # prompt -> what it was built from (mood, family, genre, display label), written into the interlude's sidecar json
        self.prompt_info = {}

    def load_model(self, with_classifier:bool=True)->None:
        # with_classifier=False: MusicGen only (editor regeneration from a prompt the user typed)
        if self.model is not None and (self.classifier is not None or not with_classifier):
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
        state = {'desc': '', 'bars': [], 'shown': 0.0, 'pushed': 0.0}
        # gradio's progress_bar finds its event through contextvars, which huggingface_hub's download threads don't inherit:
        # their updates were silently dropped. Re-enter the caller's context instead, at most ~5 updates per second
        caller_context = contextvars.copy_context()
        def _push(value:float, desc:str)->None:
            now = time.monotonic()
            if value < 1.0 and now - state['pushed'] < 0.2:
                return
            state['pushed'] = now
            caller_context.copy().run(report, value, desc=desc)
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
                        _push(state['shown'], f"{state['desc']} ({min(done, total) / 1e6:.0f}/{total / 1e6:.0f} MB)")
                return shown
        class _LoadTqdm(tqdm):
            # transformers' "Loading weights" bar in GUI mode: not drawn in the terminal, progress sent to gradio instead
            def __init__(self, *args, **kwargs):
                kwargs['file'] = io.StringIO()
                super().__init__(*args, **kwargs)
            def update(self, n=1):
                shown = super().update(n)
                if self.total:
                    _push(min(1.0, self.n / self.total), state['desc'])
                return shown
        def _fetch(repo_id:str)->None:
            # GUI only: pre-download exactly what transformers loads. The repos also hold weights it never reads:
            # MusicGen's model.fp32.safetensors (2.4 GB) and pytorch_model.bin, audiocraft-format .bin files, DeBERTa's onnx/ folder
            state['desc'] = f'Downloading {repo_id}'
            state['bars'] = []
            state['shown'] = 0.0
            state['pushed'] = 0.0
            report(0.0, desc=state['desc'])
            try:
                snapshot_download(repo_id, allow_patterns=['*.json', '*.model', '*.txt', 'model.safetensors', 'model-*-of-*.safetensors'], ignore_patterns=['*/*'], tqdm_class=_GuiTqdm)
                report(1.0, desc=state['desc'])
            except Exception as e:
                # offline or an older huggingface_hub: from_pretrained still resolves the files itself
                print(f'Pre-download of {repo_id} skipped ({str(e).splitlines()[0] if str(e) else type(e).__name__})')
        if report is not None:
            if with_classifier and self.classifier is None:
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
            if with_classifier and self.classifier is None:
                state['desc'] = 'Loading the text classifier'
                if report is not None:
                    report(0.0, desc=state['desc'])
                self.classifier = pipeline(
                    'zero-shot-classification',
                    model=self.classifier_repo,
                    device=-1,
                    dtype=torch.float32,
                    trust_remote_code=False
                )
                if report is not None:
                    report(1.0, desc=state['desc'])
            if self.model is None:
                msg = legends['msg_loading_model_on'].format(model=model_name, device=self.torch_device, dtype=str(dtype).replace('torch.', ''))
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

    def generate_prompt(self, text:str, book_text:str|list|None=None, text_supported:bool=True)->str:
        # book_text: one text, or a list of excerpts, each a str or (str, weight); text_supported=False: the chapter text is
        # in a language the classifier does not know, so only the excerpts given (e.g. metadata in a known language) are used
        samples = book_text if isinstance(book_text, list) else ([book_text] if book_text else [])
        samples = [(s, 1.0) if isinstance(s, str) else (s[0], float(s[1])) for s in samples]
        samples = [(' '.join(str(s).split())[:2000], w) for s, w in samples if str(s).strip() and w > 0]
        if not samples and text_supported:
            samples = [(' '.join(str(text).split())[:2000], 1.0)]
        detect_genre = self.genre is None and bool(samples)
        if text_supported or detect_genre:
            self.load_model()
        threads = torch.get_num_threads()
        blas_threads = self.openblas.openblas_get_num_threads() if self.openblas is not None else None
        try:
            # the classifier runs on CPU: same core policy as MusicGen on CPU (see __init__)
            if self.raise_threads:
                torch.set_num_threads(os.cpu_count() or 1)
            elif self.openblas is not None:
                self.openblas.openblas_set_num_threads(os.cpu_count() or 1)
            if detect_genre:
                # once per book: every excerpt is classified on its own and the genre with the best weighted average
                # score wins, so one odd chapter cannot decide alone
                totals = dict.fromkeys(self.genre_styles, 0.0)
                genre_bar = tqdm(total=len(samples), desc='Book genre', unit='excerpt', file=sys.stdout, dynamic_ncols=True, leave=False)
                try:
                    for k, (sample, weight) in enumerate(samples):
                        if self.progress_bar is not None:
                            self.progress_bar(k / len(samples), desc=f'Detecting the book genre ({k + 1}/{len(samples)})')
                        result = self.classifier(sample, list(self.genre_styles.keys()), hypothesis_template=interlude_templates['genre'], batch_size=8)
                        for label, score in zip(result['labels'], result['scores']):
                            totals[label] += weight * score
                        genre_bar.update(1)
                finally:
                    genre_bar.close()
                weight_sum = sum(w for _, w in samples)
                self.genre_scores = {g: round(v / weight_sum, 4) for g, v in sorted(totals.items(), key=lambda i: -i[1])}
                ranking = list(self.genre_scores.items())
                self.genre = ranking[0][0]
                msg = legends['msg_genre_detected'].format(genre=self.genre, score=f'{ranking[0][1]:.0%}', genre2=ranking[1][0], score2=f'{ranking[1][1]:.0%}', count=len(samples))
                if ranking[0][1] < interlude_genre_min_score:
                    # barely above a random guess: neutral instruments rather than a wrong genre's
                    self.genre = 'neutral'
                    msg = legends['msg_genre_unclear'].format(genre=ranking[0][0], score=f'{ranking[0][1]:.0%}', genre2=ranking[1][0], score2=f'{ranking[1][1]:.0%}', count=len(samples))
                print(msg)
                if self.progress_bar is not None:
                    self.progress_bar(1.0, desc=msg)
            palette, favoured = self.genre_styles[self.genre] if self.genre in self.genre_styles else self.neutral_style
            if text_supported:
                passage = ' '.join(str(text).split())[:1000]
                result = self.classifier(passage, list(self.moods.keys()), hypothesis_template=interlude_templates['family'], batch_size=8)
                family_scores = {label: score * (1.3 if label in favoured else 1.0) for label, score in zip(result['labels'], result['scores'])}
                family = max(family_scores, key=family_scores.get)
                result = self.classifier(passage, list(self.moods[family].keys()), hypothesis_template=interlude_templates['mood'], batch_size=8)
                mood = result['labels'][0]
            else:
                family, mood = self.neutral_moods[self.neutral_turn % len(self.neutral_moods)]
                self.neutral_turn += 1
        finally:
            torch.set_num_threads(threads)
            if blas_threads is not None:
                self.openblas.openblas_set_num_threads(blas_threads)
        emotion, cinematic, percussion = self.moods[family][mood]
        prompt = f'{emotion}, {cinematic}, {percussion}, {palette}, instrumental'
        self.prompt_info[prompt] = {'mood': mood, 'family': family, 'genre': self.genre or 'neutral', 'emotion': f'{emotion}, {cinematic}', 'percussion': percussion, 'instruments': palette, 'label': f"{mood} · {self.genre or 'neutral'}"}
        return prompt

    def generate_interlude(self, prompt:str, output_path:str, duration:int=30, samplerate:int=24000, desc:str='Interlude', is_cancelled:Optional[Callable[[], bool]]=None)->Optional[str]:
        bar = None
        try:
            self.load_model(with_classifier=False)
            # MusicGen is trained on 30 s windows: transformers hard-caps generation there
            max_new_tokens = int(max(1, min(duration, 30)) * self.model.config.audio_encoder.frame_rate)
            inputs = self.processor(text=[prompt], padding=True, return_tensors='pt')
            bar = tqdm(total=max_new_tokens, desc=desc, unit='step', file=sys.stdout, dynamic_ncols=True, leave=False)
            step = [0]
            cancelled = [False]
            guarded = [0]
            unstable = [False]
            def _progress(input_ids:torch.LongTensor, scores:torch.FloatTensor, **kwargs)->torch.BoolTensor:
                # reports the step counter (terminal bar, plus progress_bar in GUI); stops generation on a cancel request, or
                # early when most of the first steps gave non-finite logits (no point running 1500 broken steps)
                if is_cancelled is not None and is_cancelled():
                    cancelled[0] = True
                    return torch.ones(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
                step[0] += 1
                if step[0] >= 20 and guarded[0] * 2 > step[0] and (InterludeGenerator.safe_level < 2 or self.torch_device != 'cpu'):
                    unstable[0] = True
                    return torch.ones(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
                bar.update(1)
                if self.progress_bar is not None:
                    self.progress_bar(min(step[0], max_new_tokens) / max_new_tokens, desc=desc)
                return torch.zeros(input_ids.shape[0], dtype=torch.bool, device=input_ids.device)
            def _finite_logits(input_ids:torch.LongTensor, scores:torch.FloatTensor)->torch.FloatTensor:
                # runs before classifier-free guidance: a non-finite logit would make torch.multinomial fail
                # ("probability tensor contains either inf, nan or element < 0"), so it is neutralized and the step counted
                if not torch.isfinite(scores).all():
                    guarded[0] += 1
                    scores = torch.nan_to_num(scores, nan=-1e4, posinf=1e4, neginf=-1e4)
                return scores
            threads = torch.get_num_threads()
            blas_threads = self.openblas.openblas_get_num_threads() if self.openblas is not None else None
            audio = None
            # failures and non-finite logits escalate: GPU -> CPU first, then on CPU level 1 (eager attention instead of
            # SDPA, threads kept) and level 2 (eager + no thread boost). The level that works is kept for the process.
            # Autocast leaking from the caller is always switched off
            while True:
                if InterludeGenerator.safe_level >= 1:
                    try:
                        # the decoder holds the attention that matters (self + cross); the T5 encoder cannot switch anyway
                        self.model.decoder.set_attn_implementation('eager')
                    except Exception:
                        pass
                step[0] = 0
                guarded[0] = 0
                unstable[0] = False
                if bar is not None:
                    bar.reset()
                failure = None
                try:
                    if self.torch_device == 'cpu' and InterludeGenerator.safe_level < 2:
                        # the e2a process runs torch on one thread (OMP_NUM_THREADS=1): MusicGen gets every core for this call only
                        if self.raise_threads:
                            torch.set_num_threads(os.cpu_count() or 1)
                        elif self.openblas is not None:
                            # pthreads OpenBLAS read OMP_NUM_THREADS=1 when it loaded: give its own pool every core instead
                            self.openblas.openblas_set_num_threads(os.cpu_count() or 1)
                    with torch.inference_mode(), torch.autocast(device_type='cuda' if self.torch_device == 'cuda' else 'cpu', enabled=False):
                        audio = self.model.generate(**inputs.to(self.torch_device), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, logits_processor=LogitsProcessorList([_finite_logits]), stopping_criteria=StoppingCriteriaList([_progress]))
                except Exception as e:
                    # a cancel or an early stop leaves partial codes that MusicGen may fail to decode: not an error
                    if not (cancelled[0] or unstable[0]):
                        failure = e
                finally:
                    torch.set_num_threads(threads)
                    if blas_threads is not None:
                        self.openblas.openblas_set_num_threads(blas_threads)
                if cancelled[0]:
                    break
                if failure is None and not unstable[0]:
                    break
                audio = None
                reason = f'failed ({failure})' if failure is not None else 'gave non-finite logits'
                if self.torch_device != 'cpu':
                    tqdm.write(f'{desc}: generation on {self.torch_device} {reason}, retrying on cpu...', file=sys.stdout)
                    self.torch_device = 'cpu'
                    self.model = self.model.to('cpu', dtype=torch.float32)
                    continue
                if InterludeGenerator.safe_level >= 2:
                    if failure is not None:
                        raise failure
                    break
                InterludeGenerator.safe_level += 1
                tqdm.write(f"{desc}: generation {reason}, retrying with {'eager attention' if InterludeGenerator.safe_level == 1 else 'eager attention and no thread boost'}...", file=sys.stdout)
            if guarded[0] and not cancelled[0]:
                print(f'{desc}: {guarded[0]} step(s) with non-finite logits were neutralized')
            if cancelled[0]:
                msg = legends['msg_interlude_cancelled'].format(desc=desc)
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
                audio = audio * (0.76 / peak)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            # written next to the target then renamed: a crash or kill mid-write never leaves a truncated interlude for the next run to reuse
            root, ext = os.path.splitext(output_path)
            tmp_path = f'{root}.part{ext}'
            sf.write(tmp_path, np.clip(audio.T, -1.0, 1.0), samplerate, subtype='PCM_16' if ext.lower() in ('.flac', '.wav') else None)
            os.replace(tmp_path, output_path)
            # sidecar <name>.json keeps the prompt: the subtitles show it and the audiobook editor reopens it for regeneration
            with open(f'{root}.part.json', 'w', encoding='utf-8') as f:
                json.dump({'prompt': prompt, 'duration': duration, **self.prompt_info.get(prompt, {})}, f, ensure_ascii=False)
            os.replace(f'{root}.part.json', f'{root}.json')
            if bar is not None:
                bar.close()
                bar = None
            msg = legends['msg_interlude_saved'].format(path=output_path)
            print(msg)
            return output_path
        except Exception as e:
            error = legends['error_interlude'].format(e=e)
            print(error)
            return None
        finally:
            if bar is not None:
                bar.close()
