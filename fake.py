import struct
import time
import serial
ser = serial.Serial ()
ser.baudrate = 9600
ser.port = 'COM4'

ser.open ()

time.sleep (5)

temperature = -2
pluie = 1
data = struct.pack ('f', temperature)
ser.write (bytes(temperature))
ser.write (':')
ser.write (bytes(pluie))

ser.close ()
