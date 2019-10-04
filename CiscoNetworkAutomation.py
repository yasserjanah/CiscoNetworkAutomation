#!/usr/bin/env python3

__author__ = "Yasser Janah"
__email___ = "janah.y4ss3r@gmail.com"

try:
    import os
    import sys
    import telnetlib
except ImportError as err:
    exit(str(err))

class msg:
    def __init__(self):
        self.W = "\e[39m"

    def failure(self, _msg):
        pass

    def success(self, _msg):
        pass

    def warning(self, _msg):
        pass

    def info(self, _msg):
        pass

class TelnetSession:
    def __init__(self, _host):
        self._host = _host
        self._tn = telnetlib.Telnet(self._host)

    def run(self):
        self._tn.read_until(b"Username: ")
        self._tn.write("root".encode('ascii') + b"\n")
        self._tn.read_until(b"Password: ")
        self._tn.write("janah".encode('ascii') + b"\n")
        print(self._tn.read_all())


TelnetSession('localhost').run()