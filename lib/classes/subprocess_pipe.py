import subprocess, re, sys, gradio as gr

class SubprocessPipe:
	def __init__(self, cmd, session=None, total_duration=0, on_progress=None, on_error=None, on_complete=None, on_cancel=None):
		self.cmd = cmd
		self.session = session or {}
		self.total_duration = total_duration
		self.on_progress = on_progress
		self.on_error = on_error
		self.on_complete = on_complete
		self.on_cancel = on_cancel
		self.process = None
		self._stop_requested = False
		self.progress_bar = None

	def _emit(self, handler, *args):
		try:
			if callable(handler):
				handler(*args)
		except Exception as e:
			print(f"Emit error: {e}")

	def _on_progress_internal(self, percent):
		sys.stdout.write(f"\rFinal Encoding: {percent:.1f}%")
		sys.stdout.flush()
		try:
			if self.session.get("is_gui_process") and self.progress_bar:
				self.progress_bar(percent / 100, desc="Final Encoding")
		except Exception as e:
			print(f"Progress update error: {e}")

	def start(self):
		try:
			if self.session.get("is_gui_process"):
				self.progress_bar = gr.Progress(track_tqdm=False)

			self.process = subprocess.Popen(
				self.cmd,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.PIPE,
				text=False,
				bufsize=0
			)
			time_pattern = re.compile(r"out_time_ms=(\d+)")
			last_percent = 0.0

			for raw_line in self.process.stderr:
				line = raw_line.decode(errors="ignore")
				if self.session.get("cancellation_requested"):
					self.stop()
					self._emit(self.on_cancel)
					break

				match = time_pattern.search(line)
				if match and self.total_duration > 0:
					current_time = int(match.group(1)) / 1_000_000
					percent = min((current_time / self.total_duration) * 100, 100)
					if abs(percent - last_percent) >= 0.5:
						self._emit(self.on_progress or self._on_progress_internal, percent)
						last_percent = percent
				elif "progress=end" in line:
					self._emit(self.on_progress or self._on_progress_internal, 100)
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
