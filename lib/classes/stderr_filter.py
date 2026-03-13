import os, sys

class StderrFilter:
    def __init__(self, original):
        self._original = original

    def write(self, msg):
        if 'NNPACK' not in msg:
            self._original.write(msg)

    def flush(self):
        self._original.flush()

sys.stderr = StderrFilter(sys.stderr)