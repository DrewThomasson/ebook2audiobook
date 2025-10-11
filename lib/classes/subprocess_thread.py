import subprocess, threading, queue, os, time

class SubprocessThread:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.return_code = None
        self.run_time = 0
        self._stop_requested = False

    @property
    def _default_popen_kwargs(self):
        return {
            "env": os.environ.copy(),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": False,
            "universal_newlines": True,
            "bufsize": 1
        }

    def _watch_output(self, process, q):
        while True:
            line = process.stdout.readline()
            if not line:
                line = process.stderr.readline()
            if line:
                q.put(line)
            if self._stop_requested or process.poll() is not None:
                break

    def start(self, wait_limit=15):
        start_time = time.time()
        pargs = self._default_popen_kwargs
        self.process = subprocess.Popen(self.cmd, **pargs)
        self.returned = None
        q = queue.Queue()
        t = threading.Thread(target=self._watch_output, args=(self.process, q))
        t.daemon = True
        t.start()
        last_output = time.time()
        while self.returned is None:
            self.returned = self.process.poll()
            delay = time.time() - last_output
            if self.returned is None:
                try:
                    stderr = q.get_nowait()
                except queue.Empty:
                    time.sleep(0.05)
                else:
                    yield "", stderr
                    last_output = time.time()
            if delay > wait_limit:
                break
        self.run_time = time.time() - start_time
        self.return_code = self.process.returncode

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
