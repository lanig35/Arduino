#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import pyfirmata

board = pyfirmata.Arduino ('/dev/ttyACM0')
time.sleep (5)
it = pyfirmata.util.Iterator (board)
it.start()

a0  =   board.get_pin('a:0:i')

try:
    while True:
        p = a0.read ()
        print p
        if p is not None:
            p = (p*180)
            a = int(p)
            print a
except KeyboardInterrupt:
    board.exit()
    exit ()
