import os, time, inspect, contextvars

from typing import Any, Callable
from lib.conf import interface_progress_interval

def hf_download(progress_bar:Callable|None, desc:str, **kwargs:Any)->str:
    # hf_hub_download(**kwargs) with its byte progress also sent to gradio's progress_bar (GUI mode, None in headless mode).
    # huggingface_hub draws its bars in the terminal only, and xet transfers report from their own thread, which gradio's
    # progress_bar cannot reach (it finds its event through contextvars): a remote download stayed at 0.0% in the GUI.
    # The terminal bars stay as they were (huggingface_hub's own tqdm, same disable rules), each update re-enters the
    # caller's context and reaches gradio at most every interface_progress_interval seconds, or when the file completes
    from huggingface_hub import hf_hub_download
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
