#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import pyfirmata
import serial
import argparse

version = 1.0

parser = argparse.ArgumentParser (description='LED - Potentiomètre',
                                  epilog='port série /dev/ttyACM0 par défaut')
parser.add_argument ('--verbose', '-v', action='store_true',
                     help='Active le niveau de trace')
parser.add_argument ('--version', action='store_true',
                     help='Version du programme')

args = parser.parse_args ()

if args.version:
    print '{0}'.format(version)

led = 3
pot = 0

try:
    board = pyfirmata.Arduino ('/dev/ttyACM0')
except serial.SerialException as e:
    print e

time.sleep (5)
it = pyfirmata.util.Iterator (board)
it.start()

a0  =   board.get_pin('a:0:i')
l3 = board.get_pin ('d:3:p')
try:
    while True:
        p = a0.read ()
        print p
        if p is not None:
            l3.write (p)
            p = (p*180)
            a = int(p)
            print a
        time.sleep (1)
except KeyboardInterrupt:
    board.exit()
    exit ()
