import os, re, sys, platform, shutil, subprocess, json, importlib

from functools import cached_property
from typing import Union
from importlib.metadata import version, PackageNotFoundError
from lib.conf import *

class DeviceInstaller():
    
    def __init__(self):
        self.system = sys.platform
        self.python_version = sys.version_info[:2]
        self.python_version_tuple = sys.version_info

    @cached_property
    def check_platform(self)->str:
        return self.detect_platform_tag()

    @cached_property
    def check_arch(self)->str:
        return self.detect_arch_tag()

    @cached_property
    def check_hardware(self)->tuple:
        return self.detect_device()

    def check_device_info(self, mode:str)->str:
        os_env = None
        if mode == NATIVE:
            name, tag, msg = self.check_hardware
            arch = self.check_arch
            pyvenv = list(sys.version_info[:2])
            os_env = 'linux' if name == 'jetson' else self.check_platform
        else:
            if mode == BUILD_DOCKER:
                name, tag, msg = self.check_hardware
                arch = self.check_arch
                pyvenv = list(sys.version_info[:2])
                os_env = 'linux' if name == 'jetson' else 'manylinux_2_28'
                pyvenv = [3, 10] if tag in ['jetson60', 'jetson61'] else pyvenv
                device_info = {"name":name,"os":os_env,"arch":arch,"pyvenv":pyvenv,"tag":tag,"note":msg}
                with open('.device_info.json', 'w', encoding='utf-8') as f:
                    json.dump(device_info, f)
                return json.dumps(device_info)
            elif mode == FULL_DOCKER:
                try:
                    with open('.device_info.json', 'r', encoding='utf-8') as f:
                        return json.dumps(json.load(f))
                except FileNotFoundError:
                    return ''
        if all([name, tag, os_env, arch, pyvenv]):
            device_info = {"name":name,"os":os_env,"arch":arch,"pyvenv":pyvenv,"tag":tag,"note":msg}
            return json.dumps(device_info)
        return ''
        
    def get_package_version(self, pkg:str)->Union[str, bool]:
        try:
            return version(pkg)
        except PackageNotFoundError:
            return False

    def detect_platform_tag(self)->str:
        if self.system == systems['WINDOWS']:
            return 'win'
        if self.system == systems['MACOS']:
            return 'macosx_11_0'
        if self.system == systems['LINUX']:
            return 'manylinux_2_28'
        return 'unknown'

    def detect_arch_tag(self)->str:
        m=platform.machine().lower()
        if m in ('x86_64','amd64'):
            return m
        if m in ('aarch64','arm64'):
            return m
        return 'unknown'

    def detect_device(self)->str:

        def has_cmd(cmd:str)->bool:
            return shutil.which(cmd) is not None

        def try_cmd(cmd:str)->str:
            try:
                out = subprocess.check_output(
                    cmd,
                    shell = True,
                    stderr = subprocess.DEVNULL
                )
                return out.decode().lower()
            except Exception:
                return ''

        def lib_version_parse(text:str)->Union[str, None]:
            if not text:
                return None
            text = text.strip()
            if text.startswith('{'):
                try:
                    import json
                    obj = json.loads(text)

                    if isinstance(obj, dict):
                        # New CUDA JSON
                        if 'cuda' in obj and isinstance(obj['cuda'], dict):
                            v = obj['cuda'].get('version')
                            if v:
                                return str(v)

                        # Old JSON format
                        v = obj.get('version')
                        if v:
                            return str(v)

                except Exception:
                    pass
            m = re.search(
                r'cuda\s*version\s*([0-9]+(?:\.[0-9]+){1,2})',
                text,
                re.IGNORECASE
            )
            if m:
                return m.group(1)
            m = re.search(
                r'cuda\s*([0-9]+(?:\.[0-9]+)?)',
                text,
                re.IGNORECASE
            )
            if m:
                return m.group(1)
            m = re.search(
                r'rocm\s*version\s*([0-9]+(?:\.[0-9]+){0,2})',
                text,
                re.IGNORECASE
            )
            if m:
                parts = m.group(1).split('.')
                return f"{parts[0]}.{parts[1] if len(parts) > 1 else 0}"

            m = re.search(
                r'hip\s*version\s*([0-9]+(?:\.[0-9]+){0,2})',
                text,
                re.IGNORECASE
            )
            if m:
                parts = m.group(1).split('.')
                return f"{parts[0]}.{parts[1] if len(parts) > 1 else 0}"
            m = re.search(
                r'(oneapi|xpu)\s*(toolkit\s*)?version\s*([0-9]+(?:\.[0-9]+)?)',
                text,
                re.IGNORECASE
            )
            if m:
                return m.group(3)
            return None

        def toolkit_version_compare(version_str:Union[str, None], version_range:dict)->Union[int, None]:
            if version_str is None:
                return None
            min_tuple = tuple(version_range.get('min', (0, 0)))
            max_tuple = tuple(version_range.get('max', (0, 0)))
            if min_tuple == (0, 0) and max_tuple == (0, 0):
                return 0
            parts = version_str.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            current = (major, minor)
            if min_tuple != (0, 0) and current < min_tuple:
                return -1
            if max_tuple != (0, 0) and current > max_tuple:
                return 1
            return 0

        def tegra_version()->str:
            if os.path.exists('/etc/nv_tegra_release'):
                return try_cmd('cat /etc/nv_tegra_release')
            return ''

        def jetpack_version(text:str)->str:
            m1 = re.search(r'r(\d+)', text)
            m2 = re.search(r'revision:\s*([\d\.]+)', text)
            msg = ''
            if not m1 or not m2:
                msg = 'Unrecognized JetPack version. Falling back to CPU.'
                return ('unknown', msg)
            l4t_major = int(m1.group(1))
            rev = m2.group(1)
            parts = rev.split('.')
            rev_major = int(parts[0])
            rev_minor = int(parts[1]) if len(parts) > 1 else 0
            rev_patch = int(parts[2]) if len(parts) > 2 else 0
            if l4t_major < 36:
                msg = f'JetPack too old (L4T {l4t_major}). Please upgrade to JetPack 6.0+. Falling back to CPU.'
                return ('unsupported', msg)
            else:
                if rev_major == 2:
                    return ('60', msg)
                else:
                    return ('61', msg)
                msg = 'Unrecognized JetPack 6.x version. Falling back to CPU.'
            return ('unknown', msg)

        def has_amd_gpu_pci():
            # macOS: no ROCm-capable AMD GPUs
            if self.system == systems['MACOS']:
                return False
            # ---------- Linux ----------
            if os.name == "posix":
                sysfs = "/sys/bus/pci/devices"
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f"{dev}/vendor") as f:
                                if f.read().strip() not in ("0x1002", "0x1022"):
                                    continue
                            with open(f"{dev}/class") as f:
                                cls = f.read().strip()
                                if cls.startswith("0x0300") or cls.startswith("0x0302"):
                                    return True
                        except Exception:
                            pass
                if has_cmd("lspci"):
                    out = try_cmd("lspci -nn").lower()
                    return (
                        ("1002:" in out or "1022:" in out) and
                        (" vga " in out or " 3d " in out)
                    )
                return False
            # ---------- Windows ----------
            # Hardware may exist, but ROCm will still be disabled
            if os.name == "nt":
                if has_cmd("wmic"):
                    out = try_cmd("wmic path win32_VideoController get Name,PNPDeviceID").lower()
                    return "ven_1002" in out
                if has_cmd("powershell"):
                    out = try_cmd('powershell -Command "Get-PnpDevice -Class Display | Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return "ven_1002" in out
                return False
            return False

        def has_working_rocm():
            # ROCm does not exist on macOS or Windows (runtime)
            if self.system != systems['LINUX']:
                return False
            # /dev/kfd is required but not sufficient
            if not os.path.exists("/dev/kfd"):
                return False
            # rocminfo is the authoritative runtime check
            if not has_cmd("rocminfo"):
                return False
            out = try_cmd("rocminfo").lower()
            if not out:
                return False
            # Must enumerate agents
            if "agent" not in out or "gpu" not in out:
                return False
            # Guard against broken installs
            if "error" in out or "failed" in out:
                return False
            return True

        def has_nvidia_gpu_pci():
            # macOS: NVIDIA GPUs are unsupported → always False
            if self.system == systems['MACOS']:
                return False
            # ---------- Linux ----------
            if os.name == "posix":
                sysfs = "/sys/bus/pci/devices"
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f"{dev}/vendor") as f:
                                if f.read().strip() != "0x10de":
                                    continue
                            with open(f"{dev}/class") as f:
                                cls = f.read().strip()
                                if cls.startswith("0x0300") or cls.startswith("0x0302"):
                                    return True
                        except Exception:
                            pass
                if has_cmd("lspci"):
                    out = try_cmd("lspci -nn").lower()
                    return "10de:" in out and (" vga " in out or " 3d " in out)
                return False
            # ---------- Windows ----------
            if os.name == "nt":
                if has_cmd("nvidia-smi"):
                    return True
                if has_cmd("wmic"):
                    out = try_cmd(
                        "wmic path win32_VideoController get Name,PNPDeviceID"
                    ).lower()
                    return "ven_10de" in out and "display" in out
                if has_cmd("powershell"):
                    out = try_cmd(
                        'powershell -Command "Get-PnpDevice -Class Display | '
                        'Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return "ven_10de" in out
                return False
            return False

        def is_wsl2():
            if os.name != "posix":
                return False
            try:
                with open("/proc/version", "r", encoding="utf-8", errors="ignore") as f:
                    return "microsoft" in f.read().lower()
            except Exception:
                return False

        def has_working_cuda():
            if self.system == systems['MACOS']:
                return False
            if not has_cmd("nvidia-smi"):
                return False
            out = try_cmd("nvidia-smi -L").lower()
            if not out:
                return False
            if "failed" in out or "error" in out or "no devices were found" in out:
                return False
            return "gpu" in out

        def has_intel_gpu_pci():
            # macOS: Intel GPUs exist but XPU runtime is not supported
            if self.system == systems['MACOS']:
                return False
            # ---------- Linux ----------
            if os.name == "posix":
                sysfs = "/sys/bus/pci/devices"
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f"{dev}/vendor") as f:
                                if f.read().strip() != "0x8086":
                                    continue
                            with open(f"{dev}/class") as f:
                                cls = f.read().strip()
                                if cls.startswith("0x0300") or cls.startswith("0x0302"):
                                    return True
                        except Exception:
                            pass
                if has_cmd("lspci"):
                    out = try_cmd("lspci -nn").lower()
                    return "8086:" in out and (" vga " in out or " 3d " in out)
                return False
            # ---------- Windows ----------
            if os.name == "nt":
                if has_cmd("wmic"):
                    out = try_cmd(
                        "wmic path win32_VideoController get Name,PNPDeviceID"
                    ).lower()
                    return "ven_8086" in out
                if has_cmd("powershell"):
                    out = try_cmd(
                        'powershell -Command "Get-PnpDevice -Class Display | '
                        'Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return "ven_8086" in out
                return False
            return False

        def has_working_xpu():
            # No XPU on macOS
            if self.system == systems['MACOS']:
                return False
            # ---------- Linux ----------
            if os.name == "posix":
                # Must have render node
                if not os.path.exists("/dev/dri/renderD128"):
                    return False
                # Prefer Level Zero runtime check
                if has_cmd("sycl-ls"):
                    out = try_cmd("sycl-ls").lower()
                    if "level-zero" in out and "gpu" in out:
                        return True
                if has_cmd("clinfo"):
                    out = try_cmd("clinfo").lower()
                    if "intel" in out and "gpu" in out:
                        return True
                return False
            # ---------- Windows ----------
            if os.name == "nt":
                # XPU runtime is exposed via Intel GPU drivers + PyTorch
                # Best signal: oneAPI / Level Zero tooling
                if has_cmd("sycl-ls"):
                    out = try_cmd("sycl-ls").lower()
                    return "gpu" in out
                return False
            return False

        name = None
        tag = None
        msg = ''
        arch = platform.machine().lower()
        forced_tag = os.environ.get("DEVICE_TAG")

        if forced_tag:
            tag_letters = re.match(r"[a-zA-Z]+", forced_tag)
            if tag_letters:
                tag_letters = tag_letters.group(0).lower()
                name = 'cuda' if tag_letters == 'cu' else 'rocm' if tag_letters == 'rocm' else 'jetson' if tag_letters == 'jetson' else 'xpu' if tag_letters == 'xpu' else 'mps' if tag_letters == 'mps' else 'cpu'
                devices[name.upper()]['found'] = True
                tag = forced_tag
                msg = f'Hardware forced from DEVICE_TAG={tag}'
            else:
                msg = f'DEVICE_TAG not valid'
        else:
            # ============================================================
            # JETSON
            # ============================================================
            if arch in ('aarch64','arm64') and (os.path.exists('/etc/nv_tegra_release') or 'tegra' in try_cmd('cat /proc/device-tree/compatible')):
                raw = tegra_version()
                jp_code, msg = jetpack_version(raw)
                if jp_code in ['unsupported', 'unknown']:
                    pass
                elif os.path.exists('/etc/nv_tegra_release'):
                    devices['JETSON']['found'] = True
                    name = 'jetson'
                    tag = f'jetson{jp_code}'
                elif os.path.exists('/proc/device-tree/compatible'):
                    out = try_cmd('cat /proc/device-tree/compatible')
                    if 'tegra' in out:
                        devices['JETSON']['found'] = True
                        name = 'jetson'
                        tag = f'jetson{jp_code}'
                else:
                    out = try_cmd('uname -a')
                    if 'tegra' in out:
                        msg = 'Jetson GPU detected but not(?) compatible'
                    
            # ============================================================
            # ROCm
            # ============================================================
            elif has_working_rocm() and has_amd_gpu_pci():
                version = ''
                msg = ''
                if os.name == 'posix':
                    for p in (
                        '/opt/rocm/.info/version',
                        '/opt/rocm/version',
                    ):
                        if os.path.exists(p):
                            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                v = f.read()
                                version = lib_version_parse(v)
                            break
                elif os.name == 'nt':
                    for env in ('ROCM_PATH', 'HIP_PATH'):
                        base = os.environ.get(env)
                        if base:
                            for p in (
                                os.path.join(base, 'version'),
                                os.path.join(base, '.info', 'version'),
                            ):
                                if os.path.exists(p):
                                    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                        v = f.read()
                                        version = lib_version_parse(v)
                                    break
                        if version:
                            break
                if version:
                    cmp = toolkit_version_compare(version, rocm_version_range)
                    min_version = rocm_version_range["min"]
                    max_version = rocm_version_range["max"]
                    min_version_str = ".".join(map(str, min_version)) if isinstance(min_version, (tuple, list)) else str(min_version)
                    max_version_str = ".".join(map(str, max_version)) if isinstance(max_version, (tuple, list)) else str(max_version)
                    if cmp == -1:
                        msg = f'ROCm {version} < min {min_version_str}. Please upgrade.'
                    elif cmp == 1:
                        msg = f'ROCm {version} > max {max_version_str}. Falling back to CPU.'
                    elif cmp == 0:
                        devices['ROCM']['found'] = True
                        parts = version.split(".")
                        major = parts[0]
                        minor = parts[1] if len(parts) > 1 else 0
                        name = 'rocm'
                        tag = f'rocm{major}{minor}'
                    else:
                        msg = 'ROCm GPU detected but not compatible or ROCm runtime is missing.'
                else:
                    msg = 'ROCm hardware detected but AMD ROCm base runtime not installed.'

            # ============================================================
            # CUDA
            # ============================================================
            elif has_working_cuda() and (has_nvidia_gpu_pci() or is_wsl2()):
                version = ''
                msg = ''
                # 1) CUDA RUNTIME detection
                try:
                    import ctypes
                    libcudart = None
                    if os.name == "nt":
                        min_major, min_minor = cuda_version_range["min"]
                        max_major, max_minor = cuda_version_range["max"]
                        for major in range(min_major, max_major + 1):
                            start_minor = min_minor if major == min_major else 0
                            end_minor = max_minor if major == max_major else 9
                            for minor in range(start_minor, end_minor + 1):
                                dll = f"cudart64_{major}{minor}.dll"
                                try:
                                    libcudart = ctypes.CDLL(dll)
                                    break
                                except OSError:
                                    pass
                            if libcudart:
                                break
                    else:
                        # Linux + WSL2
                        libcudart = ctypes.CDLL("libcudart.so")
                    if libcudart:
                        v_int = ctypes.c_int()
                        if libcudart.cudaRuntimeGetVersion(ctypes.byref(v_int)) == 0:
                            device_count = ctypes.c_int()
                            if libcudart.cudaGetDeviceCount(ctypes.byref(device_count)) == 0:
                                v = v_int.value
                                major = v // 1000
                                minor = (v % 1000) // 10
                                if device_count.value > 0:
                                    version = f'{major}.{minor}'
                                else:
                                    msg = f'Runtime present ({major}.{minor}) but no devices.'
                except (OSError, AttributeError):
                    pass
                # CUDA TOOLKIT detection (fallback only)
                if not version:
                    if os.name == 'posix':
                        for p in (
                            '/usr/local/cuda/version.json',
                            '/usr/local/cuda/version.txt',
                        ):
                            if os.path.exists(p):
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    v = f.read()
                                    version = lib_version_parse(v)
                                break
                    elif os.name == 'nt':
                        cuda_path = os.environ.get('CUDA_PATH')
                        if cuda_path:
                            for p in (
                                os.path.join(cuda_path, 'version.json'),
                                os.path.join(cuda_path, 'version.txt'),
                            ):
                                if os.path.exists(p):
                                    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                        v = f.read()
                                        version = lib_version_parse(v)
                                    break
                if version:
                    cmp = toolkit_version_compare(version, cuda_version_range)
                    min_ver = ".".join(str(part) for part in cuda_version_range["min"])
                    max_ver = ".".join(str(part) for part in cuda_version_range["max"])
                    if cmp == -1:
                        msg = f'CUDA {version} < min {min_ver}. Please upgrade.'
                    elif cmp == 1:
                        msg = f'CUDA {version} > max {max_ver}. Falling back to CPU.'
                    elif cmp == 0:
                        devices['CUDA']['found'] = True
                        parts = version.split(".")
                        major = parts[0]
                        minor = parts[1] if len(parts) > 1 else 0
                        name = 'cuda'
                        tag = f'cu{major}{minor}'
                    else:
                        msg = 'Cuda GPU detected but not compatible or Cuda runtime is missing.'
                else:
                    msg = 'CUDA Toolkit or Runtime not installed or hardware not detected.'

            # ============================================================
            # INTEL XPU
            # ============================================================
            elif has_working_xpu() and has_intel_gpu_pci():
                version = ''
                msg = ''
                if os.name == 'posix':
                    for p in (
                        '/opt/intel/oneapi/version.txt',
                        '/opt/intel/oneapi/compiler/latest/version.txt',
                        '/opt/intel/oneapi/runtime/latest/version.txt',
                    ):
                        if os.path.exists(p):
                            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                v = f.read()
                                version = lib_version_parse(v)
                            break
                elif os.name == 'nt':
                    oneapi_root = os.environ.get('ONEAPI_ROOT')
                    if oneapi_root:
                        for p in (
                            os.path.join(oneapi_root, 'version.txt'),
                            os.path.join(oneapi_root, 'compiler', 'latest', 'version.txt'),
                            os.path.join(oneapi_root, 'runtime', 'latest', 'version.txt'),
                        ):
                            if os.path.exists(p):
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    v = f.read()
                                    version = lib_version_parse(v)
                                break
                if version:
                    cmp = toolkit_version_compare(version, xpu_version_range)
                    if cmp == -1 or cmp == 1:
                        range_display = (
                            f"{xpu_version_range.get('min')} to {xpu_version_range.get('max')}"
                            if isinstance(xpu_version_range, dict)
                            and 'min' in xpu_version_range
                            and 'max' in xpu_version_range
                            else str(xpu_version_range)
                        )
                        msg = f'XPU {version} out of supported range {range_display}. Falling back to CPU.'
                    elif cmp == 0:
                        devices['XPU']['found'] = True
                        name = 'xpu'
                        tag = 'xpu'
                    else:
                        msg = 'Intel GPU detected but Intel oneAPI Base Toolkit not installed.'
                else:
                    msg = 'Intel GPU detected but oneAPI toolkit version file not found.'

            # ============================================================
            # APPLE MPS
            # ============================================================
            elif self.system == systems['MACOS'] and arch in ('arm64', 'aarch64'):
                devices['MPS']['found'] = True
                name = 'mps'
                tag = 'mps'

            # ============================================================
            # CPU
            # ============================================================
            if tag is None:
                name = 'cpu'
                tag = 'cpu'

        name, tag, msg = (v.strip() if isinstance(v, str) else v for v in (name, tag, msg))
        return (name, tag, msg)

    def version_pkg(self, pkg_name:str, local_path:str|None=None)->str|None:
        if pkg_name:
            try:
                return version(pkg_name)
            except PackageNotFoundError:
                pass
        if not local_path or not os.path.isdir(local_path):
            return None
        version_file = os.path.join(local_path, "version.txt")
        if os.path.exists(version_file):
            try:
                with open(version_file, "r", encoding = "utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return None

    def version_tuple(self, v:str, max_parts:int=3)->tuple:
        m = re.search(r"\d+(?:\.\d+)*", v)
        if not m:
            return (0,) * max_parts
        nums = [int(n) for n in m.group(0).split(".")[:max_parts]]
        return tuple(nums + [0] * (max_parts - len(nums)))

    def eval_marker(self, marker_part:str)->tuple|bool:
        env = {
            "python_version": ".".join(map(str, sys.version_info[:2])),
            "sys_platform": sys.platform,
            "platform_system": platform.system(),
            "platform_machine": platform.machine()
        }
        m = re.match(r'(\w+)\s*(==|!=|>=|<=|>|<)\s*["\']([^"\']+)["\']', marker_part)
        if not m:
            raise ValueError(f"Unsupported marker: {marker_part}")
        key, op, value = m.groups()
        if key not in env:
            raise ValueError(f"Unknown marker variable: {key}")
        def vt(v): return tuple(map(int, v.split("."))) if v[0].isdigit() else v
        left = vt(env[key])
        right = vt(value)
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == ">=": return left >= right
        if op == "<=": return left <= right
        if op == ">": return left > right
        if op == "<": return left < right
        return False

    def install_python_packages(self)->int:
        if not os.path.exists(requirements_file):
            error = f'Warning: File {requirements_file} not found. Skipping package check.'
            print(error)
            return 1
        try:
            system = sys.platform
            arch = platform.machine().lower()
            with open(requirements_file, 'r') as f:
                contents = f.read().replace('\r', '\n')
                packages = [pkg.strip() for pkg in contents.splitlines() if pkg.strip() and re.search(r'[a-zA-Z0-9]', pkg)]
            if sys.version_info >= (3, 11):
                packages.append("pymupdf-layout")
                if system == systems['MACOS'] and arch == 'x86_64':
                    packages = [('torchaudio==2.2.2' if p.startswith('torchaudio==') else 'torch==2.2.2' if p.startswith('torch==') else p) for p in packages]
            missing_packages = []
            for package in packages:
                raw_pkg = package.strip()
                clean_pkg = re.sub(r'\[.*?\]', '', raw_pkg)
                local_path = None
                pkg_name = None
                if os.path.isdir(clean_pkg):
                    local_path = os.path.abspath(clean_pkg)
                else:
                    vcs_match = re.search(r'([\w\-]+)\s*@?\s*git\+', clean_pkg)
                    if vcs_match:
                        pkg_name = vcs_match.group(1)
                    else:
                        pkg_base = re.split(r'[<>=!]', clean_pkg, maxsplit=1)[0].strip()
                        pkg_name = pkg_base
                if ';' in raw_pkg:
                    pkg_part, marker_part = raw_pkg.split(';', 1)
                    marker_part = marker_part.strip()
                    try:
                        if not self.eval_marker(marker_part):
                            continue
                    except Exception as e:
                        print(f'Warning: Could not evaluate marker {marker_part} for {pkg_part}: {e}')
                    raw_pkg = pkg_part.strip()
                if 'git+' in raw_pkg or '://' in raw_pkg:
                    spec = importlib.util.find_spec(pkg_name)
                    if spec is None:
                        print(f'{pkg_name} (git package) is missing.')
                        missing_packages.append(raw_pkg)
                    continue
                if local_path:
                    pkg_name = os.path.basename(local_path)
                    vendor_version = self.version_pkg(None, local_path)
                    if not vendor_version:
                        print(f'{local_path} has no detectable version.')
                        missing_packages.append(raw_pkg)
                        continue
                    try:
                        installed_version = version(pkg_name)
                    except PackageNotFoundError:
                        print(f'{pkg_name} is not installed.')
                        missing_packages.append(raw_pkg)
                        continue
                    if installed_version != vendor_version:
                        print(f'{pkg_name} version mismatch: installed {installed_version} != vendor {vendor_version}.')
                        missing_packages.append(raw_pkg)
                    continue
                installed_version = self.version_pkg(pkg_name, None)
                if not installed_version:
                    print(f'{pkg_name} is not installed.')
                    missing_packages.append(raw_pkg)
                    continue
                if '+' in installed_version:
                    installed_version = installed_version.split('+', 1)[0]
                pkg_spec_part = re.split(r'[<>=!]', clean_pkg, maxsplit=1)
                spec_str = clean_pkg[len(pkg_spec_part[0]):].strip()
                if spec_str:
                    req_match = re.search(r'(==|!=|>=|<=|>|<)\s*(\d+\.\d+(?:\.\d+)?)', spec_str)
                    if req_match:
                        op, req_ver = req_match.groups()
                        req_v = self.version_tuple(req_ver, 3)
                        norm_match = re.match(r'^(\d+\.\d+(?:\.\d+)?)', installed_version)
                        short_version = norm_match.group(1) if norm_match else installed_version
                        installed_v = self.version_tuple(short_version, 3)
                        if op == '==' and installed_v != req_v:
                            print(f'{pkg_name} (installed {installed_version}) != required {req_ver}.')
                            missing_packages.append(raw_pkg)
                        elif op == '>=' and installed_v < req_v:
                            print(f'{pkg_name} (installed {installed_version}) < required {req_ver}.')
                            missing_packages.append(raw_pkg)
                        elif op == '<=' and installed_v > req_v:
                            print(f'{pkg_name} (installed {installed_version}) > allowed {req_ver}.')
                            missing_packages.append(raw_pkg)
                        elif op == '>' and installed_v <= req_v:
                            print(f'{pkg_name} (installed {installed_version}) <= required {req_ver}.')
                            missing_packages.append(raw_pkg)
                        elif op == '<' and installed_v >= req_v:
                            print(f'{pkg_name} (installed {installed_version}) >= restricted {req_ver}.')
                            missing_packages.append(raw_pkg)
                        elif op == '!=' and installed_v == req_v:
                            print(f'{pkg_name} (installed {installed_version}) == excluded {req_ver}.')
                            missing_packages.append(raw_pkg)
            if missing_packages:
                print('\nInstalling missing or upgrade packages...\n')
                subprocess.call([sys.executable, '-m', 'pip', 'cache', 'purge'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                for raw_pkg in missing_packages:
                    try:
                        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir']
                        cmd.append(raw_pkg)
                        subprocess.check_call(cmd)
                    except subprocess.CalledProcessError as e:
                        print(f'Failed to install {raw_pkg}: {e}')
                        return 1
                print('\nAll required packages are installed.')
            if not self.check_numpy():
                return 1
            return self.check_dictionary()
        except Exception as e:
            print(f'install_python_packages() error: {e}')
            return 1
          
    def check_numpy(self)->bool:
        try:
            numpy_version = self.get_package_version('numpy')
            torch_version = self.get_package_version('torch')
            numpy_version_base = self.version_tuple(numpy_version)
            torch_version_base = self.version_tuple(torch_version)
            if torch_version_base <= self.version_tuple('2.2.2') and numpy_version_base >= self.version_tuple('2.0.0'):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force', 'numpy<2'])
            return True
        except subprocess.CalledProcessError as e:
            error = f'Failed to install numpy package: {e}'
            print(error)
            return 1
        except Exception as e:
            error = f'Error while installing numpy package: {e}'
            print(error)
            return 1
          
    def check_dictionary(self)->bool:
        import unidic
        unidic_path = unidic.DICDIR
        dicrc = os.path.join(unidic_path, 'dicrc')
        if not os.path.exists(dicrc) or os.path.getsize(dicrc) == 0:
            try:
                error = 'UniDic dictionary not found or incomplete. Downloading now...'
                print(error)
                subprocess.run(['python', '-m', 'unidic', 'download'], check=True)
            except (subprocess.CalledProcessError, ConnectionError, OSError) as e:
                error = f'Failed to download UniDic dictionary. Error: {e}. Unable to continue without UniDic. Exiting...'
                raise SystemExit(error)
                return 1
        return 0
          
    def install_device_packages(self, device_info_str:str)->int:
        try:
            if device_info_str:
                device_info = json.loads(device_info_str)
                if device_info:
                    print(f'---> Hardware detected: {device_info}')
                    torch_version = self.get_package_version('torch')
                    if torch_version:
                        if device_info['tag'] not in ['cpu', 'unknown', 'unsupported']:
                            m = re.search(r'\+(.+)$', torch_version)
                            current_tag = m.group(1) if m else None
                            non_standard_tag = re.fullmatch(r'[0-9a-f]{7,40}', current_tag) if current_tag is not None else None
                            torch_version_base = torch_matrix[device_info['tag']]['base']
                            if ((non_standard_tag is None and current_tag != device_info['tag']) or (non_standard_tag is not None and non_standard_tag != device_info['tag'])):
                                try:
                                    print(f"Installing the right library packages for {device_info['name']}...")
                                    os_env = device_info['os']
                                    arch = device_info['arch']
                                    tag = device_info['tag']
                                    url = torch_matrix[device_info['tag']]['url']
                                    toolkit_version = "".join(c for c in tag if c.isdigit())
                                    if device_info['name'] == devices['JETSON']['proc']:
                                        py_major, py_minor = device_info['pyvenv']
                                        tag_py = f'cp{py_major}{py_minor}-cp{py_major}{py_minor}'
                                        torch_pkg = f"{url}/v{toolkit_version}/torch-{torch_version_base}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                        torchaudio_pkg = f"{url}/v{toolkit_version}/torchaudio-{torch_version_base}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', torch_pkg])
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', torchaudio_pkg])
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force', '--no-binary=scikit-learn', 'scikit-learn'])
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force', '--no-cache-dir', '--no-binary=scipy', 'scipy'])
                                    elif device_info['name'] == devices['MPS']['proc']:
                                        torch_tag_py = f'cp{default_py_major}{default_py_minor}-none'
                                        torchaudio_tag_py = f'cp{default_py_major}{default_py_minor}-cp{default_py_major}{default_py_minor}'
                                        torch_pkg = f'{url}/cpu/torch-{torch_version_base}-{torch_tag_py}-{os_env}_{arch}.whl'
                                        torchaudio_pkg = f'{url}/cpu/torchaudio-{torch_version_base}-{torchaudio_tag_py}-{os_env}_{arch}.whl'
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', torch_pkg, torchaudio_pkg])
                                    else:
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', f'torch=={torch_version_base}', f'torchaudio=={torch_version_base}', '--force-reinstall', '--index-url', f'https://download.pytorch.org/whl/{tag}'])
                                    check_numpy_version = self.check_numpy()
                                    if not check_numpy_version:
                                        return 1
                                except subprocess.CalledProcessError as e:
                                    error = f'Failed to install torch package: {e}'
                                    print(error)
                                    return 1
                                except Exception as e:
                                    error = f'Error while installing torch package: {e}'
                                    print(error)
                                    return 1
                        if device_info['os'] == 'linux' and ('jetpack' in device_info['note'].lower() or device_info['name'] == devices['JETSON']['proc']):
                            libgomp_src = '/usr/lib/aarch64-linux-gnu/libgomp.so'
                            if os.path.exists(libgomp_src):
                                libs_dir = os.path.join(
                                    'python_env',
                                    'lib',
                                    f'python{sys.version_info.major}.{sys.version_info.minor}',
                                    'site-packages',
                                    'scikit_learn.libs'
                                )
                                if os.path.isdir(libs_dir):
                                    for libgomp_dst in glob.glob(os.path.join(libs_dir, 'libgomp*')):
                                        if os.path.islink(libgomp_dst):
                                            if os.path.realpath(libgomp_dst) == os.path.realpath(libgomp_src):
                                                continue
                                            os.unlink(libgomp_dst)
                                        else:
                                            os.unlink(libgomp_dst)
                                        msg = 'Create symlink to use OS libgomp.'
                                        print(msg)
                                        os.symlink(libgomp_src, libgomp_dst)
                        return 0
                    else:
                        error = 'install_device_packages() error: torch version not detected'
                        print(error)
                else:
                    error = 'install_device_packages() error: device_info_str is empty'
                    print(error)
            else:
                error = f'install_device_packages() error: json.loads() could not decode device_info_str={device_info_str}'
                print(error)
            return 1     
        except Exception as e:
            error = f'install_device_packages() error: {e}'
            print(error)
            return 1