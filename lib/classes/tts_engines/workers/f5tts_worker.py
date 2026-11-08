# Runs inside lib/classes/tts_engines/venvs/f5tts, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "...", "half": bool, "custom": bool} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "voice", "file", "nfe_step", "cfg_strength", "sway_sampling_coef", "speed",
#              "cross_fade_duration", "target_rms"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
import os, sys, re, json, argparse, hashlib, gc, zipfile, urllib.request, faulthandler

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
    parser.add_argument('--ckpt', default='')
    parser.add_argument('--vocab', default='')
    parser.add_argument('--arch', default='{}')
    parser.add_argument('--model_dir', default='')
    parser.add_argument('--ema', type=int, default=1)
    parser.add_argument('--custom', default='')
    parser.add_argument('--vocoder', default='charactr/vocos-mel-24khz')
    parser.add_argument('--vocoder_dir', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', required=True)
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--ref_max', type=float, default=12.0)
    parser.add_argument('--tashkeel_url', default='')
    parser.add_argument('--tashkeel_dir', default='')
    parser.add_argument('--habibi', default='')
    args = parser.parse_args()
    try:
        os.makedirs(args.cache_dir, exist_ok=True)
        from huggingface_hub import snapshot_download
        # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink
        # probe races under threaded downloads (WinError 1314 on windows without symlink rights)
        if args.custom:
            # a custom model brings its checkpoint, its vocab and its DiT config (the "Config" line of
            # upstream's SHARED.md as json, bare or under "arch"); e2a extracts uploads flat
            ckpt_file = weights_file = os.path.join(args.custom, 'model.safetensors')
            vocab_file = os.path.join(args.custom, 'vocab.txt')
            with open(os.path.join(args.custom, 'config.json'), 'r', encoding='utf-8') as f:
                arch = json.load(f)
            arch = arch.get('arch', arch)
        else:
            # only the language's checkpoint and vocab: a repo can hold several models (SWivid/F5-TTS).
            # Downloaded once, then never checked again (an offline start keeps working). A .pt training
            # checkpoint is kept as the one weight set inference loads (see below): its .e2a.safetensors
            ckpt_file = os.path.join(args.model_dir, args.ckpt)
            vocab_file = os.path.join(args.model_dir, args.vocab)
            weights_file = f'{os.path.splitext(ckpt_file)[0]}.e2a.safetensors' if ckpt_file.endswith('.pt') else ckpt_file
            if not ((os.path.exists(weights_file) or os.path.exists(ckpt_file)) and os.path.exists(vocab_file)):
                snapshot_download(args.repo, local_dir=args.model_dir, allow_patterns=[args.ckpt, args.vocab])
            arch = json.loads(args.arch)
        if not all(os.path.exists(os.path.join(args.vocoder_dir, item)) for item in ('config.yaml', 'pytorch_model.bin')):
            snapshot_download(args.vocoder, local_dir=args.vocoder_dir, allow_patterns=['config.yaml', 'pytorch_model.bin'])
        if args.tashkeel_url and not all(os.path.exists(os.path.join(args.tashkeel_dir, item)) for item in ('encoder.onnx', 'decoder.onnx')):
            # the diacritizer's ONNX pair, a GitHub release zip: fetched once into models/tts (catt-tashkeel
            # would otherwise download it inside its own package folder)
            os.makedirs(args.tashkeel_dir, exist_ok=True)
            archive = os.path.join(args.tashkeel_dir, 'model.zip')
            urllib.request.urlretrieve(args.tashkeel_url, archive)
            with zipfile.ZipFile(archive) as zip_ref:
                zip_ref.extractall(args.tashkeel_dir)
            os.unlink(archive)
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS
            # +vulkan builds): encodec (imported by vocos) reads torch.distributed.ReduceOp at import and calls
            # is_initialized() at run time; single-process inference only needs them to exist
            import types
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        from pydub import AudioSegment
        from f5_tts.model import DiT
        from f5_tts.infer import utils_infer
        from f5_tts.infer.utils_infer import load_model, load_vocoder, chunk_text, infer_batch_process, remove_silence_edges
        if weights_file != ckpt_file and not os.path.exists(weights_file):
            # training checkpoints carry the optimizer and both weight sets (Jmica: 5.4 GB), and upstream loads
            # them whole onto the device: the one set used (EMA, or the raw weights when the checkpoint asks
            # for them) is saved once as safetensors, read through mmap, and the .pt is dropped. Upstream's
            # loader takes either set from it (no ema_model. prefix to strip on the raw ones).
            from safetensors.torch import save_file
            checkpoint = torch.load(ckpt_file, map_location='cpu', weights_only=True, mmap=True)
            weights = checkpoint['ema_model_state_dict' if args.ema else 'model_state_dict']
            save_file({k: v.contiguous() for k, v in weights.items()}, f'{weights_file}.part')
            os.replace(f'{weights_file}.part', weights_file)
            del checkpoint, weights
            gc.collect()
            os.unlink(ckpt_file)
        device = args.device
        half = False
        if device == 'cuda' and torch.cuda.is_available():
            # fp32 on sm 6.1 (Pascal) and on GTX 16xx, fp16 above (the rule upstream GPT-SoVITS uses);
            # upstream F5-TTS alone would take fp16 on every sm >= 7.0
            major, minor = torch.cuda.get_device_capability(0)
            sm = major + minor / 10.0
            half = sm > 6.1 and not (re.search(r'16\d{2}', torch.cuda.get_device_name(0)) and sm == 7.5)
        # upstream loads straight onto cuda / cpu; any other device (mps, xpu) loads on cpu and moves,
        # as safetensors' load_file does not take every torch device
        load_device = device if device in ('cuda', 'cpu') else 'cpu'
        ema_model = load_model(DiT, arch, weights_file, mel_spec_type='vocos', vocab_file=vocab_file, device=load_device)
        ema_model = ema_model.to(device=device, dtype=torch.float16 if half else torch.float32)
        vocoder = load_vocoder('vocos', True, args.vocoder_dir, load_device).to(device)
        harakat = None
        if args.habibi:
            # Habibi-TTS: its inference (habibi_tts infer_batch_process) is upstream's with the text step alone changed,
            # the text reaches the model as is (no pinyin), as <dialect id>〈ref + gen〉 for the Unified model and bare for
            # the specialized ones; the process serves one checkpoint, so upstream's step is swapped here once
            dialect_ids = {'UNK': '\u24ea', 'MSA': '\u2460', 'SAU': '\u2461', 'UAE': '\u2462', 'ALG': '\u2463', 'IRQ': '\u2464', 'EGY': '\u2465', 'MAR': '\u2466', 'OMN': '\u2467', 'TUN': '\u2468', 'LEV': '\u2469', 'SDN': '\u246a', 'LBY': '\u246b'}
            dialect_id = dialect_ids.get(args.habibi, '')
            utils_infer.convert_char_to_pinyin = lambda text_list, polyphone=True: [f'{dialect_id}\u3008{text}\u3009' if dialect_id else text for text in text_list]
            # trained on undiacritized ASR transcripts: diacritized input garbles (audio.cpp's port strips them too)
            harakat = re.compile(r'[\u0640\u064B-\u065F\u0670]')
        tashkeel = None
        if args.tashkeel_url:
            # cpu ONNX model, small next to the TTS
            from catt_tashkeel import CATTEncoderOnly
            tashkeel = CATTEncoderOnly(encoder_path=os.path.join(args.tashkeel_dir, 'encoder.onnx'), decoder_path=os.path.join(args.tashkeel_dir, 'decoder.onnx'))
            # SILMA's own spans: runs of Arabic letters / diacritics (the diacritizer drops anything else)
            arabic_runs = re.compile(r'[\u0621-\u063A\u0640-\u0652\u0670\u0671\ufefb\ufef7\ufef5\ufef9]+(?:[\s]+[\u0621-\u063A\u0640-\u0652\u0670\u0671\ufefb\ufef7\ufef5\ufef9]+)*')
        sampling_rate = int(utils_infer.target_sample_rate)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(next(ema_model.parameters()).device), 'half': half, 'custom': bool(args.custom)}) + '\n')
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
            # the reference window is part of the clip: checkpoints may cut it differently
            voice_key = f'{voice}:{os.path.getmtime(voice)}:{args.ref_max}'
            if voice_key not in refs:
                clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                if not os.path.exists(clip):
                    # keep at most ref_max, cutting at the quietest 50 ms of the last 3 s so no word is
                    # clipped; no padding: F5-TTS times the generated speech on the reference's length
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
                    # then upstream's own reference trim (preprocess_ref_audio_text): silent edges off, 50 ms
                    # tail; pydub reads and writes wav itself, no ffmpeg involved
                    (remove_silence_edges(AudioSegment.from_file(clip)) + AudioSegment.silent(duration=50)).export(clip, format='wav')
                # the transcript is kept beside the clip: Whisper runs once per voice, ever
                text_file = f'{clip[:-4]}.txt'
                if os.path.exists(text_file):
                    with open(text_file, 'r', encoding='utf-8') as f:
                        ref_text = f.read().strip()
                else:
                    # upstream's Whisper, on cpu (no VRAM taken from the model), downloaded as a plain folder,
                    # language left to Whisper: the voice is often not in the book's language; released after
                    # complete once the marker exists: config.json lands first, so a download cut during the
                    # 1.6 GB weights used to look finished forever; snapshot_download resumes what is missing
                    asr_marker = os.path.join(args.asr_dir, '.e2a_complete')
                    if not os.path.exists(asr_marker):
                        snapshot_download(args.asr_model, local_dir=args.asr_dir)
                        open(asr_marker, 'w').close()
                    from transformers import pipeline
                    from transformers.utils import logging as transformers_logging
                    # upstream's Whisper call only draws transformers' advice here (chunk_length_s on a clip that
                    # never needs chunking, its own deprecated generation arguments, the BPE cleanup it ignores):
                    # errors only while it runs, an empty transcript is caught below
                    verbosity = transformers_logging.get_verbosity()
                    transformers_logging.set_verbosity_error()
                    try:
                        utils_infer.asr_pipe = pipeline('automatic-speech-recognition', model=args.asr_dir, device='cpu')
                        ref_text = utils_infer.transcribe(clip).strip()
                    finally:
                        utils_infer.asr_pipe = None
                        transformers_logging.set_verbosity(verbosity)
                        gc.collect()
                    if not ref_text:
                        raise ValueError(f'no speech found in the voice reference {voice}')
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(ref_text)
                # upstream's own rule (preprocess_ref_audio_text): the reference text ends a sentence
                if not ref_text.endswith('. ') and not ref_text.endswith('。'):
                    ref_text += ' ' if ref_text.endswith('.') else '. '
                # the reference is read here once per voice, not by upstream's infer_process at every
                # sentence: its torchaudio.load needs torchcodec (left out) unless e2a's sitecustomize
                # shim is the one python loads, which a distro python's own sitecustomize prevents
                data, sr = sf.read(clip, dtype='float32', always_2d=True)
                refs[voice_key] = (torch.from_numpy(data.T.copy()), sr, ref_text)
            ref_audio, ref_sr, ref_text = refs[voice_key]
            text = req['text']
            if harakat is not None:
                text = harakat.sub('', text)
            speed = float(req.get('speed', 1.0))
            if tashkeel is not None and arabic_runs.search(text):
                # SILMA's own text path (silma_tts infer_process): Arabic without diacritics gets them, and the
                # speech is sped up x1.3 as F5-TTS times it on the now longer text, as it is for text already
                # heavily diacritized; the last word ends on a sukun (pause form)
                diacritics = len(re.findall(r'[\u064B-\u0652]', text))
                if diacritics < 3:
                    text = arabic_runs.sub(lambda run: tashkeel.do_tashkeel(run.group(0), verbose=False), text)
                    speed *= 1.3
                elif diacritics / len(text) > 0.2:
                    speed *= 1.3
                text = text.strip()
                ending = text[-1] if text[-1] in '.,،؟؛:!?;' else ''
                body = text[:-1].strip() if ending else text
                if body and re.match(r'[\u064B-\u0652]', body[-1]):
                    body = body[:-1] + '\u0652'
                text = body + ending
            # upstream's infer_process (utils_infer.py) without its prints: text batches sized on the reference's
            # bytes per second so reference + batch stay within ~22 s, then the batches with cross-fades
            ref_seconds = ref_audio.shape[-1] / ref_sr
            max_chars = int(len(ref_text.encode('utf-8')) / ref_seconds * (22 - ref_seconds) * speed)
            audio, _, _ = next(infer_batch_process(
                (ref_audio, ref_sr),
                ref_text,
                chunk_text(text, max_chars=max_chars),
                ema_model,
                vocoder,
                mel_spec_type='vocos',
                progress=None,
                target_rms=float(req.get('target_rms', 0.1)),
                cross_fade_duration=float(req.get('cross_fade_duration', 0.15)),
                nfe_step=int(req.get('nfe_step', 32)),
                cfg_strength=float(req.get('cfg_strength', 2.0)),
                sway_sampling_coef=float(req.get('sway_sampling_coef', -1.0)),
                speed=speed,
                device=device
            ))
            if audio is None:
                raise ValueError('no audio generated')
            audio = np.asarray(audio, dtype=np.float32).reshape(-1)
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
            except Exception:
                pass
        proto.write(json.dumps(reply) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
