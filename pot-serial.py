#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import struct
import argparse
#print sys.path
#print os.getcwd ()
#sys.path.remove ('/home/alain/Arduino')
sys.path.remove (os.getcwd())
import serial
import json
import requests
import paho.mqtt.client as mqtt

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

r = requests.post ('http://127.0.0.1:9200/sensors')
print r.status_code

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.connect (host='127.0.0.1')
client.loop_start()

count = 0

with serial.Serial () as s:
    s.baudrate = 9600
    s.timeout = args.delai 
    s.port = '/dev/ttyACM0'
    s.open ()
    print s.isOpen()
    print s.name
    s.flushInput ()

    try:
        while True:
            pot = s.read (1)
            print type(pot) # string
            if len (pot) == 0:
                break
            print pot # erreur
            d = struct.unpack ('B', pot[0])[0]
            print d
            print pot[0] # erreur
            print ord(pot[0])
            client.publish (topic='sensors/pot', payload=ord(pot[0]))
            payload = {
               'value' : ord(pot[0])
            }
            param = {'ttl': '5s'}
            r = requests.post ('http://127.0.0.1:9200/sensors/pot', 
                               params=param,
                               data=json.dumps (payload))
            print r.status_code
            if r.status_code != 201:
                print r.status_code
                print r.text
                exit (0)
            count+=1
            if count >= 5:
                break
    except KeyboardInterrupt as e:
        s.close ()
        print ('Bye!')

    print ('Arret Capture')
