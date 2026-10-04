import os, sys, re, ssl, json, glob, atexit, getpass, hashlib, platform, threading, traceback, faulthandler, urllib.request, urllib.error

from datetime import datetime, timezone
from importlib import metadata
from typing import Any

class BugReporter:
    packages = [
        'torch', 'torchaudio', 'torchcodec', 'torchcodec-xpu', 'transformers', 'coqui-tts', 'gradio', 'numpy',
        'onnxruntime', 'onnxruntime-gpu', 'onnxruntime-openvino', 'onnxruntime-directml', 'stanza', 'pyannote-audio',
        'piper-tts', 'argostranslate'
    ]
    session_keys = ['script_mode', 'is_gui_process', 'ebook_mode', 'device', 'tts_engine', 'fine_tuned', 'language', 'translate', 'output_format', 'output_channel', 'free_vram_gb']
    redact_keys = ['ebook', 'ebook_src', 'filename_noext', 'final_name', 'audiobook', 'output_dir', 'custom_model', 'voice', 'abs_url', 'abs_api_token']
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
        self.lock = threading.Lock()
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
        self.rules = [(re.compile(r'(?:[A-Za-z]:)?[^\s"\'<>|]*?[\\/](?:site|dist)-packages(?=[\\/])', flags), '<site>')]
        for path, label in sorted([(self.app_root, '<e2a>'), (home, '~')], key=lambda p: len(p[0]), reverse=True):
            for variant in {path, path.replace('\\', '/'), path.replace('/', '\\')} if len(path) >= 4 else []:
                self.rules.append((re.compile(re.escape(variant) + r'(?=[\\/\s"\':,)\]]|$)', flags), label))
        try:
            user = getpass.getuser()
        except Exception:
            user = os.path.basename(home)
        if len(user) >= 3 and user.lower() not in ['root', 'user', 'admin', 'app', 'nobody', 'runner']:
            self.rules.append((re.compile(r'(?<![\w])' + re.escape(user) + r'(?![\w])', flags), '<user>'))
        self.rules += [
            (re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b'), '<email>'),
            (re.compile(r'hf_[A-Za-z0-9]{20,}'), '<token>'),
            (re.compile(r'(?i)\b(token|api[_-]?key|secret|password|authorization)\b(["\']?\s*[:=]\s*["\']?)([^\s"\',;]+)'), r'\1\2<redacted>'),
            (re.compile(r'\b(?!127\.0\.0\.1\b|0\.0\.0\.0\b)(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b'), '<ip>')
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
                if not dump:
                    os.remove(path)
                    continue
            except Exception:
                continue
            title = dump.splitlines()[0].strip()
            frames = re.findall(r'File "([^"]+)", line (\d+) in (\S+)', dump.split('Current thread', 1)[-1])
            payload = dict(
                app='ebook2audiobook', version=self.version, kind='native', created=created,
                fingerprint=hashlib.sha1('|'.join([title] + [f'{os.path.basename(f)}:{n}' for f, _, n in frames]).encode('utf-8')).hexdigest()[:16],
                where=None, location=f'{os.path.basename(frames[0][0])}:{frames[0][1]} {frames[0][2]}' if frames else None,
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
        from lib.lang import legends
        msg = legends['msg_crash_reports_on']
        print(msg)
        return True

    def report(self, where:str|None=None, session:Any=None, exc_info:tuple|None=None, kind:str='exception', wait:bool=False)->None:
        exc_type, exc, tb = exc_info if exc_info else sys.exc_info()
        if not self.url or not isinstance(exc, Exception) or exc_type.__module__ == 'gradio.exceptions' or getattr(exc, '_e2a_reported', False):
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
                builtin = isinstance(voice, str) and os.path.abspath(voice).startswith(self.voices_dir)
                info['voice'] = os.path.relpath(os.path.abspath(voice), self.voices_dir) if builtin else '<custom>' if voice not in [None, '', 'None'] else None
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
                import psutil
                ram_gb = round(psutil.virtual_memory().total / 1024**3, 1)
            except Exception:
                pass
            self.system = dict(
                platform=platform.platform(), machine=platform.machine(), python=platform.python_version(),
                script_mode=self.script_mode, in_docker=os.environ.get('IN_DOCKER') == '1' or os.path.exists('/.dockerenv'),
                cpu_count=os.cpu_count(), ram_gb=ram_gb, device_info=device, packages=packages
            )
        return self.system

    def send(self, payload:dict, path:str|None=None)->None:
        try:
            payload['system'] = self.system_info()
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

    def on_exit(self)->None:
        try:
            faulthandler.disable()
            self.fault_file.close()
            os.remove(self.fault_path)
        except Exception:
            pass

bug_reporter = BugReporter()
