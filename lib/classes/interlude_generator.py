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

class InterludeGenerator:

    def __init__(self, device:str='cpu', channels:int=2, progress_bar:Optional[Callable]=None)->None:
        self.device = str(device or 'cpu').lower()
        self.channels = channels
        # gradio progress_bar in GUI mode, None in headless mode: downloads and generation show in both the terminal and the GUI,
        # transformers' "Loading weights" goes to the terminal in headless mode and to the GUI only in GUI mode
        self.progress_bar = progress_bar
        self.classifier_repo = 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'
        self.torch_device = None
        # set once non-finite logits showed up: the following generations go straight to the safe settings
        self.safe_mode = False
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
        # 128 moods in 16 families of 8: the family is picked first, then the mood inside it (16 + 8 classifier passes
        # per interlude instead of 128). Each mood only describes emotion, tempo and texture: the instruments come from the
        # book genre below, so the same mood sounds like a thriller in a thriller and like a fairy tale in a fairy tale
        self.moods = {
            'calm and peaceful': {
                'a tranquil dawn': 'serene, slow tempo, soft sustained chords, gentle rising melody',
                'the pastoral countryside': 'relaxed, slow tempo, airy pastoral melody, light ornaments',
                'quiet contemplation': 'still, very slow tempo, sparse notes, long pauses',
                'a lullaby': 'soothing, slow lullaby in three, soft and tender',
                'a still night': 'hushed nocturne, slow tempo, distant soft tones',
                'serene water': 'flowing, calm, gentle rippling arpeggios',
                'cozy warmth at home': 'warm, cozy, unhurried, soft major harmonies',
                'meditative stillness': 'meditative, drone based, slowly evolving texture'
            },
            'joyful and uplifting': {
                'carefree joy': 'bright, upbeat, light bouncy rhythm, major key',
                'a festive celebration': 'festive, lively tempo, celebratory rhythm',
                'bright optimism': 'optimistic, medium tempo, rising major melody',
                'warm friendship': 'warm, friendly, heartfelt major melody, medium tempo',
                'a joyful reunion': 'joyous, swelling, emotional uplift, major key',
                'springtime renewal': 'fresh, light, blossoming melody, medium tempo',
                'exuberant dancing': 'exuberant, fast dance rhythm, energetic',
                'a hopeful new beginning': 'hopeful, gradually building, uplifting major key'
            },
            'romantic and tender': {
                'first love': 'tender, innocent, sweet melody, medium slow tempo',
                'intimate tenderness': 'intimate, soft, delicate, slow tempo',
                'longing': 'yearning, slow, aching melody, suspended chords',
                'passionate romance': 'passionate, sweeping melody, swelling dynamics',
                'bittersweet love': 'bittersweet, slow, shifting between minor and major',
                'devotion': 'devoted, warm, stately slow tempo, heartfelt',
                'flirtatious charm': 'playful, charming, light swing, coy',
                'lovers reunited': 'emotional, soaring, building to a warm climax'
            },
            'melancholic and sad': {
                'grief': 'grieving, very slow, heavy minor chords, mournful',
                'loneliness': 'lonely, sparse, slow solitary melody, empty space',
                'heartbreak': 'heartbroken, slow, aching minor melody',
                'quiet sorrow': 'sorrowful, gentle, slow, subdued',
                'rainy melancholy': 'melancholic, slow, soft falling patterns, grey mood',
                'a farewell': 'wistful farewell, slow, gently fading',
                'despair': 'despairing, dark, slow, heavy, hopeless',
                'resignation': 'resigned, quiet, slow, descending phrases'
            },
            'nostalgic and reflective': {
                'childhood memories': 'nostalgic, innocent, music box like, gentle',
                'bittersweet nostalgia': 'bittersweet, warm, slow, wistful',
                'looking back on life': 'reflective, introspective, medium slow tempo',
                'faded photographs': 'faded, hazy, warm lo-fi texture, slow',
                'autumn reflection': 'autumnal, mellow, golden warmth, slow',
                'letters from the past': 'tender, intimate, reminiscent, slow',
                'the passing of time': 'contemplative, steady ticking pulse, timeless',
                'a wistful daydream': 'dreamy, floating, soft haze, slow'
            },
            'mysterious and curious': {
                'an enigmatic puzzle': 'enigmatic, curious staccato, unresolved harmonies, medium tempo',
                'a secret discovery': 'mysterious, building curiosity, shimmering textures',
                'a foggy unknown': 'foggy, ambiguous harmonies, hazy atmosphere, slow',
                'an investigation': 'investigative, steady pulse, curious motif',
                'hidden clues': 'sneaky, light staccato, inquisitive',
                'curious exploration': 'curious, wandering melody, medium tempo',
                'a strange encounter': 'uncanny, unusual intervals, sparse',
                'ancient secrets': 'ancient, modal, mysterious drones, slow'
            },
            'suspense and tension': {
                'creeping dread': 'creeping, slowly building tension, low pulses',
                'a ticking clock': 'urgent ticking rhythm, rising tension',
                'stealth': 'stealthy, quiet staccato, tiptoeing rhythm',
                'an interrogation': 'tense, sparse, cold, unresolved',
                'impending danger': 'ominous build, rising tension, swelling',
                'paranoia': 'anxious, unstable rhythm, dissonant',
                'nervous anticipation': 'nervous, restless pulse, held breath',
                'a cliffhanger': 'tense crescendo, suspended, unresolved ending'
            },
            'fear and horror': {
                'terror': 'terrifying, harsh dissonance, sudden stabs',
                'a haunted house': 'eerie, creaking textures, ghostly',
                'a lurking monster': 'menacing, low growling drones, slow',
                'a nightmare': 'nightmarish, distorted, disorienting',
                'panic': 'panicked, fast, frantic, chaotic',
                'eerie silence': 'eerie near silence, thin high tones',
                'a curse': 'cursed, dark ritualistic, slow minor',
                'psychological horror': 'unsettling, detuned, creeping, claustrophobic'
            },
            'action and chase': {
                'a high speed chase': 'fast tempo, driving rhythm, adrenaline',
                'an escape': 'urgent, fast, breathless momentum',
                'a heist': 'cool, rhythmic, slick groove, tension',
                'a fight': 'aggressive, hard hitting percussion, fast',
                'a pursuit through the city': 'relentless, pulsing, fast tempo',
                'a race against time': 'racing, accelerating, high energy',
                'a rooftop run': 'agile, fast, syncopated rhythm',
                'a getaway': 'propulsive, fast, triumphant energy'
            },
            'battle and conflict': {
                'war drums': 'thunderous drums, marching rhythm, martial',
                'a siege': 'heavy, relentless, brooding power',
                'a clash of armies': 'massive, chaotic, epic battle intensity',
                'a duel': 'tense, focused, rhythmic clashes',
                'the aftermath of battle': 'somber, slow, devastated, mournful',
                'a rebellion': 'defiant, rising, driving rhythm',
                'a call to arms': 'rallying, heroic fanfare, stirring',
                'a last stand': 'desperate, heroic, intense, climactic'
            },
            'epic and heroic': {
                "a hero's journey": 'adventurous heroic theme, building',
                'a quest beginning': 'adventurous, hopeful, setting out, medium tempo',
                'a legendary saga': 'grand, sweeping, legendary',
                'a noble sacrifice': 'noble, slow, heartbreaking grandeur',
                'a rising hero': 'ascending, inspiring, building to a climax',
                'vast landscapes': 'majestic, wide open, slow and sweeping',
                'an ancient kingdom': 'regal, stately, ancient grandeur',
                'destiny': 'fateful, powerful, building intensity'
            },
            'triumphant and victorious': {
                'victory': 'triumphant, bold, celebratory fanfare',
                'triumph over adversity': 'triumphant, emotional, soaring',
                'a coronation': 'regal, majestic, ceremonial',
                "a hero's homecoming": 'warm, triumphant, emotional',
                'an achievement': 'proud, bright, uplifting',
                'a rescue': 'relieved, rising, joyful release',
                'sunrise after the storm': 'hopeful, gradually brightening, radiant',
                'a happy ending': 'resolved, warm, satisfying final cadence'
            },
            'dark and ominous': {
                'a looming threat': 'ominous, low, slow, heavy',
                'a villain': 'sinister, menacing theme, dark',
                'a dark ritual': 'ritualistic, chant like, dark',
                'corruption': 'decaying, dissonant, slowly twisting',
                'a gathering storm': 'brooding, rumbling, building',
                'oppression': 'oppressive, cold, mechanical, bleak',
                'betrayal': 'shocking, bitter, dark turn',
                'menace': 'threatening, stalking pulse, dark'
            },
            'wonder and magical': {
                'an enchanted forest': 'enchanted, shimmering, magical, gentle',
                'a fairy tale': 'storybook, whimsical, magical',
                'a magic spell': 'sparkling, mystical, rising shimmer',
                'a new world discovered': 'awe inspiring, wide, blossoming',
                'a starry sky': 'cosmic, twinkling, vast, slow',
                'a dreamlike fantasy': 'dreamlike, floating, ethereal',
                'mythical creatures': 'majestic, mysterious, wondrous',
                'awe': 'awestruck, swelling, luminous'
            },
            'playful and humorous': {
                'mischief': 'mischievous, sneaky playful staccato',
                'whimsy': 'whimsical, light, quirky',
                'slapstick comedy': 'comedic, bouncy, exaggerated',
                'light-hearted banter': 'light, breezy, conversational rhythm',
                'a quirky character': 'quirky, odd meter, playful',
                'a cheeky prank': 'cheeky, tiptoeing, playful',
                'cartoonish antics': 'cartoonish, zany, fast',
                'bouncy fun': 'bouncy, upbeat, fun'
            },
            'solemn and spiritual': {
                'a funeral': 'solemn, slow funeral march, grave',
                'a prayer': 'prayerful, slow, reverent',
                'a sacred ritual': 'sacred, chant like, timeless',
                'redemption': 'redemptive, slowly rising, emotional release',
                'forgiveness': 'gentle, warm, healing',
                'mortality': 'contemplative, slow, profound',
                'a cathedral': 'reverberant, majestic, sacred',
                'transcendence': 'transcendent, ethereal, ascending'
            }
        }
        # book genre: its instrumentation goes into every prompt, and it favours the mood families that suit it
        # (their classifier scores weigh 1.3x). Detected once per book, see generate_prompt()
        self.genre_styles = {
            'fantasy': ('orchestral, celtic harp, flutes, choir, folk instruments', ['wonder and magical', 'epic and heroic', 'battle and conflict']),
            'science fiction': ('synthesizers, electronic textures, ambient pads, futuristic sound design', ['wonder and magical', 'mysterious and curious', 'suspense and tension']),
            'cyberpunk and dystopian': ('dark synthwave, industrial textures, distorted bass, cold electronics', ['dark and ominous', 'action and chase', 'suspense and tension']),
            'horror': ('dissonant strings, low drones, prepared piano, unsettling sound design', ['fear and horror', 'dark and ominous', 'suspense and tension']),
            'gothic': ('pipe organ, harpsichord, dark strings, choir', ['dark and ominous', 'mysterious and curious', 'melancholic and sad']),
            'thriller': ('dark cinematic score, pulsing synth bass, staccato strings', ['suspense and tension', 'action and chase', 'dark and ominous']),
            'mystery and detective': ('pizzicato strings, muted piano, clarinet, soft percussion', ['mysterious and curious', 'suspense and tension']),
            'crime and noir': ('smoky jazz, muted trumpet, upright bass, brushed drums', ['dark and ominous', 'suspense and tension', 'mysterious and curious']),
            'romance': ('piano, warm strings, acoustic guitar', ['romantic and tender', 'joyful and uplifting', 'melancholic and sad']),
            'historical fiction': ('chamber strings, harpsichord, period instruments', ['nostalgic and reflective', 'epic and heroic', 'romantic and tender']),
            'war': ('military snare, brass, low strings, timpani', ['battle and conflict', 'melancholic and sad', 'solemn and spiritual']),
            'western': ('acoustic guitar, harmonica, whistling, banjo', ['action and chase', 'nostalgic and reflective', 'calm and peaceful']),
            'adventure': ('full orchestra, bold brass, adventurous percussion', ['epic and heroic', 'action and chase', 'wonder and magical']),
            'mythology and fairy tales': ('harp, celesta, woodwinds, enchanted orchestra', ['wonder and magical', 'epic and heroic', 'playful and humorous']),
            "children's": ('glockenspiel, ukulele, pizzicato strings, toy piano', ['playful and humorous', 'joyful and uplifting', 'wonder and magical']),
            'young adult': ('indie instrumental, piano, light electronic beats', ['joyful and uplifting', 'romantic and tender', 'suspense and tension']),
            'literary fiction': ('solo piano, chamber strings, minimalist', ['nostalgic and reflective', 'melancholic and sad', 'calm and peaceful']),
            'comedy and humor': ('bouncy pizzicato, bassoon, light percussion', ['playful and humorous', 'joyful and uplifting']),
            'drama': ('piano and strings, cinematic', ['melancholic and sad', 'romantic and tender', 'nostalgic and reflective']),
            'biography and memoir': ('acoustic guitar, gentle piano, soft strings, documentary style', ['nostalgic and reflective', 'triumphant and victorious']),
            'history': ('documentary orchestral score, strings, timpani', ['epic and heroic', 'solemn and spiritual', 'nostalgic and reflective']),
            'religion and spirituality': ('ambient pads, choir, singing bowls', ['solemn and spiritual', 'calm and peaceful']),
            'philosophy': ('minimalist piano, ambient strings', ['calm and peaceful', 'nostalgic and reflective', 'mysterious and curious']),
            'science and nature': ('documentary score, ambient pads, marimba, organic textures', ['wonder and magical', 'calm and peaceful', 'mysterious and curious']),
            'self-help and business': ('modern ambient, light piano, soft electronic pulse', ['joyful and uplifting', 'calm and peaceful', 'triumphant and victorious']),
            'poetry': ('sparse piano, solo cello, intimate', ['calm and peaceful', 'melancholic and sad', 'romantic and tender'])
        }
        # set by generate_prompt() on its first call, or beforehand by the caller (e.g. a genre stored for the book)
        self.genre = None
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

    def generate_prompt(self, text:str, book_text:str|None=None)->str:
        self.load_model()
        threads = torch.get_num_threads()
        blas_threads = self.openblas.openblas_get_num_threads() if self.openblas is not None else None
        try:
            # the classifier runs on CPU: same core policy as MusicGen on CPU (see __init__)
            if self.raise_threads:
                torch.set_num_threads(os.cpu_count() or 1)
            elif self.openblas is not None:
                self.openblas.openblas_set_num_threads(os.cpu_count() or 1)
            if self.genre is None:
                # once per book: title, subject, description and its opening pages
                book_sample = ' '.join(str(book_text or text).split())[:2000]
                result = self.classifier(book_sample, list(self.genre_styles.keys()), hypothesis_template='This book belongs to the {} genre.', batch_size=8)
                self.genre = result['labels'][0]
                msg = f'Interludes: book genre detected as {self.genre}'
                print(msg)
            palette, favoured = self.genre_styles[self.genre]
            passage = ' '.join(str(text).split())[:1000]
            result = self.classifier(passage, list(self.moods.keys()), hypothesis_template='The mood of this passage is {}.', batch_size=8)
            family_scores = {label: score * (1.3 if label in favoured else 1.0) for label, score in zip(result['labels'], result['scores'])}
            family = max(family_scores, key=family_scores.get)
            result = self.classifier(passage, list(self.moods[family].keys()), hypothesis_template='This passage evokes {}.', batch_size=8)
            mood = result['labels'][0]
        finally:
            torch.set_num_threads(threads)
            if blas_threads is not None:
                self.openblas.openblas_set_num_threads(blas_threads)
        prompt = f'{self.moods[family][mood]}, {palette}, instrumental'
        self.prompt_info[prompt] = {'mood': mood, 'family': family, 'genre': self.genre, 'label': f'{mood} · {self.genre}'}
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
            guarded = [0]
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
            # attempt 1 only when attempt 0 failed: GPU failure -> CPU, or non-finite logits on CPU -> safe settings
            # (torch's own thread count, eager attention); autocast leaking from the caller is always switched off
            for attempt in range(2):
                step[0] = 0
                guarded[0] = 0
                if bar is not None:
                    bar.reset()
                try:
                    if self.torch_device == 'cpu' and not self.safe_mode:
                        # the e2a process runs torch on one thread (OMP_NUM_THREADS=1): MusicGen gets every core for this call only
                        if self.raise_threads:
                            torch.set_num_threads(os.cpu_count() or 1)
                        elif self.openblas is not None:
                            # pthreads OpenBLAS read OMP_NUM_THREADS=1 when it loaded: give its own pool every core instead
                            self.openblas.openblas_set_num_threads(os.cpu_count() or 1)
                    with torch.inference_mode(), torch.autocast(device_type='cuda' if self.torch_device == 'cuda' else 'cpu', enabled=False):
                        audio = self.model.generate(**inputs.to(self.torch_device), do_sample=True, guidance_scale=3.0, max_new_tokens=max_new_tokens, logits_processor=LogitsProcessorList([_finite_logits]), stopping_criteria=StoppingCriteriaList([_progress]))
                except Exception as e:
                    # a cancel stops generation mid-way and MusicGen may fail decoding the partial codes: that is not an error
                    if cancelled[0]:
                        break
                    if attempt == 1:
                        raise
                    audio = None
                    if self.torch_device != 'cpu':
                        print(f'Generation on {self.torch_device} failed ({e}), retrying on cpu...')
                        self.torch_device = 'cpu'
                        self.model = self.model.to('cpu', dtype=torch.float32)
                    else:
                        print(f'{desc} failed ({e}), retrying with safe settings...')
                        self.safe_mode = True
                        try:
                            self.model.set_attn_implementation('eager')
                        except Exception:
                            pass
                    continue
                finally:
                    torch.set_num_threads(threads)
                    if blas_threads is not None:
                        self.openblas.openblas_set_num_threads(blas_threads)
                # a couple of neutralized steps are harmless; more means the run is unreliable: redo it once in safe mode
                if cancelled[0] or attempt == 1 or self.torch_device != 'cpu' or guarded[0] <= max(2, max_new_tokens // 100):
                    break
                print(f'{desc}: {guarded[0]} steps produced non-finite logits, retrying with safe settings...')
                audio = None
                self.safe_mode = True
                try:
                    self.model.set_attn_implementation('eager')
                except Exception:
                    pass
            if guarded[0] and not cancelled[0]:
                print(f'{desc}: {guarded[0]} step(s) with non-finite logits were neutralized')
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
            # sidecar <name>.json keeps the prompt: the subtitles show it and the audiobook editor reopens it for regeneration
            with open(f'{root}.part.json', 'w', encoding='utf-8') as f:
                json.dump({'prompt': prompt, 'duration': duration, **self.prompt_info.get(prompt, {})}, f, ensure_ascii=False)
            os.replace(f'{root}.part.json', f'{root}.json')
            if bar is not None:
                bar.close()
                bar = None
            msg = f'Saved interlude to {output_path}'
            print(msg)
            return output_path
        except Exception as e:
            error = f'Interlude error: {e}'
            print(error)
            return None
        finally:
            if bar is not None:
                bar.close()
