import subprocess, re, threading, sys

class SubprocessPipe:
	def __init__(self, cmd, total_duration=0):
		self.cmd = cmd
		self.total_duration = total_duration
		self.progress = 0.0
		self.returncode = None
		self.process = None
		self._stop_requested = False

	def _drain_pipe(self, pipe):
		time_pattern = re.compile(rb"out_time_ms=(\d+)")
		last_print = 0.0
		for raw_line in iter(pipe.readline, b''):
			if self._stop_requested:
				break
			line = raw_line.decode(errors="ignore").strip()
			match = time_pattern.search(raw_line)
			if match and self.total_duration > 0:
				current_time = int(match.group(1)) / 1_000_000
				self.progress = min((current_time / self.total_duration) * 100, 100)
				# print progress every 0.5%
				if abs(self.progress - last_print) >= 0.5:
					sys.stdout.write(f"\rFinal Encoding: {self.progress:.1f}%")
					sys.stdout.flush()
					last_print = self.progress
			elif b"progress=end" in raw_line:
				self.progress = 100.0
				sys.stdout.write("\rFinal Encoding: 100.0%\n")
				sys.stdout.flush()
				break
			elif line and not line.startswith("out_time_ms"):
				# Print other ffmpeg lines (errors, warnings)
				print(line)
		pipe.close()

	def start(self):
		try:
			print("Export started")
			self.process = subprocess.Popen(
				self.cmd,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.PIPE,
				bufsize=0
			)
			threading.Thread(
				target=self._drain_pipe,
				args=(self.process.stderr,),
				daemon=True
			).start()

			self.process.wait()
			self.returncode = self.process.returncode
			if self.returncode == 0:
				print("\nExport completed successfully")
			elif not self._stop_requested:
				print(f"\nExport failed with return code {self.returncode}")
			return self.returncode
		except Exception as e:
			self.returncode = -1
			print(f"\nSubprocessPipe error: {e}")
			return self.returncode

	def stop(self):
		self._stop_requested = True
		if self.process and self.process.poll() is None:
			print("\nExport cancelled")
			try:
				self.process.terminate()
				self.process.wait(timeout=2)
			except Exception:
				pass
			finally:
				self.returncode = -1
				self.progress = 0.0
