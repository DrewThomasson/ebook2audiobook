import os, re, json, queue, threading, subprocess, multiprocessing, sys, gradio as gr

from collections.abc import Callable
from lib.lang import legends

class SubprocessPipe:

    def __init__(self, cmd:list[str], is_gui_process:bool, total_duration:float, msg:str=legends['msg_processing'], on_progress:Callable[[float], None]|None=None, keep_alive:bool=False, env:dict|None=None)->None:
        self.cmd = cmd
        self.is_gui_process = is_gui_process
        self.total_duration = total_duration
        self.msg = msg
        self.process = None
        self._stop_requested = False
        self.on_progress = on_progress
        self.progress_bar = False
        # keep_alive: the child is a persistent worker speaking one JSON object per
        # line (requests on its stdin, replies on its stdout, logs on its stderr).
        # result is True once the worker announced {"ready": true}, then send() is
        # the request/reply channel until stop(). Without it nothing changes.
        self.keep_alive = keep_alive
        self.env = env
        self.ready_info = {}
        self._ready = False
        self._lock = threading.Lock()
        if self.is_gui_process:
            self.progress_bar = gr.Progress(track_tqdm=False)
        self.result = self._run_process()
        
    def _emit_progress(self, percent:float)->None:
        if self.on_progress is not None:
            self.on_progress(percent)
        elif self.progress_bar:
            self.progress_bar(percent / 100.0, desc=self.msg)
        sys.stdout.write(f"\r{self.msg} - {percent:.1f}%")
        sys.stdout.flush()

    def _on_complete(self)->None:
        msg = '\n' + legends['msg_step_completed'].format(step=self.msg)
        print(msg)
        if self.progress_bar:
            self.progress_bar(1.0, desc=msg)

    def _on_error(self, err:Exception)->None:
        error = legends['error_step_failed'].format(step=self.msg, e=err)
        print(error)
        if self.progress_bar:
            self.progress_bar(0.0, desc=error)

    def _run_process(self)->bool:
        try:
            if self.keep_alive:
                self.process = subprocess.Popen(
                    self.cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=self.env
                )
                tqdm_re = re.compile(rb'(\d{1,3})%\|')
                progress_queue = queue.Queue()
                ready_queue = queue.Queue()

                def read_stderr():
                    # lives as long as the worker: its logs always reach the terminal,
                    # tqdm percents (model downloads) only feed the bar until ready.
                    buffer = b''
                    try:
                        while True:
                            chunk = self.process.stderr.read1(4096)
                            if not chunk:
                                break
                            try:
                                sys.stderr.write(chunk.decode('utf-8', errors='replace'))
                                sys.stderr.flush()
                            except Exception:
                                pass
                            if self._ready:
                                buffer = b''
                                continue
                            buffer += chunk
                            parts = re.split(rb'[\r\n]', buffer)
                            buffer = parts[-1]
                            for part in parts[:-1]:
                                match = tqdm_re.search(part)
                                if match:
                                    progress_queue.put(min(float(match.group(1)), 100.0))
                    except Exception:
                        pass

                def read_ready():
                    try:
                        ready_queue.put(self.process.stdout.readline())
                    except Exception:
                        ready_queue.put(b'')

                threading.Thread(target=read_stderr, daemon=True).start()
                threading.Thread(target=read_ready, daemon=True).start()
                last_percent = 0.0
                line = None
                while line is None:
                    try:
                        line = ready_queue.get(timeout=0.1)
                    except queue.Empty:
                        pass
                    while not progress_queue.empty():
                        percent = progress_queue.get_nowait()
                        if abs(percent - last_percent) >= 0.5:
                            self._emit_progress(percent)
                            last_percent = percent
                    if line is None and self._stop_requested:
                        return False
                self._ready = True
                try:
                    self.ready_info = json.loads(line) if line else {}
                except Exception:
                    self.ready_info = {'error': line.decode('utf-8', errors='replace').strip()}
                if self.ready_info.get('ready'):
                    self._on_complete()
                    return True
                if not line:
                    try:
                        self.process.wait(timeout=10)
                    except Exception:
                        pass
                    self.ready_info['error'] = legends['error_worker_exited'].format(code=self.process.poll())
                self._on_error(self.ready_info.get('error'))
                self.stop()
                return False
            is_ffmpeg = "ffmpeg" in os.path.basename(self.cmd[0])
            if is_ffmpeg:
                self.process = subprocess.Popen(
                    self.cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    bufsize=0,
                    env=self.env
                )
            else:
                if self.progress_bar:
                    self.process = subprocess.Popen(
                        self.cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        bufsize=0,
                        env=self.env
                    )
                else:
                    self.process = subprocess.Popen(
                        self.cmd,
                        stdout=None,
                        stderr=None,
                        env=self.env
                    )
            if is_ffmpeg:
                time_pattern = re.compile(rb'out_time_ms=(\d+)')
                last_percent = 0.0
                stderr_queue = queue.Queue()

                def read_stderr():
                    try:
                        buffer = b''
                        while True:
                            chunk = self.process.stderr.read(4096)
                            if not chunk:
                                break
                            buffer += chunk
                            while b'\n' in buffer:
                                line, buffer = buffer.split(b'\n', 1)
                                stderr_queue.put(line)
                    except Exception:
                        pass
                    finally:
                        stderr_queue.put(None)

                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stderr_thread.start()

                while True:
                    try:
                        line = stderr_queue.get(timeout=0.1)
                    except queue.Empty:
                        if self.process.poll() is not None:
                            break
                        continue

                    if line is None:  # sentinel = stderr closed
                        break
                    match = time_pattern.search(line)
                    if match and self.total_duration > 0:
                        current_time = int(match.group(1)) / 1_000_000
                        percent = min((current_time / self.total_duration) * 100, 100)
                        if abs(percent - last_percent) >= 0.5:
                            self._emit_progress(percent)
                            last_percent = percent
                    elif b'progress=end' in line:
                        self._emit_progress(100.0)
                stderr_thread.join()
            else:
                if self.progress_bar:
                    tqdm_re = re.compile(rb'(\d{1,3})%\|')
                    buffer = b''
                    last_percent = 0.0
                    while True:
                        chunk = self.process.stdout.read(1024)
                        if not chunk:
                            break
                        buffer += chunk
                        if b'\r' in buffer:
                            parts = buffer.split(b'\r')
                            buffer = parts[-1]
                            for part in parts[:-1]:
                                match = tqdm_re.search(part)
                                if match:
                                    percent = min(float(match.group(1)), 100.0)
                                    if percent - last_percent >= 0.5:
                                        self._emit_progress(percent)
                                        last_percent = percent
            self.process.wait()
            if self._stop_requested:
                return False
            elif self.process.returncode==0:
                self._on_complete()
                return True
            else:
                self._on_error(self.process.returncode)
                return False
        except Exception as e:
            self._on_error(e)
            return False

    def stop(self)->bool:
        self._stop_requested=True
        if self.process and self.process.poll() is None:
            if self.keep_alive:
                # EOF on stdin is the worker's exit signal: it returns from its loop
                # and the OS reclaims its VRAM. terminate/kill only if it hangs.
                try:
                    self.process.stdin.close()
                except Exception:
                    pass
                try:
                    self.process.wait(timeout=15)
                except Exception:
                    pass
            if self.process.poll() is None:
                try:
                    self.process.terminate()
                except Exception:
                    pass
                if self.keep_alive:
                    try:
                        self.process.wait(timeout=5)
                    except Exception:
                        try:
                            self.process.kill()
                            self.process.wait(timeout=5)
                        except Exception:
                            pass
        return False

    def send(self, request:dict)->dict:
        # one request line out, one reply line back. The lock serializes callers
        # (one worker = one model in memory), so threads take turns.
        with self._lock:
            try:
                if not self.keep_alive or self.process is None or self.process.poll() is not None:
                    return {'ok': False, 'error': legends['error_worker_exited'].format(code=self.process.poll() if self.process else None)}
                self.process.stdin.write((json.dumps(request) + '\n').encode('utf-8'))
                self.process.stdin.flush()
                line = self.process.stdout.readline()
                if not line:
                    try:
                        self.process.wait(timeout=10)
                    except Exception:
                        pass
                    return {'ok': False, 'error': legends['error_worker_exited'].format(code=self.process.poll())}
                return json.loads(line)
            except Exception as e:
                return {'ok': False, 'error': legends['error_subprocess'].format(e=e)}