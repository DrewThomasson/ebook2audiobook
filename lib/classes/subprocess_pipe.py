import subprocess, threading, re, sys, time, gradio as gr

class SubprocessPipe:
    def __init__(self, cmd, session=None, total_duration=0):
        self.cmd = cmd
        self.session = session or {}
        self.total_duration = total_duration
        self.process = None
        self._stop_requested = False
        self.progress_bar = gr.Progress(track_tqdm=False) if self.session.get("is_gui_process") else None

    def _update_progress(self, percent):
        sys.stdout.write(f"\rExport progress: {percent:.1f}%")
        sys.stdout.flush()
        if self.progress_bar and self.session.get("is_gui_process"):
            try:
                self.progress_bar(percent / 100, desc=f"Encoding {percent:.1f}%")
                time.sleep(0.01)
            except Exception as e:
                print(e)
                pass
        else:
            print('self.progress_bar failed')

    def start(self):
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
                break
            match = time_pattern.search(line)
            if match and self.total_duration > 0:
                current_time = int(match.group(1)) / 1_000_000
                percent = min((current_time / self.total_duration) * 100, 100)
                if abs(percent - last_percent) >= 0.5:
                    self._update_progress(percent)
                    last_percent = percent
            elif "progress=end" in line:
                self._update_progress(100)
        self.process.wait()
        print()
        return self.process.returncode == 0

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass
