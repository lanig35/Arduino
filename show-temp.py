#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt

# connexion serveur MQTT Mosquito
def on_connect (client, userdata, flags, rc):
    print "connecté avec code: {code}".format (code=str(rc))

def on_subscribe (client, userdata, mid, granted_qos):
    print ("sub: " + granted_qos[0])

def on_message (client, userdata, msg):
    print msg.topic

def on_disconnect (client, userdata, rc):
    print "déconnecté: {code}".format (code=str(rc))

def on_log (client, userdata, level, buf):
    print "log: {c}-{l}-{b}".format (c=client, l=level, b=buf)

client = mqtt.Client (client_id='temp', userdata='opaque')
client.will_set (topic='monitor/temp', payload='Bye', qos=0)

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_log = on_log

try:
    client.connect (host='127.0.0.1', port=1883, bind_address='127.0.0.1')
except Exception as e:
    print e
    exit (1)

client.subscribe (topic='sensors/temp', qos=0)

rc = 0
while rc == 0:
    rc = client.loop ()

print ('Fin!')

