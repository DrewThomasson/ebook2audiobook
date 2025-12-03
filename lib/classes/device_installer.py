import os, re, sys, platform, shutil, importlib, subprocess, json

from packaging.version import Version, InvalidVersion
from importlib.metadata import version, PackageNotFoundError
from packaging.specifiers import SpecifierSet
from packaging.markers import Marker
from functools import cached_property

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
        name, tag = self.check_hardware
        arch = self.check_arch
        pyenv = sys.version_info[:2]
        if mode == NATIVE:
            os_env = 'linux' if name == 'jetson' else self.check_platform
        elif mode == 'build_docker':
            os_env = 'linux' if name == 'jetson' else 'manylinux_2_28'
        if all([name, tag, os_env, arch, pyenv]):
            device_info = {"name": name, "os": os_env, "arch": arch, "pyvenv": pyenv, "tag": tag}
            return json.dumps(device_info)
        return ''
        
    def get_package_version(self, pkg:str)->str|bool:
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

        def toolkit_version_parse(text:str)->str|None:
            if not text:
                return None
            # ----- CUDA -----
            m = re.search(r'cuda\s*version\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', text, re.IGNORECASE)
            if m:
                return m.group(1)
            # ----- ROCm -----
            m = re.search(r'rocm\s*version\s*[:=]?\s*([0-9]+(?:\.[0-9]+){0,2})', text, re.IGNORECASE)
            if m:
                parts = m.group(1).split(".")
                major = parts[0]
                minor = parts[1] if len(parts) > 1 else "0"
                return f"{major}.{minor}"
            # HIP also implies ROCm
            m = re.search(r'hip\s*version\s*[:=]?\s*([0-9]+(?:\.[0-9]+){0,2})', text, re.IGNORECASE)
            if m:
                parts = m.group(1).split(".")
                major = parts[0]
                minor = parts[1] if len(parts) > 1 else "0"
                return f"{major}.{minor}"
            # ----- XPU / oneAPI -----
            m = re.search(r'(oneapi|xpu)\s*(toolkit\s*)?version\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)',
                          text, re.IGNORECASE)
            if m:
                return m.group(3)
            return None

        def toolkit_version_compare(version_str:str|None, version_range:dict)->int|None:
            if version_str is None:
                return None
            min_tuple = tuple(version_range.get('min', (0, 0)))
            max_tuple = tuple(version_range.get('max', (0, 0)))
            if min_tuple == (0, 0) and max_tuple == (0, 0):
                return 0
            parts = version_str.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
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
            if not m1 or not m2:
                msg = 'Unrecognized JetPack version. Falling back to CPU.'
                warn(msg)
                return 'unknown'
            l4t_major = int(m1.group(1))
            rev = m2.group(1)
            parts = rev.split('.')
            rev_major = int(parts[0])
            rev_minor = int(parts[1]) if len(parts) > 1 else 0

            if l4t_major < 35:
                msg = f'JetPack too old (L4T {l4t_major}). Please upgrade to JetPack 5.1+. Falling back to CPU.'
                warn(msg)
                return 'unsupported'

            if l4t_major == 35:
                if rev_major == 0 and rev_minor <= 1:
                    msg = 'JetPack 5.0/5.0.1 detected. Please upgrade to JetPack 5.1+ to use the GPU. Failing back to CPU'
                    warn(msg)
                    return 'cpu'
                if rev_major == 0 and rev_minor >= 2:
                    msg = 'JetPack 5.0.x detected. Please upgrade to JetPack 5.1+ to use the GPU. Failing back to CPU'
                    warn(msg)
                    return 'cpu'
                if rev_major == 1 and rev_minor == 0:
                    msg = 'JetPack 5.1.0 detected. Please upgrade to JetPack 5.1.2 or newer.'
                    warn(msg)
                    return '51'
                if rev_major == 1 and rev_minor == 1:
                    msg = 'JetPack 5.1.1 detected. Please upgrade to JetPack 5.1.2 or newer.'
                    warn(msg)
                    return '51'
                if (rev_major > 1) or (rev_major == 1 and rev_minor >= 2):
                    return '51'
                msg = 'Unrecognized JetPack 5.x version. Falling back to CPU.'
                warn(msg)
                return 'unknown'

            if l4t_major == 36:
                if rev_major == 2:
                    return '60'
                else:
                    return '61'
                msg = 'Unrecognized JetPack 6.x version. Falling back to CPU.'
                warn(msg)
            return 'unknown'

        def warn(msg:str)->None:
            print(f'[WARNING] {msg}')

        name = None
        tag = None
        arch = platform.machine().lower()

        # ============================================================
        # JETSON
        # ============================================================
        if arch in ('aarch64','arm64') and (os.path.exists('/etc/nv_tegra_release') or 'tegra' in try_cmd('cat /proc/device-tree/compatible')):
            raw = tegra_version()
            jp_code = jetpack_version(raw)
            if jp_code in ['unsupported', 'unknown']:
                tag = 'cpu'
            elif os.path.exists('/etc/nv_tegra_release'):
                devices['CUDA']['found'] = True
                name = 'jetson'
                tag = f'jetson{jp_code}'
            elif os.path.exists('/proc/device-tree/compatible'):
                out = try_cmd('cat /proc/device-tree/compatible')
                if 'tegra' in out:
                    devices['CUDA']['found'] = True
                    name = 'jetson'
                    tag = f'jetson{jp_code}'
            out = try_cmd('uname - a')
            if 'tegra' in out:
                msg = 'Unknown Jetson device. Failing back to cpu'
                warn(msg)
        # ============================================================
        # ROCm
        # ============================================================
        elif has_cmd('rocminfo') or os.path.exists('/opt/rocm'):
            out = try_cmd('rocminfo')
            version_str = toolkit_version_parse(out)
            cmp = toolkit_version_compare(version_str, rocm_version_range)
            if cmp == -1:
                msg = f'ROCm {version_str} < min {rocm_version_range["min"]}. Please upgrade.'
                warn(msg)
                tag = 'cpu'
            elif cmp == 1:
                msg = f'ROCm {version_str} > max {rocm_version_range["max"]}. Falling back to CPU.'
                warn(msg)
                tag = 'cpu'
            elif cmp == 0:
                devices['ROCM']['found'] = True
                name = 'rocm'
                tag = f'rocm{version_str}'
            else:
                msg = 'No ROCm version found. Falling back to CPU.'
                warn(msg)

        # ============================================================
        # CUDA
        # ============================================================
        elif has_cmd('nvcc'):
            out = try_cmd('nvcc --version')
            version_str = toolkit_version_parse(out)
            cmp = toolkit_version_compare(version_str, cuda_version_range)
            if cmp == -1:
                msg = f'CUDA {version_str} < min {cuda_version_range["min"]}. Please upgrade.'
                warn(msg)
                tag = 'cpu'
            elif cmp == 1:
                msg = f'CUDA {version_str} > max {cuda_version_range["max"]}. Falling back to CPU.'
                warn(msg)
                tag = 'cpu'
            elif cmp == 0:
                devices['CUDA']['found'] = True
                major, minor = version_str.split('.')
                name = 'cuda'
                tage = f'cu{major}{minor}'
            else:
                msg = 'No CUDA version found. Falling back to CPU.'
                warn(msg)

        # ============================================================
        # APPLE MPS
        # ============================================================
        elif sys.platform == 'darwin' and arch in ('arm64', 'aarch64'):
            devices['MPS']['found'] = True
            name = 'mps'
            tag = 'mps'

        # ============================================================
        # INTEL XPU
        # ============================================================
        elif os.path.exists('/dev/dri/renderD128'):
            out = try_cmd('lspci')
            if 'intel' in out:
                oneapi_out:str = try_cmd('sycl-ls') if has_cmd('sycl-ls') else ''
                version_str = toolkit_version_parse(oneapi_out)
                cmp = toolkit_version_compare(version_str, xpu_version_range)
                if cmp == -1 or cmp == 1:
                    msg = f'XPU {version_str} out of supported range {xpu_version_range}. Falling back to CPU.'
                    warn(msg)
                    tag = 'cpu'
                elif cmp == 0 and (has_cmd('sycl-ls') or has_cmd('clinfo')):
                    devices['XPU']['found'] = True
                    name = 'xpu'
                    tag = 'xpu'
                else:
                    msg = 'Intel GPU detected but oneAPI runtime missing → CPU'
                    warn(msg)

        elif has_cmd('clinfo'):
            out = try_cmd('clinfo')
            if 'intel' in out:
                name = 'xpu'
                tag = 'xpu'

        # ============================================================
        # CPU
        # ============================================================
        if tag is None:
            name = 'cpu'
            tag = 'cpu'
            
        return (name, tag)

    def check_and_install_requirements(self)->bool:
        if not os.path.exists(requirements_file):
            error = f'Warning: File {requirements_file} not found. Skipping package check.'
            print(error)
            return False
        try:
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
                        spec = SpecifierSet(spec_str)
                        norm_match = re.match(r'^(\d+\.\d+(?:\.\d+)?)', installed_version)
                        short_version = norm_match.group(1) if norm_match else installed_version
                        try:
                            installed_v = Version(short_version)
                        except Exception:
                            installed_v = Version('0')
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
                            if package in flexible_packages:
                                continue
                            error = f'Failed to install {package}: {e}'
                            print(error)
                            return False
                msg = '\nAll required packages are installed.'
                print(msg)
            return self.check_dictionary()
        except Exception as e:
            error = f'check_and_install_requirements() error: {e}'
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
          
    def install_device_packages(self, install_pkg:str)->bool:
        try:
            device_info = json.loads(install_pkg)
            if device_info:
                torch_version = self.get_package_version('torch')
                if torch_version:
                    if device_info['tag'] not in ['cpu', 'unknown', 'unsupported']:
                        m = re.search(r'\+(.+)$', torch_version)
                        current_tag = m.group(1) if m else None
                        if current_tag is not None:
                            non_standard_tag = re.fullmatch(r'[0-9a-f]{7,40}', current_tag)
                            if (
                                (non_standard_tag is None and current_tag != device_info['tag']) or 
                                (non_standard_tag is not None and non_standard_tag != device_info['tag'])
                            ):
                                try:
                                    torch_version_base = Version(torch_version).base_version
                                    print(device_info)
                                    print(f"{device_info['name']} hardware found! Installing the right torch library...")
                                    os_env = device_info['os']
                                    arch = device_info['arch']
                                    tag = device_info['tag']
                                    url = torch_matrix[device_info['tag']]['url']
                                    toolkit_version = "".join(c for c in tag if c.isdigit())
                                    tag_py = f'cp{default_py_major}{default_py_minor}-cp{default_py_major}{default_py_minor}'
                                    if device_info['name'] == 'jetson':
                                        torch_pkg = f"{url}/v{toolkit_version}/torch-{jetson_torch_version_base[tag]}+{tag}-{tag_py}-{os_env}_{arch}.whl"
                                        torchaudio_pkg =   f"{url}/v{toolkit_version}/torchaudio-{jetson_torch_version_base[tag]}+{tag}-{tag_py}-{os_env}_{arch}.whl"
                                    else:
                                        torch_pkg = f'{url}/{tag}/torch-{torch_version_base}+{tag}-{tag_py}-{os_env}_{arch}.whl'
                                        torchaudio_pkg = f'{url}/{tag}/torchaudio-{torch_version_base}+{tag}-{tag_py}-{os_env}_{arch}.whl'
                                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', torch_pkg, torchaudio_pkg])
                                    if device_info['name'] == 'jetson':
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '--no-cache-dir', '--use-pep517', '--no-binary', 'scikit-learn', 'scikit-learn'])
                                    if device_info['name'] == 'cuda':
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', 'deepspeed'])
                                    numpy_version = Version(self.get_package_version('numpy'))
                                    if Version(torch_version) <= Version('2.2.2') and nump_version and numpy_version >= Version('2.0.0'):
                                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', '--use-pep517', 'numpy<2'])
                                    #msg = 'Relaunching app.py...'
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
            return 1
        except InvalidVersion as e:
            error = f'install_device_packages() error: {e}'
            print(error)
            return 1      
        except Exception as e:
            error = f'install_device_packages() error: {e}'
            print(error)
            return 1