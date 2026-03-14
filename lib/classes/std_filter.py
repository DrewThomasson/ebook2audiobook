import os, sys

class StdoutFilter:
    def __init__(self, original):
        self._original = original

    def write(self, msg):
        print('coucoucouc')
        if 'NNPACK' not in msg:
            self._original.write(msg)

    def flush(self):
        self._original.flush()

class StderrFilter:
    def __init__(self, original):
        self._original = original

    def write(self, msg):
        print('ccacacacaacacacaca')
        self._original.write(msg)

    def flush(self):
        self._original.flush()