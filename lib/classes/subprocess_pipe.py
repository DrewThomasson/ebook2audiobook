import subprocess, re, sys, gradio as gr

class SubprocessPipe:
    def __init__(self,cmd:str, is_gui_process:bool, total_duration:float, msg:str='Processing'):
        self.cmd = cmd
        self.is_gui_process = is_gui_process
        self.total_duration = total_duration
        self.msg = msg
        self.process = None
        self._stop_requested = False
        self.progress_bar = None
        if self.is_gui_process:
            self.progress_bar=gr.Progress(track_tqdm=False)
        self._run_process()

    def _on_progress(self,percent:float)->None:
        sys.stdout.write(f'\r{self.msg}: {percent:.1f}%')
        sys.stdout.flush()
        if self.is_gui_process:
            self.progress_bar(percent/100, desc=self.msg)

    def _on_complete(self)->None:
        msg = f"\n{self.msg} completed"
        print(msg)
        if self.is_gui_process:
            self.progress_bar(1.0, desc=msg)

    def _on_error(self, err:Exception)->None:
        error = f"\n{self.msg} error: {err}"
        print(error)
        if self.is_gui_process:
            self.progress_bar(0.0, desc=error)

    def _run_process(self)->bool:
        try:
            self.process=subprocess.Popen(
                self.cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=False,
                bufsize=0
            )
            time_pattern=re.compile(rb'out_time_ms=(\d+)')
            last_percent=0.0
            for raw_line in self.process.stderr:
                line=raw_line.decode(errors='ignore')
                match=time_pattern.search(raw_line)
                if match and self.total_duration > 0:
                    current_time=int(match.group(1))/1_000_000
                    percent=min((current_time/self.total_duration)*100,100)
                    if abs(percent-last_percent) >= 0.5:
                        self._on_progress(percent)
                        last_percent=percent
                elif b'progress=end' in raw_line:
                    self._on_progress(100)
                    break
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