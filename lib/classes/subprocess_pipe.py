import subprocess, re, threading, sys

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

	# ✅ NEW: drain function for stderr (runs in background)
	def _drain_pipe(self, pipe):
		time_pattern = re.compile(rb"out_time_ms=(\d+)")
		last_percent = 0.0
		for raw_line in iter(pipe.readline, b''):
			if self.session.get("cancellation_requested"):
				self.stop()
				self._emit(self.on_cancel)
				break
			match = time_pattern.search(raw_line)
			if match and self.total_duration > 0:
				current_time = int(match.group(1)) / 1_000_000
				percent = min((current_time / self.total_duration) * 100, 100)
				if abs(percent - last_percent) >= 0.5:
					self._emit(self.on_progress, percent)
					last_percent = percent
			elif b"progress=end" in raw_line:
				self._emit(self.on_progress, 100)
				break
		pipe.close()

	def start(self):
		try:
			self._emit(self.on_start)

			# ✅ Updated subprocess: capture stderr, unbuffered binary mode
			self.process = subprocess.Popen(
				self.cmd,
				stdout=subprocess.DEVNULL,     # don’t capture stdout (faster)
				stderr=subprocess.PIPE,        # progress goes to stderr
				bufsize=0                      # unbuffered binary mode
			)

			# ✅ Start drain thread immediately after Popen
			threading.Thread(target=self._drain_pipe, args=(self.process.stderr,), daemon=True).start()

			# Wait for FFmpeg to finish
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
