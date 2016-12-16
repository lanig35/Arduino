#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import Tkinter
import tkMessageBox
import pyfirmata
import serial

def Fermeture ():
    print ('Fermeture')
    if tkMessageBox.askyesno ('Info', 'Sûr ?'):
        board.exit ()
        top.destroy ()

def OnStart ():
    print ('start')
    b1.config (state=Tkinter.DISABLED)
    led.write (1)
    b2.config (state=Tkinter.ACTIVE)

def OnStop ():
    print ('stop')
    b2.config (state=Tkinter.DISABLED)
    led.write (0)
    b1.config (state=Tkinter.ACTIVE)

port = '/dev/ttyACM0'
try:
    board = pyfirmata.Arduino (port)
    time.sleep (2)
except serial.SerialException as a:
    print e
    exit ()

led = board.get_pin ('d:3:o')
led.write (0)

top = Tkinter.Tk ()
top.title (u'LED potentiomètre')
top.minsize (200,30)
top.protocol ('WM_DELETE_WINDOW', Fermeture)

l = Tkinter.Label (top, text='Salut !')
l.pack ()
b1 = Tkinter.Button (top, text='Allumer', command=OnStart)
b1.config (state=Tkinter.ACTIVE)
b1.pack (side=Tkinter.LEFT)
b2 = Tkinter.Button (top, text='Eteindre', command=OnStop)
b2.config (state=Tkinter.DISABLED)
b2.pack (side=Tkinter.RIGHT)

try:
    top.mainloop()
except KeyboardInterrupt:
    board.exit ()
    top.destroy ()
