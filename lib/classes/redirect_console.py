import time
import logging

from queue import Queue, Empty
from typing import Any


class RedirectConsole:
    def __init__(self,log_buffer:Queue,real_output:Any):
        self.log_buffer=log_buffer  # Queue buffer for the log
        self.real_output=real_output  # Real terminal (sys.__stdout__ or sys.__stderr__)
        self.setup_transformers_logger()

    def write(self,message:str)->None:
        # Write to the real terminal
        self.real_output.write(message)
        self.real_output.flush()
        self.log_buffer.put(message)

    def flush(self)->None:
        self.real_output.flush()

    def isatty(self)->bool:
        return self.real_output.isatty()

    def poll_logs(self,stop_event:Any)->Generator[tuple[str,str],None,None]:
        logs=""
        errors=""
        while not stop_event.is_set() or not self.log_buffer.empty():
            try:
                # Read logs from the buffer without blocking
                log=self.log_buffer.get_nowait()
                if "An error occurred" in log:
                    errors+=log  # Capture error messages separately
                logs+=log
            except Empty:
                pass  # No logs in the buffer
            yield logs,errors  # Yield updated logs and errors
            time.sleep(0.1)  # Prevent tight looping

    def setup_transformers_logger(self)->None:
        transformers_logger=logging.getLogger("transformers")
        transformers_logger.setLevel(logging.WARNING)  # Capture warnings and above
        handler=logging.StreamHandler(self)
        handler.setFormatter(logging.Formatter("%(message)s"))  # Simplified format
        transformers_logger.addHandler(handler)