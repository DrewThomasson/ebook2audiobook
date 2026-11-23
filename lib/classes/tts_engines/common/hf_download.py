import os, time, shutil, inspect, contextvars

from typing import Any, Callable
from lib.classes.bug_reporter import bug_reporter
from lib.conf import interface_progress_interval, tts_dir
from lib.lang import legends

_hf_transfer = {'checked': False}

def _disable_xet()->bool:
    # hf_transfer / xetcluster: the accelerated transfer backends of huggingface_hub, both Rust workers whose failure is
    # reported as an opaque error raised out of hf_hub_download ("file reconstruction error: Internal Writer Error:
    # Background writer channel closed" and friends): a worker thread dies on a flaky connection, low RAM, or an
    # interrupted session, and the whole model download fails although plain HTTP would have gone through. They are
    # process-wide env switches read by huggingface_hub when it imports them, so setting them before the very first
    # download makes every later one take the robust plain path. Returns True when this call turned one off (the failed
    # download is retried right away without them); the check runs once per process
    disabled = False
    for var in ('HF_HUB_ENABLE_HF_TRANSFER', 'HF_XET_DISABLE'):
        if not _hf_transfer['checked'] and os.environ.get(var, '').lower() not in ('1', 'true', 'yes'):
            os.environ[var] = '1'
            disabled = True
    return disabled

def _retryable(e:Exception)->bool:
    # a transfer-backend or connection failure worth retrying over plain HTTP; a local problem (no disk space left,
    # permissions) is not: the message tells "System error."/"No space left", or ENOSPC/EACCES/EPERM surfaces as OSError
    try:
        import httpx
        if isinstance(e, httpx.TransportError):
            return True
    except Exception:
        pass
    if isinstance(e, OSError) and e.errno in (getattr(os, 'ENOSPC', 28), getattr(os, 'EACCES', 13), getattr(os, 'EPERM', 1)):
        return False
    text = str(e).lower()
    return any(m in text for m in ('writer', 'reconstruction', 'hf_transfer', 'xet', 'channel closed'))

def hf_download(progress_bar:Callable|None, desc:str, **kwargs:Any)->str:
    # hf_hub_download(**kwargs) with its byte progress also sent to gradio's progress_bar (GUI mode, None in headless
    # mode), and a retry of the failed downloads: the accelerated backends (hf_transfer, xet) die with opaque errors on
    # flaky connections or low-RAM machines (bug d707c3fe0b667831: piper's voice conversion stopped because the GGUF
    # download crashed inside xet's background writer), so a failure turns them off and tries again over plain HTTP
    # while there is room left on the download disk (same guard as audio_save()'s full-disk handling)
    from huggingface_hub import hf_hub_download
    target = kwargs.get('local_dir') or kwargs.get('cache_dir') or tts_dir
    for attempt in range(4):
        try:
            return _hf_download_once(hf_hub_download, progress_bar, desc, **kwargs)
        except Exception as e:
            # HF_HUB_OFFLINE set in the user's environment (e2a never sets it) and the file not on disk yet: huggingface_hub
            # says to check the connection, which sends the user the wrong way (bug b14b3fb643d63ae6: the seed_vc GGUF of
            # piper's voice conversion). No retry, the variable and where the file is expected instead
            if bug_reporter.hf_offline(e):
                error = legends['error_hf_offline'].format(file=os.path.basename(str(kwargs.get('filename'))), dir=target)
                raise RuntimeError(error) from e
            free = 0
            probe = target
            while free == 0 and probe:
                if os.path.isdir(probe):
                    free = shutil.disk_usage(probe).free
                parent = os.path.dirname(probe)
                probe = parent if parent != probe else None
            if attempt > 2 or free < 100 * 1024 ** 2 or not _retryable(e):
                raise
            if _disable_xet():
                print(f'hf_download({os.path.basename(str(kwargs.get("filename")))}): {e}\nRetrying without the accelerated transfer (hf_transfer/xet)…')
            else:
                delay = 2 ** attempt
                print(f'hf_download({os.path.basename(str(kwargs.get("filename")))}): {e}\nConnection issue: retrying in {delay}s…')
                time.sleep(delay)

def _hf_download_once(hf_hub_download:Callable, progress_bar:Callable|None, desc:str, **kwargs:Any)->str:
    # huggingface_hub draws its bars in the terminal only, and xet transfers report from their own thread, which gradio's
    # progress_bar cannot reach (it finds its event through contextvars): a remote download stayed at 0.0% in the GUI.
    # The terminal bars stay as they were (huggingface_hub's own tqdm, same disable rules), each update re-enters the
    # caller's context and reaches gradio at most every interface_progress_interval seconds, or when the file completes
    if progress_bar is None or 'tqdm_class' not in inspect.signature(hf_hub_download).parameters:
        # headless mode, or a huggingface_hub too old to take a tqdm_class
        return hf_hub_download(**kwargs)
    from huggingface_hub.utils import tqdm as hf_tqdm
    caller_context = contextvars.copy_context()
    filename = os.path.basename(kwargs.get('filename') or '')
    state = {'bars': [], 'shown': 0.0, 'pushed': 0.0}

    def _push(value:float, text:str)->None:
        now = time.monotonic()
        if value < 1.0 and now - state['pushed'] < interface_progress_interval:
            return
        state['pushed'] = now
        try:
            caller_context.copy().run(progress_bar, value, desc=text)
        except Exception:
            # a lost GUI update must never break the download
            pass

    class _GuiTqdm(hf_tqdm):
        # huggingface_hub download bars: drawn in the terminal as usual, byte progress also forwarded to gradio
        def __init__(self, *args:Any, **kwargs:Any)->None:
            super().__init__(*args, **kwargs)
            # own byte count: a disabled bar (no TTY, HF_HUB_DISABLE_PROGRESS_BARS) sets no unit and drops its updates
            # (a flag, not "self in state['bars']": tqdm compares bars by their position)
            self.gui_n = self.n or 0
            self.gui_bytes = kwargs.get('unit') == 'B'
            if self.gui_bytes:
                state['bars'].append(self)

        def update(self, n:float|None=1)->bool|None:
            shown = super().update(n)
            if self.gui_bytes:
                self.gui_n += n or 0
                # the file size: http bar, or xet reconstruction bar. xet's transfer bar is seeded with the same size
                # but grows past the network bytes it received, so the smallest known total is the file size
                totals = [b.total for b in state['bars'] if b.total]
                if totals:
                    total = min(totals)
                    # xet counts network bytes (transfer) and bytes written (reconstruction): the furthest one, never stepping back
                    done = min(max(b.gui_n for b in state['bars']), total)
                    state['shown'] = max(state['shown'], done / total)
                    _push(state['shown'], f'{desc} ({filename} {hf_tqdm.format_sizeof(done)}B / {hf_tqdm.format_sizeof(total)}B)')
            return shown

    path = hf_hub_download(tqdm_class=_GuiTqdm, **kwargs)
    if state['bars']:
        _push(1.0, f'{desc} ({filename})')
    return path
