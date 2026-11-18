import os, platform, json, psutil, subprocess, re, math

from typing import Any
from lib.conf import NATIVE, FULL_DOCKER

class VRAMDetector:
    def __init__(self):
        self.system = platform.system().lower()

    def _in_docker(self)->bool:
        if os.path.exists("/.dockerenv"):
            return True
        try:
            with open("/proc/1/cgroup", "rt", errors="ignore") as f:
                return any("docker" in line or "containerd" in line for line in f)
        except Exception:
            return False

    def _docker_memory(self):
        paths = [
            "/sys/fs/cgroup/memory.max",                     # cgroups v2
            "/sys/fs/cgroup/memory/memory.limit_in_bytes"   # cgroups v1
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "rt") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            limit = int(val)
                            if limit > 0 and limit < (1 << 60):
                                used = psutil.virtual_memory().used
                                free = max(limit - used, 0)
                                return free, limit
                except Exception:
                    pass
        mem = psutil.virtual_memory()
        return mem.available, mem.total

    def _windows_commit_available(self)->int:
        # bytes the system can still commit (RAM + pagefile). Windows refuses an allocation past the commit limit even with
        # RAM shown free: other programs holding commit (a VM, an Android emulator) leave e2a less than psutil's available.
        # XTTS then died in an access violation building its GPT on CPU, 3.9GB of commit left, 12GB RAM shown free
        try:
            import ctypes
            class MemoryStatusEx(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in ('ullTotalPhys', 'ullAvailPhys', 'ullTotalPageFile', 'ullAvailPageFile', 'ullTotalVirtual', 'ullAvailVirtual', 'ullAvailExtendedVirtual')]
            status = MemoryStatusEx()
            status.dwLength = ctypes.sizeof(MemoryStatusEx)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.ullAvailPageFile)
        except Exception:
            pass
        return 0

    @staticmethod
    def _fmt(b:int)->float:
        if not b: return 0.0
        return float(f"{b/(1024**3):.2f}")

    @staticmethod
    def _ceil_gb(b: int) -> int:
        return math.ceil(b / (1024 ** 3)) if b > 0 else 0

    def detect_vram(self, device:str, script_mode:str, as_json:bool=False)->Any:
        info = {}
        in_docker = self._in_docker()
        try:
            import torch
            # ───────────────────────────── Jetson (Unified Memory)
            if device == 'jetson':
                if os.path.exists('/etc/nv_tegra_release'):
                    try:
                        out = subprocess.check_output(['tegrastats','--interval','1000'],timeout=3).decode()
                        m = re.search(r'RAM\s+(\d+)/(\d+)MB',out)
                        if m:
                            used = int(m.group(1)) * 1024 * 1024
                            total = int(m.group(2)) * 1024 * 1024
                            free = total - used
                            info = {
                                "os": self.system,
                                "device_type": "jetson",
                                "device_name": "NVIDIA Jetson (Unified Memory)",
                                "used_bytes": used,
                                "free_bytes": free,
                                "total_bytes": total,
                                "used_vram_gb": self._ceil_gb(used),
                                "free_vram_gb": self._ceil_gb(free),
                                "total_vram_gb": self._ceil_gb(total),
                                "note": "Jetson uses unified system RAM as VRAM."
                            }
                            return json.dumps(info, indent=2) if as_json else info
                    except (subprocess.CalledProcessError, Exception):
                        mem = psutil.virtual_memory()
                        info = {
                            "os": self.system,
                            "device_type": "jetson",
                            "device_name": "NVIDIA Jetson (Unified Memory)",
                            "free_bytes": mem.available,
                            "total_bytes": mem.total,
                            "free_vram_gb": self._ceil_gb(mem.available),
                            "total_vram_gb": self._ceil_gb(mem.total),
                            "note": "tegrastats unavailable; reporting system RAM."
                        }
                        return json.dumps(info, indent=2) if as_json else info

            # ───────────────────────────── CUDA (NVIDIA)
            elif device == 'cuda':
                if torch.cuda.is_available():
                    free, total = torch.cuda.mem_get_info()
                    alloc = torch.cuda.memory_allocated()
                    resv = torch.cuda.memory_reserved()
                    info = {
                        "os": self.system,
                        "device_type": "cuda",
                        "device_name": torch.cuda.get_device_name(0),
                        "free_bytes": free,
                        "total_bytes": total,
                        "allocated_bytes": alloc,
                        "reserved_bytes": resv,
                        "free_vram_gb": self._ceil_gb(free),
                        "total_vram_gb": self._ceil_gb(total),
                        "allocated_vram_gb": self._ceil_gb(alloc),
                        "reserved_vram_gb": self._ceil_gb(resv),
                    }
                    return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── ROCm (AMD)
            elif device == 'rocm' and hasattr(torch, 'hip') and torch.hip.is_available():
                free, total = torch.hip.mem_get_info()
                alloc = torch.hip.memory_allocated()
                resv = torch.hip.memory_reserved()
                info = {
                    "os": self.system,
                    "device_type": "rocm",
                    "device_name": torch.hip.get_device_name(0),
                    "free_bytes": free,
                    "total_bytes": total,
                    "allocated_bytes": alloc,
                    "reserved_bytes": resv,
                    "free_vram_gb": self._ceil_gb(free),
                    "total_vram_gb": self._ceil_gb(total),
                    "allocated_vram_gb": self._ceil_gb(alloc),
                    "reserved_vram_gb": self._ceil_gb(resv),
                }
                return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── Intel XPU (oneAPI)
            elif device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
                free, total = torch.xpu.mem_get_info()
                alloc = torch.xpu.memory_allocated()
                resv = torch.xpu.memory_reserved()
                info = {
                    "os": self.system,
                    "device_type": "xpu",
                    "device_name": torch.xpu.get_device_name(0),
                    "free_bytes": free,
                    "total_bytes": total,
                    "allocated_bytes": alloc,
                    "reserved_bytes": resv,
                    "free_vram_gb": self._ceil_gb(free),
                    "total_vram_gb": self._ceil_gb(total),
                    "allocated_vram_gb": self._ceil_gb(alloc),
                    "reserved_vram_gb": self._ceil_gb(resv),
                }
                return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── Apple MPS (Metal)
            elif device == 'mps' and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                mem = psutil.virtual_memory()
                info = {
                    "os": self.system,
                    "device_type": "mps",
                    "device_name": "Apple GPU (Metal)",
                    "free_bytes": mem.available,
                    "total_bytes": mem.total,
                    "free_vram_gb": self._ceil_gb(mem.available),
                    "total_vram_gb": self._ceil_gb(mem.total),
                    "note": "PyTorch MPS does not expose memory info; reporting system RAM"
                }
                return json.dumps(info, indent=2) if as_json else info

        except Exception:
            pass

        # ─────────────────────────── CPU / Docker fallback
        if script_mode == FULL_DOCKER and in_docker:
            free, total = self._docker_memory()
            info = {
                "os": self.system,
                "device_type": "docker",
                "device_name": "Docker Container Memory",
                "free_bytes": free,
                "total_bytes": total,
                "free_vram_gb": self._ceil_gb(free),
                "total_vram_gb": self._ceil_gb(total),
                "note": "Running inside Docker container."
            }
        else:
            mem = psutil.virtual_memory()
            free = mem.available
            commit = self._windows_commit_available() if self.system == 'windows' else 0
            if 0 < commit < free:
                free = commit
            info = {
                "os": self.system,
                "device_type": "cpu",
                "device_name": "System RAM",
                "free_bytes": free,
                "total_bytes": mem.total,
                "free_vram_gb": self._ceil_gb(free),
                "total_vram_gb": self._ceil_gb(mem.total),
            }
            if free < mem.available:
                info['note'] = f"Windows commit limit: {self._fmt(commit)}GB left of RAM + pagefile, {self._fmt(mem.available)}GB RAM free"

        if as_json:
            return json.dumps(info, indent=2)

        # both defaults are in BYTES, like the keys they stand in for: 4096 alone
        # was 4 KB, which _ceil_gb rounded to 1GB and passed off as the total.
        total_vram_bytes = info.get('total_bytes', 4 * 1024 ** 3)
        free_vram_bytes = info.get('free_bytes', 0)
        info['total_vram_gb'] = info.get('total_vram_gb', self._ceil_gb(total_vram_bytes))
        info['free_vram_gb'] = info.get('free_vram_gb', self._ceil_gb(free_vram_bytes))

        # same shape as the accelerator branches above, which all return the full
        # dict: callers reaching for os / device_type / device_name / free_bytes /
        # total_bytes used to get None here and nowhere else.
        return info