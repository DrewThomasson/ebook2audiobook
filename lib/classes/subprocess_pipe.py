import os, subprocess, multiprocessing, sys, gradio as gr

from collections.abc import Callable

class SubprocessPipe:

    def __init__(self, cmd:str, is_gui_process:bool, total_duration:float, msg:str='Processing', on_progress:Callable[[float], None]|None=None)->None:
        self.cmd = cmd
        self.is_gui_process = is_gui_process
        self.total_duration = total_duration
        self.msg = msg
        self.process = None
        self._stop_requested = False
        self.on_progress = on_progress
        self.progress_bar = False
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
        msg = f"\n{self.msg} completed!"
        print(msg)
        if self.progress_bar:
            self.progress_bar(1.0, desc=msg)

    def _on_error(self, err:Exception)->None:
        error = f"{self.msg} failed! {err}"
        print(error)
        if self.progress_bar:
            self.progress_bar(0.0, desc=error)

    def _run_process(self)->bool:
        try:
            import re
            is_ffmpeg = "ffmpeg" in os.path.basename(self.cmd[0])
            if is_ffmpeg:
                self.process = subprocess.Popen(
                    self.cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=False,
                    bufsize=0
                )
            else:
                if self.progress_bar:
                    self.process = subprocess.Popen(
                        self.cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=False,
                        bufsize=0
                    )
                else:
                    self.process = subprocess.Popen(
                        self.cmd,
                        stdout=None,
                        stderr=None,
                        text=False
                    )
            if is_ffmpeg:
                time_pattern=re.compile(rb'out_time_ms=(\d+)')
                last_percent=0.0
                while True:
                    raw_line = self.process.stderr.readline()
                    if not raw_line:
                        break
                    line=raw_line.decode(errors='ignore')
                    match=time_pattern.search(raw_line)
                    if match and self.total_duration > 0:
                        current_time=int(match.group(1))/1_000_000
                        percent=min((current_time/self.total_duration)*100,100)
                        if abs(percent-last_percent) >= 0.5:
                            self._emit_progress(percent)
                            last_percent=percent
                    elif b'progress=end' in raw_line:
                        self._emit_progress(100.0)
                        break
            else:
                if self.progress_bar:
                    tqdm_re = re.compile(rb'(\d{1,3})%\|')
                    last_percent = 0.0
                    buffer = b""
                    while True:
                        chunk = self.process.stdout.read(1024)
                        if not chunk:
                            break
                        buffer += chunk
                        # tqdm updates via \r, keep buffer small
                        if b'\r' in buffer:
                            parts = buffer.split(b'\r')
                            buffer = parts[-1]
                            for part in parts[:-1]:
                                match = tqdm_re.search(part)
                                if match:
                                    percent = min(float(match.group(1)), 100.0)
                                    if percent - last_percent >= 0.5:
                                        yield self._emit_progress(percent)
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
            try:
                self.process.terminate()
            except Exception:
                pass
        return False