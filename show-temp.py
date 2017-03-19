#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, argparse
from util import util

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description='Plot temperature')
parser.add_argument ('--broker', '-b', default='127.0.0.1', help='MQTT broker address - default to localhost')
parser.add_argument ('--port', '-p', default=1883, type=int, help='MQTT broker port - default to 1883')
parser.add_argument ('--id', '-i', default='plot', help='Id of MQTT client - default to plot')
parser.add_argument ('--user', '-u', default='plot', help='username to log to MQTT broker')
parser.add_argument ('--debug', '-d', action='store_true', help='Enable MQTT tracing')
parser.add_argument ('--quiet', '-q', action='store_true', help='Disable console tracing')

args = parser.parse_args ()

# Gestion des logs
logger = util.init_log ('plot', args.quiet)

# récupération mot de passe pour connexion MQTT broker
try:
	mqtt_passwd = os.environ['MQTT_PASSWD']
except KeyError as e:
	logger.error ('Please set MQTT_PASSWD environment variable')
	exit (1)
	
# import des librairies 
try:
	import paho.mqtt.client as mqtt
	from matplotlib import pyplot
except ImportError as e:
	logger.critical (e)
	exit (1)

# mise en place call-backs MQTT Mosquito ('userdata' correspond au logger)
def on_connect (client, userdata, flags, rc):
	if rc != 0:
		if rc == 1:
			userdata.error ('MQTT connexion Error: incorrect protocol')
		elif rc == 2:
			userdata.error ('MQTT connexion Error: invalid client identifier')
		elif rc == 3:
			userdata.critical ('MQTT connexion Error: server unavailable')
		elif rc == 4:
			userdata.error ('MQTT connexion Error: bad username or password')
		elif rc == 5:
			userdata.error ('MQTT connexion Error: not authorized')
		else:
			userdata.critical ('MQTT connexion error: {code}'.format(code=str(rc)))
		exit (1)
	userdata.info ('MQTT connexion success')

def on_subscribe (client, userdata, mid, granted_qos):
    userdata.info ('subscribe: {q} - {m}'.format (q=str(granted_qos[0]), m=str(mid)))

def on_message (client, userdata, msg):
	userdata.info ('msg: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))
	pData.append (float(msg.payload))
	pyplot.ylim ([-10,40])
	del pData [0]
	l1.set_xdata([i for i in xrange(20)])
	l1.set_ydata(pData) # update  the data
	pyplot.draw ()

def on_disconnect (client, userdata, rc):
    userdata.info ('deconnected: {code}'.format (code=str(rc)))

def on_log (client, userdata, level, buf):
    userdata.info ('MQTT log: {l}-{b}'.format (l=level, b=buf))

# création du client MQTT et mise en place du 'will'
client = mqtt.Client (client_id=args.id, clean_session=True, userdata=logger)
client.will_set (topic='monitor/plot', payload='Aborting', qos=0, retain=True)
client.username_pw_set (username=args.user, password=mqtt_passwd)

# mise en place des call-backs
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
if args.debug is True:
	client.on_log = on_log

# tentative connection au broker MQTT
try:
    client.connect (host=args.broker, port=args.port, keepalive=60)
except IOError as e:
	logger.critical (e)
	exit (1)

		
# mise en place graphique
pyplot.ion () # mode interactif
pData = [0] * 20
fig = pyplot.figure ()
pyplot.title (u'Affichage Température')
axes = pyplot.axes ()
l1, = pyplot.plot (pData)
pyplot.ylim ([-10,40])

# abonnement température
client.subscribe (topic='sensors/temp', qos=0)

# boucle évènements
try:
	rc = 0
	while rc == 0:
		rc = client.loop ()
		# pour activer boucle évènement fenêtre
		pyplot.pause (1)
	logger.error ('broker error - {0}'.format (str(rc)))
except KeyboardInterrupt as e:
	logger.info (e)
	client.disconnect ()
	logger.info ('Ending Program')

