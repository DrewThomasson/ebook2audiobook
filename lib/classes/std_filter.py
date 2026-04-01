import os, sys

class StdoutFilter:
    def __init__(self, original):
        self._original = original

    def __getattr__(self, name):
        return getattr(self._original, name)

    def write(self, msg):
        self._original.write(msg)

    def flush(self):
        self._original.flush()

class StderrFilter:
    def __init__(self, original):
        self._original = original

    def __getattr__(self, name):
        return getattr(self._original, name)

    def write(self, msg):
        self._original.write(msg)

    def flush(self):
        self._original.flush()