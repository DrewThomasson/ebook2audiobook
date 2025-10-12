import subprocess, re, sys, gradio as gr

class SubprocessPipe:
    def __init__(self, cmd, session=None, total_duration=0):
        self.cmd = cmd
        self.session = session or {}
        self.total_duration = total_duration
        self.process = None
        self._stop_requested = False
        self.progress_bar = gr.Progress(track_tqdm=False) if self.session.get("is_gui_process") else None

    def _update_progress(self, percent):
        try:
            sys.stdout.write(f"\rExport progress: {percent:.1f}%")
            sys.stdout.flush()
            if self.session.get("is_gui_process"):
                self.progress_bar(percent / 100, desc=f"Encoding {percent:.1f}%")
        except Exception:
            pass

    def start(self):
        try:
            if self.session.get("is_gui_process"):
                try:
                    self.progress_bar(0.0, desc="Starting export…")
                except Exception:
                    pass
            print("Export started.")
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
                    break
            self.process.wait()
            if self.session.get("is_gui_process"):
                try:
                    if self.process.returncode == 0:
                        self.progress_bar(1.0, desc="Export completed")
                    else:
                        self.progress_bar(0.0, desc="Export failed")
                except Exception:
                    pass
            print("\nExport process finished.")
            return self.process.returncode == 0
        except Exception as e:
            print(f"SubprocessPipe start error: {e}")
            if self.session.get("is_gui_process"):
                try:
                    self.progress_bar(0.0, desc="Export error")
                except Exception:
                    pass
            return False

    def stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                print("\nExport process cancelled.")
                if self.session.get("is_gui_process"):
                    try:
                        self.progress_bar(0.0, desc="Cancelled")
                    except Exception:
                        pass
            except Exception:
                pass