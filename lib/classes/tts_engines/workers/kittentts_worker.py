# Runs inside lib/classes/tts_engines/venvs/kittentts, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "...", "dtype": "...", "family": "...", "voices": [...]} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "speaker", "voice", "file", "preset", "max_new_tokens", "speed"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# KittenTTS 2 through upstream's own classes (kittenml), one model per worker:
#   family kitten2: KittenTTS2, the speech LM + s3gen. "speaker" is a built-in voice, "voice" a voice file it clones
#     (the reference is cut and transcribed once per voice: upstream's own transcriber forces English)
#   family tiny: KittenTTS2Tiny (mini / nano / pico), ONNX on cpu or its fp32 weights in torch on cuda. "speaker" only:
#     e2a converts the output to a voice file itself (default_vc_model)
import os, sys, json, types, argparse, hashlib, gc, faulthandler

def plain_folder(repo:str, local_dir:str, marker:str, patterns:list)->None:
    # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink probe races under
    # threaded downloads (WinError 1314 on windows without symlink rights). Complete once the marker exists: config.json
    # lands first, so a download cut during the weights would look finished forever; snapshot_download resumes what is
    # missing
    from huggingface_hub import snapshot_download
    marker_file = os.path.join(local_dir, marker)
    if not os.path.exists(marker_file):
        snapshot_download(repo, local_dir=local_dir, allow_patterns=patterns)
        open(marker_file, 'w').close()

def read_config(repo:str, local_dir:str)->dict:
    from huggingface_hub import hf_hub_download
    config_file = os.path.join(local_dir, 'config.json')
    if not os.path.exists(config_file):
        hf_hub_download(repo, 'config.json', local_dir=local_dir)
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # same for fd 0, the request stream: upstream code reading stdin meets EOF instead of eating requests
    requests = os.fdopen(os.dup(0), 'rb')
    null_fd = os.open(os.devnull, os.O_RDONLY)
    os.dup2(null_fd, 0)
    os.close(null_fd)
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--family', required=True, choices=['kitten2', 'tiny'])
    parser.add_argument('--repo', required=True)
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--language', default='en')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--weights', default='')
    parser.add_argument('--decoder', default='default')
    parser.add_argument('--normalize', type=int, default=1)
    parser.add_argument('--s3gen_repo', default='ResembleAI/chatterbox-turbo')
    parser.add_argument('--s3gen_file', default='s3gen_meanflow.safetensors')
    parser.add_argument('--s3gen_dir', default='')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', default='')
    parser.add_argument('--cache_dir', default='')
    parser.add_argument('--ref_max', type=float, default=15.0)
    parser.add_argument('--ref_languages', default='en')
    args = parser.parse_args()
    # one short sentence per tiny model language, spoken once at load
    warmup_texts = {'en': 'Hello.', 'de': 'Hallo.', 'es': 'Hola.', 'it': 'Ciao.', 'pt': 'Olá.', 'ru': 'Привет.', 'hi': 'नमस्ते।', 'fr': 'Bonjour.', 'da': 'Hej.', 'fi': 'Hei.', 'ko': '안녕하세요.', 'nl': 'Hallo.', 'sv': 'Hej.', 'sw': 'Habari.', 'tr': 'Merhaba.'}
    try:
        config = read_config(args.repo, args.model_dir)
        device = args.device
        if args.family == 'kitten2':
            # the files the config points at for this weight packing and decoder only (upstream's own selection): the
            # repository also carries kitten-tts-2-cpp's GGUF and TorchScript decoders, ~2.5 GB nobody here reads
            from kittenml.get_model import _kitten2_files
            plain_folder(args.repo, args.model_dir, f'.e2a_complete-{args.weights}-{args.decoder}', _kitten2_files(config, args.decoder, args.weights))
            # s3gen's weights as a plain file, handed to kittenml in place of its own hf_hub_download into the HF cache
            # (hf_hub_download with local_dir moves the file in place once complete)
            from huggingface_hub import hf_hub_download
            s3gen_path = os.path.join(args.s3gen_dir, args.s3gen_file)
            if not os.path.exists(s3gen_path):
                hf_hub_download(args.s3gen_repo, args.s3gen_file, local_dir=args.s3gen_dir)
        else:
            # config.json, the vocab, this language's graph (ONNX for the weight format, or the fp32 safetensors for torch)
            # and its voices; the english CMUdict lexicon and BART G2P for english only
            entry = config['languages'][args.language]
            model_file = entry['weights_file'] if device == 'cuda' else (entry.get('model_files') or {'int8': entry['model_file']})[args.weights]
            g2p_dir = config.get('g2p_dir', 'g2p')
            patterns = ['config.json', config.get('vocab', 'vocab.json'), model_file, entry['voices']] + ([f'{g2p_dir}/*', f'{g2p_dir}/**'] if args.language == 'en' else [])
            plain_folder(args.repo, args.model_dir, f'.e2a_complete-{args.language}-{os.path.basename(model_file)}', patterns)
        import numpy as np
        import torch
        # E2A_XPU_UNUSABLE: e2a found torch xpu cannot run on this Intel GPU (unsupported iGPU, driver too old). Its
        # device count is a Windows access violation in the SYCL runtime, and transformers asks it at import, CPU
        # sessions included. Set here too: a distro python's own sitecustomize.py comes first and hides the venv's copy
        if os.environ.get('E2A_XPU_UNUSABLE') == '1' and hasattr(torch, 'xpu'):
            torch.xpu.device_count = lambda: 0
            torch.xpu.is_available = lambda: False
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS +vulkan
            # builds): single-process inference only needs these to exist for the transformers / diffusers imports
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        dtype = 'float32'
        if args.family == 'kitten2':
            from kittenml.kittentts2 import KittenTTS2, vocoder
            upstream_download = vocoder.hf_hub_download
            vocoder.hf_hub_download = lambda repo_id, filename, **kwargs: s3gen_path if (repo_id, filename) == (args.s3gen_repo, args.s3gen_file) else upstream_download(repo_id=repo_id, filename=filename, **kwargs)
            # the LM in bf16, as upstream runs it (its config's dtype), where the device has it: from sm 8.0 and ROCm,
            # Intel GPUs reporting it, mps and cpu. Elsewhere fp32: the loader hands bf16 tensors over whatever the
            # config says, so the model is cast once loaded
            use_bf16 = True
            if device == 'cuda' and torch.cuda.is_available():
                use_bf16 = bool(torch.version.hip) or torch.cuda.get_device_capability(0)[0] >= 8
            elif device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
                use_bf16 = getattr(torch.xpu, 'is_bf16_supported', lambda: True)()
            model = KittenTTS2(args.model_dir, config, device=device, decoder=args.decoder, weights=args.weights)
            if not use_bf16 and model.dtype != torch.float32:
                model.model.to(torch.float32)
                model.dtype = torch.float32
            dtype = str(model.dtype).replace('torch.', '')
            # the transcript of a voice file always comes from here: upstream's own transcriber would download
            # whisper-large-v3 into the HF cache and read every reference as English
            def no_transcriber(wav_path:str)->str:
                raise ValueError(f'no transcript for the voice reference {wav_path}')
            model.transcriber = no_transcriber
            voices = model.available_voices
        else:
            from kittenml.kittentts2_tiny import KittenTTS2Tiny
            if device == 'cuda':
                # the fp32 weights in torch, as upstream's training code runs them
                model = KittenTTS2Tiny(args.model_dir, backend='torch', device='cuda')
            else:
                # ONNX Runtime on cpu, upstream's default (no GPU provider in the venv)
                device = 'cpu'
                model = KittenTTS2Tiny(args.model_dir, device='cpu', weights=args.weights)
                dtype = args.weights
            voices = model.available_voices.get(args.language, [])
            # the language's frontend (espeak-ng, or misaki + spaCy + the BART G2P for english) loads now, and any
            # frontend error shows as a load error instead of failing the first sentence
            model.generate(warmup_texts.get(args.language, 'Hello.'), language=args.language)
        sampling_rate = int(model.sample_rate)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': device, 'dtype': dtype, 'family': args.family, 'voices': voices}) + '\n')
    ref_languages = None
    refs = {}
    while True:
        raw = requests.readline()
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
            text = req['text'].strip()
            if args.family == 'kitten2':
                voice = req.get('voice')
                if voice:
                    # the reference window is part of the clip
                    voice_key = f'{voice}:{os.path.getmtime(voice)}:{args.ref_max}'
                    if voice_key not in refs:
                        os.makedirs(args.cache_dir, exist_ok=True)
                        clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                        if not os.path.exists(clip):
                            # keep at most ref_max, cutting at the quietest 50 ms of the last 3 s so no word is clipped;
                            # no padding: s3gen tiles a short reference itself (silence would degrade its timbre estimate)
                            data, sr = sf.read(voice, dtype='float32', always_2d=True)
                            mono = data.mean(axis=1)
                            max_len = int(args.ref_max * sr)
                            if len(mono) > max_len:
                                start = max(0, max_len - 3 * sr)
                                frame = int(0.05 * sr)
                                tail = mono[start:max_len]
                                energies = [float(np.mean(tail[i:i + frame] ** 2)) for i in range(0, len(tail) - frame, frame)]
                                mono = mono[:start + int(np.argmin(energies)) * frame + frame // 2] if energies else mono[:max_len]
                            sf.write(clip, mono, sr)
                        # the transcript and the language Whisper heard are kept beside the clip: Whisper runs once per
                        # voice, ever
                        transcript = f'{clip[:-4]}.json'
                        if os.path.exists(transcript):
                            with open(transcript, 'r', encoding='utf-8') as f:
                                cached = json.load(f)
                            ref_text, ref_language = cached['text'], cached['language']
                        else:
                            # Whisper on cpu (no VRAM taken from the model), downloaded as a plain folder, language left
                            # to Whisper: the voice is often not in the book's language; released after
                            plain_folder(args.asr_model, args.asr_dir, '.e2a_complete', None)
                            import soxr
                            from transformers import pipeline
                            from transformers.utils import logging as transformers_logging
                            # the clip is handed over decoded and at Whisper's 16 kHz: a file path would go through ffmpeg
                            data, sr = sf.read(clip, dtype='float32')
                            audio_16k = soxr.resample(data, sr, 16000) if sr != 16000 else data
                            verbosity = transformers_logging.get_verbosity()
                            transformers_logging.set_verbosity_error()
                            asr_pipe = None
                            try:
                                asr_pipe = pipeline('automatic-speech-recognition', model=args.asr_dir, device='cpu')
                                result = asr_pipe({'raw': np.ascontiguousarray(audio_16k, dtype=np.float32), 'sampling_rate': 16000}, generate_kwargs={'task': 'transcribe'}, return_language=True)
                            finally:
                                del asr_pipe
                                transformers_logging.set_verbosity(verbosity)
                                gc.collect()
                            ref_text = result['text'].strip()
                            ref_language = (result.get('chunks') or [{}])[0].get('language')
                            with open(transcript, 'w', encoding='utf-8') as f:
                                json.dump({'text': ref_text, 'language': ref_language}, f, ensure_ascii=False)
                        if not ref_text:
                            raise ValueError(f'no speech found in the voice reference {voice}')
                        if ref_languages is None:
                            from transformers.models.whisper.tokenization_whisper import LANGUAGES
                            ref_languages = {LANGUAGES.get(code, code) for code in args.ref_languages.split(',') if code}
                        # upstream: the voice carries the language (accent, phonotactics)
                        if ref_language is not None and ref_language not in ref_languages:
                            print(f'kittentts_worker: the voice reference {voice} speaks {ref_language}, not {sorted(ref_languages)}: KittenTTS 2 may carry its accent or language over', file=sys.stderr)
                        refs[voice_key] = (clip, ref_text)
                    clip, ref_text = refs[voice_key]
                    speaker = {'reference': clip, 'reference_text': ref_text}
                else:
                    speaker_name = req.get('speaker') or config.get('default_voice')
                    if speaker_name not in model.voices:
                        raise ValueError(f'voice {speaker_name!r} not in {args.repo}: {model.available_voices}')
                    speaker = {'voice': speaker_name}
                audio = model.generate(text, preset=req.get('preset') or None, max_new_tokens=int(req.get('max_new_tokens', 1000)), normalize=bool(args.normalize), **speaker)
            else:
                audio = model.generate(text, voice=req.get('speaker') or None, language=args.language, speed=float(req.get('speed', 1.0)))
            audio = np.asarray(audio, dtype=np.float32).reshape(-1)
            if audio.shape[0] == 0:
                raise ValueError(f'no audio generated for: {text[:80]}')
            sf.write(req['file'], audio, sampling_rate, subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': sampling_rate, 'samples': int(audio.shape[0])}
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
                elif device == 'mps':
                    torch.mps.empty_cache()
            except Exception:
                pass
        proto.write(json.dumps(reply) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
