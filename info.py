#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import pyfirmata
import serial
import argparse
from prettytable import PrettyTable
import json

version = 1.0

parser = argparse.ArgumentParser (description='LED - Potentiomètre',
                                  epilog='port série /dev/ttyACM0 par défaut')
parser.add_argument ('--version', '-v', action='store_true',
                     help='Version du programme')
parser.add_argument ('--trace', '-t', action='store_true',
                     help='Active le niveau de trace')
parser.add_argument ('--format', '-f', choices=['text','json','table'],
                     default='text', help='Format de sortie')
parser.add_argument ('--releve', '-r', type=int, default=2, metavar='nb',
                     help='Nombre de relevés')
parser.add_argument ('delai', type=int, default=2, nargs='?',
                     choices=range(1,5),
                     help='durée (en secondes) entre 2 mesures')
args = parser.parse_args ()

if args.version:
    print '{0}'.format(version)
    exit (0)

try:
    board = pyfirmata.Arduino ('/dev/ttyACM0')
except serial.SerialException as e:
    print e
    print 'vérifier avec \"python -m serial.tools.list_ports\"'
    exit (1)

time.sleep (5)
it = pyfirmata.util.Iterator (board)
it.start()

a0 = board.get_pin('a:0:i')
a1 = board.get_pin('a:1:i')
a2 = board.get_pin('a:2:i')

sortie = PrettyTable (["#", "Température", "Lumière", "Potentiomètre"])
jdata = []
count = 1

def table (c, t, l, p):
    global sortie
    print 'xxx'
    sortie.add_row ([c, t, l, p])

def text (c, t, l, p):
    print 'c={0},t={1},l={2},p={3}'.format (c, t, l, p)

def jformat (c, t, l, p):
    global jdata
    obj = {'count':c, 'temp':t, 'lum':l, 'pot':p}
    jdata.append (obj)

format = {'text': text, 'table': table, 'json': jformat}

try:
    while count <= args.releve:
        if args.trace:
            print 'count: ', count
        p = a0.read ()
        l = a1.read ()
        t = a2.read ()
        format [args.format](count, t, l, p)
#        sortie.add_row ([count, t, l, p])
        count +=1
        time.sleep (1)
except KeyboardInterrupt:
    board.exit()
except Exception as e:
    print e

board.exit ()
if args.format == 'table':
    print sortie 
if args.format == 'json':
    print json.dumps (jdata)

exit (0)
