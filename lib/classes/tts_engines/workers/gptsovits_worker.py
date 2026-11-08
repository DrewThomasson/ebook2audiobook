# Runs inside lib/classes/tts_engines/venvs/gptsovits, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": n, "version": "...", "needs_prompt": bool, ...} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "language", "voice", "file", "speed", "top_k", "top_p",
#              "temperature", "repetition_penalty"}
#   stdout <- {"ok": true, "file": "...", "samplerate": n, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
import os, sys, json, shutil, argparse, hashlib, subprocess, faulthandler

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--weights', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='large-v3-turbo')
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--models_dir', required=True)
    parser.add_argument('--ref_min', type=float, default=3.2)
    parser.add_argument('--ref_max', type=float, default=9.5)
    args = parser.parse_args()
    try:
        # upstream resolves GPT_SoVITS/pretrained_models/..., the sv and vocoder checkpoints and
        # GPT_SoVITS/configs from the working directory, and imports from both roots
        os.chdir(args.src)
        sys.path[:0] = [args.src, os.path.join(args.src, 'GPT_SoVITS')]
        os.makedirs(args.cache_dir, exist_ok=True)
        # upstream keeps its weights inside the tree: GPT_SoVITS/pretrained_models (fast_langdetect included) and
        # GPT_SoVITS/text/G2PWModel become links (junctions on windows: no symlink rights needed) to models/tts/gptsovits,
        # so every model sits in e2a's models folder. A real folder left by an older install is moved there once.
        # G2PWModel is linked only once it exists: upstream downloads it on first chinese use into the tree, and the
        # next start moves it over (a dangling link would make upstream's rename fail)
        for rel, name in ((os.path.join('GPT_SoVITS', 'pretrained_models'), 'pretrained_models'), (os.path.join('GPT_SoVITS', 'text', 'G2PWModel'), 'G2PWModel')):
            target = os.path.abspath(os.path.join(args.models_dir, name))
            linked = os.path.islink(rel) or getattr(os.path, 'isjunction', lambda path: False)(rel)
            if linked and os.path.realpath(rel) == os.path.realpath(target):
                continue
            if linked:
                os.rmdir(rel) if sys.platform == 'win32' else os.unlink(rel)
            elif os.path.isdir(rel):
                os.makedirs(target, exist_ok=True)
                for item in os.listdir(rel):
                    if not os.path.exists(os.path.join(target, item)):
                        shutil.move(os.path.join(rel, item), os.path.join(target, item))
                shutil.rmtree(rel, ignore_errors=True)
            if name == 'pretrained_models':
                os.makedirs(target, exist_ok=True)
            if os.path.isdir(target):
                if sys.platform == 'win32':
                    import _winapi
                    _winapi.CreateJunction(target, os.path.abspath(rel))
                else:
                    os.symlink(target, rel, target_is_directory=True)
        try:
            import jieba_fast
        except ImportError:
            # jieba_fast only exists as a C build; jieba has the same API, it is just slower
            import jieba, jieba.posseg
            sys.modules['jieba_fast'] = jieba
            sys.modules['jieba_fast.posseg'] = jieba.posseg
        import nltk
        # the english frontend tags with nltk; fetched once into NLTK_DATA (set by e2a, in the venv)
        for resource, package in (('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'), ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'), ('corpora/cmudict', 'cmudict')):
            try:
                nltk.data.find(resource)
            except LookupError:
                nltk.download(package, download_dir=os.environ.get('NLTK_DATA'), quiet=True)
        from huggingface_hub import snapshot_download
        # only this version's files; the HF repo layout is the pretrained_models layout
        snapshot_download(args.repo, local_dir=os.path.join('GPT_SoVITS', 'pretrained_models'), allow_patterns=[w for w in args.weights.split(',') if w])
        import re
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0, e.g. the jetson wheels):
            # upstream's module/distrib.py reads torch.distributed.ReduceOp at import and calls
            # is_initialized() at run time; single-process inference only needs them to exist
            import types
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        from TTS_infer_pack.TTS import TTS, TTS_Config
        device = args.device
        is_half = False
        if device == 'cuda' and torch.cuda.is_available():
            # upstream config.py: fp32 on sm 6.1 (Pascal) and on GTX 16xx, fp16 above
            major, minor = torch.cuda.get_device_capability(0)
            sm = major + minor / 10.0
            is_half = sm > 6.1 and not (re.search(r'16\d{2}', torch.cuda.get_device_name(0)) and sm == 7.5)
        tts = TTS(TTS_Config({'custom': {'version': args.version, 'device': device, 'is_half': is_half}}))
        # vocoder versions (v3/v4/v5) refuse an empty prompt_text: their references get transcribed
        needs_prompt = bool(tts.configs.use_vocoder)
        sampling_rate = int(tts.vocoder_configs['sr'] if tts.configs.use_vocoder else tts.configs.sampling_rate)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'version': args.version, 'needs_prompt': needs_prompt, 'device': str(tts.configs.device), 'half': is_half}) + '\n')
    refs = {}
    while True:
        raw = sys.stdin.buffer.readline()
        if not raw:
            break
        try:
            req = json.loads(raw)
        except Exception as e:
            proto.write(json.dumps({'ok': False, 'error': f'bad request: {e}', 'oom': False}) + '\n')
            continue
        if req.get('op') != 'tts':
            proto.write(json.dumps({'ok': False, 'error': f"unknown op {req.get('op')!r}", 'oom': False}) + '\n')
            continue
        try:
            voice = req['voice']
            voice_key = f'{voice}:{os.path.getmtime(voice)}'
            if voice_key not in refs:
                # upstream accepts 3-10 s references: keep at most ref_max, cutting at the quietest
                # 50 ms of the last 3 s so no word is clipped; pad short voices with silence
                clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                if not os.path.exists(clip):
                    data, sr = sf.read(voice, dtype='float32', always_2d=True)
                    mono = data.mean(axis=1)
                    max_len = int(args.ref_max * sr)
                    if len(mono) > max_len:
                        start = max(0, max_len - 3 * sr)
                        frame = int(0.05 * sr)
                        tail = mono[start:max_len]
                        energies = [float(np.mean(tail[i:i + frame] ** 2)) for i in range(0, len(tail) - frame, frame)]
                        mono = mono[:start + int(np.argmin(energies)) * frame + frame // 2] if energies else mono[:max_len]
                    min_len = int(args.ref_min * sr)
                    if len(mono) < min_len:
                        mono = np.concatenate([mono, np.zeros(min_len - len(mono), dtype=np.float32)])
                    sf.write(clip, mono, sr)
                prompt_text = ''
                prompt_lang = req['language']
                if needs_prompt:
                    # transcript cached beside the clip: the ASR runs once per voice, across runs too
                    transcript = clip[:-4] + '.json'
                    if os.path.exists(transcript):
                        with open(transcript, 'r', encoding='utf-8') as f:
                            cached = json.load(f)
                        prompt_text, prompt_lang = cached['text'], cached['language']
                    else:
                        # faster-whisper runs in its own short-lived process, as upstream's webui does:
                        # ctranslate2 bundles intel's openmp (libiomp5) and torch its own (libomp), and
                        # both in one process crash on macOS. cpu int8, once per voice (cached on disk).
                        # The clip is decoded here (soundfile) and handed over as 16 kHz mono float32: given an
                        # array, faster-whisper skips its own PyAV decoder, whose av.open(metadata_errors=...)
                        # breaks on PyAV >= 19 (faster-whisper 1.2.1 only requires av>=11).
                        # The model is fetched as plain files into its own folder (huggingface local_dir): the
                        # HF cache layout symlinks, and huggingface_hub 0.36's symlink probe races under
                        # faster-whisper's threaded download (WinError 1314 on Windows without symlink rights).
                        # Once model.bin is there, no download step runs at all.
                        asr_out = clip[:-4] + '.asr.json'
                        asr_dir = os.path.join(os.environ.get('HF_HOME') or args.cache_dir, f'faster-whisper-{args.asr_model}')
                        asr_script = '\n'.join([
                            'import os, sys, json, math',
                            'import numpy as np, soundfile as sf',
                            'from scipy.signal import resample_poly',
                            'from faster_whisper import WhisperModel',
                            'from faster_whisper.utils import download_model',
                            'clip, model_name, out, model_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]',
                            'if not os.path.exists(os.path.join(model_dir, "model.bin")):',
                            '    model_dir = download_model(model_name, output_dir=model_dir)',
                            'data, sr = sf.read(clip, dtype="float32", always_2d=True)',
                            'audio = data.mean(axis=1)',
                            'if sr != 16000:',
                            '    g = math.gcd(16000, sr)',
                            '    audio = resample_poly(audio, 16000 // g, sr // g)',
                            'audio = np.ascontiguousarray(audio, dtype=np.float32)',
                            'segments, info = WhisperModel(model_dir, device="cpu", compute_type="int8").transcribe(audio, beam_size=5)',
                            'text = "".join(segment.text for segment in segments).strip()',
                            'with open(out, "w", encoding="utf-8") as f:',
                            '    json.dump({"text": text, "language": info.language}, f, ensure_ascii=False)'
                        ])
                        asr_run = subprocess.run([sys.executable, '-c', asr_script, clip, args.asr_model, asr_out, asr_dir], stdout=subprocess.DEVNULL)
                        if asr_run.returncode != 0 or not os.path.exists(asr_out):
                            raise RuntimeError(f'reference transcription failed (exit code {asr_run.returncode})')
                        with open(asr_out, 'r', encoding='utf-8') as f:
                            asr_result = json.load(f)
                        os.unlink(asr_out)
                        prompt_text = asr_result['text']
                        prompt_lang = {'en': 'en', 'zh': 'zh', 'ja': 'ja', 'ko': 'ko', 'yue': 'yue'}.get(asr_result['language'])
                        if prompt_lang is None or not prompt_text:
                            raise ValueError(f"reference voice language {asr_result['language']!r} cannot be transcribed for {args.version} (supported: en, zh, ja, ko, yue)")
                        with open(transcript, 'w', encoding='utf-8') as f:
                            json.dump({'text': prompt_text, 'language': prompt_lang}, f, ensure_ascii=False)
                refs[voice_key] = (clip, prompt_text, prompt_lang)
            clip, prompt_text, prompt_lang = refs[voice_key]
            chunks = []
            out_sr = sampling_rate
            for out_sr, audio in tts.run({
                'text': req['text'],
                'text_lang': req['language'],
                'ref_audio_path': clip,
                'prompt_text': prompt_text,
                'prompt_lang': prompt_lang,
                'top_k': int(req.get('top_k', 15)),
                'top_p': float(req.get('top_p', 1.0)),
                'temperature': float(req.get('temperature', 1.0)),
                'repetition_penalty': float(req.get('repetition_penalty', 1.35)),
                'speed_factor': float(req.get('speed', 1.0)),
                # e2a already sends one sentence part: no further splitting, no batching
                'text_split_method': 'cut0',
                'batch_size': 1,
                'split_bucket': False,
                'return_fragment': False,
                'seed': -1
            }):
                chunks.append(audio)
            audio = np.concatenate(chunks).astype(np.float32) / 32768.0 if chunks else np.zeros(0, dtype=np.float32)
            sf.write(req['file'], audio, int(out_sr), subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': int(out_sr), 'samples': int(audio.shape[0])}
        except Exception as e:
            # no retry here: e2a's convert() returns False and core.py unloads the
            # engine, which closes stdin and ends this process.
            error = f'{type(e).__name__}: {e}'
            reply = {'ok': False, 'error': error, 'oom': 'out of memory' in error.lower()}
            try:
                if device == 'cuda':
                    torch.cuda.empty_cache()
                elif device == 'xpu':
                    torch.xpu.empty_cache()
            except Exception:
                pass
        proto.write(json.dumps(reply) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())