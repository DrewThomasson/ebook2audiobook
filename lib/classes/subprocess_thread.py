import subprocess
import threading
import queue
import os
import time

class SubprocessThread(object):

    def __init__(self, cmd: []):
        self.cmd = cmd
        self.return_code = None
        self.process = None # type: subprocess.Popen
        self.run_time = 0


    @property
    def _default_popen_kwargs(self):
        return {
            "env": os.environ.copy(),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": True,
            "universal_newlines": True,
            "bufsize": 1,
        }


    def _watch_output(self, process: subprocess.Popen, queue):
        for line in iter(process.stderr.readline, ""):
            queue.put(line)
            if process.poll() is not None:
                return

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr


    def start(self, wait_limit = 15):

        start_time = time.time()

        pargs = self._default_popen_kwargs
        if self.cwd is not None:
            pargs['cwd'] = self.cwd

        self.process = subprocess.Popen(self.cmd, **pargs)
        self.returned = None
        last_output = time.time()
        q = queue.Queue()

        t = threading.Thread(target=self._watch_output, args=(self.process, q,))
        t.daemon = True
        t.start()

        while self.returned is None:
            self.returned = self.process.poll()

            delay = last_output-time.time()
            if self.returned is None:
                stdout = f"{last_output-time.time()} waited"
                try:
                    stderr = q.get_nowait()
                except queue.Empty:
                    time.sleep(1)
                else:
                    yield stdout, stderr
                    last_output = time.time()

            if delay > wait_limit:
                print("Waited 15 seconds, breaking")
                break

        self.run_time = time.time() - start_time