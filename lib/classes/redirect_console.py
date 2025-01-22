from queue import Queue, Empty
import time
import logging


class RedirectConsole:
    def __init__(self, log_buffer: Queue, real_output):
        self.log_buffer = log_buffer  # Queue buffer for the log
        self.real_output = real_output  # Real terminal (sys.__stdout__ or sys.__stderr__)

        # Setup for transformers logging
        self.setup_transformers_logger()

    def write(self, message: str):
        # Write to the real terminal
        self.real_output.write(message)
        self.real_output.flush()

        # Write to the log buffer
        self.log_buffer.put(message)

    def flush(self):
        self.real_output.flush()

    def isatty(self) -> bool:
        return self.real_output.isatty()

    def poll_logs(self, stop_event):
        logs = ""
        errors = ""
        while not stop_event.is_set() or not self.log_buffer.empty():
            try:
                # Read logs from the buffer without blocking
                log = self.log_buffer.get_nowait()
                if "An error occurred" in log:
                    errors += log  # Capture error messages separately
                logs += log
            except Empty:
                pass  # No logs in the buffer
            yield logs, errors  # Yield updated logs and errors
            time.sleep(0.1)  # Prevent tight looping

    def setup_transformers_logger(self):
        # Configure the `transformers` logger
        transformers_logger = logging.getLogger("transformers")
        transformers_logger.setLevel(logging.WARNING)  # Capture warnings and above

        # Create a handler that writes to this instance
        handler = logging.StreamHandler(self)
        handler.setFormatter(logging.Formatter("%(message)s"))  # Simplified format
        transformers_logger.addHandler(handler)