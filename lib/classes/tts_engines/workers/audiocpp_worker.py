# Runs on e2a's own python but imports nothing from e2a (stdlib only). Driven by SubprocessPipe(keep_alive=True).
# Starts the native audiocpp_server (0xShug0/audio.cpp) with a one-model config on a free 127.0.0.1 port, keeps it
# loaded for the session and stops it on EOF, which frees its VRAM. One worker per e2a audio.cpp engine, all of them on
# the same server package.
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": n, "backend": "...", "port": n} once /health answers (lazy_load off:
#             the TTS model is resident before the server listens)
#             {"ready": false, "error": "..."} then exit 1 if it could not start
#   stdin  -> {"op": "tts", "text", "language" ("" = the model detects it), "voice" (a voice file or None), "voice_id"
#              (built-in voice, optional), "file", "options" ({name: value}, optional)}
#             --clone: the voice file is the model's reference; otherwise the model speaks with voice_id and a voice
#             file converts its output with the --vc-model (Seed-VC)
#   stdin  -> --vc-only (the VC stage of e2a's built-in voice engines, VoiceConversion): --model/--family is the VC model
#             and the only op is {"op": "vc", "source" (the wav to convert), "voice" (the voice file), "file"}
#   stdout <- {"ok": true, "file": "..."}
#             {"ok": false, "error": "...", "oom": bool, "server_exited": bool}
#   EOF on stdin -> the server is stopped, exit 0
import os, sys, json, time, wave, math, array, base64, shutil, signal, socket, argparse, platform, tempfile, threading, subprocess
import urllib.request, urllib.error

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so nothing else can ever
    # write into the reply stream (e2a shows stderr in its log)
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--family', required=True)
    parser.add_argument('--backend', choices=['cpu', 'cuda', 'vulkan', 'metal'], default='cpu')
    parser.add_argument('--load-options', default='{}')
    parser.add_argument('--session-options', default='{}')
    parser.add_argument('--request-options', default='{}')
    parser.add_argument('--ref-min', type=float, default=3.2)
    parser.add_argument('--ref-max', type=float, default=10.0)
    parser.add_argument('--ref-text', choices=['none', 'optional', 'required'], default='none')
    parser.add_argument('--ref-fallback', default='{}')
    parser.add_argument('--asr-model', default='')
    parser.add_argument('--asr-family', default='qwen3_asr')
    parser.add_argument('--language-option', action='store_true')
    parser.add_argument('--clone', action='store_true')
    parser.add_argument('--speaker-label', action='store_true')
    parser.add_argument('--vc-model', default='')
    parser.add_argument('--vc-family', default='seed_vc')
    parser.add_argument('--vc-route', default='')
    parser.add_argument('--vc-only', action='store_true')
    parser.add_argument('--samplerate', type=int, default=24000)
    args = parser.parse_args()
    server_dir = os.path.dirname(os.path.abspath(args.server))
    work_dir = tempfile.mkdtemp(prefix='e2a_audiocpp_')
    # the package folder is shared by every audio.cpp engine: one pid file per family
    pid_file = os.path.join(server_dir, f'.e2a_server_{args.family}.pid')
    # transcripts outlive the worker: a voice already transcribed never loads the ASR model again
    transcripts_file = os.path.join(server_dir, '.e2a_transcripts.json')
    ref_fallback = json.loads(args.ref_fallback)
    asr_wanted = args.clone and args.ref_text != 'none' and bool(args.asr_model)
    vc_wanted = not args.clone and bool(args.vc_model)
    # ggml's CPU pool (also the CPU side of GPU backends): physical cores on x86 (SMT siblings slow ggml down), all elsewhere
    threads = max(1, (os.cpu_count() or 2) // (2 if platform.machine().lower() in ('x86_64', 'amd64') else 1))
    # --vc-only: the model is the VC one (same id as the lazy VC entry below), resident before the server listens
    models = [{'id': 'e2a-vc' if args.vc_only else 'e2a', 'family': args.family, 'path': os.path.abspath(args.model), 'task': 'vc' if args.vc_only else 'tts', 'mode': 'offline'}]
    for key, value in (('load_options', json.loads(args.load_options)), ('session_options', json.loads(args.session_options)), ('default_request_options', json.loads(args.request_options))):
        if value:
            models[0][key] = value
    if asr_wanted:
        # lazy: loaded on the first transcription only, unloaded right after it
        models.append({'id': 'e2a-asr', 'family': args.asr_family, 'path': os.path.abspath(args.asr_model), 'task': 'asr', 'mode': 'offline', 'lazy': True})
    if vc_wanted:
        # lazy: loaded with the first sentence spoken in a picked voice, then kept for the session
        models.append({'id': 'e2a-vc', 'family': args.vc_family, 'path': os.path.abspath(args.vc_model), 'task': 'vc', 'mode': 'offline', 'lazy': True})
    # max_loaded_models 0: loading the ASR or VC model must not evict the TTS one. busy_timeout_ms 0: this worker sends one
    # request at a time, nothing to wait for
    config = {'host': '127.0.0.1', 'port': 0, 'backend': args.backend, 'threads': threads, 'lazy_load': False, 'max_loaded_models': 0, 'busy_timeout_ms': 0, 'models': models}
    popen_kw = {}
    if sys.platform.startswith('linux'):
        # the kernel kills the server if this worker dies (SIGKILL, native crash): no orphan holding VRAM
        def pdeathsig()->None:
            import ctypes
            ctypes.CDLL('libc.so.6', use_errno=True).prctl(1, signal.SIGKILL)   # PR_SET_PDEATHSIG
        popen_kw['preexec_fn'] = pdeathsig
    elif sys.platform == 'win32':
        popen_kw['creationflags'] = 0x08000000   # CREATE_NO_WINDOW
    elif sys.platform == 'darwin' and os.path.exists(pid_file):
        # no parent-death signal on macOS: a server left by a killed worker is stopped on the next start
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            comm = subprocess.run(['ps', '-p', str(old_pid), '-o', 'comm='], capture_output=True, text=True).stdout.strip()
            if comm.endswith('audiocpp_server'):
                os.kill(old_pid, signal.SIGKILL)
        except Exception:
            pass
    job = None
    kernel32 = None
    if sys.platform == 'win32':
        # a Job Object closed with this worker kills the server (KILL_ON_JOB_CLOSE)
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.CreateJobObjectW.restype = wintypes.HANDLE
            kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
            kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
            kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
            class BASIC(ctypes.Structure):
                _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64), ('PerJobUserTimeLimit', ctypes.c_int64), ('LimitFlags', wintypes.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD), ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]
            class IO(ctypes.Structure):
                _fields_ = [(n, ctypes.c_uint64) for n in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
            class EXTENDED(ctypes.Structure):
                _fields_ = [('BasicLimitInformation', BASIC), ('IoInfo', IO), ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t), ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]
            info = EXTENDED()
            info.BasicLimitInformation.LimitFlags = 0x2000   # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            job = kernel32.CreateJobObjectW(None, None)
            if job:
                kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))   # JobObjectExtendedLimitInformation
        except Exception as e:
            job = None
            sys.stderr.write(f'audiocpp worker: no job object guard ({e})\n')
    state = {'tail': []}
    def drain(stream)->None:
        # stdout and stderr both go on to e2a's log; read to the end or a full pipe blocks the server
        for raw in iter(stream.readline, b''):
            line = raw.decode('utf-8', errors='replace').rstrip()
            sys.stderr.write(line + '\n')
            # the CPU-backend notice printed at every start is no cause: keep it out of the error tail
            if not line.startswith('audio.cpp is optimized for CUDA'):
                state['tail'] = (state['tail'] + [line])[-15:]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # never through a proxy: HTTP_PROXY would catch 127.0.0.1
    server = None
    def stop_server()->None:
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
        if sys.platform == 'darwin' and os.path.exists(pid_file):
            try:
                os.unlink(pid_file)
            except OSError:
                pass
        shutil.rmtree(work_dir, ignore_errors=True)
    # SubprocessPipe ends with terminate() only if EOF did not work: still stop the server on the way out
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        for attempt in range(5):
            # audiocpp_server takes no port 0 (1..65535) and prints its configured port, not the bound one: probe a free
            # port here. One taken in between fails the bind (after the model load), then the next attempt takes another
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(('127.0.0.1', 0))
                config['port'] = probe.getsockname()[1]
            config_file = os.path.join(work_dir, 'server.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)
            state['tail'] = []
            try:
                # cwd = the package: the server's contract lookup finds the model_specs/ shipped with this exact binary
                server = subprocess.Popen([args.server, '--config', config_file, '--no-ui'], cwd=server_dir, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **popen_kw)
            except Exception as e:
                proto.write(json.dumps({'ready': False, 'error': f'cannot start audiocpp_server: {type(e).__name__}: {e}'}) + '\n')
                return 1
            if job:
                from ctypes import wintypes
                kernel32.AssignProcessToJobObject(job, wintypes.HANDLE(int(server._handle)))
            elif sys.platform == 'darwin':
                try:
                    with open(pid_file, 'w') as f:
                        f.write(str(server.pid))
                except Exception:
                    pass
            for stream in (server.stdout, server.stderr):
                threading.Thread(target=drain, args=(stream,), daemon=True).start()
            base = f"http://127.0.0.1:{config['port']}"
            # the listening banner goes to a block-buffered stdout and shows only at exit: poll /health instead
            while server.poll() is None:
                try:
                    with opener.open(base + '/health', timeout=2) as r:
                        if r.status == 200:
                            break
                except Exception:
                    pass
                time.sleep(0.25)
            if server.poll() is None:
                break
            time.sleep(0.2)   # let drain() collect the last lines
            if not any('could not bind' in line for line in state['tail']):
                break
        if server.poll() is not None:
            tail = ' | '.join(l for l in state['tail'] if l.strip())
            proto.write(json.dumps({'ready': False, 'error': f'audiocpp_server exited ({server.poll()}): {tail}'}) + '\n')
            return 1
        def post(path:str, body:dict, timeout:float)->bytes:
            request = urllib.request.Request(base + path, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
            try:
                with opener.open(request, timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8', errors='replace')
                try:
                    detail = json.loads(detail)['error']['message']
                except Exception:
                    pass
                raise RuntimeError(f'{path}: HTTP {e.code} {detail[:400]}')
        try:
            with open(transcripts_file, 'r', encoding='utf-8') as f:
                transcripts = json.load(f)
        except Exception:
            transcripts = {}
        refs = {}
        def reference(voice:str)->tuple:
            # e2a voices run 1-5 min, the models clone from a few seconds: one clip per voice file (path + mtime), from the
            # first voiced 10 ms window, cut at the latest pause between ref_min and ref_max (never inside a word).
            # Returns (clip path, its transcript or None)
            key = f'{os.path.abspath(voice)}:{os.path.getmtime(voice)}:{args.ref_min}:{args.ref_max}'
            if key in refs:
                return refs[key]
            sr = 24000
            src = os.path.join(work_dir, f'ref_{len(refs)}_src.wav')
            dst = os.path.join(work_dir, f'ref_{len(refs)}.wav')
            # any format e2a accepts -> mono 16-bit (ffmpeg is on e2a's PATH); the server resamples per model
            run = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', voice, '-t', '120', '-ac', '1', '-ar', str(sr), '-sample_fmt', 's16', src], capture_output=True, text=True)
            if run.returncode != 0:
                raise RuntimeError(f'ffmpeg cannot read {voice}: {run.stderr.strip()[-300:]}')
            with wave.open(src, 'rb') as w:
                pcm = array.array('h', w.readframes(w.getnframes()))
            os.unlink(src)
            if sys.byteorder == 'big':
                pcm.byteswap()
            win = sr // 100
            db = [10 * math.log10(max(sum(s * s for s in pcm[i:i + win]) / win, 1e-3) / 1073741824.0) for i in range(0, len(pcm) - win + 1, win)]
            if not db:
                raise RuntimeError(f'{voice} is too short for a voice reference')
            peak = max(db)
            voiced = [i for i, d in enumerate(db) if d > peak - 35.0]
            first = max(0, voiced[0] - 5)
            last = min(len(db), voiced[-1] + 5)
            lo = first + int(args.ref_min * 100)
            hi = min(len(db), first + int(args.ref_max * 100))
            if last <= hi or lo >= hi:
                end = min(last, hi)
            else:
                # the latest pause: a window within 6 dB of the quietest one (pauses sit 20+ dB under speech), so the
                # clip stays as long as the window allows
                floor = min(db[lo:hi])
                end = max(i for i in range(lo, hi) if db[i] <= floor + 6.0)
            clip = pcm[first * win:end * win]
            fade = min(len(clip), win)
            for i in range(fade):
                clip[len(clip) - fade + i] = int(clip[len(clip) - fade + i] * (fade - 1 - i) / fade)
            if sys.byteorder == 'big':
                clip.byteswap()
            with wave.open(dst, 'wb') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(clip.tobytes())
            text = None
            if asr_wanted:
                text_key = f'{key}:{os.path.basename(args.asr_model)}'
                if text_key not in transcripts:
                    # Qwen3-ASR reads 16 kHz mono; automatic language (the voice's language is not the book's)
                    dst_16k = os.path.join(work_dir, f'ref_{len(refs)}_16k.wav')
                    run = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', dst, '-ac', '1', '-ar', '16000', '-sample_fmt', 's16', dst_16k], capture_output=True, text=True)
                    if run.returncode != 0:
                        raise RuntimeError(f'ffmpeg cannot resample {dst}: {run.stderr.strip()[-300:]}')
                    sys.stderr.write(f'audiocpp worker: transcribing the reference clip of {os.path.basename(voice)}\n')
                    try:
                        transcripts[text_key] = (json.loads(post('/v1/audio/transcriptions', {'model': 'e2a-asr', 'audio': dst_16k}, 1800)).get('text') or '').strip()
                        try:
                            with open(transcripts_file, 'w', encoding='utf-8') as f:
                                json.dump(transcripts, f, ensure_ascii=False, indent=1)
                        except Exception as e:
                            sys.stderr.write(f'audiocpp worker: cannot save transcripts ({e})\n')
                    except Exception as e:
                        # not cached: the next worker tries again. Meanwhile optional = no transcript, required = fallback
                        sys.stderr.write(f'audiocpp worker: transcription failed ({e})\n')
                    finally:
                        # the ASR model is done for this voice: give its memory back to the TTS model
                        try:
                            post('/v1/tasks/unload_models', {'model_ids': ['e2a-asr']}, 120)
                        except Exception as e:
                            sys.stderr.write(f'audiocpp worker: cannot unload the ASR model ({e})\n')
                    os.unlink(dst_16k)
                text = transcripts.get(text_key) or None
                if text is None and args.ref_text == 'required' and not ref_fallback:
                    raise RuntimeError(f'no transcript for the reference clip of {voice}: {args.family} cannot clone without one')
            refs[key] = (dst, text)
            return refs[key]
        # no route = the family's default (seed_vc: v2_vc)
        vc_route = {'route': args.vc_route} if args.vc_route else {}
        proto.write(json.dumps({'ready': True, 'samplerate': args.samplerate, 'backend': args.backend, 'port': config['port']}) + '\n')
        while True:
            raw = sys.stdin.buffer.readline()
            if not raw:
                break
            try:
                req = json.loads(raw)
            except Exception as e:
                proto.write(json.dumps({'ok': False, 'error': f'bad request: {e}', 'oom': False}) + '\n')
                continue
            if req.get('op') != ('vc' if args.vc_only else 'tts'):
                proto.write(json.dumps({'ok': False, 'error': f"unknown op {req.get('op')!r}", 'oom': False}) + '\n')
                continue
            try:
                if server.poll() is not None:
                    raise RuntimeError(f'audiocpp_server exited ({server.poll()}): ' + ' | '.join(state['tail'][-5:]))
                if args.vc_only:
                    # the source file -> the voice file's reference clip (Seed-VC resamples both itself)
                    clip, _ = reference(req['voice'])
                    result = json.loads(post('/v1/tasks/run', {'model': 'e2a-vc', 'request': {'audio': os.path.abspath(req['source']), 'voice_ref': clip, **vc_route}}, 1800))
                    if not result.get('audio'):
                        raise RuntimeError(f"voice conversion returned no audio: {str(result)[:200]}")
                    with open(req['file'], 'wb') as f:
                        f.write(base64.b64decode(result['audio']))
                    proto.write(json.dumps({'ok': True, 'file': req['file']}) + '\n')
                    continue
                text = req['text']
                if args.speaker_label:
                    # VibeVoice reads only "Speaker N:" script lines
                    text = 'Speaker 1: ' + ' '.join(text.split())
                body = {'model': 'e2a', 'input': text, 'response_format': 'wav'}
                options = dict(req.get('options') or {})
                convert_to = None
                if req.get('language'):
                    body['language'] = req['language']
                    if args.language_option:
                        # e.g. index_tts2: the language is only read from the request options
                        options.setdefault('language', req['language'])
                if req.get('voice_id'):
                    options.setdefault('voice_id', req['voice_id'])
                if req.get('voice'):
                    clip, ref_text = reference(req['voice'])
                    if args.clone:
                        body['voice_ref'] = {'type': 'path', 'path': clip}
                        if ref_text:
                            body['reference_text'] = ref_text
                        elif args.ref_text == 'required':
                            # e.g. qwen3_tts: speaker embedding only (x_vector_only_mode) instead of the transcript prompt
                            options = {**ref_fallback, **options}
                    elif vc_wanted:
                        convert_to = clip
                if options:
                    body['options'] = options
                audio = post('/v1/audio/speech', body, 1800)
                if not audio.startswith(b'RIFF'):
                    raise RuntimeError(f'not a WAV reply: {audio[:200]!r}')
                if convert_to:
                    # built-in voice -> the picked voice (Seed-VC resamples both itself)
                    vc_src = os.path.join(work_dir, 'vc_source.wav')
                    with open(vc_src, 'wb') as f:
                        f.write(audio)
                    result = json.loads(post('/v1/tasks/run', {'model': 'e2a-vc', 'request': {'audio': vc_src, 'voice_ref': convert_to, **vc_route}}, 1800))
                    if not result.get('audio'):
                        raise RuntimeError(f"voice conversion returned no audio: {str(result)[:200]}")
                    audio = base64.b64decode(result['audio'])
                # written as served (PCM or float WAV): e2a reads it with soundfile
                with open(req['file'], 'wb') as f:
                    f.write(audio)
                reply = {'ok': True, 'file': req['file']}
            except Exception as e:
                # no retry here: e2a's convert() returns False and core.py unloads the engine, which closes
                # stdin and ends this process (and the server with it)
                error = f'{type(e).__name__}: {e}'
                # a server that aborted mid-request shows up as a lost connection: give it a moment to be reaped,
                # then tell e2a so it can restart or leave that package
                try:
                    server.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                lowered = error.lower()
                reply = {'ok': False, 'error': error, 'oom': any(s in lowered for s in ('out of memory', 'failed to allocate', 'insufficient_memory')), 'server_exited': server.poll() is not None}
            proto.write(json.dumps(reply) + '\n')
        return 0
    finally:
        stop_server()

if __name__ == '__main__':
    sys.exit(main())
