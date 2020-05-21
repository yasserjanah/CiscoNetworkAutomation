#!/usr/bin/env python3

__author__ = "Yasser Janah"
__email___ = "janah.y4ss3r@gmail.com"
___desc___ = "Network Automation Script for managing Cisco Routers & Switches"
__created__ = "05/10/2019"

try:
    import os
    import sys
    import telnetlib
    import paramiko
    import netmiko
    import json
    import time
    import argparse
    import readline
    import glob
    import socket
    import base64
    import datetime
    import concurrent.futures
    import termtables as tt
    from peewee import *
    from pathlib import Path
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.validation import Validator, ValidationError
    from prompt_toolkit.formatted_text import HTML, ANSI
    from prompt_toolkit.styles import Style
except ImportError as err:
    exit(str(err))

db = SqliteDatabase('devices/devices.db')
if not os.path.exists('devices'):
    os.mkdir('devices')
if not os.path.exists('reports'):
    os.mkdir('reports')


class Routers(Model):
    hostname = CharField()
    device_type = CharField()
    host = CharField()
    priv_pass = CharField()
    telnet = CharField()
    telnet_username = CharField()
    telnet_password = CharField()
    telnet_port = CharField()
    ssh = CharField()
    ssh_use_keys = CharField()
    ssh_keys = CharField()
    ssh_username = CharField()
    ssh_password = CharField()
    ssh_port = CharField()

    class Meta:
        database = db


class Switches(Model):
    hostname = CharField()
    device_type = CharField()
    host = CharField()
    priv_pass = CharField()
    telnet = CharField()
    telnet_username = CharField()
    telnet_password = CharField()
    telnet_port = CharField()
    ssh = CharField()
    ssh_use_keys = CharField()
    ssh_keys = CharField()
    ssh_username = CharField()
    ssh_password = CharField()
    ssh_port = CharField()

    class Meta:
        database = db


class Others(Model):
    hostname = CharField()
    device_type = CharField()
    host = CharField()
    priv_pass = CharField()
    telnet = CharField()
    telnet_username = CharField()
    telnet_password = CharField()
    telnet_port = CharField()
    ssh = CharField()
    ssh_use_keys = CharField()
    ssh_keys = CharField()
    ssh_username = CharField()
    ssh_password = CharField()
    ssh_port = CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([Routers, Switches, Others], safe=True)


class msg(object):
    WHITE = u"\u001b[38;5;255m"
    BLACK = u"\u001b[38;5;0m"
    RED = u"\u001b[38;5;196m"
    GREEN = u"\u001b[38;5;40m"
    BLUE = u"\u001b[38;5;21m"
    YELLOW = u"\u001b[38;5;220m"
    MAG = u"\u001b[38;5;125m"
    BLINK = "\033[6m"
    UNDERLINE = "\033[4m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def failure(_msg: str, very=False, tab=None):
        if tab is not None:
            text = f"\t"
        else:
            text = f""
        if very is True:
            text += f"{msg.WHITE}[{msg.RED}CRITICAL{msg.WHITE}] {msg.RED}{_msg}{msg.WHITE}"
        else:
            text += f"{msg.WHITE}[{msg.RED}CRITICAL{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def success(_msg: str, very=False, tab=None):
        if tab is not None:
            text = f"\t"
        else:
            text = f""
        if very is True:
            text += f"{msg.WHITE}[{msg.GREEN}SUCCESS{msg.WHITE}] {msg.GREEN}{_msg}{msg.WHITE}"
        else:
            text += f"{msg.WHITE}[{msg.GREEN}SUUCESS{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def warning(_msg: str, very=False, tab=None):
        if tab is not None:
            text = f"\t"
        else:
            text = f""
        if very is True:
            text += f"{msg.WHITE}[{msg.YELLOW}WARNING{msg.WHITE}] {msg.YELLOW}{_msg}{msg.WHITE}"
        else:
            text += f"{msg.WHITE}[{msg.YELLOW}WARNING{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def info(_msg: str, very=False, tab=None):
        if tab is not None:
            text = f"\t"
        else:
            text = f""
        if very is True:
            text += f"{msg.WHITE}[{msg.BLUE}INFO{msg.WHITE}] {msg.BLUE}{_msg}{msg.WHITE}"
        else:
            text += f"{msg.WHITE}[{msg.BLUE}INFO{msg.WHITE}] {_msg}{msg.WHITE}"
        print(text)

    @staticmethod
    def nodata(_msg: str, very=False, tab=None):
        if tab is not None:
            text = f"\t"
        else:
            text = f""
        if very is True:
            text += f"{msg.RED}[+] {msg.RED}{_msg}{msg.WHITE}"
        else:
            text += f"{msg.RED}[+] {msg.WHITE}{_msg}{msg.WHITE}"
        print(text)


class TelnetSession:
    def __init__(self, _host: str, _user: str, _pass: str, _port: str, _priv:str, cmd: list):
        self._host = _host
        self._user = _user
        self._pass = _pass
        self._port = _port
        self._priv = _priv
        self._cmd = cmd
        self._r_name = 'reports/'+_host+'_' + \
            datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_')+".txt"
        self.saved = open(self._r_name, mode='w')

        try:
            self._tn = telnetlib.Telnet(self._host, self._port)
            msg.success(f'Connection established on {msg.GREEN}{self._host}{msg.RESET} !!')
            msg.info(
                f"configuration started on {msg.GREEN}{self._host}{msg.RESET}.")
        except Exception as err:
            msg.failure(err, True)

    def run(self):
        msg.info('starting login ...')
        self._tn.read_until(b"Username: ")
        self._tn.write(self._user.encode('ascii') + b"\n")
        time.sleep(1)
        self._tn.read_until(b"Password: ")
        self._tn.write(self._pass.encode('ascii') + b"\n")
        time.sleep(1)
        check_en = self._tn.read_very_eager()
        if (check_en == b'\r\n% Login invalid\r\n\r\nUsername: ') or (check_en == b''):
            msg.failure(f"Login Invalid ", very=True)
        if check_en == b'\r\nR1>':
            msg.success("Login Success.")
            if self._priv == "-":
                msg.failure('Password for Privileged mode detected , but no password was set.', very=True)
            else:
                msg.info('Password for Privileged mode detected')
                self._tn.write(b'enable\n')
                time.sleep(1)
                self._tn.write(self._priv.encode('ascii') + b"\n")
                time.sleep(1)
                check_go = self._tn.read_very_eager()
                if  check_go == b'enable\r\nPassword: \r\nR1#':
                    self._tn.write("conf t".encode('ascii') + b"\n")
                    msg.success('Privileged mode password is valid')
                    time.sleep(1)
                    if type(self._cmd) == str:
                        self._tn.write(self._cmd.encode('ascii') + b'\n')
                    else:
                        for c in self._cmd:
                            self._tn.write(c.encode('ascii') + b'\n')
                        #print(self._tn.read_all().decode('ascii'))
                    time.sleep(1)
                    final_r = self._tn.read_very_eager()
                    self.saved.write(final_r.decode())
                    msg.success(f"configuration ended on {msg.GREEN}{self._host}{msg.RESET} with successfully, rapport saved in {msg.RED}'{msg.YELLOW}{self._r_name}{msg.RED}'.")
                    self.saved.close()
                else:
                    msg.failure('Privileged mode password is not valid, please make sure you are set the correct one.',vary=True)



class SSHSession:
    def __init__(self, _host: str, _user: str, _pass: str, _port: str, keys: str, _priv:str, cmd: list):
        self.et = False
        self._r_name = 'reports/'+_host+'_' + \
            datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_')+".txt"
        self.saved = open(self._r_name, mode='w')
        self._host = _host
        self._user = _user
        self._pass = _pass
        self._port = _port
        self._keys = keys if keys != '' else ''
        self._cmd = cmd
        self._priv = _priv
        self.status_success = False
        try:
            self.conn_setup = paramiko.SSHClient()
            self.conn_setup.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            if self._keys == '':
                self.conn_setup.connect(self._host, port=self._port, username=self._user,
                                        password=self._pass, look_for_keys=False, allow_agent=False)
            else:
                self.conn_setup.connect(self._host, port=self._port, username=self._user,
                                        key_filename=self._keys, look_for_keys=False, allow_agent=False)
            self.connection = self.conn_setup
            self.et = True
            msg.success(f'Connection established on {msg.GREEN}{self._host}{msg.RESET} !!')
            msg.info(
                f"configuration started on {msg.GREEN}{self._host}{msg.RESET}.")
        except Exception as err:
            msg.failure(str(err), True)

    def run(self):
        if self.et == False:
            self.saved.close()
            return None
        
        if self.et == True:
            if type(self._cmd) == str:
                c = self._cmd
                stdin, stdout, stderr = self.connection.exec_command(c)
                if len(stderr.readlines()) == 0:
                    for line in stdout.readlines():
                        # print(line.strip('\n'))
                        self.saved.write(line)
                    self.status_success = True
                if len(stdout.readlines()) == 0:
                    for line in stderr.readlines():
                        # print(line.strip('\n'))
                        self.saved.write(line)
            else:
                for c in self._cmd:
                    stdin, stdout, stderr = self.connection.exec_command(c)
                    if len(stderr.readlines()) == 0:
                        for line in stdout.readlines():
                            #print(line.strip('\n'))
                            self.saved.write(line)
                        self.status_success = True
                    if len(stdout.readlines()) == 0:
                        for line in stderr.readlines():
                            #print(line.strip('\n'))
                            self.saved.write(line)
        if self.status_success != False:
            msg.success(
                f"configuration ended on {msg.GREEN}{self._host}{msg.RESET} with successfully, rapport saved in {msg.RED}'{msg.YELLOW}{self._r_name}{msg.RED}'.")
        else:
            msg.failure(
                f"configuration ended on {msg.YELLOW}{self._host}{msg.RESET} with some errors, rapport saved in {msg.RED}'{msg.YELLOW}{self._r_name}{msg.RED}'.", very=True)
        self.saved.write("\n")
        self.saved.close()


def isInSupportedTypes(text):
    if text in ['1', '2', '3']:
        return True
    return False


def isYesOrNo(text):
    if text.lower() in ['yes', 'no']:
        return True
    return False


def isNotEmpty(text):
    if text in ['', ' ']:
        return False
    return True


def isNumber(text):
    if text in ['', ' ']:
        return False
    else:
        try:
            int(text)
            return True
        except ValueError:
            return False


class Devices(object):
    """
    Controling saved Devices [ don't worry the programe do this automaticaly (^_^) ]

    [Syntax]
        e.g =>  {
                    'hostname'   : 'Router1',
                    'device_type': 'cisco_ios', # define as a cisco OS
                    'host'       : 'cisco_router.company.local', # e.g 192.168.1.1
                    'telnet':    : true
                    'telnet_username'   : 'router_telnet_user',
                    'telnet_password'   : 'RouterTelnetPassword$$',
                    'telnet_port'       :  23,
                    'ssh': true,
                    'ssh_username' : 'router_ssh_user',
                    'ssh_password' : 'RouterSshPassword$$',
                    'ssh_port'     :  22,
                    'ssh_use_keys' :  False,
                    'ssh_keys'     : '/home/user/.ssh/id_pub'
                }
    """

    def __init__(self):
        self._devicesDir = "devices/"
        self._key = '$KEY$CNAG00DKeyForEncryption&Decryption'
        self.style = Style.from_dict({
            'completion-menu.completion': 'bg:#9e0000 #ffffff',
            'completion-menu.completion.current': 'bg:#ffffff #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',
            'green': '#16ad02 bold',
            'white': '#ffffff bold',
            'red': '#bd0202 bold',
            'blue': '#000fe0 bold',
            'yellow': '#f2cf0a bold',
        })

    def _InputWithCompletion(self, question: str, words: list, _validator=None, password=False, critical=False):
        if critical != False:
            asked = "<white>[<red>+</red>]</white><white> {0} : </white>".format(
                question)
        else:
            asked = "<white>[<green>+</green>]</white><white> {0} : </white>".format(
                question)
        text = prompt(HTML(asked), completer=WordCompleter(words, ignore_case=True), complete_while_typing=True,
                      validator=_validator, mouse_support=True, is_password=password, style=self.style)
        return text

    def _addDevices(self, dtype=None):
        if dtype is None:
            msg.info("add new device")
            print(f"\t{msg.RED}1{msg.WHITE}) - {msg.BLUE}Router ")
            print(f"\t{msg.RED}2{msg.WHITE}) - {msg.BLUE}Switch ")
            print(f"\t{msg.RED}3{msg.WHITE}) - {msg.BLUE}Others ")
            validator = Validator.from_callable(isInSupportedTypes, error_message=(
                'please choice : 1) Routers - 2) Switches - 3) Others'), move_cursor_to_end=True)
            d_type = self._InputWithCompletion(question="Choice Device Type", words=[
                                               '1', '2', '3'], _validator=validator)
        validator = Validator.from_callable(isNotEmpty, error_message=(
            'please enter valid hostname'), move_cursor_to_end=True)
        if dtype is None:
            dtype = int(d_type)
        if dtype == 1:
            hostname = self._InputWithCompletion(
                question="Hostname (e.g Router1 )", words=[], _validator=validator)
        elif dtype == 2:
            hostname = self._InputWithCompletion(
                question="Hostname (e.g Switch1 )", words=[], _validator=validator)
        else:
            hostname = self._InputWithCompletion(
                question="Hostname (e.g Device1 )", words=[], _validator=validator)
        device_type = 'cisco_ios'
        validator = Validator.from_callable(isNotEmpty, error_message=(
            'please enter valid IP or domain name of Cisco equipment'), move_cursor_to_end=True)
        host = self._InputWithCompletion(
            question="IP (e.g 192.168.1.1 or cisco1.company.local)", words=[], _validator=validator)
        priv_pass = self._InputWithCompletion(
            question="if you set password for privileged mode enter it", words=[])
        validator = Validator.from_callable(isYesOrNo, error_message=(
            'please choice yes or no'), move_cursor_to_end=True)
        telnet = self._InputWithCompletion(
            question="Use Telnet [Yes/no]", words=['yes', 'no'], _validator=validator)
        if telnet.lower() in ['yes']:
            telnet = True
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet username'), move_cursor_to_end=True)
            telnet_user = self._InputWithCompletion(
                question="Telnet username", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet password'), move_cursor_to_end=True)
            telnet_pass = self._InputWithCompletion(
                question="Telnet password", words=[], _validator=validator)
            validator = Validator.from_callable(isNumber, error_message=(
                'please enter telnet port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            telnet_port = self._InputWithCompletion(
                question="Telnet port (default:23)", words=['23'], _validator=validator)
        else:
            telnet = False
            msg.warning(
                "you can't connect to this cisco equipment using telnet")
        validator = Validator.from_callable(isYesOrNo, error_message=(
            'please choice yes or no'), move_cursor_to_end=True)
        ssh = self._InputWithCompletion(
            question="Use ssh [Yes/no]", words=['yes', 'no'], _validator=validator)
        if ssh.lower() in ['yes']:
            ssh = True
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter ssh username'), move_cursor_to_end=True)
            ssh_user = self._InputWithCompletion(
                question="SSH username", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet password'), move_cursor_to_end=True)
            ssh_pass = self._InputWithCompletion(
                question="SSH password", words=[], _validator=validator)
            validator = Validator.from_callable(isNumber, error_message=(
                'please enter SSH port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            ssh_port = self._InputWithCompletion(question="SSH port (default:22)", words=[
                                                 '22'], _validator=validator)
            validator = Validator.from_callable(isYesOrNo, error_message=(
                'please choice yes or no'), move_cursor_to_end=True)
            ssh_use_keys = self._InputWithCompletion(
                question="Use ssh keys (recommended) [Yes/no]", words=['yes', 'no'], _validator=validator)
            if ssh_use_keys.lower() in ['yes']:
                ssh_use_keys = True
                validator = Validator.from_callable(isNotEmpty, error_message=(
                    'please enter SSH Keys path'), move_cursor_to_end=True)
                ssh_keys = self._InputWithCompletion(question="Keys Path", words=[str(
                    Path.home())+'/', str(os.getcwd())], _validator=validator)
            else:
                ssh_use_keys = False
        else:
            ssh = False
            msg.warning("you can't connect to this cisco equipment using SSH")
        if (ssh is False) and (telnet is False):
            msg.failure(
                "you can't connect to this device , you don't choice any method of connection ", very=True)
        hostname = hostname if (hostname != "") else "-"
        priv_pass = priv_pass if (priv_pass != "") else "-"
        device_type = device_type
        host = host if (host != "") else "-"
        if telnet is False:
            telnet_user = '-'
            telnet_pass = '-'
            telnet_port = 23
        else:
            telnet_user = telnet_user
            telnet_pass = self.encrypt(telnet_pass)
            telnet_port = telnet_port
        if ssh is False:
            ssh_use_keys = False
            ssh_keys = '-'
            ssh_user = '-'
            ssh_pass = '-'
            ssh_port = 22
        else:
            ssh_use_keys = ssh_use_keys
            if ssh_use_keys is False:
                ssh_keys = '-'
            else:
                ssh_keys = ssh_keys
            ssh_user = ssh_user
            ssh_pass = self.encrypt(ssh_pass)
            ssh_port = ssh_port if ssh_port != "" else 22
        d_type = int(dtype) if dtype is not None else int(d_type)
        if d_type == 1:
            Routers.create(hostname=hostname, device_type=device_type, host=host, priv_pass=priv_pass,
                           telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                           telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                           ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        elif d_type == 2:
            Switches.create(hostname=hostname, device_type=device_type, host=host, priv_pass=priv_pass,
                            telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                            telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                            ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        else:
            Others.create(hostname=hostname, device_type=device_type, host=host, priv_pass=priv_pass,
                          telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                          telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                          ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        db.close()
        msg.success('Device added successefly')

    def _listDevices(self, dtype=None):
        HEADERS = ['ID', 'CATEGORY', 'HOSTNAME', 'DEVICE_TYPE', 'HOST', 'TELNET',
                   'SSH', 'SSH_USE_KEYS', 'SSH_KEYS']
        if dtype == 1:
            DATA = []
            routers_data = Routers.select().dicts()
            self.sort_data(DATA, [i for i in routers_data], cat="routers")
            if DATA == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Routers{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no routers data {msg.YELLOW}found.\n", tab=True)
                return False
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Routers{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
                print(' ')
        elif dtype == 2:
            DATA = []
            switches_data = Switches.select().dicts()
            self.sort_data(DATA, [i for i in switches_data], cat="switches")
            if DATA == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Switches{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no switches data {msg.YELLOW}found.\n", tab=True)
                return False
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Switches{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
                print(' ')
        elif dtype == 3:
            DATA = []
            others_data = Others.select().dicts()
            self.sort_data(DATA, [i for i in others_data], cat="others")
            if DATA == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Others{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no others devices data {msg.YELLOW}found.\n", tab=True)
                return False
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Others{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
                print(' ')
        else:
            DATA_R = []
            DATA_S = []
            DATA_O = []
            routers_data = Routers.select().dicts()
            switches_data = Switches.select().dicts()
            others_data = Others.select().dicts()
            self.sort_data(DATA_R, [i for i in routers_data], cat="routers")
            self.sort_data(DATA_S, [i for i in switches_data], cat="switches")
            self.sort_data(DATA_O, [i for i in others_data], cat="others")
            if DATA_R == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Routers{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no routers data {msg.YELLOW}found.\n", tab=True)
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Routers{msg.RESET}:")
                table_r = tt.to_string(DATA_R, header=HEADERS, padding=(0, 1))
                print(table_r)
                print(' ')
            if DATA_S == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Switches{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no switches data {msg.YELLOW}found.\n", tab=True)
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Switches{msg.RESET}:")
                table_s = tt.to_string(DATA_S, header=HEADERS, padding=(0, 1))
                print(table_s)
                print(' ')
            if DATA_O == []:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Others{msg.RESET}:\n")
                msg.nodata(
                    f"{msg.BOLD}no others devices data {msg.YELLOW}found.\n", tab=True)
            else:
                msg.info(
                    f"{msg.UNDERLINE}List{msg.RESET} {msg.UNDERLINE}of{msg.RESET} {msg.UNDERLINE}Others{msg.RESET}:")
                table_o = tt.to_string(DATA_O, header=HEADERS, padding=(0, 1))
                print(table_o)
                print(' ')

    def sort_data(self, DATA: list, d_: list, cat=None):
        for row in d_:
            ID = row['id']
            CATEGORY = cat
            HOSTNAME = row['hostname']
            DEVICE_TYPE = row['device_type']
            HOST = row['host']
            TELNET = row['telnet']
            SSH = row['ssh']
            SSH_USE_KEYS = row['ssh_use_keys']
            SSH_KEYS = row['ssh_keys']
            DATA.append([ID, CATEGORY, HOSTNAME, DEVICE_TYPE,
                         HOST, TELNET, SSH, SSH_USE_KEYS, SSH_KEYS])
        return True

    def _deleteDevices(self, dtype=None):
        if dtype == 1:
            check = self._listDevices(dtype=1)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>router</yellow> you want delete ?", words=[], _validator=validator, critical=True)
                validator = Validator.from_callable(isYesOrNo, error_message=(
                    'please choice (yes or no) '), move_cursor_to_end=True)
                _askdelete = self._InputWithCompletion(question="Sure, you want to delete all saved devices ?", words=[
                                                       'yes', 'no'], _validator=validator, critical=True)
                print(_askdelete)
                if (_askdelete.lower() == 'yes'):
                    self.db_delete_id(ID=ID_D, dtype=dtype)
            else:
                msg.warning('no data to delete.\n')

        elif dtype == 2:
            check = self._listDevices(dtype=2)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>switch</yellow> you want delete ?", words=[], _validator=validator, critical=True)
                validator = Validator.from_callable(isYesOrNo, error_message=(
                    'please choice (yes or no) '), move_cursor_to_end=True)
                _askdelete = self._InputWithCompletion(question="Sure, you want to delete all saved devices ?", words=[
                                                       'yes', 'no'], _validator=validator, critical=True)
                print(_askdelete)
                if (_askdelete.lower() == 'yes'):
                    self.db_delete_id(ID=ID_D, dtype=dtype)
            else:
                msg.warning('no data to delete.\n')

        elif dtype == 3:
            check = self._listDevices(dtype=3)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>device</yellow> you want delete ?", words=[], _validator=validator, critical=True)
                validator = Validator.from_callable(isYesOrNo, error_message=(
                    'please choice (yes or no) '), move_cursor_to_end=True)
                _askdelete = self._InputWithCompletion(question="Sure, you want to delete all saved devices ?", words=[
                                                       'yes', 'no'], _validator=validator, critical=True)
                print(_askdelete)
                if (_askdelete.lower() == 'yes'):
                    self.db_delete_id(ID=ID_D, dtype=dtype)
            else:
                msg.warning('no data to delete.\n')

        if dtype is None:
            validator = Validator.from_callable(isYesOrNo, error_message=(
                'please choice (yes or no) '), move_cursor_to_end=True)
            _askdelete = self._InputWithCompletion(question="Sure, you want to delete all saved devices ?", words=[
                                                   'yes', 'no'], _validator=validator, critical=True)
            os.system('rm devices/devices.db')

    def db_delete_id(self, ID: int, dtype: int) -> bool:
        if dtype == 1:
            d = Routers.delete_by_id(ID)
            if d == ID:
                return True
            return False
        elif dtype == 2:
            d = Switches.delete_by_id(ID)
            if d == ID:
                return True
            return False
        elif dtype == 3:
            d = Others.delete_by_id(ID)
            if d == ID:
                return True
            return False

    def encrypt(self, clear):
        key = self._key
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()

    def decrypt(self, enc):
        key = self._key
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

    def _editDevices(self, dtype):
        if dtype == 1:
            check = self._listDevices(dtype=1)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>device</yellow> you want <blue>Edit</blue> ?", words=[], _validator=validator, critical=True)
                data = self._get_data(dtype=dtype, ID=ID_D)
                data['dtype'] = dtype
                self.prompt_edit(**data)

            else:
                msg.warning('no data to delete.\n')
        elif dtype == 2:
            check = self._listDevices(dtype=2)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>device</yellow> you want <blue>Edit</blue> ?", words=[], _validator=validator, critical=True)
                data = self._get_data(dtype=dtype, ID=ID_D)
                data['dtype'] = dtype
                self.prompt_edit(**data)

            else:
                msg.warning('no data to delete.\n')
        elif dtype == 3:
            check = self._listDevices(dtype=3)
            if check != False:
                validator = Validator.from_callable(isNumber, error_message=(
                    'please enter valid ID '), move_cursor_to_end=True)
                ID_D = self._InputWithCompletion(
                    question="Type <red>ID</red> of <yellow>device</yellow> you want <blue>Edit</blue> ?", words=[], _validator=validator, critical=True)
                data = self._get_data(dtype=dtype, ID=ID_D)
                data['dtype'] = dtype
                self.prompt_edit(**data)

            else:
                msg.warning('no data to delete.\n')

    def prompt_edit(self, **data):
        dtype = data['dtype']
        validator = Validator.from_callable(isNotEmpty, error_message=(
            'please enter valid hostname'), move_cursor_to_end=True)
        if dtype == 1:
            hostname = self._InputWithCompletion(question="Hostname [{0}]".format(
                data['hostname']), words=[], _validator=validator)
        elif dtype == 2:
            hostname = self._InputWithCompletion(question="Hostname [{0}]".format(
                data['hostname']), words=[], _validator=validator)
        else:
            hostname = self._InputWithCompletion(question="Hostname [{0}]".format(
                data['hostname']), words=[], _validator=validator)
        priv_pass = self._InputWithCompletion(
            question="password for privileged mode [{0}]".format('*' * len(data['priv_pass'])), words=[])        
        device_type = 'cisco_ios'
        validator = Validator.from_callable(isNotEmpty, error_message=(
            'please enter valid IP or domain name of Cisco equipment'), move_cursor_to_end=True)
        host = self._InputWithCompletion(question="IP [{0}]".format(
            data['host']), words=[], _validator=validator)
        validator = Validator.from_callable(isYesOrNo, error_message=(
            'please choice yes or no'), move_cursor_to_end=True)
        telnet = self._InputWithCompletion(question="Use Telnet [Yes/no] [{0}]".format(
            data['telnet']), words=['yes', 'no'], _validator=validator)
        if telnet.lower() in ['yes']:
            telnet = True
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet username'), move_cursor_to_end=True)
            telnet_user = self._InputWithCompletion(question="Telnet username [{0}]".format(
                data['telnet_user']), words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet password'), move_cursor_to_end=True)
            if data['telnet_pass'] == '-':
                telnet_pass = self._InputWithCompletion(question="Telnet password [{0}]".format(
                    '*' * len(data['telnet_pass'])), words=[], _validator=validator)
            else:
                telnet_pass = self._InputWithCompletion(question="Telnet password [{0}]".format(
                    '*' * len(self.decrypt(data['telnet_pass']))), words=[], _validator=validator)
            validator = Validator.from_callable(isNumber, error_message=(
                'please enter telnet port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            telnet_port = self._InputWithCompletion(question="Telnet port [{0}]".format(
                data['telnet_port']), words=['23'], _validator=validator)
        else:
            telnet = False
            msg.warning(
                "you can't connect to this cisco equipment using telnet")
        validator = Validator.from_callable(isYesOrNo, error_message=(
            'please choice yes or no'), move_cursor_to_end=True)
        ssh = self._InputWithCompletion(question="Use ssh [Yes/no] [{0}]".format(
            data['ssh']), words=['yes', 'no'], _validator=validator)
        if ssh.lower() in ['yes']:
            ssh = True
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter ssh username'), move_cursor_to_end=True)
            ssh_user = self._InputWithCompletion(question="SSH username [{0}]".format(
                data['ssh_user']), words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty, error_message=(
                'please enter telnet password'), move_cursor_to_end=True)
            if data['ssh_pass'] == '-':
                ssh_pass = self._InputWithCompletion(question="SSH password [{0}]".format(
                    '*' * len(data['ssh_pass'])), words=[], _validator=validator)
            else:
                ssh_pass = self._InputWithCompletion(question="SSH password [{0}]".format(
                    '*' * len(self.decrypt(data['ssh_pass']))), words=[], _validator=validator)
            validator = Validator.from_callable(isNumber, error_message=(
                'please enter SSH port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            ssh_port = self._InputWithCompletion(question="SSH port [{0}]".format(
                data['ssh_port']), words=['22'], _validator=validator)
            validator = Validator.from_callable(isYesOrNo, error_message=(
                'please choice yes or no'), move_cursor_to_end=True)
            ssh_use_keys = self._InputWithCompletion(question="Use ssh keys (recommended) [Yes/no] [{0}]".format(
                data['ssh_use_keys']), words=['yes', 'no'], _validator=validator)
            if ssh_use_keys.lower() in ['yes']:
                ssh_use_keys = True
                validator = Validator.from_callable(isNotEmpty, error_message=(
                    'please enter SSH Keys path'), move_cursor_to_end=True)
                ssh_keys = self._InputWithCompletion(question="Keys Path [{0}]".format(
                    data['ssh_keys']), words=[str(Path.home())+'/', str(os.getcwd())], _validator=validator)
            else:
                ssh_use_keys = False
        else:
            ssh = False
            msg.warning("you can't connect to this cisco equipment using SSH")
        if (ssh is False and telnet is False):
            msg.failure(
                "you can't connect to this device , you don't choice any method of connection ", very=True)
        hostname = hostname if (hostname != "") else "-"
        priv_pass = priv_pass if (priv_pass not in ['', ' ']) else "-"
        device_type = device_type
        host = host if (host != "") else "-"
        if telnet is False:
            telnet_user = '-'
            telnet_pass = '-'
            telnet_port = 23
        else:
            telnet_user = telnet_user
            telnet_pass = self.encrypt(telnet_pass)
            telnet_port = telnet_port
        if ssh is False:
            ssh_use_keys = False
            ssh_keys = '-'
            ssh_user = '-'
            ssh_pass = '-'
            ssh_port = 22
        else:
            ssh_use_keys = ssh_use_keys
            if ssh_use_keys is False:
                ssh_keys = '-'
            else:
                ssh_keys = ssh_keys
            ssh_user = ssh_user
            ssh_pass = self.encrypt(ssh_pass)
            ssh_port = ssh_port if ssh_port != "" else 22
        d_type = int(dtype) if dtype is not None else int(d_type)
        if d_type == 1:
            rwd = Routers.select().where(Routers.id == data['ID']).get()
            rwd.hostname = hostname
            rwd.device_type = device_type
            rwd.host = host
            rwd.telnet = telnet
            rwd.telnet_username = telnet_user
            rwd.telnet_password = telnet_pass
            rwd.telnet_port = telnet_port
            rwd.ssh = ssh
            rwd.ssh_use_keys = ssh_use_keys
            rwd.ssh_keys = ssh_keys
            rwd.ssh_username = ssh_user
            rwd.ssh_password = ssh_pass
            rwd.ssh_port = ssh_port
            rwd.save()
        elif d_type == 2:
            rwd = Switches.select().where(Switches.id == data['ID']).get()
            rwd.hostname = hostname
            rwd.device_type = device_type
            rwd.host = host
            rwd.telnet = telnet
            rwd.telnet_username = telnet_user
            rwd.telnet_password = telnet_pass
            rwd.telnet_port = telnet_port
            rwd.ssh = ssh
            rwd.ssh_use_keys = ssh_use_keys
            rwd.ssh_keys = ssh_keys
            rwd.ssh_username = ssh_user
            rwd.ssh_password = ssh_pass
            rwd.ssh_port = ssh_port
            rwd.save()
        else:
            rwd = Others.select().where(Others.id == data['ID']).get()
            rwd.hostname = hostname
            rwd.device_type = device_type
            rwd.host = host
            rwd.telnet = telnet
            rwd.telnet_username = telnet_user
            rwd.telnet_password = telnet_pass
            rwd.telnet_port = telnet_port
            rwd.ssh = ssh
            rwd.ssh_use_keys = ssh_use_keys
            rwd.ssh_keys = ssh_keys
            rwd.ssh_username = ssh_user
            rwd.ssh_password = ssh_pass
            rwd.ssh_port = ssh_port
            rwd.save()
        db.close()
        msg.success('Device updated successefly')

    def _get_data(self, dtype, ID):
        if dtype == 1:
            r = Routers.select().dicts()
            data = self.parse_rows(r, ID)
            return data
        elif dtype == 2:
            s = Switches.select().dicts()
            data = self.parse_rows(s, ID)
            return data
        elif dtype == 3:
            o = Others.select().dicts()
            data = self.parse_rows(o, ID)
            return data

    def parse_rows(self, f, id_):
        for row in f:
            if row['id'] == int(id_):
                ID = row['id']
                HOSTNAME = row['hostname']
                HOST = row['host']
                PRIV_PASS = row['priv_pass']
                TELNET = row['telnet']
                TELNET_USERNAME = row['telnet_username']
                TELNET_PASSWORD = row['telnet_password']
                TELNET_PORT = row['telnet_port']
                SSH = row['ssh']
                SSH_USE_KEYS = row['ssh_use_keys']
                SSH_KEYS = row['ssh_keys']
                SSH_USERNAME = row['ssh_username']
                SSH_PASSWORD = row['ssh_password']
                SSH_PORT = row['ssh_port']
                return {'ID': ID, 'hostname': HOSTNAME, 'host': HOST, 'priv_pass':PRIV_PASS, 'telnet': TELNET, 'telnet_user': TELNET_USERNAME, 'telnet_pass': TELNET_PASSWORD,
                        'telnet_port': TELNET_PORT, 'ssh': SSH, 'ssh_use_keys': SSH_USE_KEYS, 'ssh_keys': SSH_KEYS, 'ssh_user': SSH_USERNAME, 'ssh_pass': SSH_PASSWORD,
                        'ssh_port': SSH_PORT}

    def single_connect(self, args, method, cmd, ssh_keys=False):
        x = self._processData(args, method, ssh_keys)
        if method == "ssh":
            if ssh_keys == False:
                start = time.perf_counter()
                with concurrent.futures.ProcessPoolExecutor() as exe:
                    {exe.submit(exe_ssh, one, cmd): one for one in x}
                    # for f in concurrent.futures.as_completed(start_f):
                    #   one = start_f[f]
                # for one in x:
                 #   exe_ssh(one, cmds_l)
                end = time.perf_counter()
                print(f'[+] finished in {round(end-start,2)} second(s)')
            else:
                start = time.perf_counter()
                with concurrent.futures.ProcessPoolExecutor() as exe:
                    {exe.submit(exe_ssh_keys, one, cmd): one for one in x}
                    # for f in concurrent.futures.as_completed(start_f):
                    #   one = start_f[f]
                end = time.perf_counter()
                print(f'[+] finished in {round(end-start,2)} second(s)')

        elif method == "telnet":
            start = time.perf_counter()
            print(x, cmd)
            #with concurrent.futures.ProcessPoolExecutor() as exe:
             #   {exe.submit(exe_telnet, one, cmd): one for one in x}
                # for f in concurrent.futures.as_completed(start_f):
                #   one = start_f[f]
            for one in x:
                exe_telnet(one, cmd)
            end = time.perf_counter()
            print(f'[+] finished in {round(end-start,2)} second(s)')

    def connect(self, args, method, file, ssh_keys=False):
        x = self._processData(args, method, ssh_keys)
        cmds_l = Devices().readConfigfile(file)
        if method == "ssh":
            if ssh_keys == False:
                start = time.perf_counter()
                with concurrent.futures.ProcessPoolExecutor() as exe:
                    {exe.submit(exe_ssh, one, cmds_l): one for one in x}
                    # for f in concurrent.futures.as_completed(start_f):
                    #   one = start_f[f]
                #for one in x:
                 #   exe_ssh(one, cmds_l)
                end = time.perf_counter()
                print(f'[+] finished in {round(end-start,2)} second(s)')
            else:
                start = time.perf_counter()
                with concurrent.futures.ProcessPoolExecutor() as exe:
                    {exe.submit(exe_ssh_keys, one, cmds_l): one for one in x}
                    # for f in concurrent.futures.as_completed(start_f):
                    #   one = start_f[f]
                # for one in x:
                 #   exe_ssh(one, cmds_l)
                end = time.perf_counter()
                print(f'[+] finished in {round(end-start,2)} second(s)')

        elif method == "telnet":
            start = time.perf_counter()
            with concurrent.futures.ProcessPoolExecutor() as exe:
                {exe.submit(exe_telnet, one, cmds_l): one for one in x}
                # for f in concurrent.futures.as_completed(start_f):
                #   one = start_f[f]
            # for one in x:
                #   exe_ssh(one, cmds_l)
            end = time.perf_counter()
            print(f'[+] finished in {round(end-start,2)} second(s)')

    def _processData(self, args, method, ssh_keys) -> list:
        EXE = []
        ALL = self.getCredsConf(args, method)
        for item in ALL:
            if method == "ssh":
                if item['ssh'] == 'False':
                    msg.failure(
                        f"can't connect to {msg.YELLOW}{item['host']}{msg.RED} using SSH , because you don't set valid ssh username & password.", very=True)
                else:
                    if ssh_keys != False:
                        if item['ssh_use_keys'] == 'False':
                            msg.failure(
                                f"can't connect to {msg.YELLOW}{item['host']}{msg.RED} using SSH Keys , because you don't set ssh keys.", very=True)
                        else:
                            if item['priv_pass'] == '-':
                                EXE.append([item['host'], item['ssh_username'], self.decrypt(
                                    item['ssh_password']), item['ssh_port'], item['ssh_keys']])
                            else:
                                EXE.append([item['host'], item['ssh_username'], self.decrypt(
                                    item['ssh_password']), item['ssh_port'], item['ssh_keys'], item['priv_pass']])                         
                    else:
                        if item['priv_pass'] == '-':
                            EXE.append([item['host'], item['ssh_username'], self.decrypt(
                                item['ssh_password']), item['ssh_port']])
                        else:
                            EXE.append([item['host'], item['ssh_username'], self.decrypt(
                                item['ssh_password']), item['ssh_port'], item['priv_pass']])                    
            else:
                if item['telnet'] == 'False':
                    msg.failure(
                        f"can't connect to {msg.YELLOW}{item['host']}{msg.RED} using TELNET , because you don't set valid telnet username & password.", very=True)
                else:
                    if item['priv_pass'] == '-':
                        EXE.append([item['host'], item['telnet_username'], self.decrypt(
                            item['telnet_password']), item['telnet_port']])
                    else:
                        EXE.append([item['host'], item['telnet_username'], self.decrypt(
                            item['telnet_password']), item['telnet_port'], item['priv_pass']])

        return EXE

    def getCredsConf(self, args, method) -> list:
        BIGLIST = []
        host = ''
        priv_pass = ''
        telnet = False
        telnet_username = ''
        telnet_password = ''
        telnet_port = ''
        ssh = False
        ssh_username = ''
        ssh_password = ''
        ssh_port = ''
        ssh_use_keys = False
        ssh_keys = ''
        r, s, o = self._returnedDValue(args)
        if r != []:
            r_i = self.getInstance(r, 1)
            for index_of_r in r_i:
                if method == "ssh":
                    host = index_of_r.host
                    ssh = index_of_r.ssh
                    ssh_username = index_of_r.ssh_username
                    ssh_password = index_of_r.ssh_password
                    ssh_port = index_of_r.ssh_port
                    ssh_keys = index_of_r.ssh_keys
                    ssh_use_keys = index_of_r.ssh_use_keys
                    priv_pass = index_of_r.priv_pass
                    BIGLIST.append({'host': host, 'ssh': ssh, 'ssh_username': ssh_username, 'ssh_password': ssh_password,
                                    'ssh_port': ssh_port, 'ssh_use_keys': ssh_use_keys, 'ssh_keys': ssh_keys, 'priv_pass' : priv_pass})
                elif method == "telnet":
                    host = index_of_r.host
                    telnet = index_of_r.telnet
                    telnet_username = index_of_r.telnet_username
                    telnet_password = index_of_r.telnet_password
                    telnet_port = index_of_r.telnet_port
                    priv_pass = index_of_r.priv_pass
                    BIGLIST.append({'host': host, 'telnet': telnet, 'telnet_username': telnet_username,
                                    'telnet_password': telnet_password, 'telnet_port': telnet_port, 'priv_pass':priv_pass})
        if s != []:
            s_i = self.getInstance(s, 2)
            for index_of_s in s_i:
                if method == "ssh":
                    host = index_of_s.host
                    ssh = index_of_s.ssh
                    ssh_username = index_of_s.ssh_username
                    ssh_password = index_of_s.ssh_password
                    ssh_port = index_of_r.ssh_port
                    ssh_keys = index_of_s.ssh_keys
                    ssh_use_keys = index_of_s.ssh_use_keys
                    priv_pass = index_of_s.priv_pass
                    BIGLIST.append({'host': host, 'ssh': ssh, 'ssh_username': ssh_username, 'ssh_password': ssh_password,
                                    'ssh_port': ssh_port, 'ssh_use_keys': ssh_use_keys, 'ssh_keys': ssh_keys, 'priv_pass':priv_pass})
                elif method == "telnet":
                    host = index_of_s.host
                    telnet = index_of_s.telnet
                    telnet_username = index_of_s.telnet_username
                    telnet_password = index_of_s.telnet_password
                    telnet_port = index_of_s.telnet_port
                    priv_pass = index_of_s.priv_pass
                    BIGLIST.append({'host': host, 'telnet': telnet, 'telnet_username': telnet_username,
                                    'telnet_password': telnet_password, 'telnet_port': telnet_port, 'priv_pass':priv_pass})
        if o != []:
            o_i = self.getInstance(o, 3)
            for index_of_o in o_i:
                if method == "ssh":
                    host = index_of_o.host
                    ssh = index_of_o.ssh
                    ssh_username = index_of_o.ssh_username
                    ssh_password = index_of_o.ssh_password
                    ssh_port = index_of_o.ssh_port
                    ssh_keys = index_of_o.ssh_keys
                    ssh_use_keys = index_of_o.ssh_use_keys
                    priv_pass = index_of_o.priv_pass
                    BIGLIST.append({'host': host, 'ssh': ssh, 'ssh_username': ssh_username, 'ssh_password': ssh_password,
                                    'ssh_port': ssh_port, 'ssh_use_keys': ssh_use_keys, 'ssh_keys': ssh_keys, 'priv_pass':priv_pass})
                elif method == "telnet":
                    host = index_of_o.host
                    telnet = index_of_o.telnet
                    telnet_username = index_of_o.telnet_username
                    telnet_password = index_of_o.telnet_password
                    telnet_port = index_of_o.telnet_port
                    priv_pass = index_of_o.priv_pass
                    BIGLIST.append({'host': host, 'telnet': telnet, 'telnet_username': telnet_username,
                                    'telnet_password': telnet_password, 'telnet_port': telnet_port, 'priv_pass':priv_pass})

        return (BIGLIST)

    def getInstance(self, LIST, ID):
        ALL_LIST = []
        if ID == 1:
            for I in LIST:
                try:
                    d = Routers.select().where(Routers.id == int(I)).get()
                    ALL_LIST.append(d)
                except:
                    pass
        elif ID == 2:
            for I in LIST:
                try:
                    d = Switches.select().where(Switches.id == int(I)).get()
                    ALL_LIST.append(d)
                except:
                    pass
        elif ID == 3:
            for I in LIST:
                try:
                    d = Others.select().where(Others.id == int(I)).get()
                    ALL_LIST.append(d)
                except:
                    pass

        return ALL_LIST

    def _returnedDValue(self, text):
        routers_devices, switches_devices, others_devices = [], [], []
        for i in text.split('-'):
            if i.split('=')[0].lower() == 'r':
                routers_devices = i.split('=')[1].split(',')
            if i.split('=')[0].lower() == 's':
                switches_devices = i.split('=')[1].split(',')
            if i.split('=')[0].lower() == 'o':
                others_devices = i.split('=')[1].split(',')
        return routers_devices, switches_devices, others_devices

    def readConfigfile(self, file):
        cmd_list = []
        f = open(file, mode='r').readlines()
        for line in f:
            cmd_list.append(line.strip('\n'))

        return cmd_list


def exe_ssh(i, cmds_l):
    h, u, pa, po, pr = i[0], i[1], i[2], i[3], i[4]
    SSHSession(h, u, pa, po, '', pr, cmd=cmds_l).run()


def exe_ssh_keys(i, cmds_l):
    h, u, pa, po, k, pr = i[0], i[1], i[2], i[3], i[4], i[5]
    SSHSession(h, u, pa, po, k, pr, cmds_l).run()


def exe_telnet(i, cmds_l):
    try:
        h, u, pa, po, pr = i[0], i[1], i[2], i[3], i[4]
    except:
        h, u, pa, po, pr = i[0], i[1], i[2], i[3], '-' # if you face a probleme in Privilege mode , maybe change '-' to ''
    TelnetSession(h, u, pa, po, pr, cmds_l).run()


class ArgsParser(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description="CNA is Network Automation Script for speed up cisco routers & switches configurations")
        self._parser.error = self.parser_error
        self._parser.print_help = self.print_help
        self._devices = self._parser.add_argument_group('Devices Options')
        self._devices.add_argument('--devices', action='store_true')
        self._devices.add_argument('--routers', action='store_true')
        self._devices.add_argument('--switches', action='store_true')
        self._devices.add_argument('--others', action='store_true')
        self._devices.add_argument('--list', action='store_true')
        self._devices.add_argument('--add', action='store_true')
        self._devices.add_argument('--delete', action='store_true')
        self._devices.add_argument('--edit', action='store_true')
        self._config = self._parser.add_argument_group('Configuration Options')
        self._config.add_argument(
            '--connect-to', help="IDs of device you want to connect (e.g --connect-to='R=1,2,3-S=2,3,10-O=2,8,9')")
        self._config.add_argument('--config-file', help="configuration file")
        self._config.add_argument(
            '--config-cmd', help="one line of configuration")
        self._ssh = self._parser.add_argument_group('SSH Options')
        self._ssh.add_argument('--ssh', action='store_true')
        self._ssh.add_argument('--use-keys', action="store_true")
        self._telnet = self._parser.add_argument_group('Telnet Options')
        self._telnet.add_argument('--telnet', action='store_true')
        self._args = self._parser.parse_args()

    def parser_error(self, errmsg):
        print(msg.YELLOW+"Usage:"+msg.WHITE+" python3 " +
              sys.argv[0] + " [Options] use -h for help")
        print(msg.RED+"\tError: "+msg.YELLOW+errmsg + msg.WHITE+"\n")

    def print_help(self):
        print(msg.YELLOW+"Usage:"+msg.WHITE+" python3 " +
              sys.argv[0] + " --devices / --connect-to [Options]")
        print(msg.WHITE+"\n\t<< "+msg.YELLOW +
              "CNA is Network Automation script for speed up cisco routers & switches configuration "+msg.WHITE+">>")
        print(msg.WHITE+"\n\t<<"+msg.MAG+" Coded by  : "+msg.WHITE+"Yasser Janah " +
              msg.RED+"("+msg.YELLOW+"Y4SS3R005"+msg.RED+") "+msg.WHITE+">>")
        print(msg.WHITE+"\t<<"+msg.MAG+" Facebook  : "+msg.WHITE +
              "https://facebook.com/"+msg.GREEN+"yasser.janah "+msg.WHITE+">>")
        print(msg.WHITE+"\t<<"+msg.MAG+" Twitter   : "+msg.WHITE +
              "https://twitter.com/"+msg.GREEN+"yasser_janah "+msg.WHITE+">>")
        print(msg.WHITE+"\t<<"+msg.MAG+" Instagram : "+msg.WHITE +
              "https://www.instagram.com/"+msg.GREEN+"yasserjanah "+msg.WHITE+">>")
        print(msg.WHITE+"\t<<"+msg.MAG+" Linkedin  : "+msg.WHITE +
              "https://www.linkedin.com/in/"+msg.GREEN+"yasserjanah "+msg.WHITE+">>")
        print(msg.WHITE+"\t<<"+msg.MAG+" Github    : "+msg.WHITE +
              "https://github.com/"+msg.GREEN+"yasserjanah "+msg.WHITE+">>\n")

        print(msg.WHITE+'\033[1m\033[4mrequired options\033[0m:')
        print(msg.WHITE+'\t--devices\t\trequired argument ')
        print(msg.WHITE+'\t--connect-to\t\tID of devices to start config syntax : (e.g --connect-to=' +
              repr('R=1,2-S=1,2,3-O=1,2')+')')
        print(msg.WHITE+'\033[1m\033[4mDevices options\033[0m:')
        print(msg.WHITE+'\t--routers\t\trun operations on routers')
        print(msg.WHITE+'\t--switches\t\trun operations on switches')
        print(msg.WHITE+'\t--others\t\trun operations on others')
        print(msg.WHITE+'\033[1m\033[4moperations options\033[0m:')
        print(msg.WHITE+'\t--list\t\t\tlist of devices')
        print(msg.WHITE+'\t--add\t\t\tadd new devices')
        print(msg.WHITE+'\t--edit\t\t\tedit devices')
        print(msg.WHITE+'\t--delete\t\tdelete devices')
        print(msg.WHITE+'\033[1m\033[4mconfiguration options\033[0m:')
        print(msg.WHITE+'\t--config-file\t\tfile contains configuration')
        print(msg.WHITE+'\t--config-cmd\t\tsingle configuration command')
        print(msg.WHITE+'\033[1m\033[4mconnection options\033[0m:')
        print(msg.WHITE+'\t--ssh\t\t\tconnect using ssh methods')
        print(msg.WHITE+'\t\t--use-keys\tuse ssh keys')
        print(msg.WHITE+'\t--telnet\t\tconnect using telnet methods\n')

    def _GetAll(self):
        return self._args


def main():
    args = ArgsParser()._GetAll()
    if args.devices:
        if args.list and any([args.routers, args.switches, args.others, args.add, args.delete, args.edit, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            print(' ')
            Devices()._listDevices(dtype=None)
        elif args.add and any([args.routers, args.switches, args.others, args.list, args.delete, args.edit, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            print(' ')
            Devices()._addDevices(dtype=None)
        elif args.delete and any([args.routers, args.switches, args.others, args.list, args.add, args.edit, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            print(' ')
            Devices()._deleteDevices(dtype=None)
        elif args.edit and any([args.routers, args.switches, args.others, args.list, args.delete, args.add, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            msg.failure(
                '--edit works only when you speciefy device category (example : --devices [--routers/--switches/--others] --edit) ')
        elif args.routers and any([args.switches, args.others, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            if args.list and all([args.add, args.delete, args.edit]) is False:
                print(' ')
                Devices()._listDevices(dtype=1)
            elif args.add and all([args.list, args.delete, args.edit]) is False:
                print(' ')
                Devices()._addDevices(dtype=1)
            elif args.delete and all([args.add, args.list, args.edit]) is False:
                print(' ')
                Devices()._deleteDevices(dtype=1)
            elif args.edit and all([args.add, args.delete, args.list]) is False:
                print(' ')
                Devices()._editDevices(dtype=1)
            else:
                msg.failure(
                    'please speciefy the operation --routers [OPTIONS] : (example : --list or --add or --edit or --delete)')
        elif args.switches and any([args.routers, args.others, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            if args.list and any([args.add, args.delete, args.edit]) is False:
                print(' ')
                Devices()._listDevices(dtype=2)
            elif args.add and any([args.list, args.delete, args.edit]) is False:
                print(' ')
                Devices()._addDevices(dtype=2)
            elif args.delete and any([args.add, args.list, args.edit]) is False:
                print(' ')
                Devices()._deleteDevices(dtype=2)
            elif args.edit and any([args.add, args.delete, args.list]) is False:
                print(' ')
                Devices()._editDevices(dtype=2)
            else:
                msg.failure(
                    'please speciefy the operation --switches [OPTIONS] : (example : --list or --add or --edit or --delete)')
        elif args.others and any([args.routers, args.switches, args.ssh, args.use_keys, args.telnet, args.connect_to]) is False:
            if args.list and any([args.add, args.delete, args.edit]) is False:
                print(' ')
                Devices()._listDevices(dtype=3)
            elif args.add and any([args.list, args.delete, args.edit]) is False:
                print(' ')
                Devices()._addDevices(dtype=3)
            elif args.delete and any([args.add, args.list, args.edit]) is False:
                print(' ')
                Devices()._deleteDevices(dtype=3)
            elif args.edit and any([args.add, args.delete, args.list]) is False:
                print(' ')
                Devices()._editDevices(dtype=3)
            else:
                msg.failure(
                    'please speciefy the operation --others [OPTIONS] : (example : --list or --add or --edit or --delete)')
    elif args.connect_to and any([args.devices, args.routers, args.switches, args.others, args.add, args.delete, args.edit]) is False:
        if args.config_file and any([args.routers, args.switches, args.list, args.add, args.delete, args.edit]) is False:
            if args.ssh and any([args.telnet, args.use_keys]) is False:
                print(' ')
                Devices().connect(args=args.connect_to, method="ssh",
                                  ssh_keys=False, file=args.config_file)
            elif args.ssh and args.use_keys and any([args.telnet]) is False:
                print(' ')
                Devices().connect(args=args.connect_to, method="ssh",
                                  ssh_keys=args.use_keys, file=args.config_file)
            elif args.telnet and any([args.ssh, args.use_keys]) is False:
                print(' ')
                Devices().connect(args=args.connect_to, method="telnet", file=args.config_file)
            else:
                msg.failure(
                    'please speciefy the connection method: (example : --ssh or --telnet or --ssh --ssh-keys) !! see the help')
        elif args.config_cmd and any([args.routers, args.switches, args.list, args.add, args.delete, args.edit]) is False:
            if args.ssh and any([args.telnet, args.use_keys]) is False:
                print(' ')
                Devices().single_connect(args=args.connect_to,
                                         method="ssh", ssh_keys=False, cmd=args.config_cmd)
            elif args.ssh and args.use_keys and any([args.telnet]) is False:
                print(' ')
                Devices().single_connect(args=args.connect_to,
                                         method="ssh", ssh_keys=args.use_keys, cmd=args.config_cmd)
            elif args.telnet and any([args.ssh, args.use_keys]) is False:
                print(' ')
                Devices().single_connect(args=args.connect_to,
                                         method="telnet", ssh_keys=False, cmd=args.config_cmd)
            else:
                msg.failure(
                    'please speciefy the connection method: (example : --ssh or --telnet or --ssh --ssh-keys) !! see the help')
    else:
        msg.failure('--devices/--connect-to !! see the help ..')


BANNER = f"""

        {msg.YELLOW}01000011 01101001 01110011 01100011 {msg.BLINK}01101111{msg.RESET}
        {msg.BLINK}{msg.RESET}00100000 01001110 01100101 {msg.BLINK}01110100{msg.RESET} 01110111{msg.RESET}
        {msg.GREEN}01101111 01110010 {msg.BLINK}01101011{msg.RESET}{msg.GREEN} 00100000 01000001{msg.RESET}
        {msg.WHITE}01110101{msg.RESET} {msg.BLINK}01110100{msg.RESET} 01101111 01101101 01100001{msg.RESET}
        {msg.RED}{msg.BLINK}01110100{msg.RESET}{msg.RED} 01101001 01101111 01101110{msg.RESET}            {msg.UNDERLINE}Created{msg.RESET} {msg.UNDERLINE}by{msg.RESET} : {msg.BOLD}{msg.RED}Yasser Janah.{msg.RESET}
        """
if __name__ == '__main__':
    try:
        print(BANNER)
        main()
    except KeyboardInterrupt:
        exit(msg.failure("CTRL+C detected"))
    except Exception as err:
        raise (err)
        exit(msg.failure(str(err)))


"""
with concurrent.futures.ThreadPoolExecutor() as exe:
    exe.map(func, list)
"""
