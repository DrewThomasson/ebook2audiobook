import os, re, sys, platform, shutil, subprocess, importlib, json

from functools import cached_property
from typing import Union
from glob import glob
from importlib.metadata import version, PackageNotFoundError
from lib.conf import *

class DeviceInstaller():
    
    def __init__(self):
        self.system = sys.platform
        self.arch = self.check_arch
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

    @cached_property
    def cpu_baseline(self)->bool:
        machine = platform.machine().lower()
        if machine not in ('x86_64', 'amd64', 'x86'):
            return True
        from cpuinfo import get_cpu_info
        flags = set(get_cpu_info().get('flags', []))
        return {'sse4_2', 'popcnt', 'ssse3'}.issubset(flags)

    def check_device_info(self, mode:str)->str:
        if mode == NATIVE:
            name, tag, msg = self.check_hardware
            pyvenv = [3, 10] if tag in ['jetson51', 'jetson60', 'jetson61'] else list(max_python_version)
            arch = 'aarch64' if name in [devices['JETSON']['proc']] else self.arch
            os_env = 'linux' if name == devices['JETSON']['proc'] else self.check_platform
            if all([name, tag, os_env, arch, pyvenv]):
                device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyvenv, "tag": tag, "note": msg}
                return json.dumps(device_info)
        elif mode == FULL_DOCKER:
            device_info = None
            if os.path.isfile('.device_info.json'):
                try:
                    with open('.device_info.json', 'r', encoding='utf-8') as f:
                        device_info = json.load(f)
                except (OSError, json.JSONDecodeError):
                    pass
            if device_info is None:
                env_str = os.environ.get('DOCKER_DEVICE_STR', '')
                if env_str:
                    try:
                        device_info = json.loads(env_str)
                    except json.JSONDecodeError:
                        pass
            if device_info is not None:
                devices[device_info['name'].upper()]['found'] = True
                return json.dumps(device_info)
        elif mode == BUILD_DOCKER:
            name, tag, msg = self.check_hardware
            os_env = 'manylinux_2_28'
            pyvenv = [3, 10] if tag in ['jetson51', 'jetson60', 'jetson61'] else list(max_python_version)
            arch = 'aarch64' if name in [devices['JETSON']['proc']] else self.arch
            if name in [devices['JETSON']['proc'], devices['MPS']['proc']]:
                name = tag = devices['CPU']['proc']
            device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyvenv, "tag": tag, "note": msg.replace('!', '')}
            try:
                with open('.device_info.json', 'w', encoding='utf-8') as f:
                    json.dump(device_info, f)
            except OSError as e:
                print(f'warning: could not write .device_info.json: {e}', file=sys.stderr)
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
        m = platform.machine().lower()
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
                    obj = json.loads(text)
                    if isinstance(obj, dict):
                        if devices['CUDA']['proc'] in obj and isinstance(obj[devices['CUDA']['proc']], dict):
                            v = obj[devices['CUDA']['proc']].get('version')
                            if v:
                                return str(v)
                        v = obj.get('version')
                        if v:
                            return str(v)
                except Exception:
                    pass
            m = re.search(r'cuda\s*version\s*([0-9]+(?:\.[0-9]+){1,2})', text, re.IGNORECASE)
            if m:
                return m.group(1)
            m = re.search(r'cuda\s*([0-9]+(?:\.[0-9]+)?)', text, re.IGNORECASE)
            if m:
                return m.group(1)
            m = re.search(r'rocm\s*version\s*([0-9]+(?:\.[0-9]+){0,2})', text, re.IGNORECASE)
            if m:
                return m.group(1)  # CHANGED: keep full version, don't truncate to major.minor
            m = re.search(r'hip\s*version\s*([0-9]+(?:\.[0-9]+){0,2})', text, re.IGNORECASE)
            if m:
                return m.group(1)  # CHANGED: keep full version
            m = re.search(r'(oneapi|xpu)\s*(toolkit\s*)?version\s*([0-9]+(?:\.[0-9]+)?)', text, re.IGNORECASE)
            if m:
                return m.group(3)
            return None

        def version_classify(version_str:Union[str, None], version_range:dict)->tuple:
            # Returns (cmp, current_tuple, min_tuple, max_tuple)
            # cmp: -1 = below min, 0 = in range, 1 = above max, None = parse fail / unranged
            # current_tuple is (major, minor, patch) — patch defaults to 0
            if version_str is None:
                return (None, None, None, None)
            min_raw = tuple(version_range.get('min', (0, 0)))
            max_raw = tuple(version_range.get('max', (0, 0)))
            # Pad min/max to 3-tuples for consistent comparison
            min_tuple = min_raw + (0,) * (3 - len(min_raw)) if len(min_raw) < 3 else min_raw[:3]
            max_tuple = max_raw + (0,) * (3 - len(max_raw)) if len(max_raw) < 3 else max_raw[:3]
            try:
                parts = version_str.split('.')
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                patch = int(parts[2]) if len(parts) > 2 else 0
            except (ValueError, IndexError):
                return (None, None, min_tuple, max_tuple)
            current = (major, minor, patch)
            if min_tuple == (0, 0, 0) and max_tuple == (0, 0, 0):
                return (0, current, min_tuple, max_tuple)
            # Compare on (major, minor) only for the range check — patch doesn't gate
            current_mm = (major, minor)
            min_mm = min_tuple[:2]
            max_mm = max_tuple[:2]
            if min_mm != (0, 0) and current_mm < min_mm:
                return (-1, current, min_tuple, max_tuple)
            if max_mm != (0, 0) and current_mm > max_mm:
                return (1, current, min_tuple, max_tuple)
            return (0, current, min_tuple, max_tuple)

        def tegra_version()->str:
            if os.path.exists('/etc/nv_tegra_release'):
                return try_cmd('cat /etc/nv_tegra_release')
            return ''

        def jetpack_version(text:str)->tuple:
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
            if l4t_major < 35:
                msg = f'JetPack too old (L4T {l4t_major}). Please upgrade to JetPack 6+. Falling back to CPU.'
                return ('unsupported', msg)
            if l4t_major == 35:
                return ('51', msg)
            if rev_major == 2:
                return ('60', msg)
            return ('61', msg)

        def has_amd_gpu_pci():
            if self.system == systems['MACOS']:
                return False
            if os.name == 'posix':
                sysfs = '/sys/bus/pci/devices'
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f'{dev}/vendor') as f:
                                if f.read().strip() not in ('0x1002', '0x1022'):
                                    continue
                            with open(f'{dev}/class') as f:
                                cls = f.read().strip()
                                if cls.startswith('0x0300') or cls.startswith('0x0302'):
                                    return True
                        except Exception:
                            pass
                if has_cmd('lspci'):
                    out = try_cmd('lspci -nn').lower()
                    return (
                        ('1002:' in out or '1022:' in out) and
                        (' vga ' in out or ' 3d ' in out)
                    )
                return False
            if os.name == 'nt':
                if has_cmd('wmic'):
                    out = try_cmd('wmic path win32_VideoController get Name,PNPDeviceID').lower()
                    return 'ven_1002' in out
                if has_cmd('powershell'):
                    out = try_cmd('powershell -Command "Get-PnpDevice -Class Display | Select-Object -ExpandProperty InstanceId"').lower()
                    return 'ven_1002' in out
                return False
            return False

        def has_rocm():
            if self.system == systems['LINUX']:
                rocm_paths = ['/opt/rocm', '/opt/rocm/bin/rocminfo']
                if any(os.path.exists(p) for p in rocm_paths):
                    return True
                return has_cmd('rocminfo')
            elif self.system == systems['WINDOWS']:
                hip_path = os.environ.get('HIP_PATH')
                if hip_path and os.path.isdir(hip_path):
                    return True
                program_files = os.environ.get('ProgramFiles', '')
                if program_files and glob(os.path.join(program_files, 'AMD', 'ROCm', '*')):
                    return True
                return has_cmd('rocminfo')
            return False

        def has_nvidia_gpu_pci():
            if self.system == systems['MACOS']:
                return False
            if os.name == 'posix':
                sysfs = '/sys/bus/pci/devices'
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f'{dev}/vendor') as f:
                                if f.read().strip() != '0x10de':
                                    continue
                            with open(f'{dev}/class') as f:
                                cls = f.read().strip()
                                if cls.startswith('0x0300') or cls.startswith('0x0302'):
                                    return True
                        except Exception:
                            pass
                if has_cmd('lspci'):
                    out = try_cmd('lspci -nn').lower()
                    return '10de:' in out and (' vga ' in out or ' 3d ' in out)
                return False
            if os.name == 'nt':
                if has_cmd('nvidia-smi'):
                    return True
                if has_cmd('wmic'):
                    out = try_cmd('wmic path win32_VideoController get Name,PNPDeviceID').lower()
                    return 'ven_10de' in out
                if has_cmd('powershell'):
                    out = try_cmd(
                        'powershell -Command "Get-PnpDevice -Class Display | '
                        'Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return 'ven_10de' in out
                return False
            return False

        def is_wsl2():
            if os.name != 'posix':
                return False
            try:
                with open('/proc/version', 'r', encoding='utf-8', errors='ignore') as f:
                    return 'microsoft' in f.read().lower()
            except Exception:
                return False

        def has_cuda():
            if self.system == systems['MACOS']:
                return False
            if not has_cmd('nvidia-smi'):
                return False
            out = try_cmd('nvidia-smi -L').lower()
            if not out:
                return False
            if 'failed' in out or 'error' in out or 'no devices were found' in out:
                return False
            return 'gpu' in out

        def has_intel_gpu_pci():
            if self.system == systems['MACOS']:
                return False
            if os.name == 'posix':
                sysfs = '/sys/bus/pci/devices'
                if os.path.isdir(sysfs):
                    for d in os.listdir(sysfs):
                        dev = os.path.join(sysfs, d)
                        try:
                            with open(f'{dev}/vendor') as f:
                                if f.read().strip() != '0x8086':
                                    continue
                            with open(f'{dev}/class') as f:
                                cls = f.read().strip()
                                if cls.startswith('0x0300') or cls.startswith('0x0302'):
                                    return True
                        except Exception:
                            pass
                if has_cmd('lspci'):
                    out = try_cmd('lspci -nn').lower()
                    return '8086:' in out and (' vga ' in out or ' 3d ' in out)
                return False
            if os.name == 'nt':
                if has_cmd('wmic'):
                    out = try_cmd('wmic path win32_VideoController get Name,PNPDeviceID').lower()
                    return 'ven_8086' in out
                if has_cmd('powershell'):
                    out = try_cmd(
                        'powershell -Command "Get-PnpDevice -Class Display | '
                        'Select-Object -ExpandProperty InstanceId"'
                    ).lower()
                    return 'ven_8086' in out
                return False
            return False

        def has_xpu():
            if self.system == systems['MACOS']:
                return False
            if os.name == 'posix':
                if not os.path.exists('/dev/dri/renderD128'):
                    return False
                if has_cmd('sycl-ls'):
                    out = try_cmd('sycl-ls').lower()
                    if 'level-zero' in out and 'gpu' in out:
                        return True
                if has_cmd('clinfo'):
                    out = try_cmd('clinfo').lower()
                    if 'intel' in out and 'gpu' in out:
                        return True
                return False
            if os.name == 'nt':
                if has_cmd('sycl-ls'):
                    out = try_cmd('sycl-ls').lower()
                    return 'gpu' in out
                return False
            return False

        name = None
        tag = None
        msg = ''
        arch = platform.machine().lower()
        forced_tag = os.environ.get('DEVICE_TAG')

        if forced_tag:
            tag_letters = re.match(r'[a-zA-Z]+', forced_tag)
            if tag_letters:
                tag_letters = tag_letters.group(0).lower()
                name = devices['CUDA']['proc'] if tag_letters == 'cu' else devices['ROCM']['proc'] if tag_letters == devices['ROCM']['proc'] else devices['JETSON']['proc'] if tag_letters == devices['JETSON']['proc'] else devices['XPU']['proc'] if tag_letters == devices['XPU']['proc'] else devices['MPS']['proc'] if tag_letters == devices['MPS']['proc'] else devices['CPU']['proc']
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
                if jp_code not in ('unsupported', 'unknown'):
                    if os.path.exists('/etc/nv_tegra_release'):
                        devices['JETSON']['found'] = True
                        name = devices['JETSON']['proc']
                        tag = f'jetson{jp_code}'
                    elif os.path.exists('/proc/device-tree/compatible'):
                        out = try_cmd('cat /proc/device-tree/compatible')
                        if 'tegra' in out:
                            devices['JETSON']['found'] = True
                            name = devices['JETSON']['proc']
                            tag = f'jetson{jp_code}'
                    else:
                        out = try_cmd('uname -a')
                        if 'tegra' in out:
                            msg = 'Jetson GPU detected but not(?) compatible'
                if devices['JETSON']['found']:
                    os.environ['CUDA_MODULE_LOADING'] = 'LAZY'
                    os.environ['TORCH_CUDA_ENABLE_CUDA_GRAPH'] = '0'
                    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128,garbage_collection_threshold:0.6,expandable_segments:False'

            # ============================================================
            # ROCm
            # ============================================================
            elif has_rocm() and has_amd_gpu_pci():

                def _normalize_version(v:str)->tuple:
                    '''Parse version string into (major, minor, patch). Patch defaults to 0.'''
                    m = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', v or '')
                    if not m:
                        return ()
                    major = int(m.group(1))
                    minor = int(m.group(2))
                    patch = int(m.group(3)) if m.group(3) else 0
                    return (major, minor, patch)

                version = ()
                msg = ''
                hip_device_count = 0

                # 1) HIP runtime detection via ctypes (primary)
                try:
                    import ctypes
                    libhip = None

                    if os.name == 'nt':
                        hip_path = os.environ.get('HIP_PATH', '')
                        candidates = ['amdhip64.dll']
                        if hip_path:
                            candidates.insert(0, os.path.join(hip_path, 'bin', 'amdhip64.dll'))
                        for lib_name in candidates:
                            try:
                                libhip = ctypes.CDLL(lib_name)
                                break
                            except OSError:
                                continue
                    else:
                        candidates = ['libamdhip64.so']
                        min_major, _ = rocm_version_range['min']
                        max_major, _ = rocm_version_range['max']
                        for major in range(max_major + 2, min_major - 1, -1):
                            candidates.append(f'libamdhip64.so.{major}')
                        hip_lib_dirs = [
                            '/opt/rocm/lib',
                            '/opt/rocm/lib64',
                            '/usr/lib/x86_64-linux-gnu',
                            '/usr/lib64',
                        ]
                        for p in sorted(glob('/opt/rocm-*/lib'), reverse=True):
                            hip_lib_dirs.append(p)
                        for d in hip_lib_dirs:
                            if os.path.isdir(d):
                                try:
                                    for f in sorted(os.listdir(d), reverse=True):
                                        if f.startswith('libamdhip64.so.'):
                                            candidates.append(os.path.join(d, f))
                                except OSError:
                                    pass
                        for lib_name in candidates:
                            try:
                                libhip = ctypes.CDLL(lib_name)
                                break
                            except OSError:
                                continue

                    if libhip:
                        device_count = ctypes.c_int()
                        if libhip.hipGetDeviceCount(ctypes.byref(device_count)) == 0:
                            hip_device_count = device_count.value
                        v_int = ctypes.c_int()
                        if libhip.hipRuntimeGetVersion(ctypes.byref(v_int)) == 0:
                            v = v_int.value
                            if v >= 10000000:
                                major = v // 10000000
                                minor = (v % 10000000) // 100000
                                patch = v % 100000
                            elif v >= 100:
                                major = v // 100
                                minor = (v % 100) // 10
                                patch = 0
                            else:
                                major, minor, patch = v, 0, 0
                            if hip_device_count > 0:
                                version = (major, minor, patch)
                            else:
                                ver_disp = f'{major}.{minor}.{patch}' if patch else f'{major}.{minor}'
                                msg = f'HIP runtime present ({ver_disp}) but no devices.'
                except (OSError, AttributeError):
                    pass

                # 2) hipcc fallback
                if not version:
                    if os.name == 'posix' and has_cmd('hipcc'):
                        out = try_cmd('hipcc --version')
                        if out:
                            m = re.search(r'HIP version:\s*([\d.]+)', out, re.IGNORECASE)
                            if m:
                                version = _normalize_version(m.group(1))
                    elif os.name == 'nt':
                        hip_path = os.environ.get('HIP_PATH', '')
                        hipcc = os.path.join(hip_path, 'bin', 'hipcc') if hip_path else ''
                        if hipcc and os.path.isfile(hipcc):
                            out = try_cmd(f'"{hipcc}" --version')
                            if out:
                                m = re.search(r'HIP version:\s*([\d.]+)', out, re.IGNORECASE)
                                if m:
                                    version = _normalize_version(m.group(1))
                        if not version and has_cmd('hipcc'):
                            out = try_cmd('hipcc --version')
                            if out:
                                m = re.search(r'HIP version:\s*([\d.]+)', out, re.IGNORECASE)
                                if m:
                                    version = _normalize_version(m.group(1))

                # 3) torch.version.hip fallback
                if not version:
                    try:
                        import torch
                        if getattr(torch.version, 'hip', None):
                            version = _normalize_version(torch.version.hip)
                    except Exception:
                        pass

                # 4) ROCm install dir fallback
                if not version:
                    if os.name == 'posix':
                        for p in sorted(glob('/opt/rocm-*'), reverse=True):
                            base = os.path.basename(p).replace('rocm-', '')
                            v = _normalize_version(base)
                            if v:
                                version = v
                                break
                        if not version:
                            for p in ('/opt/rocm/.info/version', '/opt/rocm/version'):
                                if os.path.exists(p):
                                    try:
                                        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                            version = _normalize_version(lib_version_parse(f.read()))
                                        break
                                    except Exception:
                                        pass
                    elif os.name == 'nt':
                        program_files = os.environ.get('ProgramFiles', '')
                        if program_files:
                            for p in sorted(glob(os.path.join(program_files, 'AMD', 'ROCm', '*')), reverse=True):
                                v = _normalize_version(os.path.basename(p))
                                if v:
                                    version = v
                                    break
                        if not version:
                            for env in ('ROCM_PATH', 'HIP_PATH'):
                                base = os.environ.get(env)
                                if base:
                                    for p in (os.path.join(base, 'version'), os.path.join(base, '.info', 'version')):
                                        if os.path.exists(p):
                                            try:
                                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                                    version = _normalize_version(lib_version_parse(f.read()))
                                                break
                                            except Exception:
                                                pass
                                if version:
                                    break
                if version:
                    version_str = '.'.join(str(p) for p in version)
                    cmp, current, min_tuple, max_tuple = version_classify(version_str, rocm_version_range)
                    # min_ver / max_ver: strip trailing .0 for display (range tuples are major.minor)
                    min_ver = f'{min_tuple[0]}.{min_tuple[1]}'
                    max_ver = f'{max_tuple[0]}.{max_tuple[1]}'
                    if self.system == systems['WINDOWS'] and version < max_tuple:
                        msg = f'ROCm {version_str} on Windows; needs to be upgraded to {max_ver}.x.'
                    elif cmp == -1:
                        msg = f'ROCm {version_str} < min {min_ver}. Please upgrade.'
                    elif cmp is None:
                        msg = 'ROCm GPU detected but version unparseable.'
                    else:
                        devices['ROCM']['found'] = True
                        name = devices['ROCM']['proc']
                        compat_versions = []
                        for t, entry in torch_matrix.items():
                            if self.system not in entry['compat'] or not t.startswith('rocm'):
                                continue
                            ver_str = t[len('rocm-rel-'):] if t.startswith('rocm-rel-') else t[len('rocm'):]
                            tag_ver = _normalize_version(ver_str)
                            if not tag_ver:
                                continue
                            compat_versions.append(tag_ver)
                        tag = None
                        if compat_versions:
                            le_versions = [v for v in compat_versions if v <= version]
                            if le_versions:
                                matched = max(le_versions)
                                if self.system == systems['WINDOWS']:
                                    tag = f'rocm-rel-{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'rocm-rel-{matched[0]}.{matched[1]}'
                                else:
                                    tag = f'rocm{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'rocm{matched[0]}.{matched[1]}'
                        if cmp == 1:
                            msg = f'ROCm {version_str} > tested max {max_ver}; using {tag} torch build.' if tag else f'ROCm {version_str} detected but no compatible torch build for this OS.'
                        elif not tag:
                            msg = f'ROCm {version_str} detected but no compatible torch build for this OS.'
                else:
                    msg = 'ROCm hardware detected but AMD ROCm base runtime not installed.'

                # 5) Last-resort torch fallback
                if not devices['ROCM']['found']:
                    try:
                        import torch
                        if torch.cuda.is_available() and hasattr(torch.version, 'hip') and torch.version.hip:
                            devices['ROCM']['found'] = True
                            version = _normalize_version(torch.version.hip)
                            if version:
                                if self.system == systems['WINDOWS'] and version < tuple(rocm_version_range['max']):
                                    devices['ROCM']['found'] = False
                                    max_ver = f"{rocm_version_range['max'][0]}.{rocm_version_range['max'][1]}"
                                    msg = f'ROCm {".".join(str(p) for p in version)} on Windows; needs to be upgraded to {max_ver}.x.'
                                else:
                                    compat_versions = []
                                for t, entry in torch_matrix.items():
                                    if self.system not in entry['compat'] or not t.startswith('rocm'):
                                        continue
                                    ver_str = t[len('rocm-rel-'):] if t.startswith('rocm-rel-') else t[len('rocm'):]
                                    tag_ver = _normalize_version(ver_str)
                                    if not tag_ver:
                                        continue
                                    compat_versions.append(tag_ver)
                                tag = None
                                if compat_versions:
                                    le_versions = [v for v in compat_versions if v <= version]
                                    if le_versions:
                                        matched = max(le_versions)
                                        if self.system == systems['WINDOWS']:
                                            tag = f'rocm-rel-{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'rocm-rel-{matched[0]}.{matched[1]}'
                                        else:
                                            tag = f'rocm{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'rocm{matched[0]}.{matched[1]}'
                            msg = ''
                    except Exception:
                        pass

            # ============================================================
            # CUDA
            # ============================================================
            elif has_cuda() and (has_nvidia_gpu_pci() or is_wsl2()):
                version = ''
                msg = ''

                # 1) CUDA runtime detection via ctypes (primary)
                try:
                    import ctypes
                    libcudart = None

                    if os.name == 'nt':
                        # CUDA 12+ filename dropped the minor: 'cudart64_12.dll'
                        # CUDA 11.x still has minor suffix:   'cudart64_11{minor}.dll'
                        candidates = []
                        # Forward-compat for CUDA 13/14/15 (newest first)
                        for major in range(15, 11, -1):
                            candidates.append(f'cudart64_{major}.dll')
                        # CUDA 11.x minors (newest first)
                        for minor in range(9, -1, -1):
                            candidates.append(f'cudart64_11{minor}.dll')
                        for dll in candidates:
                            try:
                                libcudart = ctypes.CDLL(dll)
                                break
                            except OSError:
                                continue
                    else:
                        # Linux / WSL2 — SONAME is major-only for CUDA 11+
                        candidates = ['libcudart.so']
                        min_major, _ = cuda_version_range['min']
                        max_major, _ = cuda_version_range['max']
                        # Extend upward past max for tolerance
                        for major in range(max_major + 3, min_major - 1, -1):
                            candidates.append(f'libcudart.so.{major}')
                        cuda_lib_dirs = [
                            '/usr/local/cuda/lib64',
                            '/usr/lib/x86_64-linux-gnu',
                            '/usr/lib64',
                        ]
                        for d in cuda_lib_dirs:
                            if os.path.isdir(d):
                                try:
                                    for f in sorted(os.listdir(d), reverse=True):
                                        if f.startswith('libcudart.so.'):
                                            candidates.append(os.path.join(d, f))
                                except OSError:
                                    pass
                        for lib_name in candidates:
                            try:
                                libcudart = ctypes.CDLL(lib_name)
                                break
                            except OSError:
                                continue

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
                                    msg = f'CUDA runtime present ({major}.{minor}) but no devices.'
                            else:
                                v = v_int.value
                                major = v // 1000
                                minor = (v % 1000) // 10
                                msg = f'CUDA runtime present ({major}.{minor}) but cudaGetDeviceCount failed.'
                except (OSError, AttributeError):
                    pass

                # 2) CUDA toolkit version file (fallback)
                if not version:
                    if os.name == 'posix':
                        for p in ('/usr/local/cuda/version.json', '/usr/local/cuda/version.txt'):
                            if os.path.exists(p):
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    version = lib_version_parse(f.read()) or ''
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
                                        version = lib_version_parse(f.read()) or ''
                                    break

                # 3) Version comparison + tag assignment
                # Tolerant: CUDA > max is accepted (driver is backward-compatible),
                # but torch build tag clamps at max (cu128) so we install a real wheel.
                if version:
                    cmp, current, min_tuple, max_tuple = version_classify(version, cuda_version_range)
                    min_ver = f'{min_tuple[0]}.{min_tuple[1]}'
                    max_ver = f'{max_tuple[0]}.{max_tuple[1]}'
                    if cmp == -1:
                        msg = f'CUDA {version} < min {min_ver}. Please upgrade.'
                    elif cmp is None:
                        msg = f'CUDA version {version} unparseable.'
                    else:
                        devices['CUDA']['found'] = True
                        name = devices['CUDA']['proc']
                        if cmp == 1:
                            tag = f'cu{max_tuple[0]}{max_tuple[1]}'
                            msg = f'CUDA {version} > tested max {max_ver}; using cu{max_tuple[0]}{max_tuple[1]} torch build.'
                        else:
                            tag = f'cu{current[0]}{current[1]}'  # still index 0/1, ignore patch
                else:
                    msg = 'CUDA Toolkit or Runtime not installed or hardware not detected.'

                # 4) PyTorch fallback (only helps if a CUDA-enabled torch is already installed)
                if not devices['CUDA']['found']:
                    try:
                        import torch
                        if torch.cuda.is_available():
                            devices['CUDA']['found'] = True
                            torch_cuda_ver = torch.version.cuda
                            if torch_cuda_ver:
                                cmp, current, min_tuple, max_tuple = version_classify(torch_cuda_ver, cuda_version_range)
                                if cmp == 1:
                                    tag = f'cu{max_tuple[0]}{max_tuple[1]}'
                                elif cmp == 0 and current is not None:
                                    tag = f'cu{current[0]}{current[1]}'
                                else:
                                    tag = f'cu{max_tuple[0]}{max_tuple[1]}'
                            name = devices['CUDA']['proc']
                            msg = ''
                    except Exception:
                        pass

                # 5) nvidia-smi header parsing — last-resort rescue
                # Works driver-only; useful on fresh installs with no toolkit
                # and CPU-only torch (where step 4 can't help).
                if not devices['CUDA']['found'] and has_cmd('nvidia-smi'):
                    out = try_cmd('nvidia-smi')
                    # Header line: '| NVIDIA-SMI ...  Driver Version: ...  CUDA Version: 12.4 |'
                    m = re.search(r'cuda\s*version\s*:?\s*([0-9]+(?:\.[0-9]+)?)', out, re.IGNORECASE)
                    if m:
                        smi_version = m.group(1)
                        cmp, current, min_tuple, max_tuple = version_classify(smi_version, cuda_version_range)
                        max_ver = '.'.join(str(p) for p in max_tuple)
                        if cmp == -1:
                            msg = f'CUDA {smi_version} (from nvidia-smi) < min. Please upgrade.'
                        elif cmp is not None:
                            devices['CUDA']['found'] = True
                            name = devices['CUDA']['proc']
                            if cmp == 1:
                                tag = f'cu{max_tuple[0]}{max_tuple[1]}'
                                msg = f'CUDA {smi_version} (from nvidia-smi) > tested max {max_ver}; using cu{max_tuple[0]}{max_tuple[1]} torch build.'
                            else:
                                tag = f'cu{current[0]}{current[1]}'
                                msg = f'CUDA {smi_version} detected via nvidia-smi (driver-only).'

            # ============================================================
            # INTEL XPU
            # ============================================================
            elif has_xpu() and has_intel_gpu_pci():
                version = ''
                msg = ''
                xpu_device_count = 0

                # 1) Level Zero / SYCL runtime detection via ctypes (primary)
                try:
                    import ctypes
                    libze = None

                    if os.name == 'nt':
                        candidates = ['ze_loader.dll']
                        oneapi_root = os.environ.get('ONEAPI_ROOT', '')
                        if oneapi_root:
                            candidates.insert(0, os.path.join(oneapi_root, 'bin', 'ze_loader.dll'))
                        for lib_name in candidates:
                            try:
                                libze = ctypes.CDLL(lib_name)
                                break
                            except OSError:
                                continue
                    else:
                        candidates = ['libze_loader.so', 'libze_loader.so.1']
                        ze_lib_dirs = [
                            '/usr/lib/x86_64-linux-gnu',
                            '/usr/lib64',
                            '/opt/intel/oneapi/lib',
                        ]
                        for d in ze_lib_dirs:
                            if os.path.isdir(d):
                                try:
                                    for f in sorted(os.listdir(d), reverse=True):
                                        if f.startswith('libze_loader.so.'):
                                            candidates.append(os.path.join(d, f))
                                except OSError:
                                    pass
                        for lib_name in candidates:
                            try:
                                libze = ctypes.CDLL(lib_name)
                                break
                            except OSError:
                                continue

                    if libze:
                        if libze.zeInit(ctypes.c_uint(0)) == 0:
                            driver_count = ctypes.c_uint(0)
                            if libze.zeDriverGet(ctypes.byref(driver_count), None) == 0 and driver_count.value > 0:
                                xpu_device_count = driver_count.value
                except (OSError, AttributeError):
                    pass

                # 2) sycl-ls detection
                if not version:
                    if os.name == 'posix' and has_cmd('sycl-ls'):
                        out = try_cmd('sycl-ls')
                        if out:
                            gpu_lines = [l for l in out.splitlines() if 'gpu' in l.lower()]
                            if gpu_lines and xpu_device_count == 0:
                                xpu_device_count = len(gpu_lines)
                    elif os.name == 'nt':
                        oneapi_root = os.environ.get('ONEAPI_ROOT', '')
                        sycl_ls = os.path.join(oneapi_root, 'bin', 'sycl-ls') if oneapi_root else ''
                        if sycl_ls and os.path.isfile(sycl_ls):
                            out = try_cmd(f'"{sycl_ls}"')
                            if out:
                                gpu_lines = [l for l in out.splitlines() if 'gpu' in l.lower()]
                                if gpu_lines and xpu_device_count == 0:
                                    xpu_device_count = len(gpu_lines)
                        if xpu_device_count == 0 and has_cmd('sycl-ls'):
                            out = try_cmd('sycl-ls')
                            if out:
                                gpu_lines = [l for l in out.splitlines() if 'gpu' in l.lower()]
                                if gpu_lines:
                                    xpu_device_count = len(gpu_lines)

                # 3) oneAPI version file
                if not version:
                    if os.name == 'posix':
                        for p in (
                            '/opt/intel/oneapi/version.txt',
                            '/opt/intel/oneapi/compiler/latest/version.txt',
                            '/opt/intel/oneapi/runtime/latest/version.txt',
                        ):
                            if os.path.exists(p):
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    version = lib_version_parse(f.read()) or ''
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
                                        version = lib_version_parse(f.read()) or ''
                                    break

                # Version comparison + tag assignment (unranged by default: accepts anything)
                if version:
                    cmp, current, min_tuple, max_tuple = version_classify(version, xpu_version_range)
                    min_ver = '.'.join(str(p) for p in min_tuple)
                    max_ver = '.'.join(str(p) for p in max_tuple)
                    if cmp == -1:
                        msg = f'XPU oneAPI {version} < min {min_ver}. Please upgrade.'
                    elif cmp is None:
                        msg = 'Intel GPU detected but oneAPI version unparseable.'
                    else:
                        devices['XPU']['found'] = True
                        name = devices['XPU']['proc']
                        tag = devices['XPU']['proc']
                        if cmp == 1:
                            msg = f'XPU oneAPI {version} > tested max {max_ver}; using default xpu torch build.'
                elif xpu_device_count > 0:
                    msg = 'Intel GPU detected but oneAPI toolkit version file not found.'
                else:
                    msg = 'Intel GPU detected but oneAPI Base Toolkit not installed.'

                # 4) PyTorch last-resort fallback
                if not devices['XPU']['found']:
                    try:
                        import torch
                        if hasattr(torch, 'xpu') and torch.xpu.is_available():
                            devices['XPU']['found'] = True
                            xpu_device_count = torch.xpu.device_count()
                            name = devices['XPU']['proc']
                            tag = devices['XPU']['proc']
                            msg = 'XPU detected via PyTorch fallback.'
                    except Exception:
                        pass

            # ============================================================
            # APPLE MPS
            # ============================================================
            elif self.system == systems['MACOS'] and arch in ('arm64', 'aarch64'):
                devices['MPS']['found'] = True
                name = devices['MPS']['proc']
                tag = devices['MPS']['proc']

            # ============================================================
            # CPU
            # ============================================================
            if tag is None:
                name = devices['CPU']['proc']
                tag = devices['CPU']['proc']

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
        version_file = os.path.join(local_path, 'version.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding = 'utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
        return None

    def version_tuple(self, v:str, max_parts:int=3)->tuple:
        m = re.search(r'\d+(?:\.\d+)*', v)
        if not m:
            return (0,) * max_parts
        nums = [int(n) for n in m.group(0).split('.')[:max_parts]]
        return tuple(nums + [0] * (max_parts - len(nums)))

    def eval_marker(self, marker_part:str)->tuple|bool:
        env = {
            'python_version': '.'.join(map(str, sys.version_info[:2])),
            'sys_platform': sys.platform,
            'platform_system': platform.system(),
            'platform_machine': platform.machine()
        }
        m = re.match(r'(\w+)\s*(==|!=|>=|<=|>|<)\s*["\']([^"\']+)["\']', marker_part)
        if not m:
            raise ValueError(f'Unsupported marker: {marker_part}')
        key, op, value = m.groups()
        if key not in env:
            raise ValueError(f'Unknown marker variable: {key}')
        def vt(v): return tuple(map(int, v.split('.'))) if v[0].isdigit() else v
        left = vt(env[key])
        right = vt(value)
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '>': return left > right
        if op == '<': return left < right
        return False

    def install_python_packages(self)->int:
        if not os.path.exists(requirements_file):
            error = f'Warning: File {requirements_file} not found. Skipping package check.'
            print(error)
            return 1
        overrides = {}
        if self.system == systems['MACOS'] and self.arch == 'x86_64':
            overrides['numba'] = 'numba==0.62.0'
        try:
            with open(requirements_file, 'r') as f:
                contents = f.read().replace('\r', '\n')
                packages = []
                for line in contents.splitlines():
                    pkg = line.strip()
                    if not pkg or not re.search(r'[a-zA-Z0-9]', pkg):
                        continue
                    if '#' in pkg:
                        pkg = pkg.split('#', 1)[0].strip()
                        if not pkg:
                            continue
                    head = re.split(r'[<>=!\[;]', pkg, 1)[0].strip().lower()
                    if head in {'torch', 'torchaudio'}:
                        continue
                    if head in overrides:
                        pkg = overrides[head]
                    packages.append(pkg)
            missing_packages = []
            for package in packages:
                raw_pkg = package.strip()
                if ';' in raw_pkg:
                    pkg_part, marker_part = raw_pkg.split(';', 1)
                    marker_part = marker_part.strip()
                    try:
                        if not self.eval_marker(marker_part):
                            continue
                    except Exception as e:
                        print(f'Warning: Could not evaluate marker {marker_part} for {pkg_part}: {e}')
                    raw_pkg = pkg_part.strip()
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
                print('\nInstalling missing or upgrade packages…\n')
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
            return self.check_dictionary()
        except Exception as e:
            print(f'install_python_packages() error: {e}')
            return 1
          
    def check_numpy(self)->bool:
        try:
            try:
                numpy_version = self.get_package_version('numpy')
                numpy_version_base = self.version_tuple(numpy_version)
            except Exception:
                numpy_version = None
                numpy_version_base = None
            torch_version = self.get_package_version('torch')
            torch_version_base = self.version_tuple(torch_version)
            min_cpu_baseline = self.cpu_baseline
            if numpy_version is None:
                if torch_version_base <= self.version_tuple('2.2.2'):
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force-reinstall', 'py-cpuinfo', 'numpy<2'])
                elif not min_cpu_baseline:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force-reinstall', 'py-cpuinfo', 'numpy<2.4.0'])
                else:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force-reinstall', 'py-cpuinfo', 'numpy'])
            elif torch_version_base <= self.version_tuple('2.2.2') and numpy_version_base >= self.version_tuple('2.0.0'):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force-reinstall', 'py-cpuinfo', 'numpy<2'])
            elif not min_cpu_baseline and numpy_version_base >= self.version_tuple('2.4.0'):
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--force-reinstall', 'py-cpuinfo', 'numpy<2.4.0'])
            return True
        except subprocess.CalledProcessError as e:
            error = f'Failed to install numpy package: {e}'
            print(error)
            return False
        except Exception as e:
            error = f'Error while installing numpy package: {e}'
            print(error)
            return False
          
    def check_dictionary(self)->bool:
        import unidic
        unidic_path = unidic.DICDIR
        dicrc = os.path.join(unidic_path, 'dicrc')
        if not os.path.exists(dicrc) or os.path.getsize(dicrc) == 0:
            try:
                error = 'UniDic dictionary not found or incomplete. Downloading now…'
                print(error)
                subprocess.run(['python', '-m', 'unidic', 'download'], check=True)
            except (subprocess.CalledProcessError, ConnectionError, OSError) as e:
                error = f'Failed to download UniDic dictionary. Error: {e}. Unable to continue without UniDic. Exiting…'
                raise SystemExit(error)
                return 1
        return 0
          
    def install_device_packages(self, device_info_str:str)->int:

        def _needs_reinstall():
            if not torch_version_current_full:
                return True
            if tag == devices['CPU']['proc']:
                if torch_version_current_base != torch_version_matrix:
                    return True
                return current_tag is not None and current_tag != devices['CPU']['proc']
            if non_standard_tag is None:
                return current_tag != tag
            return non_standard_tag != tag

        try:
            if device_info_str:
                device_info = json.loads(device_info_str)
                if device_info:
                    print(f'---> Hardware detected: {device_info}')
                    tag = device_info.get('tag')
                    if tag in ['unknown','unsupported']:
                        return 0
                    key = 'last' if self.python_version >= (3, 12) else 'base'
                    torch_version_matrix = torch_matrix[tag].get(key) or torch_matrix[tag]['base']
                    torch_version_current_full = self.get_package_version('torch')
                    torch_version_current_base = None
                    current_tag = None
                    non_standard_tag = None
                    if torch_version_current_full:
                        m = re.search(r'\+(.+)$', torch_version_current_full)
                        current_tag = m.group(1) if m else None
                        non_standard_match = re.fullmatch(r'[0-9a-f]{7,40}', current_tag) if current_tag is not None else None
                        non_standard_tag = non_standard_match.group(0) if non_standard_match else None
                        torch_version_current_base = torch_version_current_full.split('+',1)[0]
                    if device_info['os'] == 'macosx_11_0' and device_info['arch'] == 'x86_64':
                        torch_version_matrix = torch_version_current_base = '2.2.2'
                    if _needs_reinstall():
                        try:
                            msg = f"Installing the right library packages for {device_info['name']}…"
                            print(msg)
                            os_env = device_info['os']
                            arch = device_info['arch']
                            toolkit_version = ''.join(c for c in tag if c.isdigit())
                            if device_info['name'] == devices['JETSON']['proc']:
                                url = default_jetson_url
                                py_major, py_minor = device_info['pyvenv']
                                tag_py = f'cp{py_major}{py_minor}-cp{py_major}{py_minor}'
                                torch_pkg = f"{url}/v{toolkit_version}/torch-{torch_version_matrix}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                torchaudio_pkg = f"{url}/v{toolkit_version}/torchaudio-{torch_version_matrix}%2B{tag}-{tag_py}-{os_env}_{arch}.whl"
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', torch_pkg])
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', torchaudio_pkg])
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', 'scikit-learn'])
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', 'scipy'])
                            elif device_info['name'] == devices['ROCM']['proc'] and self.system == systems['WINDOWS']:
                                url = default_pytorch_amd_url
                                py_major, py_minor = device_info['pyvenv']
                                tag_py = f'cp{py_major}{py_minor}-cp{py_major}{py_minor}'
                                extra_tag_url = torch_matrix[tag].get('extra_tag', '').replace('+', '%2B')
                                # rocm_sdk is required by torch ROCm wheels on Windows; install it first if missing
                                import importlib.util
                                if importlib.util.find_spec('rocm_sdk') is None:
                                    rocm_ver = tag[len('rocm-rel-'):] if tag.startswith('rocm-rel-') else tag
                                    sdk_pkgs = [
                                        f'{url}/{tag}/rocm_sdk_core-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{tag}/rocm_sdk_devel-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{tag}/rocm_sdk_libraries_custom-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{tag}/rocm-{rocm_ver}.tar.gz',
                                    ]
                                    msg = f'Installing ROCm SDK {rocm_ver}…'
                                    print(msg)
                                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', *sdk_pkgs])
                                torch_pkg = f'{url}/{tag}/torch-{torch_version_matrix}{extra_tag_url}-{tag_py}-{os_env}_{arch}.whl'
                                torchaudio_pkg = f'{url}/{tag}/torchaudio-{torch_version_matrix}{extra_tag_url}-{tag_py}-{os_env}_{arch}.whl'
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', '--no-deps', torch_pkg, torchaudio_pkg])
                            else:
                                url = default_pytorch_url
                                tag_dir = 'cpu' if device_info['name'] == devices['MPS']['proc'] else tag
                                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', f'torch=={torch_version_matrix}', f'torchaudio=={torch_version_matrix}', '--force-reinstall', '--index-url', f'{url}/{tag_dir}'])
                            # torchcodec is only needed (and only available) for torch >= 2.9.0 — earlier
                            # torch/torchaudio releases ship their own audio I/O backends.
                            # Routing on download.pytorch.org for >= 2.9.0:
                            #   - macOS arm64: bare wheels under /whl/cpu (via tag_dir=cpu, like torch/torchaudio)
                            #   - Linux x86_64 / Windows amd64: +cpu wheels from 0.11.1 onwards under /whl/cpu;
                            #     +cuXXX under /whl/<cuXXX>
                            #   - Linux aarch64: NO torchcodec wheels on the PyTorch index -> PyPI fallback
                            # --no-deps prevents torchcodec from yanking torch back to a different variant.
                            if self.version_tuple(torch_version_matrix, 2) >= (2, 9):
                                torchcodec_cmd = [sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', '--no-deps', 'torchcodec']
                                if (device_info['os'] == 'manylinux_2_28' and device_info['arch'] == 'aarch64') or (tag == devices['XPU']['proc']) or (tag == devices['ROCM']['proc']):
                                    pass  # PyPI fallback — no aarch64 torchcodec on any PyTorch index
                                else:
                                    # Same index as torch: cpu / cuXXX / xpu / rocmX.Y
                                    # tag_dir already maps MPS -> cpu (macOS arm64 uses bare wheels there)
                                    torchcodec_cmd += ['--index-url', f'{default_pytorch_url}/{tag_dir}']
                                subprocess.check_call(torchcodec_cmd)
                        except subprocess.CalledProcessError as e:
                            error = f'Failed to install torch package: {e}'
                            print(error)
                            return 1
                        except Exception as e:
                            error = f'Error while installing torch package: {e}'
                            print(error)
                            return 1
                    if device_info['os'] == 'linux' and ('jetpack' in device_info.get('note', '').lower() or device_info['name'] == devices['JETSON']['proc']):
                        libgomp_src = '/usr/lib/aarch64-linux-gnu/libgomp.so'
                        if os.path.exists(libgomp_src):
                            libs_dir = os.path.join('python_env', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'scikit_learn.libs')
                            if os.path.isdir(libs_dir):
                                for libgomp_dst in glob(os.path.join(libs_dir, 'libgomp*')):
                                    if os.path.islink(libgomp_dst):
                                        if os.path.realpath(libgomp_dst) == os.path.realpath(libgomp_src):
                                            continue
                                        os.unlink(libgomp_dst)
                                    else:
                                        os.unlink(libgomp_dst)
                                    msg = 'Create symlink to use OS libgomp.'
                                    print(msg)
                                    os.symlink(libgomp_src, libgomp_dst)
                    if not self.check_numpy():
                        return 1
                    return 0
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