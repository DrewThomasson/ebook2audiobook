# Runs on e2a's own python but imports nothing from e2a (stdlib only). Driven by SubprocessPipe(keep_alive=True).
# Starts the native zonos2-server (ZONOS2, Zyphra zonos2.cpp) on a free 127.0.0.1 port, keeps it loaded for the
# session and stops it on EOF, which frees its VRAM.
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 44100, "backend": "gpu|cpu", "port": n} once the server listens
#             {"ready": false, "error": "..."} then exit 1 if it could not start
#   stdin  -> {"op": "tts", "text", "language", "voice", "file", "emotion_enabled", "emotion" ({name: weight}),
#              "emotion_strength", "emotion_cfg_scale", "speaking_rate"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 44100, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> the server is stopped, exit 0
import os, sys, re, json, uuid, wave, math, array, base64, signal, argparse, threading, subprocess, unicodedata
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
    parser.add_argument('--dac', required=True)
    parser.add_argument('--spk', required=True)
    parser.add_argument('--emotion-dir', required=True)
    parser.add_argument('--backend', choices=['gpu', 'cpu'], default='cpu')
    parser.add_argument('--samplerate', type=int, default=44100)
    args = parser.parse_args()
    # --port 0: the OS picks a free port at bind time (no race, no clash between e2a instances), the server
    # reports it in its ready line, printed only once the backbone, emotion directions and DAC are loaded.
    # --batch 2: emotion_cfg_scale != 1 needs a second slot. Empty default-voices dir: e2a always clones.
    # --max: frame ceiling (DAC 44.1 kHz = 512 samples per frame, ~86 frames/s). The server default 2000 (~23 s)
    # is below a max_chars sentence read at natural pace plus its trailing silence, and a generation stopped by
    # the ceiling is decoded without its end token: the last word is cut. 3440 = 40 s, ~+0.09 GB KV per slot
    max_frames = 3440
    cmd = [args.server, args.model, '--dac', args.dac, '--spk', args.spk, '--host', '127.0.0.1', '--port', '0', '--batch', '2', '--max', str(max_frames), '--tts-default-voices-dir', '', '--tts-emotion-directions-dir', args.emotion_dir, f'--{args.backend}']
    server_dir = os.path.dirname(os.path.abspath(args.server))
    pid_file = os.path.join(server_dir, '.e2a_server.pid')
    popen_kw = {}
    if sys.platform.startswith('linux'):
        # the kernel kills the server if this worker dies (SIGKILL, native crash): no orphan holding VRAM
        def pdeathsig():
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
            if comm.endswith('zonos2-server'):
                os.kill(old_pid, signal.SIGKILL)
        except Exception:
            pass
    try:
        server = subprocess.Popen(cmd, cwd=server_dir, stdin=subprocess.DEVNULL, stdout=sys.stderr, stderr=subprocess.PIPE, **popen_kw)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'cannot start zonos2-server: {type(e).__name__}: {e}'}) + '\n')
        return 1
    job = None
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
                kernel32.AssignProcessToJobObject(job, wintypes.HANDLE(int(server._handle)))
        except Exception as e:
            sys.stderr.write(f'zonos worker: no job object guard ({e})\n')
    elif sys.platform == 'darwin':
        try:
            with open(pid_file, 'w') as f:
                f.write(str(server.pid))
        except Exception:
            pass
    def stop_server():
        if server.poll() is None:
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
    # SubprocessPipe ends with terminate() only if EOF did not work: still stop the server on the way out
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    # the server's stderr goes on to e2a's log; the ready line gives the port. Read until the end, or the
    # pipe fills up and the server blocks.
    port_found = threading.Event()
    state = {'port': None, 'tail': []}
    def read_stderr():
        for raw in iter(server.stderr.readline, b''):
            line = raw.decode('utf-8', errors='replace').rstrip()
            sys.stderr.write(line + '\n')
            state['tail'] = (state['tail'] + [line])[-15:]
            m = re.search(r'listening on http://[^:\s]+:(\d+)', line)
            if m and not port_found.is_set():
                state['port'] = int(m.group(1))
                port_found.set()
        port_found.set()
    threading.Thread(target=read_stderr, daemon=True).start()
    try:
        port_found.wait()
        if state['port'] is None:
            server.wait(timeout=10)
            tail = ' | '.join(l for l in state['tail'] if l.strip())
            proto.write(json.dumps({'ready': False, 'error': f'zonos2-server exited ({server.poll()}): {tail}'}) + '\n')
            return 1
        base = f"http://127.0.0.1:{state['port']}"
        # never through a proxy: HTTP_PROXY would otherwise catch 127.0.0.1
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        headers = {'Content-Type': 'application/json', 'X-TTS-Session-ID': f'e2a-{uuid.uuid4().hex[:12]}'}
        def post(path:str, body:dict, timeout:float)->bytes:
            request = urllib.request.Request(base + path, data=json.dumps(body).encode('utf-8'), headers=headers)
            try:
                with opener.open(request, timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                raise RuntimeError(f"{path}: HTTP {e.code} {e.read().decode('utf-8', errors='replace')[:400]}")
        proto.write(json.dumps({'ready': True, 'samplerate': args.samplerate, 'backend': args.backend, 'port': state['port']}) + '\n')
        speakers = {}
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
                if server.poll() is not None:
                    raise RuntimeError(f'zonos2-server exited ({server.poll()}): ' + ' | '.join(state['tail'][-5:]))
                text = req['text']
                # runaway guard: a generation that misses its end token babbles up to max_frames; bound it by the text.
                # The budget must hold the speech, the model's own trailing silence (0.25-0.5 s, its default
                # conditioning) and the 8 delayed-codebook frames, or the end token never comes and the last word is cut:
                # CJK / fullwidth ~0.5 s per char (0.25 cut zho/jpn/kor), digits ~0.4 s (read as words), others 0.25 s,
                # stretched for a slow speaking_rate (15 = natural), + 1.5 s fixed headroom
                rate = float(req.get('speaking_rate') or 0.0)
                seconds = sum(0.5 if unicodedata.east_asian_width(c) in ('W', 'F') else 0.4 if c.isdigit() else 0.25 for c in text) * (max(1.0, 15.0 / rate) if rate > 0.0 else 1.0) + 1.5
                body = {'text': text, 'language': req.get('language') or 'en_us', 'stream': False, 'format': 'wav', 'max_tokens': min(max_frames, int(args.samplerate / 512 * max(3.0, seconds)))}
                voice = req.get('voice')
                if voice:
                    # registered once per voice file, keyed by path + mtime so a rebuilt voice gets a new embedding.
                    # The server decodes the reference with ffmpeg (on e2a's PATH)
                    voice_key = f'{voice}:{os.path.getmtime(voice)}'
                    if voice_key not in speakers:
                        with open(voice, 'rb') as f:
                            reply = json.loads(post('/tts/speakers', {'speaker_audio_name': os.path.basename(voice), 'speaker_audio_base64': base64.b64encode(f.read()).decode('ascii')}, 600))
                        speakers[voice_key] = reply['id']
                    body['speaker_embedding_id'] = speakers[voice_key]
                if float(req.get('speaking_rate') or 0.0) > 0.0:
                    body.update(speaking_rate_enabled=True, speaking_rate=float(req['speaking_rate']))
                # all sliders at 0 is the plain cloned voice, so emotion is only sent when something is set
                emotion = {k: float(v) for k, v in (req.get('emotion') or {}).items() if abs(float(v)) > 1e-4}
                if req.get('emotion_enabled') and emotion and voice:
                    body.update(emotion_enabled=True, emotion_sliders=emotion, emotion_strength=float(req.get('emotion_strength', 1.0)), emotion_cfg_scale=float(req.get('emotion_cfg_scale', 1.0)))
                # best take: (tail ms, wav bytes, pcm, samplerate, channels). A take ending with its last 20 ms still
                # voiced stopped on the word with no trailing silence: the end of the word is lost. Up to 2 new draws
                # (fresh seed), then the take with the longest tail is kept, faded out over 20 ms if still cut (no click)
                best = None
                cut_draws = 0
                while True:
                    audio = post('/tts/generate', body, 1800)
                    if not audio.startswith(b'RIFF'):
                        raise RuntimeError(f'not a WAV reply: {audio[:200]!r}')
                    with open(req['file'], 'wb') as f:
                        f.write(audio)
                    with wave.open(req['file'], 'rb') as w:
                        sr, width, channels, frames = w.getframerate(), w.getsampwidth(), w.getnchannels(), w.getnframes()
                        pcm = array.array('h', w.readframes(frames)) if width == 2 else None
                    # with an end token the server decodes up to it, >= 10 frames (9 codebooks + 1) before the last
                    # generated one; without it every frame is decoded (max_tokens * 512 samples) and the tail is
                    # cut mid-word. One new draw (fresh seed) at the ceiling: a long sentence fits, a runaway ends
                    eos = frames < (body['max_tokens'] - 9) * 512
                    if not eos and body['max_tokens'] < max_frames:
                        sys.stderr.write(f"zonos worker: no end token within {body['max_tokens']} frames, regenerating with {max_frames}\n")
                        body['max_tokens'] = max_frames
                        continue
                    # trailing silence: 10 ms windows read back from the end (up to 500 ms) while below the voiced
                    # threshold. The model's trailing silence (trailing_silence_s conditioning) is not digital silence:
                    # DAC rebuilds the reference's room tone in it, often above peak - 45 dB, which read every take as
                    # cut. The threshold follows the take's own noise floor (10th percentile of its 10 ms windows
                    # + 10 dB), kept within [peak - 45 dB (floor -50 dBFS), peak - 20 dB]. A take stopped by the
                    # ceiling is kept as it is
                    tail_ms = 1000
                    thr = 0.0
                    win = sr // 100 * channels
                    db_win = []
                    if pcm is not None and eos and win > 0 and len(pcm) >= win:
                        if sys.byteorder == 'big':
                            pcm.byteswap()
                        peak_db = 20 * math.log10(max(max(pcm), -min(pcm), 1) / 32768.0)
                        # windows aligned on the end of the take, last window first
                        db_win = [10 * math.log10(max(sum(s * s for s in pcm[end - win:end]) / win, 1e-3) / 1073741824.0) for end in range(len(pcm), win - 1, -win)]
                        floor_db = sorted(db_win)[len(db_win) // 10]
                        thr = min(peak_db - 20.0, max(-50.0, peak_db - 45.0, floor_db + 10.0))
                        tail_ms = 0
                        while tail_ms < 500 and tail_ms // 10 < len(db_win) and db_win[tail_ms // 10] < thr:
                            tail_ms += 10
                    if best is None or tail_ms > best[0]:
                        best = (tail_ms, audio, pcm, sr, channels)
                    if tail_ms >= 20 or cut_draws >= 2:
                        break
                    cut_draws += 1
                    sys.stderr.write(f"zonos worker: last word cut (tail {tail_ms} ms, thr {thr:.1f} dBFS, last 300 ms: {' '.join(f'{d:.0f}' for d in db_win[:30])}), new draw {cut_draws}/2\n")
                tail_ms, audio, pcm, sr, channels = best
                if tail_ms < 20 and pcm is not None:
                    fade = min(len(pcm), sr // 50 * channels)
                    for i in range(fade):
                        pcm[len(pcm) - fade + i] = int(pcm[len(pcm) - fade + i] * (fade - 1 - i) / fade)
                    if sys.byteorder == 'big':
                        pcm.byteswap()
                    with wave.open(req['file'], 'wb') as w:
                        w.setnchannels(channels)
                        w.setsampwidth(2)
                        w.setframerate(sr)
                        w.writeframes(pcm.tobytes())
                    sys.stderr.write(f'zonos worker: still cut after {cut_draws} new draws, kept the longest take, faded out\n')
                else:
                    with open(req['file'], 'wb') as f:
                        f.write(audio)
                with wave.open(req['file'], 'rb') as w:
                    reply = {'ok': True, 'file': req['file'], 'samplerate': w.getframerate(), 'samples': w.getnframes()}
            except Exception as e:
                # no retry here: e2a's convert() returns False and core.py unloads the engine, which closes
                # stdin and ends this process (and the server with it)
                error = f'{type(e).__name__}: {e}'
                # a server that aborted mid-request (GPU driver assertion, e.g. MoltenVK) shows up here as a lost
                # connection: give it a moment to be reaped, then tell e2a so it can restart or leave that package
                try:
                    server.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                reply = {'ok': False, 'error': error, 'oom': 'out of memory' in error.lower() or 'failed to allocate' in error.lower(), 'server_exited': server.poll() is not None}
            proto.write(json.dumps(reply) + '\n')
        return 0
    finally:
        stop_server()

if __name__ == '__main__':
    sys.exit(main())
