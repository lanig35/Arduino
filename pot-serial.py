#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
import struct
import argparse
#print sys.path
#print os.getcwd ()
#sys.path.remove ('/home/alain/Arduino')
sys.path.remove (os.getcwd())
import serial

parser = argparse.ArgumentParser (description='Lecture potentiomètre',
                                  epilog='port série /dev/ttyACM0 par défaut')
parser.add_argument ('--verbose', '-v', action='store_true',
                     help='Active le niveau de trace')
parser.add_argument ('--baud', '-b', default=9600, type=int,
                     help='Vitesse de transmission du port série')
parser.add_argument ('delai', type=int,
                     help='Délai en secondes entre 2 lectures')

args = parser.parse_args ()
if args.verbose:
    print args 

with serial.Serial () as s:
    s.baudrate = 9600
    s.timeout = 5
    s.port = '/dev/ttyACM0'
    s.open ()
    print s.isOpen()
    print s.name
    s.flushInput ()

    while True:
#    print s.readline ()
        v = s.read (1)
        print type(v) # string
        if len (v) == 0:
            break
        print v # erreur
        d = struct.unpack ('B', v[0])[0]
        print d
        print v[0] # erreur
        print ord(v[0])

