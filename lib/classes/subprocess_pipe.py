import subprocess
import re
import sys
import time
import signal
import gradio as gr
from threading import Thread, Event, Lock

class SubprocessPipe:

    def __init__(
        self,
        cmd: list[str],
        is_gui_process: bool,
        total_duration: float,
        msg: str = "Processing",
        timeout: float | None = None,
        stall_timeout: float | None = 30.0,
        stems: list[str] | None = None,
        stem_weights: dict[str, float] | None = None
    ):
        self.cmd = cmd
        self.is_gui_process = is_gui_process
        self.total_duration = total_duration or 0.0
        self.msg = msg
        self.timeout = timeout
        self.stall_timeout = stall_timeout
        self.process = None
        self._stop_requested = False
        self._done = Event()
        self._lock = Lock()
        self.progress_bar = gr.Progress(track_tqdm=False) if self.is_gui_process else None
        self._start_ts = time.time()
        self._last_output_ts = self._start_ts
        self._last_percent = 0.0
        self._overall_percent = 0.0
        self._stems = stems or []
        self._stem_weights = stem_weights or {}
        self._stem_order = list(self._stems)
        self._stem_total_weight = self._compute_total_weight()
        self._completed_weight = 0.0
        self._current_stem = None
        self._stem_progress = 0.0
        self._prev_handlers = {}
        self._install_signal_handlers()
        try:
            self._ok = self._run_process()
        finally:
            self._restore_signal_handlers()

    def __bool__(self) -> bool:
        return bool(getattr(self, "_ok", False))

    def _compute_total_weight(self) -> float:
        if not self._stems:
            return 1.0
        w = 0.0
        for s in self._stems:
            w += float(self._stem_weights.get(s, 1.0))
        return w if w > 0 else float(len(self._stems))

    def _stem_weight(self, stem: str) -> float:
        return float(self._stem_weights.get(stem, 1.0))

    def _on_progress(self, percent: float | None) -> None:
        if percent is None:
            sys.stdout.write(f"\r{self.msg}...")
            sys.stdout.flush()
            if self.progress_bar:
                self.progress_bar(None, desc=self.msg)
            return
        sys.stdout.write(f"\r{self.msg} - {percent:.1f}%")
        sys.stdout.flush()
        if self.progress_bar:
            self.progress_bar(percent / 100.0, desc=self.msg)

    def _on_complete(self) -> None:
        msg = f"{self.msg} completed!"
        print(f"\n{msg}")
        if self.progress_bar:
            self.progress_bar(1.0, desc=msg)

    def _on_error(self, err) -> None:
        msg = f"{self.msg} failed: {err}"
        print(f"\n{msg}")
        if self.progress_bar:
            self.progress_bar(0.0, desc=msg)

    def _install_signal_handlers(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self._prev_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, self._signal_handler)
            except Exception:
                pass

    def _restore_signal_handlers(self) -> None:
        for sig, handler in self._prev_handlers.items():
            try:
                signal.signal(sig, handler)
            except Exception:
                pass

    def _signal_handler(self, signum, frame) -> None:
        self.stop()

    def _kill_process_tree(self) -> None:
        if not self.process:
            return
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                try:
                    self.process.terminate()
                except Exception:
                    pass
                try:
                    self.process.wait(timeout=2)
                except Exception:
                    try:
                        self.process.kill()
                    except Exception:
                        pass
        except Exception:
            pass

    def _set_overall_percent(self, overall: float) -> None:
        overall = max(0.0, min(100.0, overall))
        if overall - self._overall_percent >= 0.25 or overall == 100.0:
            self._overall_percent = overall
            self._on_progress(overall)

    def _update_weighted_progress(self, inner_percent: float | None) -> None:
        if not self._stems:
            if inner_percent is None:
                self._on_progress(None)
            else:
                self._set_overall_percent(inner_percent)
            return
        if self._current_stem is None:
            self._current_stem = self._stem_order[0] if self._stem_order else None
        if inner_percent is None:
            self._on_progress(None)
            return
        self._stem_progress = max(0.0, min(100.0, inner_percent))
        curr_w = self._stem_weight(self._current_stem) if self._current_stem else 0.0
        done = self._completed_weight
        total = self._stem_total_weight
        overall = ((done + (curr_w * (self._stem_progress / 100.0))) / total) * 100.0 if total > 0 else self._stem_progress
        self._set_overall_percent(overall)

    def _mark_stem_done(self, stem: str) -> None:
        if not self._stems:
            return
        if stem in self._stems:
            w = self._stem_weight(stem)
            self._completed_weight += w
            self._completed_weight = min(self._completed_weight, self._stem_total_weight)
            self._current_stem = stem
            self._stem_progress = 100.0
            self._update_weighted_progress(100.0)
            idx = self._stem_order.index(stem) if stem in self._stem_order else -1
            if idx >= 0 and idx + 1 < len(self._stem_order):
                self._current_stem = self._stem_order[idx + 1]
                self._stem_progress = 0.0

    def _watchdog(self) -> None:
        while not self._done.is_set():
            if self._stop_requested:
                self._kill_process_tree()
                return
            now = time.time()
            if self.timeout is not None and (now - self._start_ts) > float(self.timeout):
                self._stop_requested = True
                self._kill_process_tree()
                return
            if self.stall_timeout is not None and (now - self._last_output_ts) > float(self.stall_timeout):
                self._stop_requested = True
                self._kill_process_tree()
                return
            time.sleep(0.2)

    def _reader(self, stream, is_stderr: bool) -> None:
        ffmpeg_time = re.compile(rb"out_time_ms=(\d+)")
        demucs_percent = re.compile(rb"(\d{1,3})%")
        demucs_stem = None
        if self._stems:
            escaped = [re.escape(s).encode() for s in self._stems]
            demucs_stem = re.compile(rb"(" + b"|".join(escaped) + rb")", re.IGNORECASE)
        for raw in iter(stream.readline, b""):
            if self._stop_requested:
                break
            with self._lock:
                self._last_output_ts = time.time()
            if is_stderr:
                m = ffmpeg_time.search(raw)
                if m and self.total_duration > 0:
                    current = int(m.group(1)) / 1_000_000
                    inner = min((current / self.total_duration) * 100.0, 100.0)
                    self._update_weighted_progress(inner)
                    continue
            m = demucs_percent.search(raw)
            if m:
                inner = min(float(m.group(1)), 100.0)
                self._update_weighted_progress(inner)
            else:
                self._update_weighted_progress(None)
            if demucs_stem:
                sm = demucs_stem.search(raw)
                if sm:
                    stem = sm.group(1).decode(errors="ignore").lower()
                    self._mark_stem_done(stem)

    def _run_process(self) -> bool:
        try:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
            t_out = Thread(target=self._reader, args=(self.process.stdout, False), daemon=True)
            t_err = Thread(target=self._reader, args=(self.process.stderr, True), daemon=True)
            t_wd = Thread(target=self._watchdog, daemon=True)
            t_out.start()
            t_err.start()
            t_wd.start()
            self.process.wait()
            self._done.set()
            t_out.join(timeout=1)
            t_err.join(timeout=1)
            if self._stop_requested:
                self._on_error("stopped/timeout")
                return False
            if self.process.returncode == 0:
                self._set_overall_percent(100.0)
                self._on_complete()
                return True
            self._on_error(self.process.returncode)
            return False
        except Exception as e:
            self._done.set()
            self._on_error(e)
            return False

    def stop(self) -> bool:
        self._stop_requested = True
        self._kill_process_tree()
        self._done.set()
        return False