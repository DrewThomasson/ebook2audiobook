# Runs inside lib/classes/tts_engines/venvs/chattts, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "..."} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "ref", "voice"}: prepares the voice file's clone prompt
#   stdout <- {"ok": true, "cloned": bool, "language": "..." | null}: cloned false when ChatTTS cannot clone it, language
#             the one Whisper heard (null: no speech)
#   stdin  -> {"op": "tts", "text", "voice", "file", "language", "temperature", "top_k", "top_p", "repetition_penalty",
#              "speed", "tokens_per_char", "max_new_tokens"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n, "capped": bool}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# Upstream's Chat.infer (ChatTTS/core.py), text refinement off: the book text is read as written, never rewritten with
# the fillers, laughs and pauses the refine pass adds. The voice file is cloned as upstream's webui does (its DVAE
# codes as spk_smp, its transcript as txt_smp), with the reference encoded and transcribed once per voice instead of
# at every sentence. A voice it cannot clone (no English or Chinese speech in it) is refused: e2a stops there
import os, sys, re, json, argparse, hashlib, gc, logging, faulthandler

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
    parser.add_argument('--repo', default='2Noise/ChatTTS')
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
        # imported from the extracted repo root, not from an installed package
        sys.path.insert(0, args.src)
        from huggingface_hub import snapshot_download
        # plain-folder download (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink probe races
        # under threaded downloads (WinError 1314 on windows without symlink rights). Complete once the marker exists:
        # the json files land first, so a download cut during the weights would look finished forever; snapshot_download
        # resumes what is missing. Upstream's own patterns (Chat.download_models, source "huggingface")
        model_marker = os.path.join(args.model_dir, '.e2a_complete')
        if not os.path.exists(model_marker):
            snapshot_download(args.repo, local_dir=args.model_dir, allow_patterns=['*.yaml', '*.json', '*.safetensors'])
            open(model_marker, 'w').close()
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS builds):
            # vector_quantize_pytorch (ChatTTS' DVAE quantizer) imports torch.distributed.nn, which takes group and
            # ReduceOp from torch.distributed and asks torch.distributed.rpc whether it is available, and its
            # residual_fsq.py calls is_initialized() at run time; single-process inference only needs them to exist
            import types
            try:
                # importable without distributed support, it then reports itself unavailable
                import torch.distributed.rpc
            except Exception:
                torch.distributed.rpc = types.SimpleNamespace(is_available=lambda: False)
            for attr, value in (('group', types.SimpleNamespace(WORLD=None)), ('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        import soxr
        import ChatTTS
        import ChatTTS.model.gpt as chattts_gpt
        # upstream's warnings reach e2a's log, except the one its text normalizer gives for every sentence holding a
        # character it drops (quotes, question marks...); its info lines (homophone replacements) stay out
        logger = logging.getLogger('ChatTTS')
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setFormatter(logging.Formatter('chattts_worker: %(message)s'))
        log_handler.addFilter(lambda record: not record.getMessage().startswith('found invalid characters'))
        logger.addHandler(log_handler)
        device = args.device
        # every model in fp32, as upstream runs them; on mps upstream itself keeps the GPT and Vocos on the cpu
        model_device = torch.device('cuda:0' if device == 'cuda' else device)
        if model_device.type in ('cuda', 'xpu'):
            # upstream builds the GPT on the host, then copies it to the device: two fp32 copies at once, which a
            # unified-memory jetson cannot spare. Loaded straight onto the device instead (device_map, as the Orpheus
            # and Spark-TTS workers do), upstream's .to() after it is then a no-op. Not on mps: upstream keeps the GPT
            # on the cpu there
            upstream_llama = chattts_gpt.LlamaModel

            class LlamaOnDevice(upstream_llama):
                @classmethod
                def from_pretrained(cls, *args, **kwargs):
                    return upstream_llama.from_pretrained(*args, **{'device_map': str(model_device), 'low_cpu_mem_usage': True, **kwargs})

            chattts_gpt.LlamaModel = LlamaOnDevice
        chat = ChatTTS.Chat(logger)
        # source "custom": the folder above, checked against upstream's sha256 map, so a broken or changed file stops
        # here instead of speaking noise
        if not chat.load(source='custom', custom_path=args.model_dir, device=model_device, compile=False):
            raise RuntimeError(f'the ChatTTS files in {args.model_dir} do not match upstream\'s checksums: delete that folder to download them again')
        sampling_rate = int(chat.config.vocos.feature_extractor.init_args.sample_rate)
        # the host copies the other models were loaded through, back to the system before the first sentence
        gc.collect()
        if model_device.type == 'cuda':
            torch.cuda.empty_cache()
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(model_device)}) + '\n')

    class CapFlag(logging.Handler):
        # upstream reports a generation that ended on max_new_token through its logger only
        def emit(self, record:logging.LogRecord)->None:
            if record.getMessage().startswith('incomplete result'):
                self.hit = True

    cap_flag = CapFlag()
    logger.addHandler(cap_flag)
    ref_languages = None
    refs = {}

    def prepare(voice:str)->dict:
        # the voice file's clone prompt, made once per voice: cut, transcribed, encoded
        nonlocal ref_languages
        # the reference window is part of the clip
        voice_key = f'{voice}:{os.path.getmtime(voice)}:{args.ref_max}'
        if voice_key in refs:
            return refs[voice_key]
        clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
        if not os.path.exists(clip):
            # keep at most ref_max, cutting at the quietest 50 ms of the last 3 s so no word is clipped; mono at
            # the model's rate, what the DVAE encoder takes (upstream's load_audio)
            data, sr = sf.read(voice, dtype='float32', always_2d=True)
            mono = data.mean(axis=1)
            max_len = int(args.ref_max * sr)
            if len(mono) > max_len:
                start = max(0, max_len - 3 * sr)
                frame = int(0.05 * sr)
                tail = mono[start:max_len]
                energies = [float(np.mean(tail[i:i + frame] ** 2)) for i in range(0, len(tail) - frame, frame)]
                mono = mono[:start + int(np.argmin(energies)) * frame + frame // 2] if energies else mono[:max_len]
            if sr != sampling_rate:
                mono = soxr.resample(mono, sr, sampling_rate)
            sf.write(clip, mono, sampling_rate)
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
            # Whisper names the language it heard: e.g. english -> en
            from transformers.models.whisper.tokenization_whisper import LANGUAGES
            ref_languages = {LANGUAGES.get(code, code): code for code in args.ref_languages.split(',') if code}
        if ref_text and (ref_language is None or ref_language in ref_languages):
            # upstream's clone prompt: the reference's DVAE codes (spk_smp), then its text (txt_smp, normalized
            # as the sentences are) ahead of each sentence, no speaker embedding
            data, sr = sf.read(clip, dtype='float32')
            with torch.inference_mode():
                spk_smp = chat.sample_audio_speaker(np.ascontiguousarray(data, dtype=np.float32))
            txt_smp = chat.normalizer(ref_text, True, True, ref_languages.get(ref_language))
            refs[voice_key] = {'cloned': True, 'language': ref_language, 'spk_smp': spk_smp, 'txt_smp': txt_smp}
        else:
            # the clone prompt pairs the codes with their text: a reference in a language ChatTTS does not read, or
            # without speech, has none it can use
            refs[voice_key] = {'cloned': False, 'language': ref_language if ref_text else None}
        return refs[voice_key]

    while True:
        raw = sys.stdin.buffer.readline()
        if not raw:
            break
        try:
            req = json.loads(raw)
        except Exception as e:
            proto.write(json.dumps({'ok': False, 'error': f'bad request: {e}', 'oom': False}) + '\n')
            continue
        if req.get('op') not in ('ref', 'tts'):
            proto.write(json.dumps({'ok': False, 'error': f"unknown op {req.get('op')!r}", 'oom': False}) + '\n')
            continue
        try:
            ref = prepare(req['voice'])
            if req['op'] == 'ref':
                proto.write(json.dumps({'ok': True, 'cloned': ref['cloned'], 'language': ref['language']}) + '\n')
                continue
            if not ref['cloned']:
                raise ValueError(f"the voice reference {req['voice']} holds no English or Chinese speech ({ref['language'] or 'no speech'} heard): ChatTTS cannot clone it")
            text = req['text'].strip()
            # generation cap: tokens_per_char per character, a Han / kana / Hangul character counted as 3 (a whole
            # syllable), at least 5 s of speech, at most max_new_tokens
            text_units = len(text) + 2 * len(re.findall(r'[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿]', text))
            max_new_tokens = min(int(req.get('max_new_tokens', 2048)), max(250, text_units * int(req.get('tokens_per_char', 10))))
            params = ChatTTS.Chat.InferCodeParams(
                prompt=f"[speed_{min(max(int(req.get('speed', 5)), 0), 9)}]",
                spk_smp=ref['spk_smp'],
                txt_smp=ref['txt_smp'],
                temperature=float(req.get('temperature', 0.3)),
                top_K=int(req.get('top_k', 20)),
                top_P=float(req.get('top_p', 0.7)),
                repetition_penalty=float(req.get('repetition_penalty', 1.05)),
                max_new_token=max_new_tokens,
                show_tqdm=False
            )
            cap_flag.hit = False
            wavs = chat.infer([text], lang=req.get('language'), skip_refine_text=True, split_text=False, params_infer_code=params)
            audio = np.asarray(wavs[0] if len(wavs) else [], dtype=np.float32).reshape(-1)
            if audio.size == 0:
                raise ValueError(f'no audio generated for: {text[:80]}')
            sf.write(req['file'], audio, sampling_rate, subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': sampling_rate, 'samples': int(audio.shape[0]), 'capped': cap_flag.hit}
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
