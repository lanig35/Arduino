#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from matplotlib import pyplot

pyplot.ion () # mode interactif
pData = [0] * 20
fig = pyplot.figure ()
pyplot.title (u'Affichage Température')
axes = pyplot.axes ()
l1, = pyplot.plot (pData)
pyplot.ylim ([-10,40])

# connexion serveur MQTT Mosquito
def on_connect (client, userdata, flags, rc):
    print "connecté avec code: {code}".format (code=str(rc))

def on_subscribe (client, userdata, mid, granted_qos):
    print "sub: {q}".format (q=str(granted_qos[0]))

def on_message (client, userdata, msg):
    print "msg: {t}:{p}".format (t=msg.topic, p=str(msg.payload))
    pData.append (float(msg.payload))
    pyplot.ylim ([-10,40])
    del pData [0]
    l1.set_xdata([i for i in xrange(20)])
    l1.set_ydata(pData) # update  the data
    pyplot.draw ()

def on_disconnect (client, userdata, rc):
    print "déconnecté: {code}".format (code=str(rc))

def on_log (client, userdata, level, buf):
    print "log:{l}-{b}".format (l=level, b=buf)

client = mqtt.Client (client_id='temp-plot', userdata='opaque')
client.will_set (topic='monitor/temp', payload='Bye', qos=0)

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_log = on_log

try:
    client.connect (host='127.0.0.1', port=1883)
except Exception as e:
    print e
    exit (1)

client.subscribe (topic='sensors/temp', qos=0)

rc = 0
while rc == 0:
	rc = client.loop ()
	# pour activer boucle évènement fenêtre
	pyplot.pause (1)

print ('Fin!')

