import os, re, sys, csv, platform, shutil, subprocess, importlib, json, tempfile, time
from functools import cached_property, wraps
from typing import Any, Callable, Union
from glob import glob
from importlib.metadata import version, distribution, distributions, PackageNotFoundError
from lib.conf import *
from lib.lang import legends

# one install pass at a time per python env: two e2a starts (double click, a second shortcut, a headless run next to
# the GUI) ran their uv installs side by side, and the --reinstall-package of one removed files and metadata under the
# other already importing them (gradio without gradio/http_server.py nor dist-info at launch). The lock file lives in
# sys.prefix, the env uv installs into (an engine venv gets its own), is reentrant within a process and is released by
# the OS when its holder dies. The later start waits, then finds the env complete
install_lock_depth = 0

def install_lock_acquire()->Any:
    try:
        lock_file = open(os.path.join(sys.prefix, '.e2a_install.lock'), 'a+')
    except OSError:
        # read-only env (docker image layer): nothing installs into it concurrently
        return None
    waiting = False
    while True:
        try:
            if os.name == 'nt':
                import msvcrt
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_file
        except OSError:
            if not waiting:
                msg = legends['msg_install_lock_wait'].format(env=sys.prefix)
                print(msg)
                waiting = True
            time.sleep(1)

def install_lock_release(lock_file:Any)->None:
    try:
        if os.name == 'nt':
            import msvcrt
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        lock_file.close()

def install_locked(method:Callable)->Callable:
    @wraps(method)
    def wrapper(*args, **kwargs):
        global install_lock_depth
        lock_file = install_lock_acquire() if install_lock_depth == 0 else None
        install_lock_depth += 1
        try:
            return method(*args, **kwargs)
        finally:
            install_lock_depth -= 1
            if lock_file is not None:
                install_lock_release(lock_file)
    return wrapper

class DeviceInstaller():
    device_pkgs = ['onnxruntime', 'transformers']
    # 2.11 is the final torchaudio line: it works with torch 2.11 and every later torch,
    # so above it torchaudio is clamped instead of tracking torch. its patch releases
    # are not on every index (cu132: no 2.11.0 at all, only 2.11.1+cu132 on nightly),
    # so the PyTorch index path accepts any 2.11.x >= this, see torchaudio_spec().
    torchaudio_max = '2.11.0'
    # installed torch below the key -> transformers must stay below the value.
    # 2.4: 5.1+ declares torch>=2.4 and silently disables PyTorch below it.
    # 2.5: 5.15+ declares torch>=2.5, but the declared floor lies for 2.4: 5.8 breaks
    #      at import (torch.library.custom_op with string annotations, rejected by
    #      2.4's infer_schema), 5.9/5.10 fail too, 5.14 imports DTensor from its
    #      2.5-only public path. Verified on torch 2.4.1: 5.0.0 to 5.7.0 import and generate.
    # 2.6: 5.20+ declares torch>=2.6 and disables PyTorch below it (cu121/rocm6.2 install
    #      torch 2.5.1: "NameError: name 'nn' is not defined" importing core_model_loading).
    #      The declared floor lies for 2.5 too: 5.19 calls torch.accelerator (2.6+) when
    #      transformers.pipelines imports. Verified on torch 2.5.1: 5.18.0 imports, runs a
    #      pipeline and generates with MusicGen loaded from safetensors.
    # add a row when a release raises the floor again, and test it: the declared
    # floor alone is not enough.
    transformers_caps = {'2.4': '5.1', '2.5': '5.8', '2.6': '5.19'}
    # coqui-tts' own transformers floor (coqui-tts 0.28: transformers>=4.57). A bare 'transformers' keeps an older
    # release installed by hand, which coqui-tts does not run with: 4.46 imports torch.distributed.fsdp in generate()
    # and fails on torch builds without distributed (the +vulkan wheels)
    transformers_min = '4.57'
    exclusive_pkgs = {
        'onnxruntime': ['onnxruntime', 'onnxruntime-gpu', 'onnxruntime-directml']
    }
    # dependencies install_missing_dependencies() never pulls from PyPI: install_device_packages() puts them in from
    # its own wheels/indexes (a PyPI torchvision would drag a CPU torch in), finalize_exclusive_packages() swaps the
    # onnxruntime builds, demucs-simple replaces demucs, remove_obsolete_packages() takes unidic out on purpose
    dependency_skip_re = re.compile(r'^(?:torch|torchaudio|torchcodec|torchvision|onnxruntime(?:-[a-z0-9]+)?|nvidia-.*|triton|pytorch-triton.*|rocm.*|intel-.*|demucs|unidic)$')
    pip_cache_dir = os.environ.get('E2A_PIP_CACHE_DIR') or os.path.join(tempfile.gettempdir(), 'e2a_pip_cache')
    # seconds the GPU choice waits for an answer before taking the system's GPU 0, so an unattended install never hangs
    gpu_choice_timeout = 60
    # PCI vendor id -> the device its runtime serves, for the GPU choice
    gpu_pci_vendors = {0x1002: devices['ROCM']['proc'], 0x10de: devices['CUDA']['proc'], 0x8086: devices['XPU']['proc']}

    uv_install_url = 'https://docs.astral.sh/uv/getting-started/installation/'
    # official download page of the Microsoft Visual C++ redistributables (msvcp140/vcruntime140: absent from every
    # torch wheel, installed by no launcher; without them import torch dies with WinError 126)
    vcredist_url = 'https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist'

    def __init__(self):
        self.system = sys.platform
        self.arch = self.check_arch
        self.python_version = sys.version_info[:2]
        self.python_version_tuple = sys.version_info
        self.uv_bin = self.find_uv()
        if not self.uv_bin:
            # app.py checks uv first (check_uv) and the launchers install it before any DeviceInstaller: never reached by a normal run
            raise FileNotFoundError(legends['error_uv_missing'].format(url=self.uv_install_url))

    @staticmethod
    def find_uv()->Union[str, None]:
        p = shutil.which('uv')
        if p:
            return p
        candidates = [
            os.path.expanduser('~/.local/bin/uv'),
            os.path.expanduser('~/.cargo/bin/uv'),
        ]
        if os.name == 'nt':
            candidates.append(os.path.expanduser(r'~\.local\bin\uv.exe'))
            candidates.append(os.path.expanduser(r'~\.cargo\bin\uv.exe'))
        else:
            candidates.append(os.path.expanduser('~/Library/Application Support/uv/bin/uv'))
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def _uv_pip(self, subcommand:str, *args)->list:
        return [self.uv_bin, 'pip', subcommand, '--python', python_exec, *args]

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
        if machine not in (archs['X86_64'], archs['AMD64']):
            return True
        # probe in python_exec, the interpreter _uv_pip installs into. the running
        # interpreter is not guaranteed to be it (conf.py lets PY_CMD win over
        # sys.executable), and then an in-process import never sees the install.
        # same pattern as _probe_gpus() and the torchcodec AudioDecoder probe.
        probe = 'import json; from cpuinfo import get_cpu_info; print(json.dumps(get_cpu_info().get("flags", [])))'
        try:
            subprocess.check_call(self._uv_pip('install', '--no-cache', 'py-cpuinfo'))
            out = subprocess.check_output([python_exec, '-c', probe], text=True, timeout=60)
            flags = set(json.loads(out.strip().splitlines()[-1]))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, IndexError) as e:
            # conservative verdict: numpy<2.4.0 runs on any x86_64, never abort provisioning here
            error = f'cpu_baseline() error: {e} (running {sys.executable}, target {python_exec}), assuming no x86-64-v2'
            print(error)
            return False
        return {'sse4_2', 'popcnt', 'ssse3'}.issubset(flags)

    def load_device_info(self)->Union[dict, None]:
        if not os.path.isfile(device_info_json) or os.path.getsize(device_info_json) == 0:
            return None
        try:
            with open(device_info_json, 'r', encoding='utf-8') as f:
                device_info = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
        return device_info if isinstance(device_info, dict) else None

    def link_os_libgomp(self, env_dir:str, device_info:Union[dict, None])->None:
        # Jetson (aarch64, glibc's small static TLS reserve): a wheel's own libgomp copy (auditwheel renames it, e.g.
        # scikit_learn.libs/libgomp-947d5fa1.so.1.0.0) is a second libgomp in the process, which cannot load once torch's
        # took the reserve ("cannot allocate memory in static TLS block"). Every <package>.libs copy in the environment
        # (python_env or an engine's venv) becomes a link to the OS libgomp torch loads, so the process only ever has that
        # one. Already linked copies are left alone: cheap enough to run at every engine start, which fixes existing venvs
        if not device_info or device_info.get('os') != 'linux' or not ('jetpack' in device_info.get('note', '').lower() or device_info.get('name') == devices['JETSON']['proc']):
            return
        # libgomp.so.1 is the runtime soname (package libgomp1), libgomp.so only comes with a gcc dev package
        libgomp_src = next((path for path in ('/usr/lib/aarch64-linux-gnu/libgomp.so.1', '/usr/lib/aarch64-linux-gnu/libgomp.so') if os.path.exists(path)), None)
        if libgomp_src is None:
            return
        for libgomp_dst in glob(os.path.join(env_dir, 'lib', 'python*', 'site-packages', '*.libs', 'libgomp*')):
            if os.path.islink(libgomp_dst) and os.path.realpath(libgomp_dst) == os.path.realpath(libgomp_src):
                continue
            msg = legends['msg_symlink_libgomp']
            print(msg)
            try:
                # the link replaces the copy in one step: a failure never leaves the package without its libgomp
                link_tmp = f'{libgomp_dst}.e2a'
                if os.path.lexists(link_tmp):
                    os.unlink(link_tmp)
                os.symlink(libgomp_src, link_tmp)
                os.replace(link_tmp, libgomp_dst)
            except OSError as e:
                error = legends['error_symlink_libgomp'].format(file=libgomp_dst, error=e)
                print(error)

    def sync_sitecustomize(self, env_dir:str)->None:
        # components/sitecustomize.py in an engine's venv (torchaudio.load -> soundfile, coqui's config allowlisted for
        # torch.load, torch.xpu off under E2A_XPU_UNUSABLE). Copied when missing or different, an identical copy is left
        # alone: cheap enough to run at every engine start, so a venv installed before gets the patches added since
        sitecustomize_src = os.path.join(components_dir, 'sitecustomize.py')
        if self.system == systems['WINDOWS']:
            site_dirs = [os.path.join(env_dir, 'Lib', 'site-packages')]
        else:
            site_dirs = glob(os.path.join(env_dir, 'lib', 'python*', 'site-packages'))
        try:
            with open(sitecustomize_src, 'rb') as f:
                content = f.read()
        except OSError as e:
            error = legends['error_sitecustomize_sync'].format(file=sitecustomize_src, error=e)
            print(error)
            return
        for site_dir in site_dirs:
            if not os.path.isdir(site_dir):
                continue
            sitecustomize_dst = os.path.join(site_dir, 'sitecustomize.py')
            try:
                with open(sitecustomize_dst, 'rb') as f:
                    if f.read() == content:
                        continue
            except OSError:
                pass
            msg = legends['msg_sitecustomize_sync'].format(file=sitecustomize_dst)
            print(msg)
            try:
                # the new copy replaces the old one in one step: a worker starting meanwhile reads either, never half
                # of one. A copy left read-only (copy2 of a read-only source) would refuse the replace on Windows
                if os.path.exists(sitecustomize_dst) and not os.access(sitecustomize_dst, os.W_OK):
                    os.chmod(sitecustomize_dst, os.stat(sitecustomize_dst).st_mode | 0o200)
                sitecustomize_tmp = f'{sitecustomize_dst}.e2a'
                with open(sitecustomize_tmp, 'wb') as f:
                    f.write(content)
                os.replace(sitecustomize_tmp, sitecustomize_dst)
            except OSError as e:
                error = legends['error_sitecustomize_sync'].format(file=sitecustomize_dst, error=e)
                print(error)

    def check_pyvenv(self, tag:str)->list:
        # fixed per device, the same rule the launchers create python_env with: jetson wheels are cp310 only
        # (min_python_version), every other device runs max_python_version, which all other prebuilt wheels (py-pkg
        # +vulkan ones included) target. Never read from .device_info.json nor the OS python: it lives next to the
        # app, so it outlives a python_env the launcher recreated, and an older venv's record would pick wheels the
        # new venv cannot load
        if tag in ['jetson5', 'jetson6', 'jetson7']:
            return list(min_python_version)
        return list(max_python_version)

    def check_device_info(self, mode:str)->str:
        if mode == NATIVE:
            previous = self.load_device_info()
            name, tag, msg = self.check_hardware
            pyvenv = self.check_pyvenv(tag)
            arch = archs['AARCH64'] if name in [devices['JETSON']['proc']] else self.arch
            os_env = 'linux' if name == devices['JETSON']['proc'] else self.check_platform
            if all([name, tag, os_env, arch, pyvenv]):
                device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyvenv, "tag": tag, "note": re.sub(r'[^\w\s-]', '', msg.replace('!', ''))}
                if device_info != previous:
                    try:
                        with open(device_info_json, 'w', encoding='utf-8') as f:
                            json.dump(device_info, f)
                    except OSError as e:
                        error = legends['msg_device_info_write_failed'].format(e=e)
                        print(error, file=sys.stderr)
                return json.dumps(device_info)
        elif mode == BUILD_DOCKER:
            name, tag, msg = self.detect_device(BUILD_DOCKER)
            os_env = 'manylinux_2_28'
            arch = archs['AARCH64'] if name in [devices['JETSON']['proc'], devices['MPS']['proc']] or (self.system == systems['MACOS'] and self.arch == archs['ARM64']) else self.arch
            # Jetson and MPS get no image of their own: a container sees no Tegra nor Metal GPU
            if name in [devices['JETSON']['proc'], devices['MPS']['proc']]:
                name = tag = devices['CPU']['proc']
            # after the mapping above: the image is Linux with the python of its own tag, not the host's
            pyvenv = self.check_pyvenv(tag)
            if name in [devices['CPU']['proc'], devices['VULKAN']['proc']]:
                # an image without a GPU torch is the +vulkan one whenever its wheels exist: it runs on the CPU like the cpu
                # image, and a GPU passed in later (--device=/dev/dri, a VM GPU such as Podman's libkrun on macOS) is used
                # once the device is set to vulkan. The launchers run it like the cpu image on a host without /dev/dri
                linux_arch = archs['X86_64'] if arch == archs['AMD64'] else arch
                if self.vulkan_wheels_ok(tuple(pyvenv), f'{os_env}_{linux_arch}'):
                    # a macOS host takes vulkan for its Metal GPU through MoltenVK: the Linux container never sees it, and
                    # 'Vulkan GPU Metal (MoltenVK)' in the image's device_info misled every bug report sent from it
                    if name == devices['CPU']['proc'] or self.system == systems['MACOS']:
                        msg = legends['msg_vulkan_docker_image']
                    name = tag = devices['VULKAN']['proc']
                    arch = linux_arch
                else:
                    name = tag = devices['CPU']['proc']
            device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyvenv, "tag": tag, "note": re.sub(r'[^\w\s-]', '', msg.replace('!', ''))}
            try:
                with open(device_info_json, 'w', encoding='utf-8') as f:
                    json.dump(device_info, f)
            except OSError as e:
                error = legends['msg_device_info_write_failed'].format(e=e)
                print(error, file=sys.stderr)
            return json.dumps(device_info)
        elif mode == FULL_DOCKER:
            device_info = None
            if os.path.isfile(device_info_json):
                try:
                    with open(device_info_json, 'r', encoding='utf-8') as f:
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
        return ''

    def get_package_version(self, pkg:str)->Union[str, bool]:
        try:
            return version(pkg)
        except PackageNotFoundError:
            return False

    def vulkan_gpus(self)->list:
        # names of the real Vulkan GPUs the system loader sees
        return [name for _, name, _ in self.vulkan_devices()]

    @cached_property
    def vulkan_torch_ok(self)->bool:
        # the +vulkan torch applies here: this OS / arch in torch_matrix and its wheels on py-pkg for this venv's Python.
        # Already installed: no network, so an offline start keeps the Vulkan torch
        entry = torch_matrix.get(devices['VULKAN']['proc'])
        arch_tag = self.detect_arch_tag()
        if not entry or self.system not in entry['os'] or arch_tag not in entry['arch']:
            return False
        if self.get_package_version('torch') == f"{entry['last']}+{devices['VULKAN']['proc']}":
            return True
        return self.vulkan_wheels_ok(self.python_version, f'{self.detect_platform_tag()}_{arch_tag}')

    def vulkan_devices(self)->list:
        # (PCI vendor id, name, deviceType) of the real Vulkan GPUs the system loader sees, in its order: integrated (1),
        # discrete (2) or virtual (3). Software renderers (lavapipe/llvmpipe, SwiftShader: VK_PHYSICAL_DEVICE_TYPE_CPU)
        # don't count
        import ctypes
        try:
            vk = ctypes.CDLL(vulkan_loader)
        except OSError:
            return []
        class AppInfo(ctypes.Structure):
            _fields_ = [('sType', ctypes.c_int), ('pNext', ctypes.c_void_p), ('pApplicationName', ctypes.c_char_p), ('applicationVersion', ctypes.c_uint32), ('pEngineName', ctypes.c_char_p), ('engineVersion', ctypes.c_uint32), ('apiVersion', ctypes.c_uint32)]
        class InstInfo(ctypes.Structure):
            _fields_ = [('sType', ctypes.c_int), ('pNext', ctypes.c_void_p), ('flags', ctypes.c_uint32), ('pApplicationInfo', ctypes.POINTER(AppInfo)), ('enabledLayerCount', ctypes.c_uint32), ('ppEnabledLayerNames', ctypes.c_void_p), ('enabledExtensionCount', ctypes.c_uint32), ('ppEnabledExtensionNames', ctypes.c_void_p)]
        vk.vkCreateInstance.restype = ctypes.c_int
        vk.vkCreateInstance.argtypes = [ctypes.POINTER(InstInfo), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        vk.vkEnumeratePhysicalDevices.restype = ctypes.c_int
        vk.vkEnumeratePhysicalDevices.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
        vk.vkGetPhysicalDeviceProperties.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        vk.vkDestroyInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        app = AppInfo(0, None, b'e2a', 0, None, 0, (1 << 22) | (1 << 12))  # VK_STRUCTURE_TYPE_APPLICATION_INFO, Vulkan 1.1
        info = InstInfo(1, None, 0, ctypes.pointer(app), 0, None, 0, None)  # VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO
        inst = ctypes.c_void_p()
        if vk.vkCreateInstance(ctypes.byref(info), None, ctypes.byref(inst)) != 0:
            return []
        found = []
        try:
            count = ctypes.c_uint32(0)
            if vk.vkEnumeratePhysicalDevices(inst, ctypes.byref(count), None) == 0 and count.value:
                devs = (ctypes.c_void_p * count.value)()
                vk.vkEnumeratePhysicalDevices(inst, ctypes.byref(count), devs)
                for dev in devs:
                    props = ctypes.create_string_buffer(1024)  # VkPhysicalDeviceProperties is 824 bytes
                    vk.vkGetPhysicalDeviceProperties(dev, props)
                    device_type = int.from_bytes(props.raw[16:20], 'little')
                    if device_type in (1, 2, 3):  # integrated, discrete, virtual
                        found.append((int.from_bytes(props.raw[8:12], 'little'), props.raw[20:276].split(b'\0')[0].decode(errors='replace'), device_type))  # vendorID, deviceName
        finally:
            vk.vkDestroyInstance(inst, None)
        return found

    def vulkan_wheels_ok(self, py:tuple, plat:str)->bool:
        # the +vulkan torch / torchaudio (and torchcodec on macOS) wheels exist on py-pkg for this Python and platform
        # (e.g. (3, 12), 'manylinux_2_28_x86_64'). A GitHub release asset answers 302 (redirect to its storage) when
        # present, 404 when not: no redirect is followed, nothing is downloaded
        import urllib.request, urllib.error
        entry = torch_matrix.get(devices['VULKAN']['proc'])
        if not entry:
            return False
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        opener = urllib.request.build_opener(NoRedirect)
        torch_ver = entry['last']
        py_tag = f'cp{py[0]}{py[1]}'
        wheel_end = f"{devices['VULKAN']['proc']}-{py_tag}-{py_tag}-{plat}.whl"
        urls = [f'{default_jetson_url}/torch/torch-{torch_ver}%2B{wheel_end}', f'{default_jetson_url}/torchaudio/torchaudio-{self.torchaudio_version(torch_ver)}%2B{wheel_end}']
        if plat.startswith('macosx') and entry.get('codec'):
            urls.append(f"{default_jetson_url}/torchcodec/torchcodec-{entry['codec']}%2B{wheel_end}")
        for url in urls:
            try:
                code = opener.open(urllib.request.Request(url, method='HEAD'), timeout=15).status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception:
                return False
            if code not in (200, 302):
                return False
        return True

    def ask_tty(self, prompt:str, timeout:int)->Union[str, bool, None]:
        # one line typed on the terminal, read past the launchers' redirections (their capture of stdout, bash feeding the
        # script on stdin). None when there is no terminal (Docker build, GUI, CI), False without Enter within timeout
        import time
        deadline = time.monotonic() + timeout
        try:
            if self.system == systems['WINDOWS']:
                import msvcrt
                with open('CONOUT$', 'w', encoding='utf-8') as out:
                    out.write(prompt)
                    out.flush()
                    chars = []
                    while time.monotonic() < deadline:
                        if not msvcrt.kbhit():
                            time.sleep(0.05)
                            continue
                        char = msvcrt.getwch()
                        if char in ('\r', '\n'):
                            out.write('\n')
                            return ''.join(chars).strip()
                        if char == '\x03':
                            raise KeyboardInterrupt
                        if char in ('\x00', '\xe0'):
                            msvcrt.getwch()  # second half of an arrow / function key
                        elif char == '\b':
                            if chars:
                                chars.pop()
                                out.write('\b \b')
                        elif char.isprintable():
                            chars.append(char)
                            out.write(char)
                        out.flush()
                    out.write('\n')
                    return False
            import select
            # one handle each way: 'r+' would need a seekable file, a terminal is not
            with open('/dev/tty', 'w', encoding='utf-8') as tty_out, open('/dev/tty', 'r', encoding='utf-8') as tty_in:
                tty_out.write(prompt)
                tty_out.flush()
                if select.select([tty_in], [], [], timeout)[0]:
                    return tty_in.readline().strip()
                tty_out.write('\n')
                return False
        except OSError:
            return None

    def system_gpus(self, vk_devices:list)->list:
        # the GPUs in the OS's own numbering, GPU 0 first, as (PCI vendor id, model, add-in card). Windows: adapter order,
        # which the Vulkan loader enumerates in (DXGI order), WMI without a loader. Linux: PCI bus order. Model and card
        # come from the Vulkan device of the same vendor (deviceType discrete); without one the card is guessed: Intel's
        # integrated GPU is 00:02.0 on the PCI bus (on Windows: any Intel), NVIDIA and AMD count as cards
        if self.system == systems['WINDOWS'] and vk_devices:
            return [(vendor_id, model, device_type == 2) for vendor_id, model, device_type in vk_devices]
        pci = []  # (vendor id, PCI address)
        if self.system == systems['WINDOWS']:
            try:
                out = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-CimInstance Win32_VideoController | ForEach-Object { $_.PNPDeviceID }'], capture_output=True, text=True, errors='replace', timeout=20).stdout
            except (OSError, subprocess.TimeoutExpired):
                out = ''
            pci = [(int(vendor_id, 16), '') for vendor_id in re.findall(r'VEN_([0-9A-F]{4})', out, re.IGNORECASE)]
        else:
            sysfs = '/sys/bus/pci/devices'
            if os.path.isdir(sysfs):
                for dev in sorted(os.listdir(sysfs)):  # 'dddd:bb:dd.f', fixed width hex: sorted is bus order
                    try:
                        with open(os.path.join(sysfs, dev, 'class')) as f:
                            if not f.read().strip().startswith(('0x0300', '0x0302')):
                                continue
                        with open(os.path.join(sysfs, dev, 'vendor')) as f:
                            pci.append((int(f.read().strip(), 16), dev))
                    except (OSError, ValueError):
                        continue
            if not pci and shutil.which('lspci'):
                try:
                    out = subprocess.run(['lspci', '-nn'], capture_output=True, text=True, errors='replace', timeout=20).stdout
                except (OSError, subprocess.TimeoutExpired):
                    out = ''
                for address, vendor_id in re.findall(r'^(\S+) .*\[030[02]\].*\[([0-9a-f]{4}):[0-9a-f]{4}\]', out, re.IGNORECASE | re.MULTILINE):
                    pci.append((int(vendor_id, 16), address if address.count(':') == 2 else f'0000:{address}'))
        if not pci:
            return [(vendor_id, model, device_type == 2) for vendor_id, model, device_type in vk_devices]
        unmatched = list(vk_devices)
        gpus = []
        for vendor_id, address in pci:
            card = vendor_id != 0x8086 or (bool(address) and not address.endswith(':00:02.0'))
            same = [device for device in unmatched if device[0] == vendor_id]
            device = next((device for device in same if (device[2] == 2) == card), same[0] if same else None)
            if device:
                unmatched.remove(device)
                gpus.append((vendor_id, device[1], device[2] == 2))
            else:
                gpus.append((vendor_id, '', card))
        # Vulkan GPUs not on the PCI list (virtual GPUs) come last
        return gpus + [(vendor_id, model, device_type == 2) for vendor_id, model, device_type in unmatched]

    def gpu_candidates(self, gpu_results:dict)->list:
        # each way e2a can run a GPU here, as (name, tag, msg, models): a vendor runtime detect_device() found (cuda,
        # rocm, xpu) and one +vulkan torch for the GPUs whose vendor runtime is missing, when Vulkan sees them and the
        # +vulkan torch applies. Add-in cards first, then the OS's GPU order: entry 0, the default, is the card in a slot
        vk_devices = self.vulkan_devices()
        gpus = self.system_gpus(vk_devices)
        vk_vendors = {vendor_id for vendor_id, _, _ in vk_devices}
        ranked = {}
        for index, (vendor_id, model, card) in enumerate(gpus):
            result = gpu_results.get(self.gpu_pci_vendors.get(vendor_id))
            if result and result[1]:
                key, msg = (result[0], result[1]), result[2]
            elif vendor_id in vk_vendors and self.vulkan_torch_ok:
                key, msg = (devices['VULKAN']['proc'], devices['VULKAN']['proc']), None
            else:
                continue
            entry = ranked.setdefault(key, {'rank': (0 if card else 1, index), 'msg': msg, 'models': [], 'notes': []})
            entry['rank'] = min(entry['rank'], (0 if card else 1, index))
            if model and model not in entry['models']:
                entry['models'].append(model)
            # Vulkan for a GPU whose vendor runtime answered without a torch tag: its note says why (an NVIDIA GPU on the
            # +vulkan torch read only 'Vulkan Torch selected' in device_info, nothing told a missing runtime from a misread)
            if msg is None and result and result[2] and result[2] not in entry['notes']:
                entry['notes'].append(result[2])
        # a runtime that answered for a GPU missing from the listing (WSL2's CUDA: no PCI device) still counts, as a card
        for name, tag, msg in gpu_results.values():
            if tag and (name, tag) not in ranked:
                ranked[(name, tag)] = {'rank': (0, len(gpus)), 'msg': msg, 'models': [], 'notes': []}
        candidates = []
        for (name, tag), entry in sorted(ranked.items(), key=lambda item: item[1]['rank']):
            models = ', '.join(entry['models'])
            msg = entry['msg'] if entry['msg'] is not None else ' '.join(entry['notes'] + [legends['msg_vulkan_selected'].format(gpu=models or devices['VULKAN']['proc'])])
            candidates.append((name, tag, msg, models))
        return candidates

    def choose_gpu(self, candidates:list)->tuple:
        # several ways to run a GPU here and one torch serves one of them. The user's pick saved in gpu_choice_file wins
        # while it stays possible; else asked on the terminal, the answer or no answer (entry 0) being saved; else, no
        # terminal, entry 0 unsaved. Returns (name, tag, msg)
        names = [candidate[0] for candidate in candidates]
        try:
            with open(gpu_choice_file, 'r', encoding='utf-8') as f:
                saved = f.read().strip()
        except OSError:
            saved = ''
        if saved in names:
            return candidates[names.index(saved)][:3]
        options = [f'  {index}) {models} - {name} ({tag})' if models else f'  {index}) {name} ({tag})' for index, (name, tag, _, models) in enumerate(candidates)]
        prompt = '\n'.join([legends['msg_gpu_choice_header'], *options, legends['msg_gpu_choice_prompt'].format(last=len(candidates) - 1, seconds=self.gpu_choice_timeout)])
        choice = None
        while choice is None:
            answer = self.ask_tty(prompt, self.gpu_choice_timeout)
            if answer is None or answer is False or answer == '':
                choice = 0
            elif answer.isdigit() and int(answer) < len(candidates):
                choice = int(answer)
            else:
                prompt = legends['msg_gpu_choice_invalid'].format(last=len(candidates) - 1)
        name, tag = candidates[choice][:2]
        if answer is not None:
            try:
                with open(gpu_choice_file, 'w', encoding='utf-8') as f:
                    f.write(name)
            except OSError as e:
                error = legends['msg_device_info_write_failed'].format(e=e)
                print(error, file=sys.stderr)
        # stderr: the launchers read the device info from stdout
        if isinstance(answer, str):
            msg = legends['msg_gpu_choice_done'].format(device=name, tag=tag, file=gpu_choice_file)
        else:
            msg = legends['msg_gpu_choice_default'].format(devices=', '.join(names), device=name, tag=tag, file=gpu_choice_file)
        print(msg, file=sys.stderr)
        return candidates[choice][:3]

    def detect_platform_tag(self)->str:
        if self.system == systems['WINDOWS']:
            return 'win'
        if self.system == systems['MACOS']:
            return 'macosx_11_0'
        if self.system == systems['LINUX']:
            return 'manylinux_2_28'
        return 'unknown'

    def detect_arch_tag(self)->str:
        m = platform.machine().upper()
        return archs.get(m, 'unknown')

    def _cuda_row_versions(self, tag:str)->Union[tuple, None]:
        # (torch, torchaudio) versions the cuXYZ matrix row installs, None when the row is unknown
        entry = torch_matrix.get(tag)
        if not entry:
            return None
        return (entry['last'], self.torchaudio_version(entry['last']))

    def detect_device(self, mode:str=NATIVE)->tuple:
        def has_cmd(cmd:str)->bool:
            return shutil.which(cmd) is not None

        def try_cmd(cmd:str)->str:
            try:
                out = subprocess.check_output(
                    cmd,
                    shell = True,
                    stderr = subprocess.DEVNULL
                )
                # not strict UTF-8: Windows tools write the ANSI code page (GBK on a Chinese Windows), and nvidia-smi's
                # table lists the processes using the GPU. One non-ASCII name raised UnicodeDecodeError, the whole output
                # came back empty and step 4 lost the driver's CUDA version: the NVIDIA GPU fell to the +vulkan torch
                return out.decode(errors='replace').lower()
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

        cuda_arch = {}
        def cuda_min_compute_cap()->Union[tuple, None]:
            # the lowest compute capability of the NVIDIA GPUs, from nvidia-smi (no torch), read once
            if 'cap' not in cuda_arch:
                caps = []
                if has_cmd('nvidia-smi'):
                    for line in try_cmd('nvidia-smi --query-gpu=compute_cap --format=csv,noheader').splitlines():
                        m = re.match(r'\s*(\d+)\.(\d+)', line)
                        if m:
                            caps.append((int(m.group(1)), int(m.group(2))))
                cuda_arch['cap'] = min(caps) if caps else None
            return cuda_arch['cap']

        def cuda_tag(version_str:str)->str:
            # the torch_matrix CUDA row for this CUDA version: the newest one at or below it among the rows built for the
            # target OS and arch (a Docker image is Linux whatever the host), e.g. 13.1 -> cu130, 12.8 on Windows ->
            # win-cu128, 12.8 on Linux -> cu128. '' when no row fits
            target = systems['LINUX'] if mode == BUILD_DOCKER else self.system
            machine = self.detect_arch_tag()
            if target == systems['LINUX'] and machine == archs['AMD64']:
                machine = archs['X86_64']
            current = _normalize_version(version_str)[:2]
            # torch's cu128 and later builds carry no kernels below Turing (compute capability 7.5: Maxwell, Pascal,
            # Volta), "no kernel image is available" at the first op: those GPUs keep the cu126 row, whatever the driver
            cap = cuda_min_compute_cap()
            if cap is not None and cap < (7, 5):
                current = min(current, (12, 6))
            rows = []
            for key, entry in torch_matrix.items():
                m = re.fullmatch(r'(?:win-)?cu(\d+)(\d)', key)
                if m and target in entry['os'] and machine in entry['arch'] and (int(m.group(1)), int(m.group(2))) <= current:
                    rows.append(((int(m.group(1)), int(m.group(2))), key))
            return max(rows)[1] if rows else ''

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
                msg = legends['msg_jetpack_unknown']
                return ('unknown', msg)
            # L4T major -> JetPack major: R35 = 5, R36 = 6, R38+ = 7 (tags jetson5 / jetson6 / jetson7)
            l4t_major = int(m1.group(1))
            if l4t_major < 35:
                msg = legends['msg_jetpack_old'].format(version=l4t_major)
                return ('unsupported', msg)
            if l4t_major == 35:
                return ('5', msg)
            if l4t_major == 36:
                return ('6', msg)
            return ('7', msg)

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
                if not glob('/dev/dri/renderD*'):
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

        def vulkan_ok()->str:
            # the Vulkan GPU name when the +vulkan torch applies here (vulkan_torch_ok), else ''. macOS: every Mac on 11+
            # has a Metal GPU, the wheel brings MoltenVK. Elsewhere the first real Vulkan GPU
            if self.system == systems['MACOS']:
                return 'Metal (MoltenVK)' if self.vulkan_torch_ok else ''
            gpus = self.vulkan_gpus()
            return gpus[0] if gpus and self.vulkan_torch_ok else ''

        def _normalize_version(v:str)->tuple:
            '''Parse version string into (major, minor, patch). Patch defaults to 0.'''
            m = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', v or '')
            if not m:
                return ()
            major = int(m.group(1))
            minor = int(m.group(2))
            patch = int(m.group(3)) if m.group(3) else 0
            return (major, minor, patch)

        name = None
        tag = None
        msg = ''
        arch = platform.machine().lower()
        forced_tag = os.environ.get('DEVICE_TAG')
        if forced_tag:
            tag_letters = re.match(r'[a-zA-Z]+', forced_tag)
            if tag_letters:
                tag_letters = tag_letters.group(0).lower()
                name = devices['CUDA']['proc'] if tag_letters == 'cu' else devices['ROCM']['proc'] if tag_letters == devices['ROCM']['proc'] else devices['JETSON']['proc'] if tag_letters == devices['JETSON']['proc'] else devices['XPU']['proc'] if tag_letters == devices['XPU']['proc'] else devices['MPS']['proc'] if tag_letters == devices['MPS']['proc'] else devices['VULKAN']['proc'] if tag_letters == devices['VULKAN']['proc'] else devices['CPU']['proc']
                devices[name.upper()]['found'] = True
                tag = forced_tag
                if forced_tag in ['cu128', 'cu129', 'rocm7.2.1'] and self.system == systems['WINDOWS']:
                    tag = f'win-{forced_tag}'
                msg = legends['msg_hardware_forced'].format(tag=tag)
            else:
                msg = legends['msg_device_tag_invalid']
        else:
            tegra = arch in (archs['AARCH64'],archs['ARM64']) and (os.path.exists('/etc/nv_tegra_release') or 'tegra' in try_cmd('cat /proc/device-tree/compatible'))
            # vendor -> (name, tag, msg) of each GPU vendor below: they all answer, a machine can have several (GPU CHOICE)
            gpu_results = {}
            # ============================================================
            # JETSON
            # ============================================================
            if tegra:
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
                            msg = legends['msg_jetson_incompatible']
                if devices['JETSON']['found']:
                    os.environ['CUDA_MODULE_LOADING'] = 'LAZY'
                    os.environ['TORCH_CUDA_ENABLE_CUDA_GRAPH'] = '0'
                    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128,garbage_collection_threshold:0.6,expandable_segments:False'
            # ============================================================
            # ROCm
            # ============================================================
            if not tegra and has_rocm() and has_amd_gpu_pci():
                name, tag, msg = None, None, ''
                # HSA_OVERRIDE_GFX_VERSION is read once, when this process first initializes the HSA runtime:
                # the ctypes hipGetDeviceCount() below does it, and torch later reuses that loaded libhsa-runtime64.so.1,
                # so the override must be in os.environ before it. detect_gpu.py inherits it and reports it back unchanged.
                if os.name == 'posix' and not os.environ.get('HSA_OVERRIDE_GFX_VERSION'):
                    sys_path = list(sys.path)
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location('detect_gpu', detect_gpu_script)
                        detect_gpu = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(detect_gpu)
                        detect_gpu.handle_rocm_override()
                    except Exception:
                        pass  # never block device detection
                    finally:
                        sys.path[:] = sys_path  # handle_rocm_override() puts components/ first on sys.path
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
                                msg = legends['msg_hip_no_devices'].format(version=ver_disp)
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
                # 3) ROCm install dir fallback
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
                        msg = legends['msg_rocm_windows_upgrade'].format(version=version_str, max=max_ver)
                    elif cmp == -1:
                        msg = legends['msg_rocm_too_old'].format(version=version_str, min=min_ver)
                    elif cmp is None:
                        msg = legends['msg_rocm_unparseable']
                    else:
                        devices['ROCM']['found'] = True
                        name = devices['ROCM']['proc']
                        compat_versions = []
                        for t, entry in torch_matrix.items():
                            if self.system not in entry['os'] or not t.startswith('rocm'):
                                continue
                            ver_str = t[len('win-rocm'):] if t.startswith('win-rocm') else t[len('rocm'):]
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
                                    tag = f'win-rocm{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'win-rocm{matched[0]}.{matched[1]}'
                                else:
                                    tag = f'rocm{matched[0]}.{matched[1]}.{matched[2]}' if matched[2] else f'rocm{matched[0]}.{matched[1]}'
                        if cmp == 1:
                            msg = legends['msg_rocm_tested_max'].format(version=version_str, max=max_ver, tag=tag) if tag else legends['msg_rocm_torch_not_ready'].format(version=version_str)
                        elif not tag:
                            msg = legends['msg_rocm_no_torch_build'].format(version=version_str)
                else:
                    msg = legends['msg_rocm_runtime_missing']
                gpu_results[devices['ROCM']['proc']] = (name, tag, msg)
            # ============================================================
            # CUDA
            # ============================================================
            if not tegra and has_cuda() and (has_nvidia_gpu_pci() or is_wsl2()):
                name, tag, msg = None, None, ''
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
                                    msg = legends['msg_cuda_no_devices'].format(version=f'{major}.{minor}')
                            else:
                                v = v_int.value
                                major = v // 1000
                                minor = (v % 1000) // 10
                                msg = legends['msg_cuda_count_failed'].format(version=f'{major}.{minor}')
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
                # but torch build tag clamps at cuda_version_range['max'] so we install a real wheel.
                if version:
                    cmp, current, min_tuple, max_tuple = version_classify(version, cuda_version_range)
                    min_ver = f'{min_tuple[0]}.{min_tuple[1]}'
                    max_ver = f'{max_tuple[0]}.{max_tuple[1]}'
                    if cmp == -1:
                        msg = legends['msg_cuda_too_old'].format(version=version, min=min_ver)
                    elif cmp is None:
                        msg = legends['msg_cuda_unparseable'].format(version=version)
                    else:
                        tag = cuda_tag(max_ver if cmp == 1 else version)
                        if tag:
                            devices['CUDA']['found'] = True
                            name = devices['CUDA']['proc']
                            if cmp == 1:
                                msg = legends['msg_cuda_tested_max'].format(version=version, max=max_ver, tag=tag)
                        else:
                            msg = legends['msg_cuda_no_torch_build'].format(version=version)
                else:
                    msg = legends['msg_cuda_missing']
                # 4) nvidia-smi header parsing: the driver alone is enough. The cu torch wheels bring their own CUDA
                # runtime, natively as in a Docker image (Linux: the nvidia-* packages, Windows: cudart/cublas/cudnn in
                # torch/lib), so most NVIDIA users have no toolkit for steps 1-2 to find. It reads the driver, not the
                # torch installed by an earlier run. Without it an NVIDIA GPU fell to the +vulkan torch below
                if not devices['CUDA']['found'] and has_cmd('nvidia-smi'):
                    out = try_cmd('nvidia-smi')
                    # Header line: '| NVIDIA-SMI ...  Driver Version: ...  CUDA Version: 12.4 |', and from driver 620
                    # '| NVIDIA-SMI ...  KMD Version: ...  CUDA UMD Version: 13.5 |': 'cuda version' alone missed it, the
                    # NVIDIA GPU fell to the +vulkan torch. One word between 'cuda' and 'version' is accepted for that
                    m = re.search(r'cuda(?:\s+[a-z]+)?\s*version\s*:?\s*([0-9]+(?:\.[0-9]+)?)', out, re.IGNORECASE)
                    if m:
                        smi_version = m.group(1)
                        cmp, current, min_tuple, max_tuple = version_classify(smi_version, cuda_version_range)
                        max_ver = '.'.join(str(p) for p in max_tuple)
                        if cmp == -1:
                            msg = legends['msg_cuda_smi_too_old'].format(version=smi_version)
                        elif cmp is not None:
                            tag = cuda_tag(max_ver if cmp == 1 else smi_version)
                            if tag:
                                devices['CUDA']['found'] = True
                                name = devices['CUDA']['proc']
                                if cmp == 1:
                                    msg = legends['msg_cuda_tested_max'].format(version=smi_version, max=max_ver, tag=tag)
                                else:
                                    msg = legends['msg_cuda_smi_driver_only'].format(version=smi_version)
                            else:
                                msg = legends['msg_cuda_no_torch_build'].format(version=smi_version)
                gpu_results[devices['CUDA']['proc']] = (name, tag, msg)
            # ============================================================
            # INTEL XPU
            # ============================================================
            # gated on the PCI scan ALONE. has_xpu() needs sycl-ls or clinfo on PATH,
            # which are oneAPI *toolkit* binaries — torch xpu wheels ship their own
            # SYCL runtime and need none of it, so gating on them dropped real XPU
            # hosts to cpu with an empty note. The decision now happens inside the
            # branch, where a missing user-mode driver produces a message that says so.
            if not tegra and has_intel_gpu_pci():
                name, tag, msg = None, None, ''
                version = ''
                msg = ''
                xpu_device_count = 0
                ze_status = 'no-loader'
                # 1) Level Zero / SYCL runtime detection via ctypes (primary)
                try:
                    import ctypes
                    lib_ze = None
                    if os.name == 'nt':
                        candidates = ['ze_loader.dll']
                        oneapi_root = os.environ.get('ONEAPI_ROOT', '')
                        if oneapi_root:
                            candidates.insert(0, os.path.join(oneapi_root, 'bin', 'ze_loader.dll'))
                    else:
                        # versioned runtime soname FIRST. 'libze_loader.so' without the
                        # version is the devel symlink; on a rolling distro it can point
                        # at a different build than the runtime object, and loading that
                        # one makes zeInit fail version negotiation (0x78000002
                        # ZE_RESULT_ERROR_UNSUPPORTED_VERSION) on a machine whose GPU
                        # stack is otherwise fine.
                        candidates = ['libze_loader.so.1', 'libze_loader.so']
                        ze_lib_dirs = [
                            '/usr/lib/x86_64-linux-gnu',
                            '/usr/lib64',
                            '/usr/lib',
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
                    # a loader that dlopens is not a loader that works. Only zeInit
                    # returning success ends the search — otherwise fall through to the
                    # next candidate and keep the last failure for the note.
                    for lib_name in candidates:
                        try:
                            lib_ze = ctypes.CDLL(lib_name)
                        except OSError:
                            continue
                        try:
                            # argtypes are mandatory here: without them ctypes marshals a
                            # handle taken out of the array as a C int and truncates the
                            # top 32 bits of the pointer.
                            lib_ze.zeDriverGet.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_void_p)]
                            lib_ze.zeDeviceGet.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_void_p)]
                            lib_ze.zeDeviceGetProperties.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
                            rc = lib_ze.zeInit(ctypes.c_uint(0))
                        except (AttributeError, ValueError):
                            ze_status = 'not-a-loader'
                            continue
                        if rc != 0:
                            ze_status = f'init-failed 0x{rc & 0xffffffff:x}'
                            continue
                        ze_status = 'no-driver'
                        driver_count = ctypes.c_uint(0)
                        if lib_ze.zeDriverGet(ctypes.byref(driver_count), None) == 0 and driver_count.value > 0:
                            drivers = (ctypes.c_void_p * driver_count.value)()
                            if lib_ze.zeDriverGet(ctypes.byref(driver_count), drivers) == 0:
                                ze_status = 'no-device'
                                # ze_device_properties_t starts with {stype, pNext, type}.
                                # stype is 4 bytes padded up to pointer alignment, so
                                # 'type' sits two pointer widths in on any ABI we ship on.
                                ptr_size = ctypes.sizeof(ctypes.c_void_p)
                                for drv in drivers:
                                    if not drv:
                                        continue
                                    device_count = ctypes.c_uint(0)
                                    if lib_ze.zeDeviceGet(ctypes.c_void_p(drv), ctypes.byref(device_count), None) != 0:
                                        continue
                                    if device_count.value == 0:
                                        continue
                                    ze_devices = (ctypes.c_void_p * device_count.value)()
                                    if lib_ze.zeDeviceGet(ctypes.c_void_p(drv), ctypes.byref(device_count), ze_devices) != 0:
                                        continue
                                    for dev in ze_devices:
                                        if not dev:
                                            continue
                                        # the device type filter is a REFINEMENT, not a gate:
                                        # a device the loader enumerated is a device. If the
                                        # properties query fails for any reason the device is
                                        # still counted — worst case an NPU inflates the count
                                        # on a box that already passed the Intel GPU PCI scan.
                                        # Skipping on failure turned every properties error
                                        # into a phantom 'no driver installed'.
                                        props = (ctypes.c_ubyte * 1024)()
                                        # ZE_STRUCTURE_TYPE_DEVICE_PROPERTIES == 0x3.
                                        # 0x1 is ZE_STRUCTURE_TYPE_DRIVER_PROPERTIES and the
                                        # Intel driver rejects the call outright when it is
                                        # passed here.
                                        ctypes.c_uint.from_buffer(props, 0).value = 0x3
                                        if lib_ze.zeDeviceGetProperties(ctypes.c_void_p(dev), ctypes.byref(props)) != 0:
                                            xpu_device_count += 1
                                            ze_status = 'ok-unverified'
                                            continue
                                        # ZE_DEVICE_TYPE_GPU == 1, ZE_DEVICE_TYPE_VPU == 5.
                                        if ctypes.c_uint.from_buffer(props, ptr_size * 2).value == 1:
                                            xpu_device_count += 1
                                            ze_status = 'ok'
                        break
                except (OSError, AttributeError, ValueError):
                    pass
                # 2) sycl-ls detection — only reached when the loader itself could not be
                # dlopen'd. torch xpu runs on Level Zero, so an OpenCL-only line is not a
                # usable device: both the underscore ('level_zero:gpu', 2024+) and the
                # hyphen ('Intel(R) Level-Zero', older) spellings count, nothing else does.
                if xpu_device_count == 0:
                    sycl_out = ''
                    if os.name == 'posix' and has_cmd('sycl-ls'):
                        sycl_out = try_cmd('sycl-ls')
                    elif os.name == 'nt':
                        oneapi_root = os.environ.get('ONEAPI_ROOT', '')
                        sycl_ls = os.path.join(oneapi_root, 'bin', 'sycl-ls') if oneapi_root else ''
                        if sycl_ls and os.path.isfile(sycl_ls):
                            sycl_out = try_cmd(f'"{sycl_ls}"')
                        if not sycl_out and has_cmd('sycl-ls'):
                            sycl_out = try_cmd('sycl-ls')
                    if sycl_out:
                        gpu_lines = [l for l in sycl_out.splitlines() if 'gpu' in l.lower() and ('level_zero' in l.lower() or 'level-zero' in l.lower())]
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
                # Tag assignment. The device count decides — it is the same condition
                # torch.xpu.is_available() answers at runtime. The oneAPI version file
                # only annotates the note: a stale or absent toolkit must never veto a
                # working GPU, which is what the old version-first ordering did.
                if xpu_device_count > 0:
                    devices['XPU']['found'] = True
                    name = devices['XPU']['proc']
                    tag = devices['XPU']['proc']
                    plural = 's' if xpu_device_count > 1 else ''
                    if version:
                        cmp, current, min_tuple, max_tuple = version_classify(version, xpu_version_range)
                        min_ver = '.'.join(str(p) for p in min_tuple)
                        max_ver = '.'.join(str(p) for p in max_tuple)
                        if cmp == -1:
                            msg = legends['msg_xpu_oneapi_too_old'].format(count=xpu_device_count, version=version, min=min_ver)
                        elif cmp == 1:
                            msg = legends['msg_xpu_oneapi_tested_max'].format(count=xpu_device_count, version=version, max=max_ver)
                        elif cmp is None:
                            msg = legends['msg_xpu_oneapi_unparseable'].format(count=xpu_device_count)
                        else:
                            msg = legends['msg_xpu_oneapi_ok'].format(count=xpu_device_count, version=version)
                    else:
                        msg = legends['msg_xpu_oneapi_missing'].format(count=xpu_device_count)
                else:
                    # Hardware is on the bus but nothing usable answered. Name the missing
                    # layer instead of tagging xpu: wheels would install and then die in
                    # engine.to(device) with 'No XPU devices are available'.
                    kmd = ''
                    for node in glob('/dev/dri/renderD*'):
                        sysfs = os.path.join('/sys/class/drm', os.path.basename(node), 'device')
                        try:
                            with open(os.path.join(sysfs, 'vendor')) as f:
                                if f.read().strip() != '0x8086':
                                    continue
                        except OSError:
                            continue
                        kmd = os.path.basename(os.path.realpath(os.path.join(sysfs, 'driver')))
                        break
                    if os.name == 'nt':
                        msg = legends['msg_intel_no_l0_device'].format(status=ze_status)
                    elif not glob('/dev/dri/renderD*'):
                        msg = legends['msg_intel_no_render_node']
                    elif not kmd:
                        msg = legends['msg_intel_render_unbound']
                    elif ze_status == 'no-loader':
                        msg = legends['msg_intel_no_l0_loader'].format(kmd=kmd)
                    elif ze_status.startswith('init-failed'):
                        msg = legends['msg_intel_zeinit_failed'].format(kmd=kmd, status=ze_status[len('init-failed '):])
                    elif ze_status == 'no-driver':
                        msg = legends['msg_intel_l0_no_driver'].format(kmd=kmd)
                    elif has_xpu():
                        msg = legends['msg_intel_sycl_no_l0'].format(kmd=kmd)
                    else:
                        msg = legends['msg_intel_l0_no_device'].format(kmd=kmd, status=ze_status)
                gpu_results[devices['XPU']['proc']] = (name, tag, msg)
            # ============================================================
            # GPU CHOICE
            # ============================================================
            # one torch serves one way of running a GPU: its vendor runtime found above, or the +vulkan torch for a GPU
            # without one (gpu_candidates). Several go to choose_gpu(). None: the vendors' notes stay for the CPU fallback
            if not tegra and self.system != systems['MACOS']:
                candidates = self.gpu_candidates(gpu_results)
                if len(candidates) > 1:
                    name, tag, msg = self.choose_gpu(candidates)
                elif candidates:
                    name, tag, msg = candidates[0][:3]
                else:
                    name, tag = None, None
                    msg = ' '.join(result[2] for result in gpu_results.values() if result[2])
                for key in ('ROCM', 'CUDA', 'XPU', 'VULKAN'):
                    devices[key]['found'] = bool(tag) and name == devices[key]['proc']
                if devices['ROCM']['found']:
                    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:False'
                    os.environ['PYTORCH_HIP_ALLOC_CONF'] = 'expandable_segments:False'
            # ============================================================
            # APPLE MPS
            # ============================================================
            if tag is None and self.system == systems['MACOS'] and arch in (archs['ARM64'], archs['AARCH64']):
                devices['MPS']['found'] = True
                name = devices['MPS']['proc']
                tag = devices['MPS']['proc']
            # ============================================================
            # VULKAN
            # ============================================================
            # Linux / Windows decided Vulkan in GPU CHOICE above. macOS (MPS or nothing found) and a Jetson whose JetPack
            # has no torch build take the +vulkan torch when vulkan_ok(), ahead of MPS: the +vulkan wheels keep MPS on
            # Apple Silicon, so MPS stays found and selectable. Intel macOS always takes it
            if tag in (None, devices['MPS']['proc']) and (tegra or self.system == systems['MACOS']):
                vulkan_gpu = vulkan_ok()
                if not vulkan_gpu and self.system == systems['MACOS'] and self.detect_arch_tag() == archs['X86_64']:
                    # PyTorch has no Intel macOS wheel after 2.2.2: the +vulkan build is the only current torch there
                    vulkan_gpu = 'Metal (MoltenVK)'
                if vulkan_gpu:
                    devices['VULKAN']['found'] = True
                    name = devices['VULKAN']['proc']
                    tag = devices['VULKAN']['proc']
                    msg = legends['msg_vulkan_selected'].format(gpu=vulkan_gpu)
            # ============================================================
            # CPU
            # ============================================================
            if tag is None:
                name = devices['CPU']['proc']
                tag = devices['CPU']['proc']
                # an empty note here is a silent fallback and unreadable in a log: it
                # cannot be told apart from a deliberate cpu box. Record what was seen
                # on the bus so the next log line says which gate was missed.
                if not msg:
                    seen = []
                    if has_nvidia_gpu_pci():
                        seen.append('NVIDIA')
                    if has_amd_gpu_pci():
                        seen.append('AMD')
                    if has_intel_gpu_pci():
                        seen.append('Intel')
                    if seen:
                        msg = legends['msg_gpu_runtime_silent'].format(gpus=' + '.join(seen))
                    else:
                        msg = legends['msg_no_gpu_pci']
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

    def torchaudio_version(self, torch_version:str)->str:
        # Single source of truth for "which torchaudio goes with this torch".
        # Below the ceiling torchaudio tracks torch exactly; above it, torchaudio
        # simply stopped existing, so clamp rather than request a phantom version.
        # See the torchaudio_max comment on the class for why clamping is safe.
        if self.version_tuple(torch_version, 3) > self.version_tuple(self.torchaudio_max, 3):
            return self.torchaudio_max
        return torch_version

    def torchaudio_spec(self, torch_version:str)->str:
        # requirement for the PyTorch index path (CUDA, CPU, XPU, ROCm linux). from the
        # ceiling on, any 2.11.x patch is valid and uv takes the highest one the stable or
        # nightly index carries for this tag. explicit wheel URLs (jetson, vulkan, windows
        # rocm) keep torchaudio_version(): their filenames are exact.
        if self.version_tuple(torch_version, 3) >= self.version_tuple(self.torchaudio_max, 3):
            return f'torchaudio~={self.torchaudio_max}'
        return f'torchaudio=={torch_version}'

    def torchaudio_ok(self, installed_version:str, torch_version:str)->bool:
        # does the installed torchaudio base version satisfy torchaudio_spec(torch_version)
        if self.version_tuple(torch_version, 3) >= self.version_tuple(self.torchaudio_max, 3):
            installed = self.version_tuple(installed_version, 3)
            ceiling = self.version_tuple(self.torchaudio_max, 3)
            return installed[:2] == ceiling[:2] and installed >= ceiling
        return installed_version == torch_version

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

    def pkg_head(self, requirement:str)->str:
        return re.sub(r'[-_.]+', '-', re.split(r'[<>=!\[;]', requirement, 1)[0].strip().lower())

    def apply_pins(self, requirements:list, pins:list)->list:
        if not pins:
            return list(requirements)
        heads = {self.pkg_head(spec) for spec in pins}
        kept = [pkg for pkg in requirements if self.pkg_head(pkg) not in heads]
        return kept + pins

    @install_locked
    def install_python_packages(self)->int:
        if not os.path.exists(requirements_file):
            error = legends['error_requirements_missing'].format(file=requirements_file)
            print(error)
            return 1
        self.remove_obsolete_packages()
        overrides = {}
        packages = []
        onnx_pkg = 'onnxruntime'
        if self.system != systems['MACOS']:
            onnx_pkg = self.select_pkg('onnxruntime')
        packages.append(onnx_pkg)
        if onnx_pkg == 'onnxruntime-directml':
            packages.append('protobuf<7')
        packages.append(self.select_pkg('transformers'))
        if self.system == systems['MACOS'] and platform.machine().lower() in ('x86_64', 'amd64'):
            overrides['llvmlite'] = 'llvmlite==0.44.0'
            #overrides['numba'] = 'numba==0.61.0'
            #overrides['pymupdf'] = 'pymupdf<2.0'
            packages.append(overrides['llvmlite'])
            #packages.append(overrides['numba'])
            #packages.append(overrides['pymupdf'])
        try:
            with open(requirements_file, 'r') as f:
                contents = f.read().replace('\r', '\n')
                for line in contents.splitlines():
                    pkg = line.strip()
                    if not pkg or not re.search(r'[a-zA-Z0-9]', pkg):
                        continue
                    if '#' in pkg:
                        pkg = pkg.split('#', 1)[0].strip()
                        if not pkg:
                            continue
                    head = re.sub(r'[-_.]+', '-', re.split(r'[<>=!\[;]', pkg, 1)[0].strip().lower())
                    if head in {'torch', 'torchaudio'} or head in self.device_pkgs:
                        continue
                    if head in overrides:
                        if overrides[head] is None:
                            continue
                        pkg = overrides[head]
                    if pkg in packages:
                        continue
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
                        error = legends['error_marker_eval'].format(marker=marker_part, pkg=pkg_part, e=e)
                        print(error)
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
                        msg = legends['msg_git_pkg_missing'].format(pkg=pkg_name)
                        print(msg)
                        missing_packages.append(raw_pkg)
                    continue
                if local_path:
                    pkg_name = os.path.basename(local_path)
                    vendor_version = self.version_pkg(None, local_path)
                    if vendor_version is None:
                        msg = legends['msg_no_version'].format(path=local_path)
                        print(msg)
                        missing_packages.append(raw_pkg)
                        continue
                    try:
                        installed_version = version(pkg_name)
                    except PackageNotFoundError:
                        error = legends['msg_pkg_not_installed'].format(pkg=pkg_name)
                        print(error)
                        missing_packages.append(raw_pkg)
                        continue
                    if installed_version != vendor_version:
                        msg = legends['msg_pkg_version_mismatch'].format(pkg=pkg_name, installed=installed_version, vendor=vendor_version)
                        print(msg)
                        missing_packages.append(raw_pkg)
                    continue
                installed_version = self.version_pkg(pkg_name, None)
                if installed_version is None:
                    msg = legends['msg_pkg_not_installed'].format(pkg=pkg_name)
                    print(msg)
                    if pkg_name == 'demucs-simple':
                        subprocess.run(
                            self._uv_pip('uninstall', 'demucs'),
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    missing_packages.append(raw_pkg)
                    continue
                if '+' in installed_version:
                    installed_version = installed_version.split('+', 1)[0]
                pkg_spec_part = re.split(r'[<>=!]', clean_pkg, maxsplit=1)
                spec_str = clean_pkg[len(pkg_spec_part[0]):].strip()
                if spec_str:
                    norm_match = re.match(r'^(\d+\.\d+(?:\.\d+)?)', installed_version)
                    short_version = norm_match.group(1) if norm_match else installed_version
                    installed_v = self.version_tuple(short_version, 3)
                    # FIX: Evaluate ALL specifiers (e.g. both >=0.36.2 and <1.0)
                    violated = False
                    for op, req_ver in re.findall(r'(==|!=|>=|<=|>|<)\s*(\d+\.\d+(?:\.\d+)?)', spec_str):
                        req_v = self.version_tuple(req_ver, 3)
                        if op == '==' and installed_v != req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                        elif op == '>=' and installed_v < req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                        elif op == '<=' and installed_v > req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                        elif op == '>' and installed_v <= req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                        elif op == '<' and installed_v >= req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                        elif op == '!=' and installed_v == req_v:
                            msg = legends['msg_pkg_violates'].format(pkg=pkg_name, installed=installed_version, req=f'{op}{req_ver}', spec=clean_pkg)
                            print(msg)
                            violated = True
                            break
                    if violated and raw_pkg not in missing_packages:
                        missing_packages.append(raw_pkg)
            if missing_packages:
                msg = legends['msg_installing_missing']
                print(msg)
                base_cmd = self._uv_pip('install', '--cache-dir', self.pip_cache_dir)
                base_cmd = self._uv_pip('install', '--cache-dir', self.pip_cache_dir)
                if self.system == systems['MACOS'] and platform.machine().lower() in ('x86_64', 'amd64'):
                    base_cmd += ['--only-binary', 'llvmlite,numba,pymupdf']
                pins = [spec for spec in overrides.values() if spec]
                for dpkg in self.device_pkgs:
                    try:
                        pin = self.select_pkg(dpkg)
                        if pin not in pins:
                            pins.append(pin)
                    except Exception:
                        pass
                try:
                    subprocess.check_call(base_cmd + self.apply_pins(missing_packages, pins))
                except subprocess.CalledProcessError:
                    for raw_pkg in missing_packages:
                        try:
                            subprocess.check_call(base_cmd + self.apply_pins([raw_pkg], pins))
                        except subprocess.CalledProcessError:
                            try:
                                subprocess.check_call(base_cmd + ['--reinstall-package', self.pkg_head(raw_pkg.split('@', 1)[0])] + self.apply_pins([raw_pkg], pins))
                            except subprocess.CalledProcessError as e:
                                msg = legends['msg_install_pkg_failed'].format(pkg=raw_pkg, e=e)
                                print(msg)
                                return 1
                importlib.invalidate_caches()
                still_missing = []
                for raw_pkg in missing_packages:
                    pkg_name = re.split(r'[<>=!\[;]', re.sub(r'\[.*?\]', '', raw_pkg.strip()), maxsplit=1)[0].strip()
                    if not pkg_name:
                        continue
                    try:
                        version(pkg_name)
                    except PackageNotFoundError:
                        still_missing.append(raw_pkg)
                if still_missing:
                    msg = legends['msg_force_reinstall'].format(count=len(still_missing))
                    print(msg)
                    try:
                        subprocess.check_call(base_cmd + [arg for pkg in still_missing for arg in ('--reinstall-package', self.pkg_head(pkg.split('@', 1)[0]))] + self.apply_pins(still_missing, pins))
                    except subprocess.CalledProcessError:
                        for raw_pkg in still_missing:
                            try:
                                subprocess.check_call(base_cmd + ['--reinstall-package', self.pkg_head(raw_pkg.split('@', 1)[0])] + self.apply_pins([raw_pkg], pins))
                            except subprocess.CalledProcessError as e:
                                msg = legends['msg_reinstall_pkg_failed'].format(pkg=raw_pkg, e=e)
                                print(msg)
                                return 1
                    importlib.invalidate_caches()
                    for raw_pkg in still_missing:
                        pkg_name = re.split(r'[<>=!\[;]', re.sub(r'\[.*?\]', '', raw_pkg.strip()), maxsplit=1)[0].strip()
                        if not pkg_name: continue
                        try:
                            version(pkg_name)
                        except PackageNotFoundError:
                            msg = legends['msg_pkg_still_missing'].format(pkg=pkg_name)
                            print(msg)
                            print(f'DEBUG: sys.executable = {sys.executable}')
                            print(f'DEBUG: sys.prefix = {sys.prefix}')
                            return 1
                msg = legends['msg_all_packages_ok']
                print(msg)
            self.remove_unusable_torchcodec()
            if self.install_missing_dependencies() == 1:
                return 1
            if self.repair_incomplete_packages() == 1:
                return 1
            # a requirement depending on the plain build (piper-tts, minisbd -> onnxruntime) installs it next to the
            # device build picked above, and both unpack into site-packages/onnxruntime/: keep onnx_pkg only.
            # last step: install_missing_dependencies() brings the plain build back with the dependency it installs
            # (argostranslate -> minisbd -> onnxruntime), and the two builds mixed in one folder fail at the first
            # import ("cannot import name 'set_default_logger_callback' from 'onnxruntime.capi._pybind_state'").
            # runs on every pass, not only after an install, to also repair envs that already hold both
            self.finalize_exclusive_packages({'onnxruntime': onnx_pkg})
        except Exception as e:
            error = f'install_python_packages() error: {e}'
            print(error)
            self.drop_pip_cache()
            return 1

    def remove_unusable_torchcodec(self)->None:
        # pyannote-audio 4 depends on torchcodec, so on torch < 2.9 (cu118/121/124, rocm <= 6.2.4, jetson5/6: no
        # torchcodec matches them, see has_torchcodec_stack()) PyPI's newest one comes along, built for the newest
        # torch: its library fails to load at every pyannote import (Windows: 0xC0000139 entry point not found).
        # pyannote runs without it (soundfile, background_detector.pyannote_patch()), e2a never imports it, and
        # install_missing_dependencies() skips torchcodec, so it stays out
        try:
            torchcodec_version = self.get_package_version('torchcodec')
            if not torchcodec_version or self.has_torchcodec_stack() or not self.get_package_version('torch'):
                return
            msg = legends['msg_removing_unusable_torchcodec'].format(version=torchcodec_version, torch=self.get_package_version('torch'))
            print(msg)
            subprocess.call(self._uv_pip('uninstall', 'torchcodec'))
        except Exception as e:
            error = f'remove_unusable_torchcodec(): {e}'
            print(error)

    def lacks_record_files(self, dist:Any)->bool:
        # a code file RECORD lists is gone. RECORD itself: Distribution.files leaves out the entries whose file is gone
        # (python >= 3.12)
        code_suffixes = ('.py', '.so', '.pyd', '.dll', '.dylib')
        for row in csv.reader((dist.read_text('RECORD') or '').splitlines()):
            if row and row[0].endswith(code_suffixes) and not os.path.exists(dist.locate_file(row[0])):
                return True
        return False

    def package_incomplete(self, pkg:str)->bool:
        # pkg installed but some of its code files are gone (see repair_incomplete_packages())
        try:
            return self.lacks_record_files(distribution(pkg))
        except PackageNotFoundError:
            return False
        except Exception as e:
            error = f'package_incomplete({pkg}): {e}'
            print(error)
            return False

    def repair_incomplete_packages(self)->int:
        # an install cut short (closed terminal, antivirus, full disk) can leave a package with its metadata but not
        # all its files: the version checks and uv pip check pass and the import fails (gradio without
        # gradio/history.py: "cannot import name 'history' from partially initialized module 'gradio'"). RECORD lists
        # each package's files: the same version is reinstalled when code files are missing. Left out: the device
        # step's packages (dependency_skip_re, install_device_packages() repairs the torch family from its own wheels)
        # and packages installed from a URL or a local path (direct_url.json)
        incomplete = {}
        try:
            for dist in distributions():
                name = self.pkg_head(dist.metadata['Name'] or '')
                if not name or name in incomplete or self.dependency_skip_re.match(name) or dist.read_text('direct_url.json'):
                    continue
                if self.lacks_record_files(dist):
                    incomplete[name] = dist.version
        except Exception as e:
            error = f'repair_incomplete_packages(): {e}'
            print(error)
            return 0
        if not incomplete:
            return 0
        msg = legends['msg_reinstalling_incomplete'].format(pkgs=', '.join(incomplete))
        print(msg)
        # --no-deps: the same version only gets its files back, its dependencies are install_missing_dependencies()'
        # job. Resolving them again puts the plain onnxruntime back next to onnxruntime-gpu (piper-tts -> onnxruntime)
        cmd = self._uv_pip('install', '--cache-dir', self.pip_cache_dir, '--no-deps')
        for name in incomplete:
            cmd += ['--reinstall-package', name]
        try:
            subprocess.check_call(cmd + [f'{name}=={ver}' for name, ver in incomplete.items()])
        except subprocess.CalledProcessError as e:
            msg = legends['msg_install_pkg_failed'].format(pkg=', '.join(incomplete), e=e)
            print(msg)
            return 1
        importlib.invalidate_caches()
        return 0

    def pinned_heads(self)->set:
        # the packages requirements.txt pins or caps (==, <, ~=): their version is e2a's choice, never raised for another
        heads = set()
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    pkg = line.split('#', 1)[0].strip()
                    if pkg and re.search(r'==|<|~=', pkg):
                        heads.add(self.pkg_head(pkg))
        except OSError:
            pass
        return heads

    def install_missing_dependencies(self)->int:
        # requirements.txt only lists the top packages: a dependency of theirs removed afterwards (uninstalled by
        # hand, interrupted install, antivirus) is never put back, and every start then fails at import (gradio
        # without uvicorn). uv pip check lists them. Of the version conflicts only a floor is raised (below), the others
        # are left alone (some are intended, see transformers_caps and sitecustomize.py), and so are the packages the
        # device step installs from its own
        # wheels or swaps (torch family, GPU runtimes, onnxruntime builds: onnxruntime-gpu stands for onnxruntime)
        try:
            result = subprocess.run(self._uv_pip('check'), capture_output=True, text=True, encoding='utf-8', errors='replace')
        except OSError:
            return 0
        output = f'{result.stdout}\n{result.stderr}'
        missing = []
        for req in re.findall(r"requires `([^`]+)`, but it's not installed", output):
            if not self.dependency_skip_re.match(self.pkg_head(req)) and req not in missing:
                missing.append(req)
        # a dependency below a floor another package declares (anyio 4.16 needs typing_extensions>=4.16, an older one
        # installed since fails at import): raised when only a floor is asked for and e2a neither pins it
        # (requirements.txt), installs it per device (device_pkgs) nor leaves it to the device step. Upper bounds stay
        outdated = []
        pinned = self.pinned_heads()
        for req, installed in re.findall(r"requires `([^`]+)`, but `([^`]+)` is installed", output):
            # without its environment marker (" ; python_full_version < '3.15'"): uv only reports the ones that apply
            spec = req.split(';', 1)[0].strip()
            head = self.pkg_head(spec)
            ops = set(re.findall(r'===|==|!=|~=|>=|<=|>|<', spec))
            if ops and ops <= {'>=', '>'} and head not in pinned and head not in self.device_pkgs and not self.dependency_skip_re.match(head) and spec not in outdated:
                outdated.append(spec)
        if not missing and not outdated:
            return 0
        if missing:
            msg = legends['msg_installing_missing_deps'].format(pkgs=', '.join(missing))
            print(msg)
        if outdated:
            msg = legends['msg_upgrading_outdated_deps'].format(pkgs=', '.join(outdated))
            print(msg)
        missing = missing + outdated
        # a missing device package (transformers) comes back with its cap; the other pins stay out, they are not missing
        heads = {self.pkg_head(req) for req in missing}
        pins = []
        for dpkg in self.device_pkgs:
            try:
                pin = self.select_pkg(dpkg)
                if self.pkg_head(pin) in heads:
                    pins.append(pin)
            except Exception:
                pass
        try:
            subprocess.check_call(self._uv_pip('install', '--cache-dir', self.pip_cache_dir, *self.apply_pins(missing, pins)))
        except subprocess.CalledProcessError as e:
            msg = legends['msg_install_pkg_failed'].format(pkg=', '.join(missing), e=e)
            print(msg)
            return 1
        importlib.invalidate_caches()
        return 0

    def remove_obsolete_packages(self)->int:
        # packages removed from requirements.txt that must also be uninstalled
        # from existing envs when users update.
        # unidic: replaced by unidic-lite. fugashi prefers full unidic when
        # importable, but its dicdir is empty without 'python -m unidic download',
        # so a leftover install breaks Japanese TTS (mecabrc not found).
        obsolete_packages = ['unidic']
        try:
            for pkg_name in obsolete_packages:
                dicdir = None
                if pkg_name == 'unidic':
                    try:
                        import unidic
                        dicdir = unidic.DICDIR
                    except (ImportError, AttributeError):
                        pass
                try:
                    version(pkg_name)
                except PackageNotFoundError:
                    continue
                msg = legends['msg_removing_obsolete'].format(pkg=pkg_name)
                print(msg)
                try:
                    subprocess.check_call(self._uv_pip('uninstall', pkg_name))
                    if pkg_name == 'unidic' and dicdir:
                        dicdir = os.path.abspath(str(dicdir))
                        if os.path.isdir(dicdir) and dicdir != os.path.abspath(os.sep):
                            print(f'Removing UniDic dictionary directory: {dicdir}')
                            shutil.rmtree(dicdir, ignore_errors=True)
                except subprocess.CalledProcessError as e:
                    msg = legends['msg_remove_obsolete_failed'].format(pkg=pkg_name, e=e)
                    print(msg)
            return 0
        except Exception as e:
            error = f'remove_obsolete_packages() error: {e}'
            print(error)
            return 0

    def check_numpy(self)->bool:
        try:
            numpy_version = self.get_package_version('numpy') or None
            torch_version = self.get_package_version('torch') or None
            min_cpu_baseline = self.cpu_baseline
            numpy_pkg = None
            if torch_version is None:
                return False
            torch_version_base = self.version_tuple(torch_version)
            if numpy_version is None:
                if torch_version_base <= self.version_tuple('2.2.2'):
                    numpy_pkg = 'numpy<2'
                elif not min_cpu_baseline:
                    numpy_pkg = 'numpy<2.4.0'
                else:
                    numpy_pkg = 'numpy'
            else:
                numpy_version_base = self.version_tuple(numpy_version)
                if torch_version_base <= self.version_tuple('2.2.2') and numpy_version_base >= self.version_tuple('2.0.0'):
                    numpy_pkg = 'numpy<2'
                elif not min_cpu_baseline and numpy_version_base >= self.version_tuple('2.4.0'):
                    numpy_pkg = 'numpy<2.4.0'
            if numpy_pkg is not None:
                subprocess.check_call(self._uv_pip('install', '--no-cache', numpy_pkg))
            return True
        except subprocess.CalledProcessError as e:
            error = legends['error_numpy_install_failed'].format(e=e)
            print(error)
            return False
        except Exception as e:
            error = legends['error_numpy_install'].format(e=e)
            print(error)
            return False

    def has_directml_gpu(self)->bool:
        if self.system != systems['WINDOWS']:
            return False
        cmd = [
            'powershell', '-NoProfile', '-NonInteractive', '-Command',
            'Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name'
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=30).decode(errors='ignore').lower()
        except Exception as e:
            error = f'has_directml_gpu(): {e}'
            print(error)
            return False
        blacklist = ('microsoft basic display', 'remote display', 'standard vga', 'virtual', 'vmware', 'parallels', 'citrix')
        vendors = ('nvidia', 'amd', 'radeon', 'intel', 'arc', 'qualcomm', 'adreno')
        for line in out.splitlines():
            name = line.strip()
            if not name or any(b in name for b in blacklist):
                continue
            if any(v in name for v in vendors):
                return True
        return False

    def has_torchcodec_stack(self)->bool:
        # single source of truth for the whole dependency universe:
        #   torch >= 2.9 -> torchcodec exists -> pyannote 4 -> hub 1.x -> transformers 5
        #   torch <  2.9 -> no torchcodec     -> pyannote 3.4.0 -> hub 1.x (use_auth_token via sitecustomize)
        # transformers itself is not part of this split: it follows the torch floor,
        # see select_pkg('transformers') and transformers_caps.
        # torch_matrix tags with codec '' (cu118/cu121/cu124, rocm<=6.2.4, jetson5/jetson6)
        # top out below 2.9 and must stay on the old branch.
        # (2, 9) is the same boundary _needs_reinstall() uses to decide whether
        # torchcodec gets installed at all.
        torch_version = self.get_package_version('torch') or ''
        return self.version_tuple(torch_version, 2) >= (2, 9)

    def torch_cuda_major(self)->int:
        # read from the local version tag of the installed torch wheel
        # ('2.6.0+cu124' -> 12) so torch never has to be imported here. Wheels from
        # the default PyPI index carry no local tag, so fall back to whichever
        # nvidia runtime series torch pulled in. 0 when there is no cuda at all.
        torch_version = self.get_package_version('torch') or ''
        match = re.search(r'\+cu(\d{2,3})', torch_version)
        if match:
            digits = match.group(1)
            return int(digits[:-1]) if len(digits) == 3 else int(digits)
        for major in (13, 12, 11):
            if self.get_package_version(f'nvidia-cuda-runtime-cu{major}'):
                return major
        return 0

    def select_pkg(self, pkg:str)->str:
        # device-dependent requirements that PEP 508 markers cannot express.
        # returns a pip requirement string, no side effects: removing the losing
        # alternatives is finalize_exclusive_packages()'s job, after the
        # requirements pass.
        match pkg:
            case 'onnxruntime':
                name, tag, msg = self.check_hardware
                # onnxruntime-gpu ships x86_64 + win_amd64 wheels only: there is no
                # aarch64 GPU wheel on PyPI, so jetson and any arm64 CUDA host must
                # stay on the CPU build (NVIDIA's jetson wheels are cp310/numpy<2).
                # cp311 is the oldest wheel in the current release, so below 3.11
                # pip would backtrack to an ancient onnxruntime-gpu that pins numpy<2.
                # CUDA ONLY: onnxruntime-gpu is the CUDA/TensorRT build. On an xpu or
                # rocm host it installs ~250 MB, finds no CUDA provider and falls back
                # to CPU without a word — the exact silent degradation the cuda_major
                # check below exists to prevent. Intel wants onnxruntime-openvino and
                # AMD onnxruntime-rocm; neither is wired in here, so both fall through
                # to the plain CPU build (and to directml on Windows).
                if self.python_version >= (3, 11) and self.arch in [archs['X86_64'], archs['AMD64']] and devices['CUDA']['found']:
                    # torch and onnxruntime must share the same CUDA major, or the
                    # CUDA provider fails to load, ORT falls back to CPU silently and
                    # piper just runs slower with no error. The onnxruntime-gpu wheel
                    # series: <=1.18.1 is CUDA 11, 1.19-1.26 is CUDA 12, 1.27+ is
                    # CUDA 13. No cuda major found means there is nothing to match,
                    # so leave it uncapped.
                    cuda_major = self.torch_cuda_major()
                    if cuda_major == 11:
                        # the last CUDA 11 wheel is onnxruntime-gpu 1.18.1, built
                        # against numpy 1.x. check_numpy() leaves a cu118 box (torch
                        # 2.7.1) on numpy 2.x, and 1.18.1 does not declare numpy<2,
                        # so pip installs it and ORT then fails at import with the
                        # _ARRAY_API / dtype-size ABI error. No usable GPU build
                        # exists for CUDA 11 here, so stay on the CPU one.
                        return 'onnxruntime'
                    if cuda_major == 12:
                        return 'onnxruntime-gpu<1.27'
                    return 'onnxruntime-gpu'
                if name == devices['CPU']['proc'] or self.python_version < (3, 12) or self.system != systems['WINDOWS']:
                    return 'onnxruntime'
                if not self.has_directml_gpu():
                    return 'onnxruntime'
                return 'onnxruntime-directml'
            case 'transformers':
                # not in requirements.txt: it arrives through coqui-tts (transformers>=4.57,
                # no upper bound), so left alone the resolver takes the newest release even
                # when the installed torch is below its floor, and transformers then disables
                # PyTorch at import:
                #   Disabling PyTorch because PyTorch >= 2.5 is required but found 2.2.2
                # the torch floor is the only thing arbitrated here. Nothing patches the rest
                # anymore (sitecustomize.py only allowlists XttsConfig for torch.load): below
                # torch 2.6 transformers also refuses torch.load, so a .bin checkpoint fails,
                # the main env's transformers models load from safetensors.
                # listed in device_pkgs so the cap rides along on every install call and
                # coqui-tts cannot drag transformers back above it.
                torch_version = self.get_package_version('torch') or ''
                if torch_version:
                    for torch_floor, transformers_cap in self.transformers_caps.items():
                        if self.version_tuple(torch_version, 2) < self.version_tuple(torch_floor, 2):
                            return f'transformers>={self.transformers_min},<{transformers_cap}'
                return f'transformers>={self.transformers_min}'
            case _:
                raise ValueError(f'select_pkg(): no rule for {pkg}')

    def is_pkg_importable(self, pkg:str)->bool:
        # a directory left in site-packages with no __init__.py still imports, as a
        # namespace package with no attributes:
        #   AttributeError: module 'onnxruntime' has no attribute '__version__'
        #   ImportError: cannot import name 'InferenceSession' ... (unknown location)
        # spec.origin is None in exactly that case.
        import importlib.util
        try:
            spec = importlib.util.find_spec(pkg.replace('-', '_'))
            return spec is not None and spec.origin is not None
        except Exception:
            return False

    def clean_pkg_dir(self, pkg:str)->None:
        # pip uninstall only removes what a distribution's RECORD lists. When two
        # distributions share one import package (onnxruntime, onnxruntime-gpu and
        # onnxruntime-directml all unpack into site-packages/onnxruntime/) the
        # other one's files survive: __init__.py goes, stale provider .so files
        # stay. Nothing but deleting the directory clears that.
        import sysconfig
        try:
            purelib = sysconfig.get_paths().get('purelib')
            if not purelib:
                return
            pkg_dir = os.path.join(purelib, pkg.replace('-', '_'))
            if os.path.isdir(pkg_dir):
                msg = legends['msg_removing_leftover'].format(path=pkg_dir)
                print(msg)
                shutil.rmtree(pkg_dir, ignore_errors=True)
        except Exception as e:
            error = f'clean_pkg_dir(): {e}'
            print(error)

    def drop_pip_cache(self)->None:
        try:
            if os.path.isdir(self.pip_cache_dir):
                shutil.rmtree(self.pip_cache_dir, ignore_errors=True)
        except Exception as e:
            error = f'drop_pip_cache(): {e}'
            print(error)

    def finalize_exclusive_packages(self, specs:dict|None=None)->int:
        # specs: {pkg: requirement} already chosen by the caller (skips a second select_pkg probe)
        try:
            for pkg, choices in self.exclusive_pkgs.items():
                spec = (specs or {}).get(pkg) or self.select_pkg(pkg)
                keep = re.split(r'[<>=!\[;]', spec, 1)[0].strip()
                installed = [choice for choice in choices if self.get_package_version(choice)]
                losers = [choice for choice in installed if choice != keep]
                # also repair an env already hollowed out by a previous swap
                broken = bool(installed) and not self.is_pkg_importable(pkg)
                if not losers and not broken:
                    continue
                msg = legends['msg_resolving_pkg'].format(pkg=pkg, keep=keep, remove=', '.join(losers) if losers else legends['msg_broken_install'])
                print(msg)
                if installed:
                    subprocess.call(self._uv_pip('uninstall', *installed))
                self.clean_pkg_dir(pkg)
                # install the full spec, not the bare name: keeps caps like onnxruntime-gpu<1.27 (CUDA 12)
                subprocess.check_call(self._uv_pip('install', '--cache-dir', self.pip_cache_dir, spec))
            return 0
        except Exception as e:
            error = f'finalize_exclusive_packages() error: {e}'
            print(error)
            return 0

    def torch_probe_child(self)->Union[dict, None]:
        # run components/detect_gpu.py in a child process and parse its json line: None when the child could not run to
        # its end (missing python, timeout, unreadable output). Used before installing a GPU torch at all -- an access
        # violation inside python312.dll kills the child without any usable traceback, so only a probe that runs early
        # can tell a working wheel from one that crashes natively on this driver
        try:
            proc = subprocess.run([python_exec, detect_gpu_script], capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                return None
            data = json.loads(proc.stdout.strip() or '{}')
            return data if isinstance(data, dict) else None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError, ValueError):
            return None

    def cuda_torch_crashes(self, tag_dir:str, torch_version_matrix:str, torchaudio_version_matrix:str, py_major:int, py_minor:int)->bool:
        # a cuXYZ torch build whose kernels predate the installed CUDA driver can corrupt memory natively instead of
        # failing cleanly: 'Windows fatal exception: access violation' inside python312.dll once xtts runs. When the
        # exact pinned versions import fine but no device answers (or the child dies), those wheels are unusable with
        # this driver and e2a must pick another row before installing anything. A probe that cannot run (no network,
        # download cut short) is not a crash: the normal install flow stands
        url = default_pytorch_url
        tag_py = f'cp{py_major}{py_minor}'
        with tempfile.TemporaryDirectory(prefix='e2a_probe_') as probe_dir:
            cmd = self._uv_pip('install', '--target', probe_dir, '--no-cache', '--no-deps',
                               f'torch=={torch_version_matrix}', f'torchaudio=={torchaudio_version_matrix}',
                               '--index-url', f'{url}/{tag_dir}', '--extra-index-url', f'{default_pytorch_nightly_url}/{tag_dir}',
                               '--index-strategy', 'unsafe-best-match')
            if subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
                return False
            env = {**os.environ, 'PYTHONPATH': probe_dir + os.pathsep + os.environ.get('PYTHONPATH', '')}
            try:
                proc = subprocess.run([python_exec, detect_gpu_script], capture_output=True, text=True, timeout=120, env=env)
            except (subprocess.TimeoutExpired, OSError):
                return False
            if proc.returncode != 0:
                # nonzero exit: an import error prints it, a native crash (access violation) leaves nothing but the code
                return True
            try:
                data = json.loads(proc.stdout.strip() or '{}')
            except json.JSONDecodeError:
                return True
            return int(data.get('count') or 0) == 0

    def system_dll_missing(self, name:str)->bool:
        # True only when the file is nowhere on the DLL search path: not System32 (where the VC++ redistributables
        # install), not next to the python.exe, and not loadable through the process' AddDllDirectory set. An existing
        # file that fails to load stays False: something else is wrong then and vcredist would not help
        if self.system != systems['WINDOWS']:
            return False
        try:
            import ctypes
            windir = os.environ.get('SystemRoot', r'C:\Windows')
            if os.path.isfile(os.path.join(windir, 'System32', name)) or os.path.isfile(os.path.join(os.path.dirname(sys.executable), name)):
                return False
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.c_void_p
            kernel32.LoadLibraryExW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_uint32]
            LOAD_LIBRARY_AS_DATAFILE = 0x00000002
            LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000
            handle = kernel32.LoadLibraryExW(name, None, LOAD_LIBRARY_AS_DATAFILE | LOAD_LIBRARY_SEARCH_DEFAULT_DIRS)
            if handle:
                kernel32.FreeLibrary(ctypes.c_void_p(handle))
                return False
            return True
        except Exception:
            return False

    vulkan_libomp_marker = os.path.join(sys.prefix, '.e2a_vulkan_torch_libomp')

    def vulkan_torch_lacks_libomp(self, torch_url:str)->bool:
        # the Windows +vulkan torch links MSVC's LLVM OpenMP runtime (libomp140.x86_64.dll), which no VC++
        # redistributable installs: a wheel published without it in torch/lib does not import ("Error loading shm.dll or
        # one of its dependencies"). The repacked wheel keeps the same version, so the missing file tells them apart. It
        # is reinstalled only when the published wheel changed since the last install (ETag or size and date from a HEAD
        # request, kept in python_env): an unfixed wheel is not downloaded again at every start
        self.vulkan_libomp_signature = None
        try:
            torch_dist = distribution('torch')
            lib_dir = str(torch_dist.locate_file(os.path.join('torch', 'lib')))
            torch_cpu = os.path.join(lib_dir, 'torch_cpu.dll')
            if not os.path.isfile(torch_cpu) or os.path.isfile(os.path.join(lib_dir, 'libomp140.x86_64.dll')):
                return False
            import mmap
            with open(torch_cpu, 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
                if data.find(b'libomp140.x86_64.dll') < 0:
                    return False
            import urllib.request
            with urllib.request.urlopen(urllib.request.Request(torch_url, method='HEAD'), timeout=15) as response:
                headers = response.headers
            signature = headers.get('ETag') or f"{headers.get('Content-Length')}|{headers.get('Last-Modified')}"
            previous = ''
            if os.path.isfile(self.vulkan_libomp_marker):
                with open(self.vulkan_libomp_marker, 'r', encoding='utf-8') as f:
                    previous = f.read().strip()
            if signature == previous:
                return False
            msg = legends['msg_vulkan_torch_libomp'].format(dll='libomp140.x86_64.dll')
            print(msg)
            self.vulkan_libomp_signature = signature
            return True
        except Exception:
            # no torch, unreadable file, offline: nothing to decide on, the normal checks stand
            return False

    def save_vulkan_libomp_try(self)->None:
        signature = getattr(self, 'vulkan_libomp_signature', None)
        if not signature:
            return
        try:
            with open(self.vulkan_libomp_marker, 'w', encoding='utf-8') as f:
                f.write(signature)
        except OSError:
            pass

    @install_locked
    def install_device_packages(self, device_info_str:str)->int:
        def _tag_ok(installed_tag):
            # CPU index: '/whl/cpu' -> bare on macOS, '+cpu' on linux/windows; both are fine
            if tag == devices['CPU']['proc']:
                return installed_tag is None or installed_tag == devices['CPU']['proc']
            # MPS: installed from '/whl/cpu' on macOS arm64 -> bare wheels
            elif device_info['name'] == devices['MPS']['proc']:
                return installed_tag is None
            # ROCm Windows (TheRock): matrix key is 'win-rocmX.Y.Z' (kept distinct from
            # the linux 'rocmX.Y' keys) but the wheel's local version drops 'win-',
            # e.g. tag='win-rocm7.2.1' -> '+rocm7.2.1' (optionally with a build suffix).
            elif device_info['name'] == devices['ROCM']['proc'] and self.system == systems['WINDOWS']:
                wheel_tag = tag.replace('win-', '')
                return installed_tag == wheel_tag or (installed_tag is not None and installed_tag.startswith(f'{wheel_tag}-'))
            # CUDA, XPU, ROCm Linux, Jetson: must be exactly '+<tag>'
            # (a pure hex local version means a custom/dev build -> reinstall)
            elif device_info['name'] == devices['CUDA']['proc'] and self.system == systems['WINDOWS']:
                wheel_tag = tag.replace('win-', '')
                return installed_tag == wheel_tag or (installed_tag is not None and installed_tag.startswith(f'{wheel_tag}-'))
            return installed_tag == tag

        def _needs_reinstall():
            # torch: base version + local tag must match what we'd install for this device
            if not torch_version_current_full:
                return True
            if torch_version_current_base != torch_version_matrix:
                return True
            if not _tag_ok(current_tag):
                return True
            # torchaudio: base version + local tag must match what we'd install for this device.
            # Compare against torchaudio_spec, not torch_version_matrix — above the
            # ceiling the two differ by design, and any 2.11.x patch is accepted there:
            # an exact compare would report "needs reinstall" on every single run and
            # reinstall torch with it.
            torchaudio_full = self.get_package_version('torchaudio')
            if not torchaudio_full:
                return True
            torchaudio_base = torchaudio_full.split('+', 1)[0]
            if not self.torchaudio_ok(torchaudio_base, torch_version_matrix):
                return True
            m_ta = re.search(r'\+(.+)$', torchaudio_full)
            torchaudio_tag = m_ta.group(1) if m_ta else None
            if not _tag_ok(torchaudio_tag):
                return True
            # torchcodec: presence only (when torch >= 2.9 needs it)
            if self.version_tuple(torch_version_matrix, 2) >= (2, 9) and not self.get_package_version('torchcodec'):
                return True
            # the right versions with files gone (install cut short, antivirus): every check above passes and the first
            # import fails (torch without torch/amp/: "cannot import name 'amp' from partially initialized module
            # 'torch'"). repair_incomplete_packages() leaves the torch family to this step, which reinstalls it from the
            # device's own wheels. torchcodec only where this step installs it
            pkgs = ['torch', 'torchaudio']
            if self.version_tuple(torch_version_matrix, 2) >= (2, 9) and torchcodec_version_matrix:
                pkgs.append('torchcodec')
            incomplete = [pkg for pkg in pkgs if self.package_incomplete(pkg)]
            if incomplete:
                msg = legends['msg_reinstalling_incomplete'].format(pkgs=', '.join(incomplete))
                print(msg)
                return True
            # a system DLL the torch family links is absent (WinError 126 at import): the VC++ redistributable was
            # never installed. No wheel carries these files, so reinstalling alone fixes nothing -- prompt for it
            # first, then fall through to the reinstall that lets e2a boot once the user has installed it
            if self.system == systems['WINDOWS']:
                missing = sorted({dep.lower() for dep in ('msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll') if self.system_dll_missing(dep)})
                if missing:
                    msg = legends['msg_vcredist_missing'].format(dlls=', '.join(missing), url=self.vcredist_url)
                    print(msg)
            # Windows +vulkan torch published without the OpenMP runtime it links: same version as the fixed wheel
            if device_info['name'] == devices['VULKAN']['proc'] and self.system == systems['WINDOWS']:
                py_major, py_minor = device_info['pyvenv']
                vulkan_torch_url = f"{default_jetson_url}/torch/torch-{torch_version_matrix}%2B{tag}-cp{py_major}{py_minor}-cp{py_major}{py_minor}-{device_info['os']}_{device_info['arch']}.whl"
                if self.vulkan_torch_lacks_libomp(vulkan_torch_url):
                    return True
            return False

        def _probe_gpus()->dict:
            # 'probed': the child ran to its end (or died in torch), so a count of 0 is torch's own answer. A probe that
            # could not run (timeout on a cold start, missing python, unreadable output) says nothing about the GPU
            try:
                proc = subprocess.run([python_exec, detect_gpu_script], capture_output=True, text=True, timeout=30)
                if proc.returncode != 0:
                    # Windows reports a native crash as an NTSTATUS (0xc0000005 access violation), POSIX as -signal
                    code = f'{proc.returncode:#x}' if proc.returncode > 255 else str(proc.returncode)
                    return {'count': 0, 'backend': None, 'probed': True, 'error': proc.stderr.strip() or f'exit code {code}'}
                return {**json.loads(proc.stdout.strip() or '{}'), 'probed': True}
            except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
                return {'count': 0, 'backend': None, 'error': str(e)}

        try:
            if device_info_str:
                device_info = json.loads(device_info_str)
                if device_info:
                    msg = legends['msg_hardware_detected'].format(info=device_info)
                    print(msg)
                    tag = device_info.get('tag')
                    if tag in ['unknown','unsupported']:
                        return 0
                    matrix_entry = torch_matrix.get(tag)
                    if not matrix_entry:
                        error = legends['error_no_torch_matrix'].format(tag=tag)
                        print(error)
                        return 1
                    # one python per device (check_pyvenv), so one torch version per row: 'last'
                    torch_version_matrix = matrix_entry['last']
                    torchcodec_version_matrix = matrix_entry.get('codec') or ''
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
                    if _needs_reinstall():
                        try:
                            msg = legends['msg_installing_libs'].format(name=device_info['name'])
                            print(msg)
                            os_env = device_info['os']
                            arch = device_info['arch']
                            tag_dir = 'cpu' if device_info['name'] == devices['MPS']['proc'] else tag
                            py_major, py_minor = device_info['pyvenv']
                            tag_py = f'cp{py_major}{py_minor}'
                            torchaudio_version_matrix = self.torchaudio_version(torch_version_matrix)
                            is_cpu_aarch64_linux = (
                                tag == devices['CPU']['proc']
                                and device_info['os'] in ('manylinux_2_28', 'linux')
                                and device_info['arch'] == archs['AARCH64']
                            )
                            #### torch/torchaudio installation
                            subprocess.check_call(self._uv_pip('install', '--no-cache', 'filelock', 'typing-extensions', 'jinja2', 'fsspec', 'networkx', 'sympy'))
                            if device_info['name'] == devices['JETSON']['proc']:
                                url = default_jetson_url
                                torch_pkg = f"{url}/torch/torch-{torch_version_matrix}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                torchaudio_pkg = f"{url}/torchaudio/torchaudio-{self.torchaudio_version(torchaudio_version_matrix)}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torch_pkg))
                                subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torchaudio_pkg))
                                subprocess.check_call(self._uv_pip('install', '--no-cache', 'scikit-learn'))
                                subprocess.check_call(self._uv_pip('install', '--no-cache', 'scipy'))
                            elif device_info['name'] == devices['VULKAN']['proc']:
                                # +vulkan torch / torchaudio from py-pkg (build-torch-vulkan.sh / .cmd)
                                url = default_jetson_url
                                torch_pkg = f"{url}/torch/torch-{torch_version_matrix}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                torchaudio_pkg = f"{url}/torchaudio/torchaudio-{torchaudio_version_matrix}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torch_pkg, torchaudio_pkg))
                                self.save_vulkan_libomp_try()
                            elif device_info['name'] == devices['ROCM']['proc'] and self.system == systems['WINDOWS']:
                                url = default_pytorch_amd_url
                                real_tag = tag.replace('win-', '')
                                url_tag = tag.replace('win-rocm', 'rocm-rel-')
                                # rocm_sdk is required by torch ROCm wheels on Windows; install it first if missing
                                import importlib.util
                                if importlib.util.find_spec('rocm_sdk') is None:
                                    rocm_ver = tag[len('win-rocm'):] if tag.startswith('win-rocm') else tag
                                    sdk_pkgs = [
                                        f'{url}/{url_tag}/rocm_sdk_core-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{url_tag}/rocm_sdk_devel-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{url_tag}/rocm_sdk_libraries_custom-{rocm_ver}-py3-none-{os_env}_{arch}.whl',
                                        f'{url}/{url_tag}/rocm-{rocm_ver}.tar.gz',
                                    ]
                                    msg = legends['msg_installing_rocm_sdk'].format(version=rocm_ver)
                                    print(msg)
                                    subprocess.check_call(self._uv_pip('install', '--no-cache', *sdk_pkgs))
                                torch_pkg = f'{url}/{url_tag}/torch-{torch_version_matrix}%2B{real_tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl'
                                torchaudio_pkg = f'{url}/{url_tag}/torchaudio-{self.torchaudio_version(torchaudio_version_matrix)}%2B{real_tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl'
                                subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torch_pkg, torchaudio_pkg))
                            else:
                                url = default_pytorch_url
                                url_nightly = default_pytorch_nightly_url
                                # uv gives --extra-index-url priority over --index-url and by default stops at the
                                # first index that has the package: without unsafe-best-match a stable pin that the
                                # nightly index lacks (e.g. torch==2.2.2 on intel macOS) finds no version at all
                                # 'win-cuXYZ' rows keep the Windows torch apart, their wheels are on the plain cuXYZ index
                                torch_url_tag = tag_dir.replace('win-', '') if tag_dir.startswith('win-cu') else tag_dir
                                torchaudio_url_tag = torch_url_tag
                                subprocess.check_call(self._uv_pip('install', '--reinstall-package', 'torch', '--no-cache', f'torch=={torch_version_matrix}', '--index-url', f'{url}/{torch_url_tag}', '--extra-index-url', f'{url_nightly}/{torch_url_tag}', '--index-strategy', 'unsafe-best-match'))
                                subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', self.torchaudio_spec(torch_version_matrix), '--index-url', f'{url}/{torchaudio_url_tag}', '--extra-index-url', f'{url_nightly}/{torchaudio_url_tag}', '--index-strategy', 'unsafe-best-match'))
                            if not self.check_numpy():
                                return 1
                            #### torchcodec installation
                            if self.version_tuple(torch_version_matrix, 2) >= (2, 9) and torchcodec_version_matrix:
                                if device_info['name'] == devices['JETSON']['proc']:
                                    # jetson7 (torch >= 2.9): no aarch64 torchcodec on PyPI, built like torch/torchaudio
                                    torchcodec_wheel_url = f"{default_jetson_url}/torchcodec/torchcodec-{torchcodec_version_matrix}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                    rc = subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torchcodec_wheel_url))
                                elif device_info['name'] == devices['VULKAN']['proc'] and self.system == systems['MACOS']:
                                    torchcodec_wheel_url = f"{default_jetson_url}/torchcodec/torchcodec-{torchcodec_version_matrix}%2B{tag}-{tag_py}-{tag_py}-{os_env}_{arch}.whl"
                                    rc = subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torchcodec_wheel_url))
                                elif is_cpu_aarch64_linux:
                                    torchcodec_wheel_url = f"{default_torchcodec_arm_url}/{tag}/torchcodec-{torchcodec_version_matrix}%2B{tag}-{tag_py}-{tag_py}-manylinux_2_27_{arch}.{os_env}_{arch}.whl"
                                    rc = subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', torchcodec_wheel_url))
                                else:
                                    if device_info['name'] == devices['XPU']['proc']:
                                        # all from PyPI: the xpu index only mirrors torchcodec's Linux CPU build, and under uv's
                                        # first-index rule it hid PyPI's Windows wheel. Intel's plugin (torchcodec-xpu, with
                                        # torchlib-xpu) is Linux only and follows torchcodec's versions, so it takes the same pin
                                        torchcodec_pkgs = [f'torchcodec=={torchcodec_version_matrix}']
                                        if self.system == systems['LINUX']:
                                            torchcodec_pkgs += [f'torchcodec-xpu=={torchcodec_version_matrix}', 'torchlib-xpu']
                                            msg = legends['msg_installing_torchcodec_xpu']
                                        else:
                                            msg = legends['msg_installing_torchcodec_xpu_no_plugin']
                                        print(msg)
                                        rc = subprocess.call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', *torchcodec_pkgs))
                                    else:
                                        # the CPU build where the device's index has none: e2a only decodes audio with it
                                        # (torchaudio.load). ROCm and Vulkan, and CUDA on Windows (cu128 / cu129 carry no
                                        # Windows torchcodec, and since 0.12 one build serves every torch >= 2.11)
                                        cpu_torchcodec = device_info['name'] in [devices['ROCM']['proc'], devices['VULKAN']['proc']] or (device_info['name'] == devices['CUDA']['proc'] and self.system == systems['WINDOWS'])
                                        torchcodec_index_url = f'{default_pytorch_url}/cpu' if cpu_torchcodec else f"{default_pytorch_url}/{tag_dir.replace('win-', '')}"
                                        rc = subprocess.check_call(self._uv_pip('install', '--reinstall', '--no-cache', '--no-deps', f'torchcodec=={torchcodec_version_matrix}', '--index-url', torchcodec_index_url))
                                if rc == 0:
                                    try:
                                        subprocess.check_call([python_exec, '-c', 'from torchcodec.decoders import AudioDecoder'])
                                    except subprocess.CalledProcessError:
                                        error = legends['error_torchcodec_import']
                                        print(error)
                                        return 1
                                else:
                                    error = legends['error_torchcodec_missing']
                                    print(error)
                                    return 1
                        except subprocess.CalledProcessError as e:
                            error = legends['error_torch_install_failed'].format(e=e)
                            print(error)
                            return 1
                        except Exception as e:
                            error = legends['error_torch_install'].format(e=e)
                            print(error)
                            return 1
                    self.link_os_libgomp('python_env', device_info)
                    # an inherited one would make sitecustomize.py answer 0 for torch in the probe too: it asks torch
                    # itself, and the verdict below sets it again
                    os.environ.pop('E2A_XPU_UNUSABLE', None)
                    gpu_info = _probe_gpus()
                    device_info_dict['gpu_count'] = gpu_info['count']
                    device_info_dict['gpu_backend'] = gpu_info['backend']
                    if gpu_info.get('error'):
                        error = legends['error_gpu_detection_warning'].format(e=gpu_info['error'])
                        print(error)
                    # check_hardware() set devices['XPU']['found'] from Level Zero listing an Intel GPU, which does not
                    # mean torch xpu runs on it: on an iGPU it does not support or an old driver, torch.xpu.is_available()
                    # answers 0 or kills the process (Windows access violation in device_count()). Only this probe, in
                    # its own process, can ask safely: XPU off, so nothing in the app (the device dropdown,
                    # VoiceExtractor, the session device check) asks torch.xpu again. Third-party code still asks it
                    # on its own (transformers at import, CPU conversions included): with E2A_XPU_UNUSABLE set,
                    # components/sitecustomize.py makes torch.xpu report no device in this process, torch not imported
                    # yet, and in every child that inherits it
                    if device_info['name'] == devices['XPU']['proc'] and gpu_info['count'] == 0 and gpu_info.get('probed'):
                        devices['XPU']['found'] = False
                        os.environ['E2A_XPU_UNUSABLE'] = '1'
                        msg = legends['msg_xpu_unusable']
                        print(msg)
                    if gpu_info['count'] > 0:
                        idx = ','.join(str(i) for i in range(gpu_info['count']))
                        if gpu_info['backend'] == 'cuda':
                            os.environ['CUDA_VISIBLE_DEVICES'] = idx
                        elif gpu_info['backend'] == 'rocm':
                            os.environ['HIP_VISIBLE_DEVICES'] = idx
                            # detect_gpu.py resolved it in its own child process, count > 0 means torch found the GPU under it
                            if gpu_info.get('hsa_override') and not os.environ.get('HSA_OVERRIDE_GFX_VERSION'):
                                os.environ['HSA_OVERRIDE_GFX_VERSION'] = gpu_info['hsa_override']
                        elif gpu_info['backend'] == 'xpu':
                            os.environ['ONEAPI_DEVICE_SELECTOR'] = f'level_zero:{idx}'
                            os.environ['ZE_AFFINITY_MASK'] = idx
                    return 0
                else:
                    error = 'install_device_packages() error: json.loads() could not decode device_info_str'
                    print(error)
            else:
                error = 'install_device_packages() error: device_info_str is empty'
                print(error)
            return 1
        except Exception as e:
            error = f'install_device_packages() error: {e}'
            print(error)
            return 1

    def check_voices(self)->int:
        from pathlib import Path, PurePosixPath
        from urllib.parse import urlparse, unquote
        import zipfile
        import json
        from typing import Optional
        from huggingface_hub import hf_hub_download, get_hf_file_metadata, hf_hub_url
        from tqdm import tqdm
        voices_dir:Path = Path('./voices')
        version_file:Path = voices_dir / '.version.json'
        def has_wav()->bool:
            return any(voices_dir.rglob('*.wav'))
        try:
            voices_dir.mkdir(parents=True, exist_ok=True)
            parts:tuple = PurePosixPath(unquote(urlparse(voices_url).path)).parts
            i:int = parts.index('datasets')
            repo_id:str = f'{parts[i+1]}/{parts[i+2]}'
            r:int = parts.index('resolve')
            filename:str = '/'.join(parts[r+2:])
            remote_etag:Optional[str] = None
            try:
                url:str = hf_hub_url(repo_id, filename, repo_type='dataset')
                metadata = get_hf_file_metadata(url)
                remote_etag = metadata.etag
            except Exception:
                pass
            local_etag:Optional[str] = None
            if version_file.exists():
                try:
                    with open(version_file, 'r') as f:
                        local_etag = json.load(f).get('etag')
                except Exception:
                    pass
            if has_wav() and (remote_etag is None or local_etag == remote_etag):
                return 0
            zip_path:Path = Path(hf_hub_download(repo_id=repo_id, filename=filename, repo_type='dataset', local_dir='.'))
            print(f'Downloaded {zip_path.stat().st_size / (1024*1024):.1f} MB to {zip_path}')
            with zipfile.ZipFile(zip_path, 'r') as zf:
                members:list = zf.infolist()
                desc:str = 'Extracting voices'
                for member in tqdm(members, desc=desc, unit='file'):
                    zf.extract(member, './')
            if remote_etag:
                with open(version_file, 'w') as f:
                    json.dump({"etag": remote_etag}, f)
            if zip_path.exists():
                zip_path.unlink()
            return 0 if has_wav() else 1
        except Exception as e:
            error:str = f'check_voices() error: {e}'
            print(error)
        return 1