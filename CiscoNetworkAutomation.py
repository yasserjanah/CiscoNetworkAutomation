#!/usr/bin/env python3

__author__ = "Yasser Janah"
__email___ = "janah.y4ss3r@gmail.com"
___desc___ = "Network Automation Script for managing Cisco Routers & Switches"

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

db = SqliteDatabase('devices/devices.sql')

class Routers(Model):
    hostname = CharField()
    device_type = CharField()
    host = CharField()
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
    WHITE  = u"\u001b[38;5;255m"
    RED    = u"\u001b[38;5;196m"
    GREEN  = u"\u001b[38;5;40m"
    BLUE   = u"\u001b[38;5;21m"
    YELLOW = u"\u001b[38;5;220m"
    BLINK = "\033[6m"
    UNDERLINE = "\033[4m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
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
        self._devicesDir    = "devices/"
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

    def _InputWithCompletion(self, question:str , words:list, _validator=None, password=False):
        asked = "<white>[<green>+</green>]</white><white> {0} : </white>".format(question)
        text = prompt(HTML(asked), completer=WordCompleter(words, ignore_case=True), complete_while_typing=True, validator=_validator, mouse_support=True, is_password=password, style=self.style)
        return text

    def _addDevices(self, dtype=None):
        if dtype is None:
            msg.info("add new device")
            print(f"\t{msg.RED}1{msg.WHITE}) - {msg.BLUE}Router ")
            print(f"\t{msg.RED}2{msg.WHITE}) - {msg.BLUE}Switch ")
            print(f"\t{msg.RED}3{msg.WHITE}) - {msg.BLUE}Others ")
            validator = Validator.from_callable(isInSupportedTypes,error_message=('please choice : 1) Routers - 2) Switches - 3) Others'), move_cursor_to_end=True)
            d_type = self._InputWithCompletion(question="Choice Device Type", words=['1', '2', '3'], _validator=validator)
        validator = Validator.from_callable(isNotEmpty ,error_message=('please enter valid hostname'), move_cursor_to_end=True)
        hostname = self._InputWithCompletion(question="Hostname (e.g Router1 )", words=[], _validator=validator)
        device_type = 'cisco_ios'
        validator = Validator.from_callable(isNotEmpty ,error_message=('please enter valid IP or domain name of Cisco equipment'), move_cursor_to_end=True)
        host = self._InputWithCompletion(question="IP (e.g 192.168.1.1 or cisco1.company.local)", words=[], _validator=validator)
        validator = Validator.from_callable(isYesOrNo ,error_message=('please choice yes or no'), move_cursor_to_end=True)
        telnet = self._InputWithCompletion(question="Use Telnet [Yes/no]", words=['yes', 'no'], _validator=validator)
        if telnet.lower() in ['yes']:
            telnet = True
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter telnet username'), move_cursor_to_end=True)
            telnet_user = self._InputWithCompletion(question="Telnet username", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter telnet password'), move_cursor_to_end=True)
            telnet_pass = self._InputWithCompletion(question="Telnet password", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter telnet port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            telnet_port = self._InputWithCompletion(question="Telnet port (default:23)", words=['23'], _validator=validator)
        else:
            telnet = False
            msg.warning("you can't connect to this cisco equipment using telnet")
        ssh = self._InputWithCompletion(question="Use ssh [Yes/no]", words=['yes', 'no'], _validator=validator)
        if ssh.lower() in ['yes']:
            ssh = True
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter ssh username'), move_cursor_to_end=True)
            ssh_user = self._InputWithCompletion(question="SSH username", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter telnet password'), move_cursor_to_end=True)
            ssh_pass = self._InputWithCompletion(question="SSH password", words=[], _validator=validator)
            validator = Validator.from_callable(isNotEmpty ,error_message=('please enter SSH port , PRESS <TAB> for default value '), move_cursor_to_end=True)
            ssh_port = self._InputWithCompletion(question="SSH port (default:22)", words=['22'], _validator=validator)
            ssh_use_keys = self._InputWithCompletion(question="Use ssh keys (recommended) [Yes/no]", words=['yes', 'no'], _validator=validator)
            if ssh_use_keys.lower() in ['yes']:
                ssh_use_keys = True
                validator = Validator.from_callable(isNotEmpty ,error_message=('please enter SSH Keys path'), move_cursor_to_end=True)
                ssh_keys = self._InputWithCompletion(question="Keys Path", words=[str(Path.home())+'/', str(os.getcwd())], _validator=validator)
            else: ssh_use_keys = False
        else: 
            ssh = False
            msg.warning("you can't connect to this cisco equipment using SSH")
        hostname = hostname if (hostname != "") else "-"
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
            if ssh_use_keys is False: ssh_keys = '-'
            else: ssh_keys = ssh_keys
            ssh_user = ssh_user
            ssh_pass = self.encrypt(ssh_pass)
            ssh_port = ssh_port if ssh_port != "" else 22
        d_type = int(dtype) if dtype is not None else int(d_type)
        print('[+] telnet PASS '+telnet_pass)
        print('[+] SSH PASS : '+ssh_pass)
        if d_type == 1:
            Routers.create(hostname=hostname, device_type=device_type, host=host,
                        telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                        telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                        ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        elif d_type == 2:
            Switches.create(hostname=hostname, device_type=device_type, host=host,
                        telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                        telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                        ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        else:
            Others.create(hostname=hostname, device_type=device_type, host=host,
                        telnet=telnet, telnet_username=telnet_user, telnet_password=telnet_pass,
                        telnet_port=telnet_port, ssh=ssh, ssh_use_keys=ssh_use_keys, ssh_keys=ssh_keys,
                        ssh_username=ssh_user, ssh_password=ssh_pass, ssh_port=ssh_port)
        db.close()
        msg.success('Device added successefly')
    
    def _listDevices(self, dtype=None):
        HEADERS = ['ID', 'CATEGORY' ,'HOSTNAME' , 'DEVICE_TYPE', 'HOST', 'TELNET', 
                'SSH', 'SSH_USE_KEYS', 'SSH_KEYS']
        if dtype == 1:
            DATA = []
            routers_data = Routers.select().dicts()
            self.sort_data(DATA, [i for i in routers_data], cat="routers")
            if DATA == []:
                print('[+] no data')
            else:
                msg.info(f"{msg.UNDERLINE}List of Routers{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
        elif dtype == 2:
            DATA = []
            switches_data = Switches.select().dicts()
            self.sort_data(DATA, [i for i in switches_data], cat="switches")
            if DATA == []:
                print('[+] no data')
            else:
                msg.info(f"{msg.UNDERLINE}List of Switches{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
        elif dtype == 3:
            DATA = []
            others_data = Others.select().dicts()
            self.sort_data(DATA, [i for i in others_data], cat="others")
            if DATA == []:
                print('[+] no data')
            else:
                msg.info(f"{msg.UNDERLINE}List of Others Devices{msg.RESET}:")
                table = tt.to_string(DATA, header=HEADERS, padding=(0, 1))
                print(table)
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
                print("[+] no routers's data")
            else:
                print()
                msg.info(f"{msg.UNDERLINE}List of Routers{msg.RESET}:")
                table_r = tt.to_string(DATA_R, header=HEADERS, padding=(0, 1))
                print(table_r)
            if DATA_S == []:
                print("[+] no switches's data")
            else:
                print()
                msg.info(f"{msg.UNDERLINE}List of Switches{msg.RESET}:")
                table_s = tt.to_string(DATA_S, header=HEADERS, padding=(0, 1))
                print(table_s)
            if DATA_O == []:
                print("[+] no others devices's data")
            else:
                print()
                msg.info(f"{msg.UNDERLINE}List of Others{msg.RESET}:")
                table_o = tt.to_string(DATA_O, header=HEADERS, padding=(0, 1))
                print(table_o)

            

    def sort_data(self, DATA:list ,d_:list, cat=None):
        for row in d_:
            ID = row['id']
            CATEGORY = cat
            HOSTNAME = row['hostname']
            DEVICE_TYPE = row['device_type']
            HOST = row['host']
            TELNET = row['telnet']
            print('[+] encrypted telnet '+TELNET)
            print('[+] cleared telnet '+self.decrypt(TELNET))
            SSH = row['ssh']
            SSH_USE_KEYS = row['ssh_use_keys']
            SSH_KEYS = row['ssh_keys']
            DATA.append([ID, CATEGORY, HOSTNAME, DEVICE_TYPE, HOST, TELNET, SSH, SSH_USE_KEYS, SSH_KEYS])
        return True

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

class ArgsParser(object):
    def __init__(self):
        self._parser  = argparse.ArgumentParser(description="CNA is Network Automation Script for speed up cisco routers & switches configurations")
        self._devices = self._parser.add_argument_group('Devices Options')
        self._devices.add_argument('--devices', action='store_true')
        self._devices.add_argument('--routers', action='store_true')
        self._devices.add_argument('--switches', action='store_true')
        self._devices.add_argument('--list', action='store_true')
        self._devices.add_argument('--add', action='store_true')
        self._devices.add_argument('--delete', action='store_true')
        self._connect = self._parser.add_argument_group('Connection Options')
        self._connect.add_argument('--connect', action='store_true')
        self._ssh = self._parser.add_argument_group('SSH Options')
        self._ssh.add_argument('--ssh', action='store_true')
        self._ssh.add_argument('--use-keys', action="store_true")
        self._telnet = self._parser.add_argument_group('Telnet Options')
        self._telnet.add_argument('--telnet', action='store_true')
        self._args = self._parser.parse_args()
    
    def _GetAll(self):
        return self._args

def main():
    args = ArgsParser()._GetAll()
    if args.devices and any([args.ssh, args.telnet, args.use_keys, args.connect]) is False:
        if args.list and any([args.routers, args.switches]) is False:
            print('list of all devices')
            Devices()._listDevices(dtype=None)
        elif args.add and any([args.routers, args.switches]) is False:
            Devices()._addDevices(dtype=None)
        elif args.routers and any([args.switches]) is False:
            print('routers only')
            if args.list:
                print('list routers')
                Devices()._listDevices(dtype=1)
            elif args.add:
                print('add routers')
                Devices()._addDevices(dtype=1)
            elif args.delete:
                print('delete routers')
        elif args.switches and any([args.routers]) is False:
            print('switches only')
            if args.list:
                print('list switches')
                Devices()._listDevices(dtype=2)
            elif args.add:
                print('add switches')
                Devices()._addDevices(dtype=2)
            elif args.delete:
                print('delete switches')
        else:
            print(f" --switches doesn't allowed with --routers")
    elif args.connect and any([args.devices, args.routers, args.switches]) is False:
        print("connection options")
        if args.ssh and any([args.telnet]) is False:
            print('ssh ')
            if args.use_keys:
                print("use keys")
        elif args.telnet and any([args.ssh, args.use_keys]) is False:
            print('Telnet')
    else:
        msg.failure('--connect is not allowed with --devices')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(msg.failure("CTRL+C detected"))
    except Exception as err:
        raise (err)
        #exit(msg.failure(str(err)))