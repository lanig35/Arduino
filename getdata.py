import serial
import json

/* penser au context manager with */
ser = serial.Serial (port='COM4', baudrate=9600, timeout=10)

table = {}
ser.reset_input_buffer()
/* lecture 1er buffer non traite */
ser.readline ()

while True:
    /* attention gestion du timeout */
    data = msg.rstrip().split ('-')
    table['temp'] = float (val(0))
    table ['lum'] = int(val[1])
    table['pot']=int(val[2])
    print (json.dumps (table))
