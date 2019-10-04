#!/usr/bin/env python3

try:
    import os
    import sys
except ImportError as err:
    exit(str(err))

class msg:
    def __init__(self, _msg):
        self._img = _msg

    def failure(self):
        pass

    def success(self):
        pass

    def warning(self):
        pass

    def info(self):
        pass