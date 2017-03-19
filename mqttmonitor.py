#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os, argparse, time
from util import util

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description='MQTT metrics gateway to InfluxDB')
parser.add_argument ('--broker', '-b', default='127.0.0.1', help='MQTT broker address - default to localhost')
parser.add_argument ('--port', '-p', default=1883, type=int, help='MQTT broker port - default to 1883')
parser.add_argument ('--id', '-i', default='monitor', help='Id of MQTT client - default to monitor')
parser.add_argument ('--user', '-u', default='monitor', help='username to connect to MQTT broker')
parser.add_argument ('--debug', '-d', action='store_true', help='Enable MQTT tracing')
parser.add_argument ('--quiet', '-q', action='store_true', help='Disable console tracing')

args = parser.parse_args ()

# initialisation des logs
logger = util.init_log ('mqttmonitor', args.quiet)

# import des librairies 
try:
	import requests
	import paho.mqtt.client as mqtt
except ImportError as e:
	logger.error (e)
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
	
def on_bytes (client, userdata, msg):
	userdata.info ('bytes: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))
	if msg.topic.find ('sent') >= 0:
		data = 'bytes,direction=sent value={0}'.format (msg.payload)
	elif msg.topic.find ('received') >= 0:
		data = 'bytes,direction=received value={0}'.format (msg.payload)
	else:
		userdata.error ('unexpected topic: {t}'.format (t=msg.topic))
		data = None
	
	if data is not None:
		params = {'db': 'mqtt'}
		r = requests.post ('http://127.0.0.1:8086/write', params=params, data=data)
		if r.status_code != 204:
			userdata.warning ('influxdb: error {0} - {1}'.format (str(r.status_code), r.text))

def on_publish (client, userdata, msg):
	userdata.info ('bytes: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))
	if msg.topic.find ('dropped') >= 0:
		data = 'publish,direction=dropped value={0}'.format (msg.payload)
	elif msg.topic.find ('received') >= 0:
		data = 'publish,direction=received value={0}'.format (msg.payload)
	elif msg.topic.find ('sent') >= 0:
		data = 'publish,direction=sent value={0}'.format (msg.payload)
	else:
		userdata.error ('unexpected topic: {t}'.format (t=msg.topic))
		data = None
	
	if data is not None:
		params = {'db': 'mqtt'}
		r = requests.post ('http://127.0.0.1:8086/write', params=params, data=data)
		if r.status_code != 204:
			userdata.warning ('influxdb: error {0} - {1}'.format (str(r.status_code), r.text))	

def on_msg (client, userdata, msg):
	userdata.info ('message: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))
	if msg.topic.find ('sent') >= 0:
		data = 'messages,direction=sent value={0}'.format (msg.payload)
	elif msg.topic.find ('received') >= 0:
		data = 'messages,direction=received value={0}'.format (msg.payload)
	else:
		userdata.error ('unexpected topic: {t}'.format (t=msg.topic))
		data = None
	
	if data is not None:
		params = {'db': 'mqtt'}
		r = requests.post ('http://127.0.0.1:8086/write', params=params, data=data)
		if r.status_code != 204:
			userdata.warning ('influxdb: error {0} - {1}'.format (str(r.status_code), r.text))
	
def on_disconnect (client, userdata, rc):
	userdata.info ('deconnected: {code}'.format (code=str(rc)))
	
def on_log (client, userdata, level, buf):
    userdata.info ('MQTT log: {l}-{b}'.format (l=level, b=buf))

# récupération mot de passe pour connexion MQTT broker
try:
	mqtt_passwd = os.environ['MQTT_PASSWD']
except KeyError as e:
	logger.error ('Please set MQTT_PASSWD environment variable')
	exit (1)
	
# création du client MQTT et mise en place du 'will'
client = mqtt.Client (client_id=args.id, clean_session=True, userdata=logger)
client.will_set (topic='monitor/monitor', payload='Aborting', qos=0, retain=True)
client.username_pw_set (username=args.user, password=mqtt_passwd)

# mise en place des call-backs
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
if args.debug is True:
	client.on_log = on_log

# création base influxdb
params = {'q': 'CREATE DATABASE mqtt WITH DURATION 2d NAME mqttmon'}
r = requests.post ('http://127.0.0.1:8086/query', params=params)
if r.status_code != 204:
	logger.error (r.text)

# connection au broker MQTT
try:
	client.connect (host=args.broker, port=args.port, keepalive=60)
except IOError as e:
	logger.critical (e)
	exit (1)

# abonnement métriques broker
client.subscribe (topic='$SYS/broker/load/bytes/+/1min')
client.subscribe (topic='$SYS/broker/load/messages/+/1min')
client.subscribe (topic='$SYS/broker/load/publish/+/1min')

client.message_callback_add (sub='$SYS/broker/load/bytes/+/1min', callback=on_bytes)
client.message_callback_add (sub='$SYS/broker/load/messages/+/1min', callback=on_msg)
client.message_callback_add (sub='$SYS/broker/load/publish/+/1min', callback=on_publish)

logger.info ('Starting program')

# boucle évènements
try:
	client.loop_forever ()
except KeyboardInterrupt as e:
	logger.info (e)
	client.disconnect ()
	logger.info ('Ending Program')

