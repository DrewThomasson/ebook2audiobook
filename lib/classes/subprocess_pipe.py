import subprocess, threading, os, time, uuid, tempfile, stat

class SubprocessPipe:
    def __init__(self, cmd, session=None, total_duration=0):
        self.session = session or {}
        self.total_duration = total_duration
        base_dir = self.session.get("process_dir", tempfile.gettempdir())
        os.makedirs(base_dir, exist_ok=True)
        session_id = self.session.get("id", uuid.uuid4().hex)
        self.pipe_path = os.path.join(base_dir, f"subproc_{session_id}.pipe")
        self.process = None
        self._stop_requested = False
        # prepend stdbuf to disable buffering
        self.cmd = ["stdbuf", "-oL", "-eL"] + cmd

    def _ensure_pipe_exists(self):
        if not os.path.exists(self.pipe_path):
            os.mkfifo(self.pipe_path)
        elif not stat.S_ISFIFO(os.stat(self.pipe_path).st_mode):
            os.remove(self.pipe_path)
            os.mkfifo(self.pipe_path)

    def _reader(self, q):
        while not self._stop_requested:
            self._ensure_pipe_exists()
            try:
                with open(self.pipe_path, "r", encoding="utf-8", errors="ignore") as pipe:
                    for line in iter(pipe.readline, ""):
                        if not line.strip():
                            continue
                        q.append(line.strip())
                        if self._stop_requested or self.session.get("cancellation_requested"):
                            break
            except Exception:
                time.sleep(0.05)

    def start(self):
        self._ensure_pipe_exists()
        output_queue = []
        # launch ffmpeg with output redirected to FIFO
        pipe_writer = open(self.pipe_path, "w")
        self.process = subprocess.Popen(
            self.cmd,
            stdout=pipe_writer,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
        t = threading.Thread(target=self._reader, args=(output_queue,))
        t.daemon = True
        t.start()
        while self.process.poll() is None:
            if self.session.get("cancellation_requested"):
                self.stop()
                break
            time.sleep(0.05)
        self._stop_requested = True
        t.join(timeout=2)
        pipe_writer.close()
        try:
            os.remove(self.pipe_path)
        except Exception:
            pass
        for line in output_queue:
            yield line

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass
