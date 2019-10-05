#!/usr/bin/env python3

__author__ = "Yasser Janah"
__email___ = "janah.y4ss3r@gmail.com"

try:
    import os
    import sys
    import telnetlib
    import time
except ImportError as err:
    exit(str(err))

class msg(object):
    WHITE  = u"\u001b[38;5;255m"
    RED    = u"\u001b[38;5;196m"
    GREEN  = u"\u001b[38;5;40m"
    BLUE   = u"\u001b[38;5;21m"
    YELLOW = u"\u001b[38;5;220m"
    
    @staticmethod
    def failure(_msg:str, very=False):
        if very is True:
            text = f"{msg.WHITE}[{msg.RED}CRITICAL{msg.WHITE}] {msg.RED}{_msg}{msg.WHITE}"
        else:
            text = f"{msg.WHITE}[{msg.RED}CRITICAL{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def success(_msg:str):
        text = f"{msg.WHITE}[{msg.GREEN}SUCCESS{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def warning(_msg:str):
        text = f"{msg.WHITE}[{msg.YELLOW}WARNING{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def info(_msg:str):
        text = f"{msg.WHITE}[{msg.BLUE}INFO{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

class TelnetSession:
    def __init__(self, _host:str, _port=23):
        self._host = _host
        self._port = _port
        try:
            self._tn = telnetlib.Telnet(self._host, self._port)
            msg.success("Connection etablished !! ")
        except Exception as err:
            exit(msg.failure(err, True))

    def run(self):
        msg.info('starting login .....')
        self._tn.read_until(b"Username: ")
        self._tn.write("root".encode('ascii') + b"\n")
        time.sleep(1)
        self._tn.read_until(b"Password: ")
        msg.info('writing password .....')
        self._tn.write("janah".encode('ascii') + b"\n")
        time.sleep(1)
        self._tn.write(b'exit\n')
        print(self._tn.read_all().decode('ascii'))


TelnetSession('10.0.0.1').run()