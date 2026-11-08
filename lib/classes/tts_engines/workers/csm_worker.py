# Runs inside lib/classes/tts_engines/venvs/csm, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "...", "dtype": "...", "watermark": bool} once loaded
#             {"ready": false, "error": "...", "gated": bool, "repo": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "voice", "file", "temperature", "top_k", "tokens_per_char", "max_new_tokens"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n, "capped": bool}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# Upstream's Generator.generate (generator.py) through transformers' CsmForConditionalGeneration (upstream's own code needs
# torchtune / moshi and the gated Llama tokenizer): the voice file is the one context segment (speaker 0: its transcript,
# then its Mimi frames and the audio EOS frame) and the sentence the next segment of the same speaker, sampled with
# upstream's temperature / top-k for every codebook. The reference is cut and transcribed once per voice instead of being
# passed at every sentence, Mimi runs in fp32 as moshi runs it, and upstream's silentcipher watermark marks the result
import os, sys, re, json, argparse, hashlib, gc, faulthandler

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True)
    parser.add_argument('--repo', default='unsloth/csm-1b')
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', required=True)
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--ref_max', type=float, default=10.0)
    parser.add_argument('--ref_languages', default='en')
    parser.add_argument('--silentcipher', default='')
    parser.add_argument('--silentcipher_type', default='44.1k')
    parser.add_argument('--silentcipher_ckpt', default='44_1_khz/73999_iteration')
    parser.add_argument('--silentcipher_dir', default='')
    args = parser.parse_args()
    try:
        os.makedirs(args.cache_dir, exist_ok=True)
        from huggingface_hub import snapshot_download
        from huggingface_hub.errors import GatedRepoError
        repo = args.repo
        try:
            # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink probe
            # races under threaded downloads (WinError 1314 on windows without symlink rights). Complete once the
            # marker exists: config.json lands first, so a download cut during the weights would look finished forever;
            # snapshot_download resumes what is missing. The transformers checkpoint only: sesame/csm-1b also carries
            # upstream's own ckpt.pt (6 GB) and its prompt wavs
            model_marker = os.path.join(args.model_dir, '.e2a_complete')
            if not os.path.exists(model_marker):
                snapshot_download(args.repo, local_dir=args.model_dir, allow_patterns=['*.json', '*.safetensors', '*.jinja'])
                open(model_marker, 'w').close()
            if args.silentcipher:
                # the watermark model's checkpoint folder only, same marker rule
                repo = args.silentcipher
                watermark_marker = os.path.join(args.silentcipher_dir, '.e2a_complete')
                if not os.path.exists(watermark_marker):
                    snapshot_download(args.silentcipher, local_dir=args.silentcipher_dir, allow_patterns=[f'{args.silentcipher_ckpt}/*'])
                    open(watermark_marker, 'w').close()
        except GatedRepoError as e:
            # e2a turns this into its own alert (accept the conditions, set HF_TOKEN)
            proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}', 'gated': True, 'repo': repo}) + '\n')
            return 1
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS +vulkan
            # builds): single-process inference only needs these to exist for accelerate / transformers imports
            import types
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        import soxr
        from transformers import AutoProcessor, CsmForConditionalGeneration
        from transformers.utils import logging as transformers_logging
        device = args.device
        dtype = torch.float32
        if device == 'cuda' and torch.cuda.is_available():
            # bf16 from sm 8.0 (and ROCm), the dtype upstream runs; else fp16, but fp32 on sm 6.1 (Pascal) and on
            # GTX 16xx (the rule e2a's other engines use)
            major, minor = torch.cuda.get_device_capability(0)
            sm = major + minor / 10.0
            if torch.version.hip or sm >= 8.0:
                dtype = torch.bfloat16
            elif sm > 6.1 and not (re.search(r'16\d{2}', torch.cuda.get_device_name(0)) and sm == 7.5):
                dtype = torch.float16
        elif device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
            dtype = torch.bfloat16 if getattr(torch.xpu, 'is_bf16_supported', lambda: True)() else torch.float16
        elif device == 'mps':
            dtype = torch.float16
        processor = AutoProcessor.from_pretrained(args.model_dir)
        # straight onto the GPU (device_map): no full host copy first, which a unified-memory jetson cannot spare;
        # sesame's checkpoint is fp32 on disk and cast while loading
        model = CsmForConditionalGeneration.from_pretrained(args.model_dir, dtype=dtype, low_cpu_mem_usage=True, **({'device_map': 'cuda:0' if device == 'cuda' else device} if device != 'cpu' else {}))
        model.eval()
        if dtype != torch.float32:
            # Mimi in fp32, as upstream runs it (moshi's loader, beside the bf16 backbone): cast back, and its weights
            # read again from the checkpoint so they are not their own bf16 / fp16 rounding. transformers renames Mimi
            # keys while loading, so each weight is found by its shape and rounded values rather than its name; one not
            # found keeps its cast-back value
            codec_model = model.codec_model.to(torch.float32)
            from safetensors import safe_open
            originals = {}
            for name in sorted(os.listdir(args.model_dir)):
                if not name.endswith('.safetensors'):
                    continue
                with safe_open(os.path.join(args.model_dir, name), framework='pt', device='cpu') as weights:
                    for key in weights.keys():
                        if key.startswith('codec_model.'):
                            weight = weights.get_tensor(key)
                            if weight.is_floating_point():
                                weight = weight.float()
                                originals[(tuple(weight.shape), hashlib.sha1(weight.to(dtype).float().numpy().tobytes()).hexdigest())] = weight
            with torch.no_grad():
                for tensor in list(codec_model.parameters()) + list(codec_model.buffers()):
                    if tensor.is_floating_point():
                        weight = originals.get((tuple(tensor.shape), hashlib.sha1(tensor.detach().cpu().numpy().tobytes()).hexdigest()))
                        if weight is not None:
                            tensor.copy_(weight)
            # the codebooks cache their embedding on first use: rebuilt from the fp32 buffers
            for module in codec_model.modules():
                if getattr(module, '_embed', None) is not None:
                    module._embed = None
            del originals
            gc.collect()
        sampling_rate = int(processor.feature_extractor.sampling_rate)
        # the backbone's positions hold the whole prompt and the generated frames (upstream's max_seq_len)
        max_positions = int(getattr(model.config, 'max_position_embeddings', 2048))
        watermarker = None
        if args.silentcipher:
            # upstream's own watermarking.py (its public CSM_1B_GH_WATERMARK key and watermark()), loaded from the
            # extracted tree by path: the tree root also has generic module names (models, generator); the watermark
            # model from its plain folder instead of upstream's load_watermarker(), which fetches it into the HF cache
            import importlib.util
            spec = importlib.util.spec_from_file_location('csm_watermarking', os.path.join(args.src, 'watermarking.py'))
            watermarking = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(watermarking)
            import silentcipher
            import torchaudio
            ckpt_path = os.path.join(args.silentcipher_dir, args.silentcipher_ckpt)
            watermarker = silentcipher.get_model(model_type=args.silentcipher_type, ckpt_path=ckpt_path, config_path=os.path.join(ckpt_path, 'hparams.yaml'), device=str(model.device))
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}', 'gated': False}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(model.device), 'dtype': str(dtype).replace('torch.', ''), 'watermark': watermarker is not None}) + '\n')
    ref_languages = None
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
            # the reference window is part of the clip
            voice_key = f'{voice}:{os.path.getmtime(voice)}:{args.ref_max}'
            if voice_key not in refs:
                clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                if not os.path.exists(clip):
                    # keep at most ref_max, cutting at the quietest 50 ms of the last 3 s so no word is clipped; no
                    # padding: the context frames are the reference as is, silence would be part of the voice
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
                # the transcript and the language Whisper heard are kept beside the clip: Whisper runs once per voice, ever
                transcript = f'{clip[:-4]}.json'
                if os.path.exists(transcript):
                    with open(transcript, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                    ref_text, ref_language = cached['text'], cached['language']
                else:
                    # Whisper on cpu (no VRAM taken from the model), downloaded as a plain folder, language left to
                    # Whisper: the voice is often not in the book's language; released after. Complete once the
                    # marker exists: config.json lands first, so a download cut during the 1.6 GB weights would look
                    # finished forever; snapshot_download resumes what is missing
                    asr_marker = os.path.join(args.asr_dir, '.e2a_complete')
                    if not os.path.exists(asr_marker):
                        snapshot_download(args.asr_model, local_dir=args.asr_dir)
                        open(asr_marker, 'w').close()
                    from transformers import pipeline
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
                if ref_languages is None:
                    from transformers.models.whisper.tokenization_whisper import LANGUAGES
                    ref_languages = {LANGUAGES.get(code, code) for code in args.ref_languages.split(',') if code}
                # a context segment is always text and audio: a reference in another language keeps the transcript
                # Whisper heard (its true text), one without speech an empty text
                if ref_language is not None and ref_language not in ref_languages:
                    print(f'csm_worker: the voice reference {voice} speaks {ref_language}, not {sorted(ref_languages)}: CSM may carry its accent or language over', file=sys.stderr)
                data, sr = sf.read(clip, dtype='float32')
                ref_audio = np.ascontiguousarray(soxr.resample(data, sr, sampling_rate) if sr != sampling_rate else data, dtype=np.float32)
                refs[voice_key] = (ref_text, ref_audio)
            ref_text, ref_audio = refs[voice_key]
            text = req['text'].strip()
            tokenizer = processor.tokenizer
            # upstream's segments as transformers' chat template writes them: <bos>[speaker]text<eos>, then the audio
            # frames and the audio EOS frame for a segment that has audio
            prompt = f'{tokenizer.bos_token}[0]{ref_text}{tokenizer.eos_token}{processor.audio_token}{processor.audio_eos_token}{tokenizer.bos_token}[0]{text}{tokenizer.eos_token}'
            inputs = processor(text=[prompt], audio=[ref_audio], return_tensors='pt').to(model.device)
            # generation cap: tokens_per_char frames per character, at least 5 s of speech, at most max_new_tokens and
            # what the backbone's positions leave after the prompt (upstream refuses a prompt that leaves less)
            room = max_positions - int(inputs['input_ids'].shape[1])
            max_new_tokens = min(int(req.get('max_new_tokens', 1125)), max(63, len(text) * int(req.get('tokens_per_char', 3))), room)
            if max_new_tokens <= 0:
                raise ValueError(f'the voice reference and the sentence fill the {max_positions} positions of the model: {text[:80]}')
            temperature = float(req.get('temperature', 0.9))
            top_k = int(req.get('top_k', 50))
            verbosity = transformers_logging.get_verbosity()
            # CSM's generate warns at every call about the stopping criteria it ignores
            transformers_logging.set_verbosity_error()
            try:
                with torch.inference_mode():
                    # upstream samples every codebook with the same top-k / temperature, no top-p
                    output = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,
                        temperature=temperature,
                        top_k=top_k,
                        top_p=1.0,
                        depth_decoder_do_sample=True,
                        depth_decoder_temperature=temperature,
                        depth_decoder_top_k=top_k,
                        depth_decoder_top_p=1.0
                    )
            finally:
                transformers_logging.set_verbosity(verbosity)
            # the generated frames only (batch, frames, codebooks), cut at the first all-EOS frame as transformers'
            # output_audio does
            frames = output[0]
            del output, inputs
            eos_idxs = (frames == model.config.codebook_eos_token_id).all(dim=-1).nonzero()
            capped = eos_idxs.numel() == 0 and frames.shape[0] >= max_new_tokens
            if eos_idxs.numel() != 0:
                frames = frames[:int(eos_idxs.min())]
            if capped:
                print(f'csm_worker: no end of speech within {max_new_tokens} frames (cap reached: a loop, or a cap too low for this text), the part is cut there: {text[:80]}', file=sys.stderr)
            if frames.shape[0] == 0:
                raise ValueError(f'no audio frames generated for: {text[:80]}')
            with torch.inference_mode():
                audio = model.codec_model.decode(frames.transpose(0, 1).unsqueeze(0)).audio_values[0, 0].float()
                if watermarker is not None:
                    # upstream's own call (generator.py), back at Mimi's rate after
                    audio, watermark_rate = watermarking.watermark(watermarker, audio, sampling_rate, watermarking.CSM_1B_GH_WATERMARK)
                    audio = torchaudio.functional.resample(audio, orig_freq=watermark_rate, new_freq=sampling_rate)
            audio = audio.cpu().numpy().astype(np.float32).reshape(-1)
            del frames
            sf.write(req['file'], audio, sampling_rate, subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': sampling_rate, 'samples': int(audio.shape[0]), 'capped': capped}
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
