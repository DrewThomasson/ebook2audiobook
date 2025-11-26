import os
import sysconfig
import shutil

from lib.conf import *

########## sitecustomize.py
try:
    iu = importlib.import_module("transformers.utils.import_utils")
    site_packages_path = sysconfig.get_paths()['purelib']
    src_pyfile = os.path.join(components_dir, 'sitecustomize.py')
    dst_pyfile = os.path.join(site_packages_path, 'sitecustomize.py')
    if not os.path.exists(dst_pyfile) or os.path.getmtime(dst_pyfile) < os.path.getmtime(src_pyfile):
        shutil.copy2(src_pyfile, dst_pyfile)
except Exception as e:
    pass
##############

import platform
import argparse
import filecmp
import importlib.util
import socket
import subprocess
import sys
import tempfile
import time
import warnings
import re

from typing import Tuple
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

from lib.lang import default_language_code
from lib.models import TTS_ENGINES, default_fine_tuned, default_engine_settings

def check_virtual_env(script_mode:str)->bool:
    current_version=sys.version_info[:2]  # (major, minor)
    search_python_env = str(os.path.basename(sys.prefix))
    if search_python_env == 'python_env' or script_mode == FULL_DOCKER or current_version >= min_python_version and current_version <= max_python_version:
        return True
    error=f'''***********
Wrong launch! ebook2audiobook must run in its own virtual environment!
NOTE: If you are running a Docker so you are probably using an old version of ebook2audiobook.
To solve this issue go to download the new version at https://github.com/DrewThomasson/ebook2audiobook
If the directory python_env does not exist in the ebook2audiobook root directory,
run your command with "./ebook2audiobook.sh" for Linux and Mac or "ebook2audiobook.cmd" for Windows
to install it all automatically.
{install_info}
***********'''
    print(error)
    return False

def check_python_version()->bool:
    current_version = sys.version_info[:2]  # (major, minor)
    if current_version < min_python_version or current_version > max_python_version:
        error = f'''***********
Wrong launch: Your OS Python version is not compatible! (current: {current_version[0]}.{current_version[1]})
In order to install and/or use ebook2audiobook correctly you must delete completly the folder python_env
and run "./ebook2audiobook.sh" for Linux and Mac or "ebook2audiobook.cmd" for Windows.
{install_info}
***********'''
        print(error)
        return False
    else:
        return True

def detect_platform_tag()->str:
    if sys.platform.startswith('win'):
        return 'win'
    if sys.platform == 'darwin':
        return 'macosx'
    if sys.platform.startswith('linux'):
        return 'manylinux'
    return 'unknown'

def detect_arch_tag()->str:
    m=platform.machine().lower()
    if m in ('x86_64','amd64'):
        return m
    if m in ('aarch64','arm64'):
        return m
    return 'unknown'

def detect_gpu()->str:

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
		m = re.search(r'cuda version:\s*([0-9]+\.[0-9]+)', text)
		if m:
			return m.group(1)
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
			if rev_major == 3:
				return '61'
			msg = 'Unrecognized JetPack 6.x version. Falling back to CPU.'
			warn(msg)
		return 'unknown'

	def warn(msg:str)->None:
		print(f'[WARNING] {msg}')

	arch:str = platform.machine().lower()

	# ============================================================
	# CUDA
	# ============================================================
	if has_cmd('nvidia-smi'):
		out = try_cmd('nvidia-smi')
		version_str:str|None = toolkit_version_parse(out)
		cmp = toolkit_version_compare(version_str, cuda_version_range)

		if cmp == -1:
			msg = f'CUDA {version_str} < min {cuda_version_range["min"]}. Please upgrade.'
			warn(msg)
			return 'cpu'
		if cmp == 1:
			msg = f'CUDA {version_str} > max {cuda_version_range["max"]}. Falling back to CPU.'
			warn(msg)
			return 'cpu'
		if cmp == 0:
			devices['CUDA']['found'] = True
			major, minor = version_str.split('.')
			return f'cu{major}{minor}'

		msg = 'No CUDA version found. Falling back to CPU.'
		warn(msg)
		return 'cpu'

	# ============================================================
	# ROCm
	# ============================================================
	if has_cmd('rocminfo') or os.path.exists('/opt/rocm'):
		out = try_cmd('rocminfo')
		version_str = toolkit_version_parse(out)
		cmp = toolkit_version_compare(version_str, rocm_version_range)

		if cmp == -1:
			msg = f'ROCm {version_str} < min {rocm_version_range["min"]}. Please upgrade.'
			warn(msg)
			return 'cpu'
		if cmp == 1:
			msg = f'ROCm {version_str} > max {rocm_version_range["max"]}. Falling back to CPU.'
			warn(msg)
			return 'cpu'
		if cmp == 0:
			devices['ROCM']['found'] = True
			return f'rocm{version_str}'

		msg = 'No ROCm version found. Falling back to CPU.'
		warn(msg)
		return 'cpu'

	# ============================================================
	# APPLE MPS
	# ============================================================
	if sys.platform == 'darwin' and arch in ('arm64', 'aarch64'):
		devices['MPS']['found'] = True
		return 'mps'

	# ============================================================
	# INTEL XPU
	# ============================================================
	if os.path.exists('/dev/dri/renderD128'):
		out = try_cmd('lspci')
		if 'intel' in out:
			oneapi_out:str = try_cmd('sycl-ls') if has_cmd('sycl-ls') else ''
			version_str = toolkit_version_parse(oneapi_out)
			cmp = toolkit_version_compare(version_str, xpu_version_range)

			if cmp == -1 or cmp == 1:
				msg = f'XPU {version_str} out of supported range {xpu_version_range}. Falling back to CPU.'
				warn(msg)
				return 'cpu'

			if cmp == 0 and (has_cmd('sycl-ls') or has_cmd('clinfo')):
				devices['XPU']['found'] = True
				return 'xpu'

			msg = 'Intel GPU detected but oneAPI runtime missing → CPU'
			warn(msg)
			return 'cpu'

	if has_cmd('clinfo'):
		out = try_cmd('clinfo')
		if 'intel' in out:
			return 'xpu'

	# ============================================================
	# JETSON
	# ============================================================
	if arch in ('aarch64','arm64') and (os.path.exists('/etc/nv_tegra_release') or 'tegra' in try_cmd('cat /proc/device-tree/compatible')):
		raw = tegra_version()
		jp_code = jetpack_version(raw)
		if jp_code in ['unsupported', 'unknown']:
			return 'cpu'
		if os.path.exists('/etc/nv_tegra_release'):
			devices['CUDA']['found'] = True
			return f'jetson-{jp_code}'
		if os.path.exists('/proc/device-tree/compatible'):
			out = try_cmd('cat /proc/device-tree/compatible')
			if 'tegra' in out:
				devices['CUDA']['found'] = True
				return f'jetson-{jp_code}'
		out = try_cmd('uname -a')
		if 'tegra' in out:
			msg = 'Unknown Jetson device. Failing back to cpu'
			warn(msg)
			return 'cpu'

	# ============================================================
	# CPU
	# ============================================================
	return 'cpu'

def parse_torch_version(current:str)->str:
    from packaging.version import Version, InvalidVersion
    try:
        parsed = Version(current)
    except InvalidVersion:
        parsed = Version(current.split('+')[0])
    return parsed
    
def recheck_torch()->bool:
    try:
        import torch
        import numpy as np
        from packaging.version import Version, InvalidVersion
        torch_version = getattr(torch, '__version__', False)
        if torch_version:
            torch_version_parsed = parse_torch_version(torch_version)
            backend_specs = {"os": detect_platform_tag(), "arch": detect_arch_tag(), "pyvenv": sys.version_info[:2], "gpu": detect_gpu()}
            print(backend_specs)
            if backend_specs['gpu'] not in ['cpu', 'unknown', 'unsupported']:
                m = re.search(r'\+(.+)$', torch_version)
                current_tag = m.group(1) if m else None
                if current_tag is not None:
                    non_standard_tag = re.fullmatch(r'[0-9a-f]{7,40}', current_tag)
                    if (
                        non_standard_tag is None and current_tag != backend_specs['gpu'] or 
                        non_standard_tag is not None and backend_specs['gpu'] in ['jetson-51', 'jetson-60', 'jetson-61'] and non_standard_tag != torch_mapping[backend_specs['gpu']]['tag']
                       ):
                        try:
                            backend_tag = torch_mapping[backend_specs['gpu']]['tag']
                            backend_os = backend_specs['os']
                            backend_arch = backend_specs['arch']
                            backend_url = torch_mapping[backend_specs['gpu']]['url']
                            if backend_specs['gpu'] == 'jetson-51':
                                torch_pkg = f''
                            elif backend_specs['gpu'] in ['jetson-60', 'jetson-61']:
                                jetson_torch_version = default_jetson60_torch if backend_specs['gpu'] == 'jetson-60' else default_jetson61_torch
                                torch_pkg = f'{backend_url}/v{backend_tag}/pytorch/torch-{jetson_torch_version}-{default_py_tag}-linux_{backend_arch}.whl'                    
                            else:
                                torch_pkg = f'{backend_url}/{backend_tag}/torch/torch-{torch_version_parsed}+{gpu_tag}-{default_py_tag}-{backend_os}_{backend_arch}.whl'
                            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', torch_pkg])
                        except subprocess.CalledProcessError as e:
                            error = f'Failed to install {packages}: {e}'
                            print(error)
                            return False
        numpy_version = Version(np.__version__)
        if torch_version_parsed <= Version('2.2.2') and numpy_version >= Version('2.0.0'):
            try:
                msg = 'torch version needs numpy < 2. downgrading numpy to 1.26.4...'
                print(msg)
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '--use-pep517', 'numpy<2'])
                return True
            except subprocess.CalledProcessError as e:
                error = f'Failed to downgrade to numpy < 2: {e}'
                print(error)
                return False
        else:
            return True
    except ImportError:
        error = f'recheck_torch(): torch not yet installed...'
        print(error)
        return False
    except InvalidVersion:
        error = f'recheck_torch(): Torch or Numpy error Version.'
        print(error)
        return False      
    except Exception as e:
        error = f'recheck_torch() error: {e}'
        print(error)
        return False

def check_and_install_requirements(file_path:str)->bool:
    if not os.path.exists(file_path):
        error = f'Warning: File {file_path} not found. Skipping package check.'
        print(error)
        return False
    try:
        try:
            from packaging.specifiers import SpecifierSet
            from packaging.version import Version, InvalidVersion
            from tqdm import tqdm
            from packaging.markers import Marker
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'packaging', 'tqdm'])
            from packaging.specifiers import SpecifierSet
            from packaging.version import Version, InvalidVersion
            from tqdm import tqdm
            from packaging.markers import Marker
        torch_version = False
        if recheck_torch():
            import torch
            torch_version = torch.__version__            
        cuda_only_packages = ('deepspeed')
        with open(file_path, 'r') as f:
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
            if pkg_name in cuda_only_packages:
                has_cuda_build = False
                if torch_version:
                    has_cuda_build = any(marker in torch_version for marker in cuda_markers)
                if not has_cuda_build:
                    continue
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
            tmp_dir = tempfile.mkdtemp()
            os.environ['TMPDIR'] = tmp_dir
            subprocess.call([sys.executable, '-m', 'pip', 'cache', 'purge'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            with tqdm(total = len(packages), desc = 'Installation 0.00%', bar_format = '{desc}: {n_fmt}/{total_fmt} ', unit = 'step') as t:
                for package in tqdm(missing_packages, desc = 'Installing', unit = 'pkg'):
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '--use-pep517', package])
                        t.update(1)
                    except subprocess.CalledProcessError as e:
                        if package in flexible_packages:
                            continue
                        error = f'Failed to install {package}: {e}'
                        print(error)
                        return False
            msg = '\nAll required packages are installed.'
            print(msg)
        if recheck_torch():
            return True
        return False
    except Exception as e:
        error = f'check_and_install_requirements() error: {e}'
        raise SystemExit(error)
        return False
       
def check_dictionary()->bool:
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

def is_port_in_use(port:int)->bool:
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0',port))==0

def kill_previous_instances(script_name: str):
    current_pid = os.getpid()
    this_script_path = os.path.realpath(script_name)
    import psutil
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
            # unify case and absolute paths for comparison
            joined_cmd = ' '.join(cmdline).lower()
            if this_script_path.lower().endswith(script_name.lower()) and \
               (script_name.lower() in joined_cmd) and \
               proc.info['pid'] != current_pid:
                print(f"[WARN] Found running instance PID={proc.info['pid']} -> killing it.")
                proc.kill()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def main()->None:
    # Argument parser to handle optional parameters with descriptions
    parser = argparse.ArgumentParser(
        description='Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.',
        epilog='''
Example usage:    
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file' --language eng
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.sh
    Headless mode:
    ./ebook2audiobook.sh --headless --ebook '/path/to/file' --language eng
    
Tip: to add of silence (1.4 seconds) into your text just use "###" or "[pause]".
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    options = [
        '--script_mode', '--session', '--share', '--headless', 
        '--ebook', '--ebooks_dir', '--language', '--voice', '--device', '--tts_engine', 
        '--custom_model', '--fine_tuned', '--output_format', '--output_channel',
        '--temperature', '--length_penalty', '--num_beams', '--repetition_penalty', 
        '--top_k', '--top_p', '--speed', '--enable_text_splitting',
        '--text_temp', '--waveform_temp',
        '--output_dir', '--version', '--workflow', '--help'
    ]
    tts_engine_list_keys = [k for k in TTS_ENGINES.keys()]
    tts_engine_list_values = [k for k in TTS_ENGINES.values()]
    all_group = parser.add_argument_group('**** The following options are for all modes', 'Optional')
    all_group.add_argument(options[0], type=str, help=argparse.SUPPRESS)
    parser.add_argument(options[1], type=str, help='''Session to resume the conversion in case of interruption, crash, 
    or reuse of custom models and custom cloning voices.''')
    gui_group = parser.add_argument_group('**** The following option are for gradio/gui mode only', 'Optional')
    gui_group.add_argument(options[2], action='store_true', help='''Enable a public shareable Gradio link.''')
    headless_group = parser.add_argument_group('**** The following options are for --headless mode only')
    headless_group.add_argument(options[3], action='store_true', help='''Run the script in headless mode''')
    headless_group.add_argument(options[4], type=str, help='''Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.''')
    headless_group.add_argument(options[5], type=str, help=f'''Relative or absolute path of the directory containing the files to convert. 
    Cannot be used when --ebook is present.''')
    headless_group.add_argument(options[6], type=str, default=default_language_code, help=f'''Language of the e-book. Default language is set 
    in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py''')
    headless_optional_group = parser.add_argument_group('optional parameters')
    headless_optional_group.add_argument(options[7], type=str, default=None, help='''(Optional) Path to the voice cloning file for TTS engine. 
    Uses the default voice if not present.''')
    headless_optional_group.add_argument(options[8], type=str, default=default_device, choices=list(devices.values()), help=f'''(Optional) Pprocessor unit type for the conversion. 
    Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.''')
    headless_optional_group.add_argument(options[9], type=str, default=None, choices=tts_engine_list_keys+tts_engine_list_values, help=f'''(Optional) Preferred TTS engine (available are: {tts_engine_list_keys+tts_engine_list_values}.
    Default depends on the selected language. The tts engine should be compatible with the chosen language''')
    headless_optional_group.add_argument(options[10], type=str, default=None, help=f'''(Optional) Path to the custom model zip file cntaining mandatory model files. 
    Please refer to ./lib/models.py''')
    headless_optional_group.add_argument(options[11], type=str, default=default_fine_tuned, help='''(Optional) Fine tuned model path. Default is builtin model.''')
    headless_optional_group.add_argument(options[12], type=str, default=default_output_format, help=f'''(Optional) Output audio format. Default is {default_output_format} set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[13], type=str, default=default_output_channel, help=f'''(Optional) Output audio channel. Default is {default_output_channel} set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[14], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'], help=f"""(xtts only, optional) Temperature for the model. 
    Default to config.json model. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[15], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'], help=f"""(xtts only, optional) A length penalty applied to the autoregressive decoder. 
    Default to config.json model. Not applied to custom models.""")
    headless_optional_group.add_argument(options[16], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'], help=f"""(xtts only, optional) Controls how many alternative sequences the model explores. Must be equal or greater than length penalty. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[17], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'], help=f"""(xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[18], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'], help=f"""(xtts only, optional) Top-k sampling. 
    Lower values mean more likely outputs and increased audio generation speed. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[19], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p'], help=f"""(xtts only, optional) Top-p sampling. 
    Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.""")
    headless_optional_group.add_argument(options[20], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'], help=f"""(xtts only, optional) Speed factor for the speech generation. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[21], action='store_true', help=f"""(xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[22], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['text_temp'], help=f"""(bark only, optional) Text Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[23], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'], help=f"""(bark only, optional) Waveform Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[24], type=str, help=f'''(Optional) Path to the output directory. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[25], action='version', version=f'ebook2audiobook version {prog_version}', help='''Show the version of the script and exit''')
    headless_optional_group.add_argument(options[26], action='store_true', help=argparse.SUPPRESS)
    
    for arg in sys.argv:
        if arg.startswith('--') and arg not in options:
            error = f'Error: Unrecognized option "{arg}"'
            print(error)
            sys.exit(1)

    args = vars(parser.parse_args())

    if not 'help' in args:
        if not check_virtual_env(args['script_mode']):
            sys.exit(1)

        if not check_python_version():
            sys.exit(1)

        # Check if the port is already in use to prevent multiple launches
        if not args['headless'] and is_port_in_use(interface_port):
            error = f'Error: Port {interface_port} is already in use. The web interface may already be running.'
            print(error)
            sys.exit(1)

        args['script_mode'] = args['script_mode'] if args['script_mode'] else NATIVE
        args['session'] = 'ba800d22-ee51-11ef-ac34-d4ae52cfd9ce' if args['workflow'] else args['session'] if args['session'] else None
        args['share'] =  args['share'] if args['share'] else False
        args['ebook_list'] = None

        print(f"v{prog_version} {args['script_mode']} mode")

        if args['script_mode'] == NATIVE:
            check_pkg = check_and_install_requirements(requirements_file)
            if check_pkg:
                if not check_dictionary():
                    sys.exit(1)
            else:
                error = 'Some packages could not be installed'
                print(error)
                sys.exit(1)

        import lib.functions as f
        f.context = f.SessionContext() if f.context is None else f.context
        f.context_tracker = f.SessionTracker() if f.context_tracker is None else f.context_tracker
        f.active_sessions = set() if f.active_sessions is None else f.active_sessions
        # Conditions based on the --headless flag
        if args['headless']:
            args['is_gui_process'] = False
            args['chapters_preview'] = False
            args['event'] = ''
            args['audiobooks_dir'] = os.path.abspath(args['output_dir']) if args['output_dir'] else audiobooks_cli_dir
            args['device'] = devices['CUDA'] if args['device'] == devices['CUDA'] else args['device']
            args['tts_engine'] = TTS_ENGINES[args['tts_engine']] if args['tts_engine'] in TTS_ENGINES.keys() else args['tts_engine'] if args['tts_engine'] in TTS_ENGINES.values() else None
            args['output_split'] = default_output_split
            args['output_split_hours'] = default_output_split_hours
            args['xtts_temperature'] = args['temperature']
            args['xtts_length_penalty'] = args['length_penalty']
            args['xtts_num_beams'] = args['num_beams']
            args['xtts_repetition_penalty'] = args['repetition_penalty']
            args['xtts_top_k'] = args['top_k']
            args['xtts_top_p'] = args['top_p']
            args['xtts_speed'] = args['speed']
            args['xtts_enable_text_splitting'] = False
            args['bark_text_temp'] = args['text_temp']
            args['bark_waveform_temp'] = args['waveform_temp']
            engine_setting_keys = {engine: list(settings.keys()) for engine, settings in default_engine_settings.items()}
            valid_model_keys = engine_setting_keys.get(args['tts_engine'], [])
            renamed_args = {}
            for key in valid_model_keys:
                if key in args:
                    renamed_args[f"{args['tts_engine']}_{key}"] = args.pop(key)
            args.update(renamed_args)
            # Condition to stop if both --ebook and --ebooks_dir are provided
            if args['ebook'] and args['ebooks_dir']:
                error = 'Error: You cannot specify both --ebook and --ebooks_dir in headless mode.'
                print(error)
                sys.exit(1)
            # convert in absolute path voice, custom_model if any
            if args['voice']:
                if os.path.exists(args['voice']):
                    args['voice'] = os.path.abspath(args['voice'])
            if args['custom_model']:
                if os.path.exists(args['custom_model']):
                    args['custom_model'] = os.path.abspath(args['custom_model'])
            if not os.path.exists(args['audiobooks_dir']):
                error = 'Error: --output_dir path does not exist.'
                print(error)
                sys.exit(1)                
            if args['ebooks_dir']:
                args['ebooks_dir'] = os.path.abspath(args['ebooks_dir'])
                if not os.path.exists(args['ebooks_dir']):
                    error = f'Error: The provided --ebooks_dir "{args["ebooks_dir"]}" does not exist.'
                    print(error)
                    sys.exit(1)                   
                args['ebook_list'] = []
                for file in os.listdir(args['ebooks_dir']):
                    if any(file.endswith(ext) for ext in ebook_formats):
                        full_path = os.path.abspath(os.path.join(args['ebooks_dir'], file))
                        args['ebook_list'].append(full_path)
                progress_status, passed = f.convert_ebook_batch(args)
                if passed is False:
                    error = f'Conversion failed: {progress_status}'
                    print(error)
                    sys.exit(1)
            elif args['ebook']:
                args['ebook'] = os.path.abspath(args['ebook'])
                if not os.path.exists(args['ebook']):
                    error = f'Error: The provided --ebook "{args["ebook"]}" does not exist.'
                    print(error)
                    sys.exit(1) 
                progress_status, passed = f.convert_ebook(args)
                if passed is False:
                    error = f'Conversion failed: {progress_status}'
                    print(error)
                    sys.exit(1)
            else:
                error = 'Error: In headless mode, you must specify either an ebook file using --ebook or an ebook directory using --ebooks_dir.'
                print(error)
                sys.exit(1)       
        else:
            args['is_gui_process'] = True
            passed_arguments = sys.argv[1:]
            allowed_arguments = {'--share', '--script_mode'}
            passed_args_set = {arg for arg in passed_arguments if arg.startswith('--')}
            if passed_args_set.issubset(allowed_arguments):
                try:
                    from lib.gradio import build_interface
                    app = build_interface(args)
                    if app is not None:
                        app.queue(
                            default_concurrency_limit=interface_concurrency_limit
                        ).launch(
                            debug=bool(int(os.environ.get('GRADIO_DEBUG', '0'))),
                            show_error=debug_mode, favicon_path='./favicon.ico', 
                            server_name=interface_host, 
                            server_port=interface_port, 
                            share= args['share'], 
                            max_file_size=max_upload_size
                        )
                except OSError as e:
                    error = f'Connection error: {e}'
                    f.alert_exception(error, None)
                except socket.error as e:
                    error = f'Socket error: {e}'
                    f.alert_exception(error, None)
                except KeyboardInterrupt:
                    error = 'Server interrupted by user. Shutting down...'
                    f.alert_exception(error, None)
                except Exception as e:
                    error = f'An unexpected error occurred: {e}'
                    f.alert_exception(error, None)
            else:
                error = 'Error: In GUI mode, no option or only --share can be passed'
                print(error)
                sys.exit(1)

if __name__ == '__main__':
    main()
