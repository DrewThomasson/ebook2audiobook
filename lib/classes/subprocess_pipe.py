import subprocess, threading, os, time, uuid, tempfile, fcntl, re, gradio as gr

class SubprocessPipe:
    def __init__(self, cmd, session=None, total_duration=0):
        self.cmd = cmd
        self.session = session or {}
        self.total_duration = total_duration
        base_dir = self.session.get("process_dir", tempfile.gettempdir())
        os.makedirs(base_dir, exist_ok=True)
        session_id = self.session.get("id", uuid.uuid4().hex)
        self.pipe_path = os.path.join(base_dir, f"subproc_{session_id}.pipe")
        self.process = None
        self._stop_requested = False
        self.progress_bar = gr.Progress(track_tqdm=False) if self.session.get("is_gui_process") else None

    def _create_pipe(self):
        if os.path.exists(self.pipe_path):
            try:
                os.remove(self.pipe_path)
            except Exception:
                pass
        os.mkfifo(self.pipe_path, mode=0o666)

    def _update_progress(self, percent):
        if self.progress_bar and self.session.get("is_gui_process"):
            self.progress_bar(percent / 100, desc=f"Encoding {percent:.1f}%")
        sys.stdout.write(f"\rExport progress: {percent:.1f}%")
        sys.stdout.flush()

    def start(self):
        self._create_pipe()
        read_fd = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)
        write_fd = os.open(self.pipe_path, os.O_WRONLY)
        os.set_blocking(read_fd, False)
        self.process = subprocess.Popen(
            self.cmd,
            stdout=write_fd,
            stderr=subprocess.STDOUT,
            bufsize=0,
            universal_newlines=True
        )
        time_pattern = re.compile(r"out_time_ms=(\d+)")
        def reader():
            last_update = 0
            while not self._stop_requested:
                try:
                    data = os.read(read_fd, 4096)
                    if not data:
                        if self.process.poll() is not None:
                            break
                        time.sleep(0.05)
                        continue
                    for line in data.decode("utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        match = time_pattern.search(line)
                        if match and self.total_duration > 0:
                            current_time = int(match.group(1)) / 1_000_000
                            percent = min((current_time / self.total_duration) * 100, 100)
                            if percent - last_update >= 0.2:
                                self._update_progress(percent)
                                last_update = percent
                        if "progress=end" in line:
                            self._update_progress(100)
                            return
                        if self.session.get("cancellation_requested"):
                            self.stop()
                            return
                except BlockingIOError:
                    time.sleep(0.05)
                except Exception:
                    break
        t = threading.Thread(target=reader)
        t.daemon = True
        t.start()
        while self.process.poll() is None:
            if self.session.get("cancellation_requested"):
                self.stop()
                break
            time.sleep(0.05)
        self._stop_requested = True
        t.join(timeout=2)
        os.close(read_fd)
        os.close(write_fd)
        try:
            os.remove(self.pipe_path)
        except Exception:
            pass

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass
