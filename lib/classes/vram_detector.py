import os, platform, json, psutil, subprocess, re
from typing import Any

class VRAMDetector:
    def __init__(self):
        self.system = platform.system().lower()

    @staticmethod
    def _fmt(b:int)->str:
        if not b: return 'Unknown'
        if b >= 1024**3: return f'{b/1024**3:.2f} GB'
        if b >= 1024**2: return f'{b/1024**2:.2f} MB'
        if b >= 1024: return f'{b/1024:.2f} KB'
        return f'{b} B'

    def detect_vram(self, device:str, as_json:bool=False)->Any:
        info = {}
        # ───────────────────────────── CUDA (NVIDIA)
        try:
            import torch
            if device == 'cuda':
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
                        "free_human": self._fmt(free),
                        "total_human": self._fmt(total),
                        "allocated_human": self._fmt(alloc),
                        "reserved_human": self._fmt(resv),
                    }
                    return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── ROCm (AMD)
            if hasattr(torch, 'hip') and torch.hip.is_available():
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
                    "free_human": self._fmt(free),
                    "total_human": self._fmt(total),
                    "allocated_human": self._fmt(alloc),
                    "reserved_human": self._fmt(resv),
                }
                return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── Intel XPU (oneAPI)
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
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
                    "free_human": self._fmt(free),
                    "total_human": self._fmt(total),
                    "allocated_human": self._fmt(alloc),
                    "reserved_human": self._fmt(resv),
                }
                return json.dumps(info, indent=2) if as_json else info

            # ─────────────────────────── Apple MPS (Metal)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                info = {
                    "os": self.system,
                    "device_type": "mps",
                    "device_name": "Apple GPU (Metal)",
                    "note": "PyTorch MPS does not expose memory info; reporting system RAM",
                }
                mem = psutil.virtual_memory()
                info['free_bytes'] = mem.available
                info['total_bytes'] = mem.total
                info['free_human'] = self._fmt(mem.available)
                info['total_human'] = self._fmt(mem.total)
                return json.dumps(info, indent=2) if as_json else info

        except Exception:
            pass

        # ─────────────────────────── CPU fallback
        mem = psutil.virtual_memory()
        info = {
            "os": self.system,
            "device_type": "cpu",
            "device_name": "System RAM",
            "free_bytes": mem.available,
            "total_bytes": mem.total,
            "free_human": self._fmt(mem.available),
            "total_human": self._fmt(mem.total),
        }
        return json.dumps(info, indent=2) if as_json else info