import os, re, sys, platform, shutil, subprocess, json

from functools import cached_property
from typing import Union
from importlib.metadata import version, PackageNotFoundError
from lib.conf import *

class DeviceInstaller():

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
        name, tag, msg = self.check_hardware
        arch = self.check_arch
        pyvenv = sys.version_info[:2]
        if mode == NATIVE:
            os_env = 'linux' if name == 'jetson' else self.check_platform
        elif mode == 'build_docker':
            os_env = 'linux' if name == 'jetson' else 'manylinux_2_28'
            pyvenv = [3,10] if tag in ['jetson51', 'jetson60', 'jetson61'] else pyvenv
        if all([name, tag, os_env, arch, pyvenv]):
            device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyvenv, "tag": tag, "note": msg}
            return json.dumps(device_info)
        return ''
        
    def get_package_version(self, pkg:str)->Union[str, bool]:
        try:
            return version(pkg)
        except PackageNotFoundError:
            return False

    def detect_platform_tag(self)->str:
        if sys.platform.startswith('win'):
            return 'win'
        if sys.platform == 'darwin':
            return 'macosx_11_0'
        if sys.platform.startswith('linux'):
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

        def toolkit_version_parse(text:str)->Union[str, None]:
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
            if l4t_major < 35:
                msg = f'JetPack too old (L4T {l4t_major}). Please upgrade to JetPack 5.1+. Falling back to CPU.'
                return ('unsupported', msg)
            if l4t_major == 35:
                if rev_major == 0 and rev_minor <= 1:
                    msg = 'JetPack 5.0/5.0.1 detected. Please upgrade to JetPack 5.1+ to use the GPU. Failing back to CPU'
                    return ('cpu', msg)
                if rev_major == 0 and rev_minor >= 2:
                    msg = 'JetPack 5.0.x detected. Please upgrade to JetPack 5.1+ to use the GPU. Failing back to CPU'
                    return ('cpu', msg)
                if rev_major == 1 and rev_minor == 0:
                    msg = 'JetPack 5.1.0 detected. Please upgrade to JetPack 5.1.2 or newer.'
                    return ('51', msg)
                if rev_major == 1 and rev_minor == 1:
                    msg = 'JetPack 5.1.1 detected. Please upgrade to JetPack 5.1.2 or newer.'
                    return ('51', msg)
                if (rev_major > 1) or (rev_major == 1 and rev_minor >= 2):
                    return ('51', msg)
                msg = 'Unrecognized JetPack 5.x version. Falling back to CPU.'
                return ('unknown', msg)
            if l4t_major == 36:
                if rev_major == 2:
                    return ('60', msg)
                else:
                    return ('61', msg)
                msg = 'Unrecognized JetPack 6.x version. Falling back to CPU.'
            return ('unknown', msg)

        def has_amd_gpu_pci():
            # macOS: no ROCm-capable AMD GPUs
            if sys.platform == "darwin":
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
                    out = try_cmd(
                        "wmic path win32_VideoController get Name,PNPDeviceID"
                    ).lower()
                    return "ven_1002" in out
                if has_cmd("powershell"):
                    out = try_cmd(
                        'powershell -Command "Get-PnpDevice -Class Display | '
                        'Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return "ven_1002" in out
                return False
            return False

        def has_working_rocm():
            # ROCm does not exist on macOS or Windows (runtime)
            if sys.platform != "linux":
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
            if sys.platform == "darwin":
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

        def has_working_cuda():
            # CUDA does not exist on macOS
            if sys.platform == "darwin":
                return False
            # nvidia-smi is the only reliable cross-platform signal
            if not has_cmd("nvidia-smi"):
                return False
            out = try_cmd("nvidia-smi -L").lower()
            if not out:
                return False
            # Guard against common failure states
            if "failed" in out or "error" in out or "no devices were found" in out:
                return False
            return "gpu" in out

        def has_intel_gpu_pci():
            # macOS: Intel GPUs exist but XPU runtime is not supported
            if sys.platform == "darwin":
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
            if sys.platform == "darwin":
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
            out = try_cmd('uname -a')
            if 'tegra' in out:
                msg = 'Jetson GPU detected but not(?) compatible'
                
        # ============================================================
        # ROCm
        # ============================================================
        elif has_working_rocm() and has_amd_gpu_pci():
            version_out = ''
            if os.name == 'posix':
                for p in (
                    '/opt/rocm/.info/version',
                    '/opt/rocm/version',
                ):
                    if os.path.exists(p):
                        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                            version_out = f.read()
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
                                    version_out = f.read()
                                break
                    if version_out:
                        break
            if not version_out:
                msg = 'ROCm hardware detected but ROCm toolkit version file not found.'
            else:
                version_str = toolkit_version_parse(version_out)
                cmp = toolkit_version_compare(version_str, rocm_version_range)
                if cmp == -1:
                    msg = f'ROCm {version_str} < min {rocm_version_range["min"]}. Please upgrade.'
                elif cmp == 1:
                    msg = f'ROCm {version_str} > max {rocm_version_range["max"]}. Falling back to CPU.'
                elif cmp == 0:
                    devices['ROCM']['found'] = True
                    parts = version_str.split(".")
                    major = parts[0]
                    minor = parts[1] if len(parts) > 1 else 0
                    name = 'rocm'
                    tag = f'rocm{major}{minor}'
                else:
                    msg = 'ROCm GPU detected but not compatible or ROCm runtime is missing.'
                
        # ============================================================
        # CUDA
        # ============================================================
        elif has_working_cuda() and has_nvidia_gpu_pci():
            version_out = ''
            if os.name == 'posix':
                for p in (
                    '/usr/local/cuda/version.json',
                    '/usr/local/cuda/version.txt',
                ):
                    if os.path.exists(p):
                        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                            version_out = f.read()
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
                                version_out = f.read()
                            break
            if not version_out:
                msg = 'CUDA hardware detected but CUDA toolkit version file not found.'
            else:
                version_str = toolkit_version_parse(version_out)
                cmp = toolkit_version_compare(version_str, cuda_version_range)

                if cmp == -1:
                    msg = f'CUDA {version_str} < min {cuda_version_range["min"]}. Please upgrade.'
                elif cmp == 1:
                    msg = f'CUDA {version_str} > max {cuda_version_range["max"]}. Falling back to CPU.'
                elif cmp == 0:
                    devices['CUDA']['found'] = True
                    parts = version_str.split(".")
                    major = parts[0]
                    minor = parts[1] if len(parts) > 1 else 0
                    name = 'cuda'
                    tag = f'cu{major}{minor}'
                else:
                    msg = 'Cuda GPU detected but not compatible or Cuda runtime is missing.'

        # ============================================================
        # INTEL XPU
        # ============================================================
        elif has_working_xpu() and has_intel_gpu_pci():
            version_out = ''
            if os.name == 'posix':
                for p in (
                    '/opt/intel/oneapi/version.txt',
                    '/opt/intel/oneapi/compiler/latest/version.txt',
                    '/opt/intel/oneapi/runtime/latest/version.txt',
                ):
                    if os.path.exists(p):
                        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                            version_out = f.read()
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
                                version_out = f.read()
                            break
            if not version_out:
                msg = 'Intel GPU detected but oneAPI toolkit version file not found.'
            else:
                version_str = toolkit_version_parse(version_out)
                cmp = toolkit_version_compare(version_str, xpu_version_range)
                if cmp == -1 or cmp == 1:
                    msg = f'XPU {version_str} out of supported range {xpu_version_range}. Falling back to CPU.'
                elif cmp == 0:
                    devices['XPU']['found'] = True
                    name = 'xpu'
                    tag = 'xpu'
                else:
                    msg = 'Intel GPU detected but not compatible or oneAPI runtime is missing.'

        # ============================================================
        # APPLE MPS
        # ============================================================
        elif sys.platform == 'darwin' and arch in ('arm64', 'aarch64'):
            devices['MPS']['found'] = True
            name = 'mps'
            tag = 'mps'

        # ============================================================
        # CPU
        # ============================================================
        if tag is None:
            name = 'cpu'
            tag = 'cpu'
            
        return (name, tag, msg)

    def install_python_packages(self)->bool:
        if not os.path.exists(requirements_file):
            error = f'Warning: File {requirements_file} not found. Skipping package check.'
            print(error)
            return False
        try:
            import importlib
            from tqdm import tqdm        
            with open(requirements_file, 'r') as f:
                contents = f.read().replace('\r', '\n')
                packages = [pkg.strip() for pkg in contents.splitlines() if pkg.strip() and re.search(r'[a-zA-Z0-9]', pkg)]
            if sys.version_info >= (3, 11):
                packages.append("pymupdf-layout")
            missing_packages = []
            cuda_markers = ('+cu', '+xpu', '+nv', '+git')
            for package in packages:
                if ';' in package:
                    pkg_part, marker_part = package.split(';', 1)
                    marker_part = marker_part.strip()
                    try:
                        from packaging.markers import Marker
                        marker = Marker(marker_part)
                        if not marker.evaluate():
                            continue
                    except Exception as e:
                        error = f'Warning: Could not evaluate marker {marker_part} for {pkg_part}: {e}'
                        print(error)
                    package = pkg_part.strip()
                if 'git+' in package or '://' in package:
                    pkg_name_match = re.search(r'([\w\-]+)\s*@?\s*git\+', package)
                    pkg_name = pkg_name_match.group(1) if pkg_name_match else None
                    if pkg_name:
                        spec = importlib.util.find_spec(pkg_name)
                        if spec is None:
                            msg = f'{pkg_name} (git package) is missing.'
                            print(msg)
                            missing_packages.append(package)
                    else:
                        error = f'Unrecognized git package: {package}'
                        print(error)
                        missing_packages.append(package)
                    continue
                clean_pkg = re.sub(r'\[.*?\]', '', package)
                pkg_name = re.split(r'[<>=]', clean_pkg, maxsplit=1)[0].strip()
                try:
                    installed_version = version(pkg_name)
                except PackageNotFoundError:
                    error = f'{pkg_name} is not installed.'
                    print(error)
                    missing_packages.append(package)
                    continue
                if '+' in installed_version:
                    continue
                else:
                    spec_str = clean_pkg[len(pkg_name):].strip()
                    if spec_str:
                        from packaging.specifiers import SpecifierSet
                        from packaging.version import Version, InvalidVersion
                        spec = SpecifierSet(spec_str)
                        norm_match = re.match(r'^(\d+\.\d+(?:\.\d+)?)', installed_version)
                        short_version = norm_match.group(1) if norm_match else installed_version
                        try:
                            installed_v = Version(short_version)
                        except InvalidVersion as e:
                            error = f'install_device_packages() Version error: {e}'
                            print(error)
                            return 1 
                        req_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', spec_str)
                        if req_match:
                            req_v = Version(req_match.group(1))
                            imajor, iminor = installed_v.major, installed_v.minor
                            rmajor, rminor = req_v.major, req_v.minor
                            if '==' in spec_str:
                                if imajor != rmajor or iminor != rminor:
                                    error = f'{pkg_name} (installed {installed_version}) not in same major.minor as required {req_v}.'
                                    print(error)
                                    missing_packages.append(package)
                            elif '>=' in spec_str:
                                if (imajor < rmajor) or (imajor == rmajor and iminor < rminor):
                                    error = f'{pkg_name} (installed {installed_version}) < required {req_v}.'
                                    print(error)
                                    missing_packages.append(package)
                            elif '<=' in spec_str:
                                if (imajor > rmajor) or (imajor == rmajor and iminor > rminor):
                                    error = f'{pkg_name} (installed {installed_version}) > allowed {req_v}.'
                                    print(error)
                                    missing_packages.append(package)
                            elif '>' in spec_str:
                                if (imajor < rmajor) or (imajor == rmajor and iminor <= rminor):
                                    error = f'{pkg_name} (installed {installed_version}) <= required {req_v}.'
                                    print(error)
                                    missing_packages.append(package)
                            elif '<' in spec_str:
                                if (imajor > rmajor) or (imajor == rmajor and iminor >= rminor):
                                    error = f'{pkg_name} (installed {installed_version}) >= restricted {req_v}.'
                                    print(error)
                                    missing_packages.append(package)
                            else:
                                if installed_v not in spec:
                                    error = f'{pkg_name} (installed {installed_version}) does not satisfy {spec_str}.'
                                    print(error)
                                    missing_packages.append(package)
            if missing_packages:
                msg = '\nInstalling missing or upgrade packages...\n'
                print(msg)
                subprocess.call([sys.executable, '-m', 'pip', 'cache', 'purge'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                with tqdm(total = len(packages), desc = 'Installation 0.00%', bar_format = '{desc}: {n_fmt}/{total_fmt} ', unit = 'step') as t:
                    for package in tqdm(missing_packages, desc = 'Installing', unit = 'pkg'):
                        try:
                            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', package])
                            t.update(1)
                        except subprocess.CalledProcessError as e:
                            error = f'Failed to install {package}: {e}'
                            print(error)
                            return False
                msg = '\nAll required packages are installed.'
                print(msg)
            return self.check_dictionary()
        except Exception as e:
            error = f'install_python_packages() error: {e}'
            print(error)
            return False
          
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
                return False
        return True
          
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
                            if ((non_standard_tag is None and current_tag != device_info['tag']) or (non_standard_tag is not None and non_standard_tag != device_info['tag'])):
                                try:
                                    from packaging.version import Version
                                    torch_version_base = Version(torch_version).base_version
                                    print(f"Installing the right library packages for {device_info['name']}...")
                                    os_env = device_info['os']
                                    arch = device_info['arch']
                                    tag = device_info['tag']
                                    url = torch_matrix[device_info['tag']]['url']
                                    toolkit_version = "".join(c for c in tag if c.isdigit())
                                    if device_info['name'] == devices['JETSON']['proc']:
                                        py_major, py_minor = device_info['pyvenv']
                                        tag_py = f'cp{py_major}{py_minor}-cp{py_major}{py_minor}'
                                        torch_pkg = f"{url}/v{toolkit_version}/torch-{jetson_torch_version_base[tag]}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                        torchaudio_pkg = f"{url}/v{toolkit_version}/torchaudio-{jetson_torch_version_base[tag]}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', torch_pkg, torchaudio_pkg])
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', 'scikit-learn'])
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', 'scikit-learn'])
                                    elif device_info['name'] == devices['MPS']['proc']:
                                        torch_tag_py = f'cp{default_py_major}{default_py_minor}-none'
                                        torchaudio_tag_py = f'cp{default_py_major}{default_py_minor}-cp{default_py_major}{default_py_minor}'
                                        torch_pkg = f'{url}/cpu/torch-{torch_version_base}-{torch_tag_py}-{os_env}_{arch}.whl'
                                        torchaudio_pkg = f'{url}/cpu/torchaudio-{torch_version_base}-{torchaudio_tag_py}-{os_env}_{arch}.whl'
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', torch_pkg, torchaudio_pkg])
                                    else:
                                        tag_py = f'cp{default_py_major}{default_py_minor}-cp{default_py_major}{default_py_minor}'
                                        torch_pkg = f'{url}/{tag}/torch-{torch_version_base}%2B{tag}-{tag_py}-{os_env}_{arch}.whl'
                                        torchaudio_pkg = f'{url}/{tag}/torchaudio-{torch_version_base}%2B{tag}-{tag_py}-{os_env}_{arch}.whl'
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', torch_pkg, torchaudio_pkg])
                                        if device_info['name'] == 'cuda':
                                            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', '--progress-bar', 'on', '--disable-pip-version-check', 'deepspeed'])
                                    #msg = 'Relaunching app...'
                                    #print(msg)
                                    #os.execv(sys.executable, [sys.executable] + sys.argv)
                                except subprocess.CalledProcessError as e:
                                    error = f'Failed to install torch package: {e}'
                                    print(error)
                                    return 1
                                except Exception as e:
                                    error = f'Error while installing torch package: {e}'
                                    print(error)
                                    return 1
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