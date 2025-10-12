import subprocess, re

class SubprocessPipe:
    def __init__(self, cmd, session=None, total_duration=0, on_start=None, on_progress=None, on_complete=None, on_error=None, on_cancel=None):
        self.cmd = cmd
        self.session = session or {}
        self.total_duration = total_duration
        self.on_start = on_start
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        self.on_cancel = on_cancel
        self.process = None
        self._stop_requested = False

    def _emit(self, handler, *args):
        try:
            if callable(handler):
                handler(*args)
        except Exception:
            pass

    def start(self):
        try:
            self._emit(self.on_start)
            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            time_pattern = re.compile(r"out_time_ms=(\d+)")
            last_percent = 0.0
            for line in self.process.stdout:
                if self.session.get("cancellation_requested"):
                    self.stop()
                    self._emit(self.on_cancel)
                    return False
                match = time_pattern.search(line)
                if match and self.total_duration > 0:
                    current_time = int(match.group(1)) / 1_000_000
                    percent = min((current_time / self.total_duration) * 100, 100)
                    if abs(percent - last_percent) >= 0.5:
                        self._emit(self.on_progress, percent)
                        last_percent = percent
                elif "progress=end" in line:
                    self._emit(self.on_progress, 100)
                    break
            self.process.wait()
            if self.process.returncode == 0:
                self._emit(self.on_complete, True)
                return True
            else:
                self._emit(self.on_error, self.process.returncode)
                return False
        except Exception as e:
            self._emit(self.on_error, e)
            return False

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass
