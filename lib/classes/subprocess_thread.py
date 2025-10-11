import subprocess
import threading
import queue
import os
import time
import sys
import shutil

class SubprocessThread:
    def __init__(self, cmd, cwd=None, env=None, shell=False):
        self.cmd = cmd
        self.cwd = cwd or os.getcwd()
        self.env = env or os.environ.copy()
        self.shell = shell
        self.process = None
        self.return_code = None
        self.run_time = 0
        self._stop_requested = False

    @property
    def _default_popen_kwargs(self):
        return {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": self.shell,
            "universal_newlines": True,
            "bufsize": 1,
            "cwd": self.cwd,
            "env": self.env,
        }

    def _watch_output(self, process, q):
        for line in iter(process.stderr.readline, ""):
            if line:
                q.put(line)
            if self._stop_requested or process.poll() is not None:
                break
        process.stderr.close()

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass

    def start(self, wait_limit=15):
        start_time = time.time()
        pargs = self._default_popen_kwargs
        # Auto resolve ffmpeg / ffprobe if in PATH
        if isinstance(self.cmd, list):
            self.cmd = " ".join([shutil.which(x) if shutil.which(x) else x for x in self.cmd])
        self.process = subprocess.Popen(self.cmd, **pargs)
        self.returned = None
        last_output = time.time()
        q = queue.Queue()
        t = threading.Thread(target=self._watch_output, args=(self.process, q,))
        t.daemon = True
        t.start()
        while self.returned is None and not self._stop_requested:
            self.returned = self.process.poll()
            try:
                stderr = q.get_nowait()
            except queue.Empty:
                time.sleep(0.1)
            else:
                yield "", stderr
                last_output = time.time()
            if (time.time() - last_output) > wait_limit:
                print("SubprocessThread: Timeout, no output in 15s")
                break
        self.run_time = time.time() - start_time
        self.return_code = self.process.returncode
