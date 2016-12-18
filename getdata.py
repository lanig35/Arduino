#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.remove (os.getcwd())
import serial
import json
import paho.mqtt.client as mqtt

# connexion serveur MQTT Mosquito
def on_connect (client, userdata, flags, rc):
    print "connecté avec code: " + str(rc)

client = mqtt.Client ()
client.on_connect = on_connect
client.connect (host='127.0.0.1')
client.loop_start ()

# penser au context manager 'with'
#ser = serial.Serial (port='COM4', baudrate=9600, timeout=10)
with serial.Serial (port='/dev/ttyACM0', baudrate=9600, timeout=10) as ser:
    ser.flushInput ()
    # 1er buffer non traité
    ser.readline ()
    table = {'temp': 0.0, 'lum': 0, 'pot': 0}
    try:
        while True:
            msg = ser.readline ()   # ajouter traitement timeout
            data = msg.rstrip().split ('-')
            table['temp'] = float (data[0])
            table ['lum'] = int(data[1])
            table['pot']=int(data[2])
            print (json.dumps (table))

            # publication MQTT
            client.publish (topic='sensors/pot', payload=table['pot'])
            client.publish (topic='sensors/temp', payload=table['temp'])
            client.publish (topic='sensors/lum', payload=table['lum'])
    except KeyboardInterrupt as e:
        print (e)
        ser.close ()

    print ('Arrêt capture')

