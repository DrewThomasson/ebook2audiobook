# Runs inside lib/classes/tts_engines/venvs/sparktts, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 16000, "device": "...", "dtype": "..."} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "voice", "file", "temperature", "top_k", "top_p", "tokens_per_char",
#              "max_new_tokens"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 16000, "samples": n, "capped": bool}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# Upstream's SparkTTS.inference (cli/SparkTTS.py), voice cloning prompt and token layout unchanged, with the reference
# tokenized once per voice instead of at every sentence and the LLM loaded in the device's dtype instead of fp32
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
    parser.add_argument('--repo', default='SparkAudio/Spark-TTS-0.5B')
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', required=True)
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--ref_max', type=float, default=10.0)
    parser.add_argument('--ref_languages', default='en,zh')
    args = parser.parse_args()
    try:
        os.makedirs(args.cache_dir, exist_ok=True)
        # upstream is not a package: sparktts is imported from the extracted repo root
        sys.path.insert(0, args.src)
        from huggingface_hub import snapshot_download
        # plain-folder download (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink probe races
        # under threaded downloads (WinError 1314 on windows without symlink rights). Complete once the marker exists:
        # config.yaml lands first, so a download cut during the weights would look finished forever; snapshot_download
        # resumes what is missing. The model only, not the repo's figures
        model_marker = os.path.join(args.model_dir, '.e2a_complete')
        if not os.path.exists(model_marker):
            snapshot_download(args.repo, local_dir=args.model_dir, allow_patterns=['config.yaml', 'BiCodec/*', 'LLM/*', 'wav2vec2-large-xlsr-53/*'])
            open(model_marker, 'w').close()
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS +vulkan
            # builds): upstream's residual_fsq.py imports torch.distributed and calls is_initialized() at run time;
            # single-process inference only needs them to exist
            import types
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        w2v_dir = os.path.join(args.model_dir, 'wav2vec2-large-xlsr-53')
        w2v_bin = os.path.join(w2v_dir, 'pytorch_model.bin')
        w2v_weights = os.path.join(w2v_dir, 'model.safetensors')
        if os.path.exists(w2v_bin):
            # transformers loads a .bin through torch.load only with torch >= 2.6 (CVE-2025-32434), which the older
            # torch builds e2a ships for some devices are not: the wav2vec2 weights are saved once as safetensors,
            # which transformers prefers and loads on any torch, and the .bin is dropped
            if not os.path.exists(w2v_weights):
                from safetensors.torch import save_file
                weights = torch.load(w2v_bin, map_location='cpu', weights_only=True)
                save_file({k: v.contiguous() for k, v in weights.items()}, f'{w2v_weights}.part', metadata={'format': 'pt'})
                os.replace(f'{w2v_weights}.part', w2v_weights)
                del weights
                gc.collect()
            os.unlink(w2v_bin)
        import soundfile as sf
        import soxr
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from sparktts.models.audio_tokenizer import BiCodecTokenizer
        from sparktts.utils.token_parser import TASK_TOKEN_MAP
        device = args.device
        dtype = torch.float32
        if device == 'cuda' and torch.cuda.is_available():
            # bf16 from sm 8.0 (and ROCm); fp32 below, and on mps / cpu: a 0.5B model fits anywhere in fp32, and
            # Qwen2's activations can overflow fp16
            major, _ = torch.cuda.get_device_capability(0)
            if torch.version.hip or major >= 8:
                dtype = torch.bfloat16
        elif device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
            dtype = torch.bfloat16 if getattr(torch.xpu, 'is_bf16_supported', lambda: True)() else torch.float32
        llm_dir = os.path.join(args.model_dir, 'LLM')
        tokenizer = AutoTokenizer.from_pretrained(llm_dir)
        # straight onto the GPU (device_map): no full host copy first, which a unified-memory jetson cannot spare
        model = AutoModelForCausalLM.from_pretrained(llm_dir, dtype=dtype, low_cpu_mem_usage=True, **({'device_map': 'cuda:0' if device == 'cuda' else device} if device != 'cpu' else {}))
        model.eval()
        eos = model.generation_config.eos_token_id
        eos_ids = set(eos if isinstance(eos, (list, tuple)) else [eos]) - {None}
        # BiCodec and wav2vec2 in fp32 on the model's device, as upstream runs them
        audio_device = torch.device('cuda:0' if device == 'cuda' else device)
        audio_tokenizer = BiCodecTokenizer(args.model_dir, device=audio_device)
        sampling_rate = int(audio_tokenizer.config['sample_rate'])
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(model.device), 'dtype': str(dtype).replace('torch.', '')}) + '\n')
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
                    # padding: BiCodec repeats a short reference itself for its speaker tokens, and silence would end
                    # up in the prompt's semantic tokens
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
                if ref_languages is None:
                    from transformers.models.whisper.tokenization_whisper import LANGUAGES
                    ref_languages = {LANGUAGES.get(code, code) for code in args.ref_languages.split(',') if code}
                # upstream's cloning prompt carries the reference's text and semantic tokens when the text is known
                # ("recommended for cloning in the same language"): a reference in a language Spark-TTS does not
                # speak, or without speech, clones from its speaker tokens alone
                prompt_text = ref_text if ref_text and (ref_language is None or ref_language in ref_languages) else None
                if prompt_text is None:
                    print(f'sparktts_worker: the voice reference {voice} is cloned from its speaker tokens alone (no speech in {sorted(ref_languages)} heard: {ref_language or "none"})', file=sys.stderr)
                with torch.inference_mode():
                    global_ids, semantic_ids = audio_tokenizer.tokenize(clip)
                global_tokens = ''.join(f'<|bicodec_global_{i}|>' for i in global_ids.reshape(-1).tolist())
                # upstream's process_prompt: task, content (reference text then the sentence, joined as is), speaker
                # tokens, then the reference's semantic tokens the generation continues from
                prompt_head = TASK_TOKEN_MAP['tts'] + '<|start_content|>' + (prompt_text or '')
                prompt_tail = '<|end_content|><|start_global_token|>' + global_tokens + '<|end_global_token|>'
                if prompt_text:
                    prompt_tail += '<|start_semantic_token|>' + ''.join(f'<|bicodec_semantic_{i}|>' for i in semantic_ids.reshape(-1).tolist())
                refs[voice_key] = (prompt_head, prompt_tail, global_ids)
                del semantic_ids
            prompt_head, prompt_tail, global_ids = refs[voice_key]
            text = req['text'].strip()
            model_inputs = tokenizer([prompt_head + text + prompt_tail], return_tensors='pt').to(model.device)
            # generation cap: tokens_per_char per character, a Han / kana / Hangul character counted as 3 (a whole
            # syllable), at least 5 s of speech, at most max_new_tokens
            text_units = len(text) + 2 * len(re.findall(r'[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿]', text))
            max_new_tokens = min(int(req.get('max_new_tokens', 3000)), max(250, text_units * int(req.get('tokens_per_char', 10))))
            with torch.inference_mode():
                output = model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=float(req.get('temperature', 0.8)),
                    top_k=int(req.get('top_k', 50)),
                    top_p=float(req.get('top_p', 0.95)),
                    pad_token_id=tokenizer.pad_token_id
                )
            generated = output[0, model_inputs['input_ids'].shape[1]:].tolist()
            del output, model_inputs
            capped = len(generated) >= max_new_tokens and not eos_ids.intersection(generated)
            if capped:
                print(f'sparktts_worker: no end of speech within {max_new_tokens} tokens (cap reached: a loop, or a cap too low for this text), the part is cut there: {text[:80]}', file=sys.stderr)
            semantic = [int(token) for token in re.findall(r'bicodec_semantic_(\d+)', tokenizer.decode(generated, skip_special_tokens=True))]
            if not semantic:
                raise ValueError(f'no audio tokens generated for: {text[:80]}')
            with torch.inference_mode():
                audio = audio_tokenizer.detokenize(global_ids.to(audio_device).squeeze(0), torch.tensor([semantic], dtype=torch.long, device=audio_device))
            audio = np.asarray(audio, dtype=np.float32).reshape(-1)
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
