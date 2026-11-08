# Runs inside lib/classes/tts_engines/venvs/omnivoice, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000, "device": "...", "half": bool, "custom": bool} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "language", "voice", "file", "num_step", "guidance_scale", "speed"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 24000, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
import os, sys, json, argparse, hashlib, shutil, gc, faulthandler

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--custom', default='')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', required=True)
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--ref_min', type=float, default=3.2)
    parser.add_argument('--ref_max', type=float, default=9.5)
    args = parser.parse_args()
    try:
        os.makedirs(args.cache_dir, exist_ok=True)
        from huggingface_hub import snapshot_download
        # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink
        # probe races under threaded downloads (WinError 1314 on windows without symlink rights)
        if args.custom:
            # a custom model brings its own weights and tokenizer; the audio tokenizer and chat template
            # are the base model's when the upload does not carry them (e2a extracts uploads flat)
            snapshot_download(args.repo, local_dir=args.model_dir, allow_patterns=['audio_tokenizer/*', 'chat_template.jinja'])
            model_path = args.custom
            for item in ('audio_tokenizer', 'chat_template.jinja'):
                src = os.path.join(args.model_dir, item)
                dst = os.path.join(model_path, item)
                if os.path.exists(src) and not os.path.exists(dst):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
        else:
            snapshot_download(args.repo, local_dir=args.model_dir)
            model_path = args.model_dir
        import re
        import numpy as np
        import torch
        import soundfile as sf
        from omnivoice import OmniVoice, VoiceClonePrompt
        device = args.device
        half = False
        if device == 'cuda' and torch.cuda.is_available():
            # fp32 on sm 6.1 (Pascal) and on GTX 16xx, fp16 above (the rule upstream GPT-SoVITS uses)
            major, minor = torch.cuda.get_device_capability(0)
            sm = major + minor / 10.0
            half = sm > 6.1 and not (re.search(r'16\d{2}', torch.cuda.get_device_name(0)) and sm == 7.5)
        model = OmniVoice.from_pretrained(model_path, device_map='cuda:0' if device == 'cuda' else device, dtype=torch.float16 if half else torch.float32)
        sampling_rate = int(model.sampling_rate)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': str(model.device), 'half': half, 'custom': bool(args.custom)}) + '\n')
    # prompts depend on the model's audio tokenizer: one cache entry per voice and model
    model_tag = hashlib.sha1(os.path.abspath(model_path).encode('utf-8')).hexdigest()[:8]
    prompts = {}
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
            if voice_key not in prompts:
                clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                if not os.path.exists(clip):
                    # upstream asks for 3-10 s references: keep at most ref_max, cutting at the quietest
                    # 50 ms of the last 3 s so no word is clipped; pad short voices with silence
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
                prompt_file = f'{clip[:-4]}.{model_tag}.prompt.pt'
                if os.path.exists(prompt_file):
                    prompt = VoiceClonePrompt.load(prompt_file)
                else:
                    # the transcript comes from OmniVoice's own Whisper, on cpu (no VRAM taken from the
                    # model), downloaded as a plain folder; released once the prompt is saved
                    # complete once the marker exists: config.json lands first, so a download cut during the
                    # 1.6 GB weights used to look finished forever; snapshot_download resumes what is missing
                    asr_marker = os.path.join(args.asr_dir, '.e2a_complete')
                    if not os.path.exists(asr_marker):
                        snapshot_download(args.asr_model, local_dir=args.asr_dir)
                        open(asr_marker, 'w').close()
                    model.load_asr_model(model_name=args.asr_dir, device='cpu')
                    prompt = model.create_voice_clone_prompt(ref_audio=clip, ref_text=None)
                    prompt.save(prompt_file)
                    model._asr_pipe = None
                    gc.collect()
                prompts[voice_key] = prompt
            audio = model.generate(
                text=req['text'],
                language=req['language'],
                voice_clone_prompt=prompts[voice_key],
                speed=float(req.get('speed', 1.0)),
                num_step=int(req.get('num_step', 32)),
                guidance_scale=float(req.get('guidance_scale', 2.0))
            )
            audio = np.asarray(audio[0], dtype=np.float32).reshape(-1)
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