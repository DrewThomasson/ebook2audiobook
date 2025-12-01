import os, platform, json, psutil, subprocess, re
from typing import Any

class VRAMDetector:
    def __init__(self):
        self.system = platform.system().lower()

    @staticmethod
    def _fmt(b:int)->float:
        if not b: return 0.0
        return float(f"{b/(1024**3):.2f}")

    def detect_vram(self, device:str, as_json:bool=False)->Any:
        info = {}

        # ───────────────────────────── Jetson (Unified Memory)
        if os.path.exists('/etc/nv_tegra_release'):
            try:
                out = subprocess.check_output(['tegrastats','--interval','1000'],timeout=3).decode()
                m = re.search(r'RAM\s+(\d+)/(\d+)MB',out)
                if m:
                    used=int(m.group(1))*1024*1024
                    total=int(m.group(2))*1024*1024
                    free=total-used
                    info={
                        "os":self.system,
                        "device_type":"jetson",
                        "device_name":"NVIDIA Jetson (Unified Memory)",
                        "used_bytes":used,
                        "free_bytes":free,
                        "total_bytes":total,
                        "used_vram_gb":self._fmt(used),
                        "free_vram_gb":self._fmt(free),
                        "total_vram_gb":self._fmt(total),
                        "note":"Jetson uses unified system RAM as VRAM."
                    }
                    return json.dumps(info,indent=2) if as_json else info
            except Exception:
                mem=psutil.virtual_memory()
                info={
                    "os":self.system,
                    "device_type":"jetson",
                    "device_name":"NVIDIA Jetson (Unified Memory)",
                    "free_bytes":mem.available,
                    "total_bytes":mem.total,
                    "free_vram_gb":self._fmt(mem.available),
                    "total_vram_gb":self._fmt(mem.total),
                    "note":"tegrastats unavailable; reporting system RAM."
                }
                return json.dumps(info,indent=2) if as_json else info

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
                        "free_vram_gb": self._fmt(free),
                        "total_vram_gb": self._fmt(total),
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
                    "free_vram_gb": self._fmt(free),
                    "total_vram_gb": self._fmt(total),
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
                    "free_vram_gb": self._fmt(free),
                    "total_vram_gb": self._fmt(total),
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
                info['free_vram_gb'] = self._fmt(mem.available)
                info['total_vram_gb'] = self._fmt(mem.total)
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
            "free_vram_gb": self._fmt(mem.available),
            "total_vram_gb": self._fmt(mem.total),
        }
        
        vram_dict = json.dumps(info, indent=2) if as_json else info
        total_vram_bytes = vram_dict.get('total_bytes', 4096)
        total_vram_gb = int(((total_vram_bytes / (1024 ** 3) * 100) / 100) + 0.1)
        free_vram_bytes = vram_dict.get('free_bytes', 0)
        free_vram_gb = float(int(free_vram_bytes / (1024 ** 3) * 100) / 100) if free_vram_bytes > 0 else 0
        
        return {"total_vram_gb": total_vram_gb, "free_vram_gb": free_vram_gb}