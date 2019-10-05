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
    from pathlib import Path
except ImportError as err:
    exit(str(err))

global COMMANDS
COMMANDS = [1, 2, 3]
def Complete(text, stat):
    for cmd in COMMANDS:
        if cmd.startswith(text):
            if not stat:
                return cmd
            else:
                stat -= 1

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


#TelnetSession('10.0.0.1').run()
class Devices(object):
    """
    Controling saved Devices [ don't worry the programe do this automaticaly (^_^) ]

    [Syntax]
        e.g =>  Devices {
                    'ID'         : 1
                    'hostname'   : 'Router1',
                    'device_type': 'cisco_ios', # define as a cisco OS
                    'host'       : 'cisco_router.company.local',
                    'telnet':{
                            'username' : 'router_telnet_user',
                            'password' : 'RouterTelnetPassword$$',
                            'port'     :  23,
                            }
                    'ssh': {
                            'username' : 'router_ssh_user',
                            'password' : 'RouterSshPassword$$',
                            'port'     :  22,
                            'use_keys' :  False,
                            'keys'     : '/home/user/.ssh/id_pub'
                            }
                    }
    """
    def __init__(self):
        self._devicesDir    = "devices/"
        self._routerFile    = os.path.join(self._devicesDir, "routers.json")
        self._switchesFile  = os.path.join(self._devicesDir, "switches.json")
        self._othersFile  = os.path.join(self._devicesDir, "others.json")
        self._key = 'CNAG00DKeyForEncryption&Decryption'

    def _addDevice(self, dtype=None):
        if dtype is None:
            print(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Choice Device Type : ")
            print(f"\t       {msg.RED}1{msg.WHITE}) - {msg.BLUE}Router ")
            print(f"\t       {msg.RED}2{msg.WHITE}) - {msg.BLUE}Switch ")
            print(f"\t       {msg.RED}3{msg.WHITE}) - {msg.BLUE}Others ")
            readline.parse_and_bind("tab: complete")
            readline.set_completer(Complete)
            d_type = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Router or Switch (e.g 1 for routers) : {msg.WHITE}"))
        COMMANDS = []
        readline.parse_and_bind("tab: complete")
        readline.set_completer(Complete)
        hostname = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Hostname (e.g R1) : {msg.WHITE}"))
        device_type = 'cisco_ios'
        host = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Host (e.g 192.168.1.1) : {msg.WHITE}"))
        COMMANDS = ['y', 'n']
        readline.parse_and_bind("tab: complete")
        readline.set_completer(Complete)
        telnet = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Use Telnet [Y/n] : {msg.WHITE}"))
        if telnet.lower() in ['', 'y']:
            telnet = True
            COMMANDS = []
            readline.parse_and_bind("tab: complete")
            readline.set_completer(Complete)
            telnet_user = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Telnet username : {msg.WHITE}"))
            telnet_pass = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Telnet password : {msg.WHITE}"))
            telnet_port = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Telnet port (default:23) : {msg.WHITE}"))
        else: telnet = False
        COMMANDS = ['y', 'n']
        readline.parse_and_bind("tab: complete")
        readline.set_completer(Complete)
        ssh = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] Use SSH [Y/n] : {msg.WHITE}"))
        if ssh.lower() in ['', 'y']:
            ssh = True
            COMMANDS = ['y', 'n']
            readline.parse_and_bind("tab: complete")
            readline.set_completer(Complete)
            ssh_use_keys = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] use ssh keys (recommended) [Y/n]: {msg.WHITE}"))
            if ssh_use_keys.lower() in ['', 'y']:
                ssh_use_keys = True
                COMMANDS = [str(Path.home())]
                readline.parse_and_bind("tab: complete")
                readline.set_completer(Complete)
                ssh_keys = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] keys path : {msg.WHITE}"))
            else: ssh_use_keys = False
            COMMANDS = []
            readline.parse_and_bind("tab: complete")
            readline.set_completer(Complete)
            ssh_user = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] SSH username : {msg.WHITE}"))
            ssh_pass = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] SSH password : {msg.WHITE}"))
            ssh_port = str(input(f"\t{msg.WHITE}[{msg.GREEN}ADD{msg.WHITE}] SSH port (default:22) : {msg.WHITE}"))
        else: ssh = False
        data = {}
        data['hostname'] = hostname
        data['device_type'] = device_type
        data['host'] = host
        data['telnet'] = telnet
        data['telnet_username'] = telnet_user if telnet != False else ''
        data['telnet_password'] = telnet_pass if telnet != False else ''
        data['telnet_port'] = telnet_port if telnet != False else 23
        data['ssh'] = ssh
        data['ssh_use_keys'] = ssh_use_keys
        data['ssh_keys'] = ssh_keys if (ssh_use_keys and ssh_use_keys != False) else ''
        data['ssh_username'] = ssh_user
        data['ssh_password'] = ssh_pass
        data['ssh_port'] = ssh_port if ssh_port != "" else 22
        d_type = dtype
        if d_type == 1:
            f = open(self._routerFile, mode='a')
        elif d_type == 2:
            f = open(self._switchesFile, mode='a')
        else:
            f = open(self._othersFile, mode='a')
        json_data = json.dumps(data)
        f.write(json_data)
        f.close()
        msg.success('Device added successefly')

    def encrypt(clear):
        key = self._key
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()

    def decrypt(enc):
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
    print("==========================================")
    print("Devices\t:  ",args.devices)
    print("Routers\t:  ",args.routers)
    print("Switches\t: ",args.switches)
    print("List\t:  ",args.list)
    print("Add\t:  ",args.add)
    print("Delete\t:  ",args.delete)
    print("Ssh\t:  ",args.ssh)
    print("Use-Keys\t:  ",args.use_keys)
    print("Telnet\t:  ",args.telnet)
    print("==========================================")
    if args.devices and any([args.ssh, args.telnet, args.use_keys, args.connect]) is False:
        if args.list and any([args.routers, args.switches]) is False:
            print('list of all devices')
        elif args.add and any([args.routers, args.switches]) is False:
            Devices()._addDevice(dtype=None)
        elif args.routers and any([args.switches]) is False:
            print('routers only')
            if args.list:
                print('list routers')
            elif args.add:
                print('add routers')
                Devices()._addDevice(dtype=1)
            elif args.delete:
                print('delete routers')
        elif args.switches and any([args.routers]) is False:
            print('switches only')
            if args.list:
                print('list switches')
            elif args.add:
                print('add switches')
                Devices()._addDevice(dtype=2)
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
        exit(msg.failure(str(err)))