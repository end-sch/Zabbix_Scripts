#!/usr/bin/env python3
import telnetlib
import re
from sys import argv
import json

HOST = argv[1] #IP da OLT
FUNCAO = argv[2] #Recebe a definition
USER = "user"
PWD = "pass"


try:
        tn = telnetlib.Telnet(HOST, timeout=5)

        tn.read_until(b"Username(1-32 chars):", timeout=2)
        tn.write(USER.encode('utf-8') + b"\n")
        if PWD:
            tn.read_until(b"Password(1-16 chars):", timeout=2)
            tn.write(PWD.encode('utf-8') + b"\n")
except:
        print('Não foi possível se conectar ao Host.')
        exit()


def lista_onus():
        tn.write(b"show onu-status\n")
        output = (tn.read_until(b"####", 3).decode('utf-8')).splitlines()
        p1, p2, p3, p4 = 0, 0, 0, 0
        for line in output:
                if 'Up' in line:
                        line = line.split(' ')
                        onu = line[0]
                        if "0/1" in onu:
                                p1 = p1 + 1
                        elif "0/2" in onu:
                                p2 = p2 + 1
                        elif "0/3" in onu:
                                p3 = p3 + 1
                        elif "0/4" in onu:
                                p4 = p4 + 1
        lista = {
                                "pons": {
                                        "PON 0/1": p1,
                                        "PON 0/2": p2,
                                        "PON 0/3": p3,
                                        "PON 0/4": p4
                                }
                        }
        print(json.dumps(lista, indent=4, sort_keys=True))


def defaults():
        tn.write(b"""enable\n
                        configure terminal\n""")
        # Ajusta horário
        tn.write(b"""sntp client\n
                        sntp client mode unicast\n
                        sntp server 187.63.191.4\n
                        !\n
                        clock timezone brasilia -3\n
                        !\n
                        screen-rows per-page 0\n
                        !\n
                        snmp-server community bitsnmp ro permit view iso\n
                        !\n""")
        # Deleta ONUs offline
        tn.write(b"show onu-status\n")
        output = (tn.read_until(b"####", 3).decode('utf-8')).splitlines()
        for line in output:
                if 'Down' in line:
                        line = re.split(' +', line)
                        tn.write("no onu-binding onu ".encode('utf-8') + line[0].encode('utf-8') + b"\n y \n")
                        tn.read_until(b"####", 1)
        # Salva
        tn.write(b"exit\n copy running-config startup-config\n y\n")
        tn.read_until(b"####", 1)


def onus_online():
        tn.write(b"show onu-status\n")
        output = (tn.read_until(b"####", 3).decode('utf-8')).splitlines()
        p1, p2, p3, p4 = 0, 0, 0, 0
        for line in output:
                if 'ONU' in line:
                        onus_online = [line]
                if 'Up' in line:
                        onus_online += [line]
                        line = line.split(' ')
                        onu = line[0]
                        if "0/1" in onu:
                                p1 = p1 + 1
                        elif "0/2" in onu:
                                p2 = p2 + 1
                        elif "0/3" in onu:
                                p3 = p3 + 1
                        elif "0/4" in onu:
                                p4 = p4 + 1
        print('PON 0/1: ' + str(p1) + ' || PON 0/2: ' + str(p2) + ' || PON 0/3: ' + str(p3) + ' || PON 0/4: ' + str(p4))
        print()
        for linha in onus_online:
                print(linha)


if FUNCAO == 'lista_onus':
        lista_onus()
elif FUNCAO == 'defaults':
        defaults()
elif FUNCAO == 'onus_online':
        onus_online()
