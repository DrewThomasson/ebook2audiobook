import subprocess, re, sys, gradio as gr

class SubprocessPipe:
	def __init__(self, cmd, session, total_duration):
		self.cmd = cmd
		self.session = session
		self.total_duration = total_duration
		self.process = None
		self._stop_requested = False
		self.progress_bar = None
		self.start()  # synchronous — starts immediately (for Gradio compatibility)

	def _on_start(self):
		print("Export started")
		if self.session.get("is_gui_process"):
			self.progress_bar = gr.Progress(track_tqdm=False)
			self.progress_bar(0.0, desc="Starting export...")

	def _on_progress(self, percent):
		sys.stdout.write(f"\rFinal Encoding: {percent:.1f}%")
		sys.stdout.flush()
		if self.session.get("is_gui_process"):
			self.progress_bar(percent / 100, desc="Final Encoding")

	def _on_complete(self):
		print("\nExport completed successfully")
		if self.session.get("is_gui_process"):
			self.progress_bar(1.0, desc="Export completed")

	def _on_error(self, err):
		print(f"\nExport failed: {err}")
		if self.session.get("is_gui_process"):
			self.progress_bar(0.0, desc="Export failed")

	def _on_cancel(self):
		print("\nExport cancelled")
		if self.session.get("is_gui_process"):
			self.progress_bar(0.0, desc="Cancelled")

	def start(self):
		try:
			self._on_start()
			self.process = subprocess.Popen(
				self.cmd,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.PIPE,
				text=False,
				bufsize=0
			)
			time_pattern = re.compile(rb"out_time_ms=(\d+)")
			last_percent = 0.0

			for raw_line in self.process.stderr:
				if self._stop_requested:
					break

				line = raw_line.decode(errors="ignore")
				if self.session.get("cancellation_requested"):
					self.stop()
					self._on_cancel()
					break

				match = time_pattern.search(raw_line)
				if match and self.total_duration > 0:
					current_time = int(match.group(1)) / 1_000_000
					percent = min((current_time / self.total_duration) * 100, 100)
					if abs(percent - last_percent) >= 0.5:
						self._on_progress(percent)
						last_percent = percent
				elif b"progress=end" in raw_line:
					self._on_progress(100)
					break

			self.process.wait()
			if self._stop_requested:
				self._on_cancel()
			elif self.process.returncode == 0:
				self._on_complete()
				return True
			else:
				self._on_error(self.process.returncode)
				return False

		except Exception as e:
			self._on_error(e)
			return False

	def stop(self):
		self._stop_requested = True
		if self.process and self.process.poll() is None:
			try:
				self.process.terminate()
			except Exception:
				pass
