import os, sys, re, ssl, json, glob, time, errno, atexit, shutil, signal, struct, getpass, hashlib, platform, threading, traceback, subprocess, faulthandler, urllib.request, urllib.error

from datetime import datetime, timezone
from importlib import metadata
from typing import Any

class BugReporter:
    packages = [
        'torch', 'torchaudio', 'torchcodec', 'torchcodec-xpu', 'transformers', 'coqui-tts', 'gradio', 'numpy',
        'onnxruntime', 'onnxruntime-gpu', 'onnxruntime-openvino', 'onnxruntime-directml', 'stanza', 'pyannote-audio',
        'piper-tts', 'ptts', 'argostranslate'
    ]
    session_keys = ['script_mode', 'is_gui_process', 'ebook_mode', 'device', 'tts_engine', 'fine_tuned', 'language', 'translate', 'output_format', 'output_channel', 'free_vram_gb']
    redact_keys = ['ebook', 'ebook_src', 'filename_noext', 'final_name', 'audiobook', 'output_dir', 'custom_model', 'voice', 'abs_url', 'abs_api_token']
    # GPU runtime libraries torch / onnxruntime load, listed when installed (their pins drift independently of torch)
    native_re = re.compile(r'^(?:nvidia-(?:cudnn|cublas|cuda-runtime|cuda-nvrtc|nvjitlink)(?:-cu\d+)?|rocm-sdk-core|intel-sycl-rt)$')
    env_keys = ['CUDA_VISIBLE_DEVICES', 'NVIDIA_VISIBLE_DEVICES', 'NVIDIA_DRIVER_CAPABILITIES', 'HIP_VISIBLE_DEVICES', 'ROCR_VISIBLE_DEVICES', 'HSA_OVERRIDE_GFX_VERSION', 'ZE_AFFINITY_MASK', 'ONEAPI_DEVICE_SELECTOR', 'LD_LIBRARY_PATH', 'LD_PRELOAD']
    # GPU stack errors worth a self-test in a fresh process (plain "CUDA out of memory" is not: VRAM state says it all)
    gpu_error_re = re.compile(r'CUDNN_STATUS|CUBLAS_STATUS|CUFFT_|CUSOLVER_STATUS|CUDA error|CUDA driver|cuda runtime error|no kernel image|HIP error|hipError|MIOpen|miopenStatus|UR_RESULT_ERROR|PI_ERROR', re.IGNORECASE)
    # host RAM exhausted: torch's CPU allocator (Windows "not enough memory", Linux "can't allocate memory"), a C++
    # bad_alloc (MSVC words it "bad allocation"). python / numpy MemoryError is matched by type
    host_oom_re = re.compile(r'DefaultCPUAllocator|std::bad_alloc|\bbad allocation\b', re.IGNORECASE)
    dll_error_re = re.compile(r'Error loading "([^"]+?\.(?:dll|pyd))"', re.IGNORECASE)
    pyd_error_re = re.compile(r'DLL load failed while importing (\w+)')
    selftest_timeout = 45
    # exit codes of a child killed by the same Ctrl+C: SIGINT (POSIX, raw and shell style), STATUS_CONTROL_C_EXIT (Windows)
    interrupt_codes = {-2, 130, 0xC000013A, -1073741510}
    # how long a live report waits for a Ctrl+C racing with it (see send())
    grace = 1.0
    # tiny workload run by gpu_selftest() in a fresh interpreter; prints one JSON line, one key per step
    selftest_code = '''
import json, sys
dev = sys.argv[1]
out = {}
def step(name:str, fn)->bool:
    try:
        value = fn()
        out[name] = 'ok' if value is None else value
        return True
    except BaseException as e:
        out[name] = f'FAIL {type(e).__name__}: {str(e).strip()[:300]}'
        return False
def context()->None:
    torch.zeros(1, device=dev).sum().item()
def device()->str:
    if dev == 'cuda':
        free, total = torch.cuda.mem_get_info()
        props = torch.cuda.get_device_properties(torch.cuda.current_device())
        arch = getattr(props, 'gcnArchName', '') if torch.version.hip else f'sm_{props.major}{props.minor}'
        return f'{props.name} {arch}, {free / 1024**3:.2f} of {total / 1024**3:.2f} GB free'
    return torch.xpu.get_device_name() if dev == 'xpu' else 'mps'
def matmul()->None:
    a = torch.randn(256, 256, device=dev)
    (a @ a).sum().item()
def conv1d()->None:
    torch.nn.functional.conv1d(torch.randn(1, 1, 24000, device=dev), torch.randn(1, 1, 64, device=dev)).sum().item()
def conv1d_no_cudnn()->None:
    torch.backends.cudnn.enabled = False
    conv1d()
if step('import', lambda: __import__('torch').__version__):
    import torch
    if step('context', context):
        step('device', device)
        if dev == 'cuda':
            step('cudnn', lambda: torch.backends.cudnn.version())
        step('matmul', matmul)
        if not step('conv1d', conv1d) and dev == 'cuda':
            step('conv1d_no_cudnn', conv1d_no_cudnn)
print(json.dumps(out))
'''
    max_per_run = 10
    max_traceback = 24000
    max_message = 2000
    timeout = 8

    def __init__(self):
        self.url = ''
        self.version = ''
        self.script_mode = ''
        self.app_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
        self.voices_dir = ''
        self.fault_path = ''
        self.fault_file = None
        self.system = None
        self.ctx = None
        self.rules = []
        self.redact = []
        self.sent = set()
        self.selftest = None
        self.interrupted = False
        self.exiting = False
        self.sigint_hook = None
        self.lock = threading.Lock()
        self.selftest_lock = threading.Lock()
        self.sys_hook = sys.excepthook
        self.thread_hook = threading.excepthook

    def install(self, url:str, version:str, script_mode:str, reports_dir:str, voices_dir:str, enabled:bool)->bool:
        url = (url or '').strip()
        if not enabled or not url.startswith('https://'):
            return False
        self.url = url
        self.version = version
        self.script_mode = script_mode
        self.voices_dir = os.path.abspath(voices_dir)
        flags = re.IGNORECASE if sys.platform == 'win32' else 0
        home = os.path.expanduser('~')
        # the app and home folders are matched whole as site-packages prefixes: they may hold spaces (C:\Users\First
        # Last), where the generic part stops, and the start of the folder (a first name) stayed in the report
        prefixes = sorted({v for p in (self.app_root, home) if len(p) >= 4 for v in (p, p.replace('\\', '/'), p.replace('/', '\\'))}, key=len, reverse=True)
        known = ''.join(f'{re.escape(p)}|' for p in prefixes)
        self.rules = [(re.compile(r'(?:' + known + r'(?:[A-Za-z]:)?)[^\s"\'<>|]*?[\\/](?:site|dist)-packages(?=[\\/])', flags), '<site>')]
        for path, label in sorted([(self.app_root, '<e2a>'), (home, '~')], key=lambda p: len(p[0]), reverse=True):
            for variant in {path, path.replace('\\', '/'), path.replace('/', '\\')} if len(path) >= 4 else []:
                self.rules.append((re.compile(re.escape(variant) + r'(?=[\\/\s"\':,)\]]|$)', flags), label))
        try:
            user = getpass.getuser()
        except Exception:
            user = os.path.basename(home)
        # the profile folder's own name too: on Windows it can differ from the account name getuser() returns
        for name in sorted({user, os.path.basename(home)}, key=len, reverse=True):
            if len(name) >= 3 and name.lower() not in ['root', 'user', 'admin', 'app', 'nobody', 'runner']:
                self.rules.append((re.compile(r'(?<![\w])' + re.escape(name) + r'(?![\w])', flags), '<user>'))
        self.rules += [
            (re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b'), '<email>'),
            (re.compile(r'hf_[A-Za-z0-9]{20,}'), '<token>'),
            (re.compile(r'(?i)\b(token|api[_-]?key|secret|password|authorization)\b(["\']?\s*[:=]\s*["\']?)([^\s"\',;]+)'), r'\1\2<redacted>'),
            # not glued to '-', '.' or a word char: a dotted version such as the WSL kernel in
            # Linux-5.15.167.4-microsoft-standard-WSL2 is not an address (a trailing sentence dot is fine)
            (re.compile(r'(?<![\w.-])(?!127\.0\.0\.1\b|0\.0\.0\.0\b)(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?!\.?[\w-])'), '<ip>')
        ]
        sys.excepthook = self.on_uncaught
        threading.excepthook = self.on_thread
        try:
            import psutil
        except Exception:
            psutil = None
        os.makedirs(reports_dir, exist_ok=True)
        for path in glob.glob(os.path.join(reports_dir, 'faulthandler-*.log')):
            try:
                if psutil is not None and psutil.pid_exists(int(os.path.basename(path)[13:-4])):
                    continue
                created = datetime.fromtimestamp(os.path.getmtime(path), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    dump = f.read().strip()
                # faulthandler appends one record per exception it sees, on Windows first-chance ones the process
                # survived too. The last record is what the process died on: Ctrl+C (0xC000013A) is the user quitting.
                # 0xC0000139 (entry point not found) is raised and handled inside LoadLibrary, Python gets an OSError
                # (a torchcodec built for another torch, caught by pyannote)
                records = [r.strip() for r in re.split(r'(?m)^(?=Windows fatal exception:|Fatal Python error:)', dump) if r.strip()]
                if records and '0xc000013a' in records[-1].splitlines()[0].lower():
                    records = []
                records = [r for r in records if '0xc0000139' not in r.splitlines()[0].lower()]
                if not records:
                    os.remove(path)
                    continue
                dump = records[-1]
            except Exception:
                continue
            title = dump.splitlines()[0].strip()
            # one block per thread: faulthandler marks the crashing one 'Current thread' only when it runs Python code
            frame_re = r'File "([^"]+)", line (\d+) in (\S+)'
            blocks = re.split(r'\n\s*\n', dump)
            current = next((b for b in blocks if b.lstrip().startswith('Current thread')), None)
            if current is not None:
                frames = re.findall(frame_re, current)
                sig = [f'{os.path.basename(f)}:{n}' for f, _, n in frames]
                location = f'{os.path.basename(frames[0][0])}:{frames[0][1]} {frames[0][2]}' if frames else None
            else:
                # crash in a native thread (torch/OpenMP/driver worker) that has no Python frame of its own: sign it
                # with what each Python thread was running instead of blaming the first thread listed
                tops = [re.search(frame_re, b) for b in blocks if b.lstrip().startswith('Thread 0x')]
                sig = sorted({f'{os.path.basename(m.group(1))}:{m.group(3)}' for m in tops if m})
                location = 'non-Python thread'
            payload = dict(
                app='ebook2audiobook', version=self.version, kind='native', created=created,
                fingerprint=hashlib.sha1('|'.join([title] + sig).encode('utf-8')).hexdigest()[:16],
                where=None, location=location,
                error_type=title.split(':')[-1].strip(), error_message=title, root_type=None, root_message=None,
                traceback=dump[:self.max_traceback], session={}
            )
            threading.Thread(target=self.send, args=(payload, path), name='e2a-bug-report').start()
        try:
            self.fault_path = os.path.join(reports_dir, f'faulthandler-{os.getpid()}.log')
            self.fault_file = open(self.fault_path, 'w', encoding='utf-8')
            faulthandler.enable(file=self.fault_file, all_threads=True)
            atexit.register(self.on_exit)
        except Exception:
            pass
        # Ctrl+C and a normal quit report nothing: chain the SIGINT handler (the app's KeyboardInterrupt flow is
        # unchanged), and hook the end of the main thread, which runs before threads are joined and atexit handlers
        try:
            prev = signal.getsignal(signal.SIGINT)
            if callable(prev):
                self.sigint_hook = prev
                signal.signal(signal.SIGINT, self.on_sigint)
        except Exception:
            pass
        try:
            getattr(threading, '_register_atexit', atexit.register)(self.on_shutdown)
        except Exception:
            pass
        from lib.lang import legends
        msg = legends['msg_crash_reports_on']
        print(msg)
        return True

    def report(self, where:str|None=None, session:Any=None, exc_info:tuple|None=None, kind:str='exception', wait:bool=False)->None:
        exc_type, exc, tb = exc_info if exc_info else sys.exc_info()
        if not self.url or not isinstance(exc, Exception) or exc_type.__module__ == 'gradio.exceptions' or getattr(exc, '_e2a_reported', False):
            return
        if self.quitting(exc) or self.disk_full(exc) or self.app_control_blocked(exc):
            return
        try:
            exc._e2a_reported = True
        except Exception:
            pass
        try:
            if not session and tb is not None:
                caller = tb.tb_frame.f_locals
                session = caller.get('session') if hasattr(caller.get('session'), 'get') else getattr(caller.get('self'), 'session', None)
            chain, cur = [], exc
            while cur is not None and len(chain) < 8 and all(cur is not c for c in chain):
                chain.append(cur)
                cur = cur.__cause__ or (None if cur.__suppress_context__ else cur.__context__)
            root = chain[-1]
            frames = traceback.extract_tb(tb)
            root_frames = frames if root is exc else traceback.extract_tb(root.__traceback__)
            sig = [exc_type.__qualname__] + [f'{os.path.basename(f.filename)}:{f.name}' for f in frames]
            if root is not exc:
                sig += [type(root).__qualname__] + [f'{os.path.basename(f.filename)}:{f.name}' for f in root_frames]
            fingerprint = hashlib.sha1('|'.join(sig).encode('utf-8')).hexdigest()[:16]
            with self.lock:
                if fingerprint in self.sent or len(self.sent) >= self.max_per_run:
                    return
                self.sent.add(fingerprint)
            info = {}
            if session and hasattr(session, 'get') and session.get('id'):
                info = {k: session.get(k) for k in self.session_keys if session.get(k) is None or isinstance(session.get(k), (str, int, float, bool))}
                voice = session.get('voice')
                voice_path = os.path.abspath(voice) if isinstance(voice, str) else ''
                try:
                    builtin = bool(voice_path) and os.path.commonpath((voice_path, self.voices_dir)) == self.voices_dir
                except ValueError:
                    builtin = False
                info['voice'] = os.path.relpath(voice_path, self.voices_dir) if builtin else '<custom>' if voice not in [None, '', 'None'] else None
                info['custom_model'] = bool(session.get('custom_model'))
                ebook = session.get('ebook') or session.get('ebook_src')
                info['ebook_ext'] = os.path.splitext(ebook)[1].lower() if isinstance(ebook, str) else None
                meta = session.get('metadata') or {}
                with self.lock:
                    for value in [session.get(k) for k in self.redact_keys if not (k == 'voice' and builtin)] + [meta.get('title'), meta.get('creator')]:
                        if isinstance(value, str) and value.strip() not in ['', 'None']:
                            for v in [value, os.path.basename(value), os.path.splitext(os.path.basename(value))[0]]:
                                if len(v) >= 6 and v not in self.redact:
                                    self.redact.append(v)
                    self.redact = sorted(self.redact[-64:], key=len, reverse=True)
            text = ''.join(traceback.format_exception(exc_type, exc, tb))
            if len(text) > self.max_traceback:
                text = f'{text[:self.max_traceback // 2]}\n... [truncated] ...\n{text[-self.max_traceback // 2:]}'
            last = root_frames[-1] if root_frames else None
            payload = dict(
                app='ebook2audiobook', version=self.version, kind=kind, created=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                fingerprint=fingerprint, where=where, location=f'{os.path.basename(last.filename)}:{last.lineno} {last.name}' if last else None,
                error_type=exc_type.__qualname__, error_message=str(exc)[:self.max_message],
                root_type=type(root).__qualname__, root_message=str(root)[:self.max_message],
                traceback=text, session=info
            )
            # read on the crashing thread, before the caller's cleanup frees VRAM; the slow probes run in send()
            try:
                runtime = self.gpu_state(info.get('device'))
            except Exception as e:
                runtime = dict(error=f'{type(e).__name__}: {str(e)[:200]}')
            # here too, not in send(): the caller unloads the engine right after, which stops its workers
            if any(isinstance(e, MemoryError) or self.host_oom_re.search(str(e)) for e in chain):
                runtime['ram'] = self.ram_state()
            if runtime:
                payload['runtime'] = runtime
            if wait:
                self.send(payload)
            else:
                threading.Thread(target=self.send, args=(payload,), name='e2a-bug-report').start()
        except Exception:
            pass
        finally:
            del exc, tb

    def scrub(self, value:Any)->Any:
        if isinstance(value, dict):
            return {k: self.scrub(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.scrub(v) for v in value]
        if not isinstance(value, str):
            return value
        value = self.rules[0][0].sub(self.rules[0][1], value)
        for v in list(self.redact):
            value = value.replace(v, '<private>')
        for pattern, new in self.rules[1:]:
            value = pattern.sub(new, value)
        return value

    def system_info(self)->dict:
        if self.system is None:
            device, packages, ram_gb = {}, {}, None
            try:
                with open(os.path.join(self.app_root, '.device_info.json'), 'r', encoding='utf-8') as f:
                    device = json.load(f)
            except Exception:
                pass
            for name in self.packages:
                try:
                    packages[name] = metadata.version(name)
                except Exception:
                    pass
            try:
                for dist in metadata.distributions():
                    name = re.sub(r'[-_.]+', '-', (dist.metadata['Name'] or '').lower())
                    if self.native_re.match(name):
                        packages[name] = dist.version
            except Exception:
                pass
            try:
                import psutil
                ram_gb = round(psutil.virtual_memory().total / 1024**3, 1)
            except Exception:
                pass
            self.system = dict(
                platform=platform.platform(), machine=platform.machine(), python=platform.python_version(),
                script_mode=self.script_mode, in_docker=os.environ.get('IN_DOCKER') == '1' or os.path.exists('/.dockerenv'),
                cpu_count=os.cpu_count(), ram_gb=ram_gb, device_info=device, gpus=self.gpu_list(),
                env={k: os.environ[k] for k in self.env_keys if os.environ.get(k)}, packages=packages
            )
        return self.system

    def gpu_list(self)->list:
        # the GPUs the OS sees, whatever torch thinks. Windows: name and driver version. Linux: vendor, PCI id and
        # kernel driver (nvidia-smi adds the NVIDIA driver version at crash time)
        gpus = []
        try:
            if sys.platform == 'win32':
                cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', "Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + ' | driver ' + $_.DriverVersion }"]
                out = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=20).stdout
                gpus = [line.strip() for line in out.splitlines() if line.strip()]
            elif sys.platform.startswith('linux'):
                vendors = {'0x10de': 'NVIDIA', '0x1002': 'AMD', '0x8086': 'Intel'}
                for card in sorted(glob.glob('/sys/class/drm/card*')):
                    if not re.fullmatch(r'card\d+', os.path.basename(card)):
                        continue
                    def read(name:str)->str:
                        try:
                            with open(os.path.join(card, 'device', name), 'r') as f:
                                return f.read().strip()
                        except OSError:
                            return '?'
                    vendor = read('vendor')
                    driver = os.path.basename(os.path.realpath(os.path.join(card, 'device', 'driver')))
                    gpus.append(f"{vendors.get(vendor, vendor)} {vendor[2:]}:{read('device')[2:]} | driver {driver}")
        except Exception as e:
            gpus.append(f'{type(e).__name__}: {str(e)[:200]}')
        return gpus[:8]

    def gpu_state(self, device:str|None)->dict:
        # crash-time view of the torch already loaded here. Never imports torch nor creates a GPU context:
        # a torch that cannot import is one of the crashes this has to report
        torch = sys.modules.get('torch')
        state = {}
        if torch is None:
            return state
        def grab(key:str, fn)->None:
            try:
                value = fn()
                if value is not None:
                    state[key] = value
            except Exception as e:
                state[key] = f'{type(e).__name__}: {str(e).strip()[:200]}'
        def gb(n:int)->float:
            return round(n / 1024**3, 2)
        grab('cudnn', lambda: torch.backends.cudnn.version())
        cuda = getattr(torch, 'cuda', None)
        if cuda is not None and cuda.is_initialized():
            def cuda_device()->str:
                props = cuda.get_device_properties(cuda.current_device())
                arch = getattr(props, 'gcnArchName', '') if getattr(torch.version, 'hip', None) else f'sm_{props.major}{props.minor}'
                return f'{props.name} {arch} ({cuda.current_device() + 1} of {cuda.device_count()})'
            grab('device', cuda_device)
            grab('vram_free_total_gb', lambda: [gb(n) for n in cuda.mem_get_info()])
            grab('torch_alloc_reserved_peak_gb', lambda: [gb(cuda.memory_allocated()), gb(cuda.memory_reserved()), gb(cuda.max_memory_allocated())])
        xpu = getattr(torch, 'xpu', None)
        if xpu is not None and getattr(xpu, 'is_initialized', lambda: False)():
            grab('device', lambda: xpu.get_device_name())
            grab('torch_alloc_reserved_peak_gb', lambda: [gb(xpu.memory_allocated()), gb(xpu.memory_reserved()), gb(xpu.max_memory_allocated())])
        if device == 'mps' and getattr(torch, 'mps', None) is not None:
            grab('mps_alloc_driver_gb', lambda: [gb(torch.mps.current_allocated_memory()), gb(torch.mps.driver_allocated_memory())])
        return state

    def ram_state(self)->dict:
        # host RAM at a failed CPU allocation: the system's, the commit limit (Windows refuses an allocation once RAM +
        # pagefile are committed, even with RAM shown free) and e2a's share with its workers (voice conversion server,
        # engine venv workers), to tell a leak in e2a from a machine short of RAM. Other programs are not named
        state = {}
        def gb(n:int)->float:
            return round(n / 1024**3, 2)
        try:
            import psutil
            vm = psutil.virtual_memory()
            state['available_total_gb'] = [gb(vm.available), gb(vm.total)]
            if sys.platform == 'win32':
                import ctypes
                class MemoryStatusEx(ctypes.Structure):
                    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in ('ullTotalPhys', 'ullAvailPhys', 'ullTotalPageFile', 'ullAvailPageFile', 'ullTotalVirtual', 'ullAvailVirtual', 'ullAvailExtendedVirtual')]
                status = MemoryStatusEx()
                status.dwLength = ctypes.sizeof(MemoryStatusEx)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                    state['commit_available_limit_gb'] = [gb(status.ullAvailPageFile), gb(status.ullTotalPageFile)]
            else:
                swap = psutil.swap_memory()
                state['swap_free_total_gb'] = [gb(swap.free), gb(swap.total)]
            def usage(proc:Any)->int:
                mem = proc.memory_info()
                # Windows: private bytes are what the commit limit counts
                return getattr(mem, 'private', 0) or mem.rss
            proc = psutil.Process()
            own = usage(proc)
            workers = []
            for child in proc.children(recursive=True):
                try:
                    script = next((os.path.basename(arg) for arg in child.cmdline()[1:] if arg.endswith('.py')), '')
                    workers.append((usage(child), f'{child.name()} {script}'.strip()))
                except psutil.Error:
                    pass
            workers.sort(reverse=True)
            state['e2a_gb'] = gb(own)
            state['workers_gb'] = [f'{name}: {gb(n)}' for n, name in workers[:8]]
            state['e2a_total_gb'] = gb(own + sum(n for n, _ in workers))
        except Exception as e:
            state['error'] = f'{type(e).__name__}: {str(e)[:200]}'
        return state

    def runtime_info(self, payload:dict)->dict:
        # crash-time diagnostics, gathered off the crashing thread: what a remote machine cannot be asked afterwards
        runtime = payload.pop('runtime', None) or {}
        text = f"{payload.get('error_message') or ''}\n{payload.get('root_message') or ''}"
        smi = self.smi_state()
        if smi:
            runtime['nvidia_smi'] = smi
        if sys.platform == 'win32':
            target = self.dll_target(text, payload.get('traceback') or '')
            if target:
                runtime['dll_probe'] = self.dll_probe(target)
        if self.gpu_error_re.search(text):
            runtime['gpu_selftest'] = self.gpu_selftest(payload)
        return runtime

    def smi_state(self)->dict:
        # every process' VRAM, not only torch's, and the driver version: on NVIDIA the first suspects of a GPU crash
        exe = shutil.which('nvidia-smi')
        if not exe:
            return {}
        def query(arg:str)->list:
            res = subprocess.run([exe, arg, '--format=csv,noheader,nounits'], capture_output=True, text=True, errors='replace', timeout=10)
            return [[p.strip() for p in line.split(',')] for line in res.stdout.strip().splitlines()] if res.returncode == 0 else []
        state = {}
        try:
            fields = '--query-gpu=name,driver_version,memory.used,memory.total,utilization.gpu'
            rows = query(f'{fields},compute_cap') or query(fields)
            state['gpus'] = [f'{r[0]} | driver {r[1]} | {r[2]}/{r[3]} MiB used | {r[4]}% busy' + (f' | cc {r[5]}' if len(r) > 5 else '') for r in rows if len(r) >= 5][:8]
            apps = [r[1] for r in query('--query-compute-apps=pid,used_memory') if len(r) >= 2]
            if apps:
                state['compute_apps'] = f'{len(apps)} process(es), {sum(int(a) for a in apps if a.isdigit())} MiB'
        except Exception as e:
            state['error'] = f'{type(e).__name__}: {str(e)[:200]}'
        return state

    def gpu_selftest(self, payload:dict)->dict|str:
        # the same tiny workload in a fresh interpreter. Passing there: the GPU stack is sound and the crash comes
        # from this process' state (VRAM, a sticky error). Failing there: driver, libraries or install. Runs once
        # per process, later reports reuse the result
        with self.selftest_lock:
            if self.selftest is None:
                device = (payload.get('session') or {}).get('device') or (self.system or {}).get('device_info', {}).get('name') or ''
                dev = 'xpu' if device == 'xpu' else 'mps' if device == 'mps' else 'cuda'
                try:
                    env = dict(os.environ, DISABLE_SITECUSTOMIZE='1')
                    res = subprocess.run([sys.executable, '-I', '-c', self.selftest_code, dev], capture_output=True, text=True, errors='replace', timeout=self.selftest_timeout, env=env)
                    line = next((l for l in reversed(res.stdout.splitlines()) if l.startswith('{')), None)
                    self.selftest = json.loads(line) if line else f'no result (exit {res.returncode}): {res.stderr.strip()[-300:]}'
                except subprocess.TimeoutExpired:
                    self.selftest = f'timeout after {self.selftest_timeout}s'
                except Exception as e:
                    self.selftest = f'{type(e).__name__}: {str(e)[:200]}'
            return self.selftest

    def dll_target(self, text:str, trace:str)->str|None:
        # the DLL / extension Windows failed to load: named by torch's loader ('Error loading "...dll"'), or found
        # next to the module whose import raised 'DLL load failed while importing X'
        m = self.dll_error_re.search(text)
        if m:
            return m.group(1)
        m = self.pyd_error_re.search(text)
        files = re.findall(r'File "([^"]+)", line \d+', trace)
        if m and files:
            hits = glob.glob(os.path.join(os.path.dirname(files[-1]), f'{m.group(1)}*.pyd'))
            return hits[0] if hits else None
        return None

    def dll_probe(self, start:str)->dict:
        # WinError 126 names the file being loaded, not the dependency that is missing: walk the import tables of
        # the package's own DLLs to name it. Files are only read; a dependency not on disk is looked up the way the
        # loader would, as a data file (no code runs, no dependency is followed)
        name = os.path.basename(start)
        if not os.path.isfile(start):
            return dict(dll=name, missing=[f'{name} (the file itself)'])
        # the package's own DLL dirs (torch\lib, onnxruntime\capi...): dependencies found there are walked too
        own = {os.path.normcase(os.path.dirname(start))}
        parts = os.path.normpath(start).split(os.sep)
        idx = next((i for i, p in enumerate(parts) if p.lower() in ['site-packages', 'dist-packages']), None)
        if idx is not None and idx + 2 < len(parts):
            own |= {os.path.normcase(os.path.dirname(p)) for p in glob.glob(os.path.join(os.sep.join(parts[:idx + 2]), '**', '*.dll'), recursive=True)}
        dirs = sorted(own) + [os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32'), os.path.dirname(sys.executable)] + os.environ.get('PATH', '').split(os.pathsep)
        missing, unreadable, seen, queue = [], [], set(), [start]
        while queue and len(seen) < 256:
            path = queue.pop(0)
            try:
                deps = self.pe_imports(path)
            except Exception as e:
                unreadable.append(f'{os.path.basename(path)} ({type(e).__name__}: {str(e)[:120]})')
                continue
            for dep in deps:
                key = dep.lower()
                if key in seen or key.startswith(('api-ms-win-', 'ext-ms-')):
                    continue
                seen.add(key)
                found = next((p for p in (os.path.join(d, dep) for d in dirs if d) if os.path.isfile(p)), None)
                if found is None and not self.dll_loadable(dep):
                    missing.append(f'{dep} (needed by {os.path.basename(path)})')
                elif found is not None and os.path.normcase(os.path.dirname(found)) in own:
                    queue.append(found)
        return dict(dll=name, package_dlls=sum(len(glob.glob(os.path.join(d, '*.dll'))) for d in own), missing=missing or None, unreadable=unreadable or None)

    def dll_loadable(self, dep:str)->bool:
        # LOAD_LIBRARY_AS_DATAFILE | LOAD_LIBRARY_SEARCH_DEFAULT_DIRS: the process' DLL search (os.add_dll_directory
        # dirs included) without running the DLL nor resolving its own imports
        try:
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.c_void_p
            kernel32.LoadLibraryExW.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_uint32]
            kernel32.FreeLibrary.argtypes = [ctypes.c_void_p]
            handle = kernel32.LoadLibraryExW(dep, None, 0x00000002 | 0x00001000)
            if handle:
                kernel32.FreeLibrary(handle)
                return True
        except Exception:
            pass
        return False

    def pe_imports(self, path:str)->list:
        # DLL names in a PE file's import table (delay-loaded imports excluded: they cannot fail a load). Raises on
        # a truncated file, e.g. an install interrupted mid-copy
        with open(path, 'rb') as f:
            size = os.fstat(f.fileno()).st_size
            def read(offset:int, length:int)->bytes:
                f.seek(offset)
                data = f.read(length)
                if len(data) < length:
                    raise ValueError(f'truncated at {size} bytes')
                return data
            pe = struct.unpack('<I', read(0x3C, 4))[0]
            if read(pe, 4) != b'PE\0\0':
                raise ValueError('not a PE file')
            sections, opt_size = struct.unpack('<2xH12xH2x', read(pe + 4, 20))
            opt = pe + 24
            magic = struct.unpack('<H', read(opt, 2))[0]
            rva = struct.unpack('<I', read(opt + (112 if magic == 0x20b else 96) + 8, 4))[0]
            table = [struct.unpack('<8xIIII', read(opt + opt_size + i * 40, 24)) for i in range(sections)]
            end = max((raw + rsize for _, _, rsize, raw in table), default=0)
            if end > size:
                raise ValueError(f'truncated: {size} of {end} bytes')
            if not rva:
                return []
            def offset(addr:int)->int:
                for vsize, va, rsize, raw in table:
                    if va <= addr < va + max(vsize, rsize):
                        return raw + addr - va
                raise ValueError(f'rva {addr:#x} outside sections')
            names, pos = [], offset(rva)
            for _ in range(1024):
                desc = struct.unpack('<5I', read(pos, 20))
                if not any(desc):
                    break
                f.seek(offset(desc[3]))
                names.append(f.read(256).split(b'\0', 1)[0].decode('ascii', 'replace'))
                pos += 20
            return names

    def quitting(self, exc:BaseException)->bool:
        # Ctrl+C or the app quitting: what fails from then on is a side effect (children killed by the same Ctrl+C,
        # threads torn down with the interpreter), not a bug
        if self.interrupted or self.exiting or sys.is_finalizing() or not threading.main_thread().is_alive():
            return True
        # uninstalled while still running: the app keeps going from memory and fails on what was deleted under it
        if not os.path.isfile(os.path.join(self.app_root, 'app.py')):
            return True
        cur, depth = exc, 0
        while cur is not None and depth < 8:
            if isinstance(cur, (KeyboardInterrupt, SystemExit)) or (isinstance(cur, subprocess.CalledProcessError) and cur.returncode in self.interrupt_codes):
                return True
            if self.stdio_gone(cur):
                return True
            cur, depth = cur.__cause__ or cur.__context__, depth + 1
        return False

    def stdio_gone(self, exc:BaseException)->bool:
        # the terminal (or the program reading the output through a pipe) was closed: print() itself raises,
        # BrokenPipeError / EPIPE on POSIX, EINVAL on Windows (ERROR_NO_DATA, the pipe is being closed)
        if not isinstance(exc, OSError) or not (isinstance(exc, BrokenPipeError) or exc.errno in (errno.EPIPE, errno.EINVAL)):
            return False
        frames = traceback.extract_tb(exc.__traceback__)
        line = (frames[-1].line or '').strip() if frames else ''
        return line.startswith('print(') or '.stdout.write(' in line or '.stderr.write(' in line

    # Windows code integrity: an App Control policy (WDAC) or Smart App Control refusing a file, mostly an unsigned one
    app_control_codes = (4551, 4556, 4557, 4558, 4559, 4560)

    def app_control_blocked(self, exc:BaseException)->bool:
        # the user's Windows refusing the file, not a bug. "DLL load failed while importing X: <text>" carries no error
        # code, only Windows' own text for it in the system language: compared with the texts FormatError() gives here
        if sys.platform != 'win32':
            return False
        texts = []
        try:
            import ctypes
            for code in self.app_control_codes:
                text = ctypes.FormatError(code).strip().rstrip('.')
                if len(text) > 15 and '<' not in text:
                    texts.append(text)
        except Exception:
            pass
        cur, depth = exc, 0
        while cur is not None and depth < 8:
            if isinstance(cur, OSError) and getattr(cur, 'winerror', None) in self.app_control_codes:
                return True
            message = str(cur)
            if any(text in message for text in texts):
                return True
            cur, depth = cur.__cause__ or cur.__context__, depth + 1
        return False

    def disk_full(self, exc:BaseException)->bool:
        # a full disk is the user's machine, not a bug: OSError ENOSPC anywhere in the chain
        # (Windows ERROR_DISK_FULL and ERROR_HANDLE_DISK_FULL map to it too)
        cur, depth = exc, 0
        while cur is not None and depth < 8:
            if isinstance(cur, OSError) and cur.errno == errno.ENOSPC:
                return True
            cur, depth = cur.__cause__ or cur.__context__, depth + 1
        return False

    def send(self, payload:dict, path:str|None=None)->None:
        if path is None:
            # a child killed by Ctrl+C can fail a worker thread before the main thread runs the SIGINT handler:
            # give that handler a moment, then drop the report if Ctrl+C came. Reports queued before a normal
            # quit still go out (their threads are joined at exit)
            try:
                time.sleep(self.grace)
            except KeyboardInterrupt:
                return
            if self.interrupted:
                return
        try:
            system = self.system_info()
            # a native crash from an earlier run (path set) has no runtime state left to read: this process is new
            runtime = self.runtime_info(payload) if path is None else {}
            payload['system'] = dict(system, runtime=runtime) if runtime else system
            if path is None and self.interrupted:
                return
            body = json.dumps(self.scrub(payload), ensure_ascii=False).encode('utf-8')
            req = urllib.request.Request(self.url, data=body, method='POST', headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': f"ebook2audiobook/{self.version}"})
            if self.ctx is None:
                try:
                    import certifi
                    self.ctx = ssl.create_default_context(cafile=certifi.where())
                except Exception:
                    self.ctx = ssl.create_default_context()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout, context=self.ctx) as resp:
                    status = resp.status
            except urllib.error.HTTPError as e:
                status = e.code
            if path is not None and 200 <= status < 500 and status not in [408, 429]:
                os.remove(path)
            if 200 <= status < 300:
                from lib.lang import legends
                msg = legends['msg_crash_report_sent'].format(fingerprint=payload['fingerprint'], location=payload.get('location') or '')
                print(msg)
        except Exception:
            pass

    def on_uncaught(self, exc_type:type, exc:BaseException, tb:Any)->None:
        self.sys_hook(exc_type, exc, tb)
        self.report(None, None, (exc_type, exc, tb), 'uncaught', True)

    def on_thread(self, args:Any)->None:
        self.thread_hook(args)
        self.report(f'thread {args.thread.name}' if args.thread else None, None, (args.exc_type, args.exc_value, args.exc_traceback), 'thread')

    def on_sigint(self, signum:int, frame:Any)->None:
        # Ctrl+C means quit: report nothing more, and drop the native crash log so a crash while exiting (CUDA
        # teardown...) is not sent at the next start either. Then the previous handler (KeyboardInterrupt) as before
        self.interrupted = True
        self.on_exit()
        self.sigint_hook(signum, frame)

    def on_shutdown(self)->None:
        # the main thread ended: a normal quit. Same as Ctrl+C for what is raised from now on, but reports already
        # queued are still sent
        self.on_exit()

    def on_exit(self)->None:
        # idempotent: Ctrl+C, end of the main thread and atexit all land here
        self.exiting = True
        try:
            faulthandler.disable()
            if self.fault_file is not None and not self.fault_file.closed:
                self.fault_file.close()
            if self.fault_path and os.path.exists(self.fault_path):
                os.remove(self.fault_path)
        except Exception:
            pass

bug_reporter = BugReporter()
