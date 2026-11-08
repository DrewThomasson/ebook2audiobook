# Runs inside lib/classes/tts_engines/venvs/orpheus, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "...", "dtype": "...", "custom": bool} once loaded
#             {"ready": false, "error": "...", "gated": bool, "repo": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "speaker", "file", "temperature", "top_p", "repetition_penalty",
#              "tokens_per_char", "max_new_tokens"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n, "capped": bool}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# Upstream's runtime (orpheus_tts) needs vllm: this is its transformers path (upstream's Colab notebooks) with the
# package's prompt format (engine_class.py _format_prompt) and token layout (decoder.py), decoded per sentence in one
# pass instead of upstream's 28-token streaming window
import os, sys, re, json, argparse, faulthandler

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='')
    parser.add_argument('--model_dir', default='')
    parser.add_argument('--custom', default='')
    parser.add_argument('--tokenizer', default='unsloth/orpheus-3b-0.1-ft')
    parser.add_argument('--tokenizer_dir', required=True)
    parser.add_argument('--snac', default='hubertsiuzdak/snac_24khz')
    parser.add_argument('--snac_dir', required=True)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    # Orpheus' special ids (Llama 3 vocabulary + Orpheus' own): start of human, end of text, end of human, start of
    # AI, start of speech, end of speech, pad. Audio tokens start at 128266, 4096 codes per position, 7 positions per
    # SNAC frame
    start_of_human, end_of_text, end_of_human, start_of_ai, start_of_speech, end_of_speech, pad_token = 128259, 128009, 128260, 128261, 128257, 128258, 128263
    audio_base = 128266
    try:
        from huggingface_hub import snapshot_download
        from huggingface_hub.errors import GatedRepoError
        repo = args.repo
        try:
            # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink
            # probe races under threaded downloads (WinError 1314 on windows without symlink rights)
            if args.custom:
                # a custom model brings its weights (one file, or index + shards), config and tokenizer (e2a extracts
                # uploads flat); its optional "orpheus_speaker" config key is the speaker name it was trained with
                model_path = args.custom
                with open(os.path.join(model_path, 'config.json'), 'r', encoding='utf-8') as f:
                    custom_speaker = json.load(f).get('orpheus_speaker') or None
            else:
                # complete once the marker exists: config.json lands first, so a download cut during the weights
                # would look finished forever; snapshot_download resumes what is missing. Weights, configs and
                # tokenizer only: the multilingual repos also carry their training state (optimizer.pt 26 GB)
                model_path = args.model_dir
                custom_speaker = None
                model_marker = os.path.join(model_path, '.e2a_complete')
                if not os.path.exists(model_marker):
                    snapshot_download(repo, local_dir=model_path, allow_patterns=['*.json', '*.safetensors', 'tokenizer*'])
                    open(model_marker, 'w').close()
            # a checkpoint without its own tokenizer takes the shared one (text tokens only come from it)
            tokenizer_path = model_path
            if not os.path.exists(os.path.join(model_path, 'tokenizer.json')):
                repo = args.tokenizer
                tokenizer_path = args.tokenizer_dir
                if not all(os.path.exists(os.path.join(tokenizer_path, item)) for item in ('tokenizer.json', 'tokenizer_config.json')):
                    snapshot_download(args.tokenizer, local_dir=tokenizer_path, allow_patterns=['tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json'])
            repo = args.snac
            if not all(os.path.exists(os.path.join(args.snac_dir, item)) for item in ('config.json', 'pytorch_model.bin')):
                snapshot_download(args.snac, local_dir=args.snac_dir, allow_patterns=['config.json', 'pytorch_model.bin'])
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
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from snac import SNAC
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
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        # straight onto the GPU (device_map): no full host copy first, which a unified-memory jetson cannot spare;
        # the multilingual checkpoints are fp32 on disk and cast while loading
        model = AutoModelForCausalLM.from_pretrained(model_path, dtype=dtype, low_cpu_mem_usage=True, **({'device_map': 'cuda:0' if device == 'cuda' else device} if device != 'cpu' else {}))
        model.eval()
        # SNAC is small: on the model's GPU for cuda / xpu, on cpu otherwise
        snac_device = device if device in ('cuda', 'xpu') else 'cpu'
        snac = SNAC.from_pretrained(args.snac_dir).eval().to(snac_device)
        sampling_rate = 24000
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}', 'gated': False}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(model.device), 'dtype': str(dtype).replace('torch.', ''), 'custom': bool(args.custom)}) + '\n')
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
            text = req['text'].strip()
            speaker = req.get('speaker') or custom_speaker
            # upstream's prompt (engine_class.py _format_prompt): the speaker's name written before the text, the
            # tokenizer adds its <|begin_of_text|>, then the turn closes and the speech opens
            prompt = f'{speaker}: {text}' if speaker else text
            input_ids = torch.tensor([[start_of_human] + tokenizer(prompt).input_ids + [end_of_text, end_of_human, start_of_ai, start_of_speech]], dtype=torch.long, device=model.device)
            # generation cap: tokens_per_char per character, a Han / kana / Hangul character counted as 3 (a whole
            # syllable, ~0.2 s of speech, against ~0.07 s for a latin letter), at most max_new_tokens
            text_units = len(text) + 2 * len(re.findall(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]', text))
            max_new_tokens = min(int(req.get('max_new_tokens', 4096)), max(28 * 20, text_units * int(req.get('tokens_per_char', 20))))
            with torch.inference_mode():
                output = model.generate(
                    input_ids=input_ids,
                    attention_mask=torch.ones_like(input_ids),
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=float(req.get('temperature', 0.4)),
                    top_p=float(req.get('top_p', 0.9)),
                    repetition_penalty=float(req.get('repetition_penalty', 1.1)),
                    eos_token_id=end_of_speech,
                    pad_token_id=pad_token
                )
            generated = output[0, input_ids.shape[1]:].tolist()
            del output, input_ids
            capped = end_of_speech not in generated and len(generated) >= max_new_tokens
            if capped:
                print(f'orpheus_worker: no end of speech within {max_new_tokens} tokens (cap reached: a loop, or a cap too low for this text), the part is cut there: {text[:80]}', file=sys.stderr)
            # audio tokens into SNAC frames, each token checked against its position in the frame (upstream counts
            # positions by index, so one stray or missing token shifts every frame after it): a token out of step
            # drops the partial frame, a position 0 starts a new one
            frames = []
            frame = []
            for token in generated:
                if token < audio_base:
                    continue
                position, code = divmod(token - audio_base, 4096)
                if position > 6:
                    continue
                if position == len(frame):
                    frame.append(code)
                    if len(frame) == 7:
                        frames.append(frame)
                        frame = []
                else:
                    frame = [code] if position == 0 else []
            if not frames:
                raise ValueError(f'no audio tokens generated for: {text[:80]}')
            # SNAC's three codebooks (decoder.py): 1 code per frame at 12 Hz, 2 at 24 Hz, 4 at 47 Hz
            codes = [
                torch.tensor([[f[0] for f in frames]], dtype=torch.long, device=snac_device),
                torch.tensor([[c for f in frames for c in (f[1], f[4])]], dtype=torch.long, device=snac_device),
                torch.tensor([[c for f in frames for c in (f[2], f[3], f[5], f[6])]], dtype=torch.long, device=snac_device)
            ]
            with torch.inference_mode():
                audio = snac.decode(codes)
            audio = audio.reshape(-1).float().cpu().numpy().astype(np.float32)
            del codes
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
