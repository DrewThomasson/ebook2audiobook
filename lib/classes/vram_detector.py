import os, platform, subprocess, re, json, psutil, tempfile, time

from typing import Any, Optional, Union, Callable

class VRAMDetector:
	def __init__(self)->None:
		self.system:str = platform.system().lower()

	def _run(self, cmd:list[str], timeout:int = 3)->str:
		try:
			result = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.DEVNULL, text = True, timeout = timeout)
			return result.stdout.strip()
		except Exception:
			return ""

	def _parse_bytes(self, val:str)->int:
		if not val:
			return 0
		val = val.strip().upper()
		m = re.findall(r"([\d.]+)", val)
		if not m:
			return 0
		n = float(m[0])
		if "GB" in val: return int(n*1024**3)
		if "MB" in val: return int(n*1024**2)
		if "KB" in val: return int(n*1024)
		return int(n)

	def _fmt(self, b:int)->str:
		if not b: return "Unknown"
		if b> = 1024**3: return f"{b/1024**3:.1f} GB"
		if b> = 1024**2: return f"{b/1024**2:.1f} MB"
		return f"{b} B"

	# ---- Windows GPU detection ----
	def _get_windows_vram(self)->list[dict[str,Any]]:
		gpus = []
		out = self._run(["wmic","path","win32_VideoController","get","Name,AdapterRAM","/format:list"])
		for block in out.split("\n\n"):
			if "Name = " not in block: continue
			name = re.search(r"Name = (.*)", block)
			vram = re.search(r"AdapterRAM = (\d+)", block)
			if name:
				val = int(vram.group(1)) if vram else 0
				gpus.append({"name":name.group(1).strip(),"vram_bytes":val,"vram":self._fmt(val)})
		if any(g["vram_bytes"]>0 for g in gpus):
			return gpus
		with tempfile.NamedTemporaryFile(delete = False, suffix = ".txt") as tf:
			path = tf.name
		try:
			subprocess.Popen(["dxdiag","/t",path],stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
			for _ in range(30):
				if os.path.exists(path) and os.path.getsize(path)>0:
					break
				time.sleep(0.1)
			with open(path,encoding = "utf-16",errors = "ignore") as f:
				data = f.read()
		except Exception:
			data = ""
		finally:
			try: os.remove(path)
			except: pass
		for m in re.finditer(r"Card name:\s*(.*?)\r?\n.*?(?:Dedicated Memory|Display Memory):\s*([^\r\n]+)", data, re.S):
			name,mem = m.groups()
			vb = self._parse_bytes(mem)
			if vb:
				gpus.append({"name":name.strip(),"vram_bytes":vb,"vram":self._fmt(vb)})
		return gpus

	def _get_windows_shared(self)->int:
		try:
			with tempfile.NamedTemporaryFile(delete = False, suffix = ".txt") as tf:
				path = tf.name
			subprocess.Popen(["dxdiag","/t",path],stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
			for _ in range(30):
				if os.path.exists(path) and os.path.getsize(path)>0:
					break
				time.sleep(0.1)
			with open(path,encoding = "utf-16",errors = "ignore") as f:
				data = f.read()
		except Exception:
			data = ""
		finally:
			try: os.remove(path)
			except: pass
		m = re.search(r"Shared Memory:\s*([^\r\n]+)", data)
		return self._parse_bytes(m.group(1)) if m else 0

	# ---- Linux/macOS simplified ----
	def _get_linux_vram(self)->list[dict[str,Any]]:
		out = self._run(["nvidia-smi","--query-gpu = name,memory.total","--format = csv,noheader,nounits"])
		gpus = []
		for line in out.splitlines():
			if "," not in line: continue
			name,mem = line.split(",",1)
			vb = int(mem.strip())*1024**2
			gpus.append({"name":name.strip(),"vram_bytes":vb,"vram":self._fmt(vb)})
		return gpus

	def _get_linux_shared(self)->int:
		return psutil.virtual_memory().total//4 if hasattr(psutil,"virtual_memory") else 0

	def _get_macos_vram(self)->list[dict[str,Any]]:
		out = self._run(["system_profiler","SPDisplaysDataType","-json"])
		try:data = json.loads(out)
		except: return []
		g = []
		for gpu in data.get("SPDisplaysDataType",[]):
			v = self._parse_bytes(gpu.get("spdisplays_vram",""))
			g.append({"name":gpu.get("_name","GPU"),"vram_bytes":v,"vram":self._fmt(v)})
		return g

	def _get_macos_shared(self)->int:
		out = self._run(["system_profiler","SPDisplaysDataType","-json"])
		try:data = json.loads(out)
		except:return 0
		for gpu in data.get("SPDisplaysDataType",[]):
			for key in ("spdisplays_vram_shared","spdisplays_vram_dynamic"):
				if key in gpu:
					return self._parse_bytes(gpu[key])
		return 0

	# ---- main API ----
	def detect_vram(self,as_json:bool = False)->Any:
		sys = self.system
		if sys =  = "windows":
			g = self._get_windows_vram(); s = self._get_windows_shared()
		elif sys =  = "linux":
			g = self._get_linux_vram(); s = self._get_linux_shared()
		elif sys =  = "darwin":
			g = self._get_macos_vram(); s = self._get_macos_shared()
		else:
			g = []; s = 0
		total = sum(x.get("vram_bytes",0) for x in g)
		res = {
			"os":sys,
			"gpu_count":len(g),
			"gpus":g,
			"total_vram_bytes":total,
			"total_vram_human":self._fmt(total),
			"shared_memory_bytes":s,
			"shared_memory_human":self._fmt(s),
			"total_combined_human":self._fmt(total+s)
		}
		return json.dumps(res,indent = 2) if as_json else res
