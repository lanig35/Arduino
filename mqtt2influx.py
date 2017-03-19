#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-
import os, logging, logging.handlers, argparse, time
try:
	import requests
	import paho.mqtt.client as mqtt
except ImportError as e:
	print (e)
	exit (1)

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description='Plot temperature')
parser.add_argument ('--broker', '-b', default='127.0.0.1', help='MQTT broker address - default to localhost')
parser.add_argument ('--port', '-p', default=1883, type=int, help='MQTT broker port - default to 1883')
parser.add_argument ('--id', '-i', default='plot', help='Id of MQTT client - default to plot')
parser.add_argument ('--log', '-l', action='store_true', help='Enable MQTT tracing')
parser.add_argument ('--quiet', '-q', action='store_true', help='Disable console tracing')
parser.add_argument ('--user', '-u', default='plot', help='username to connect to MQTT broker')

args = parser.parse_args ()

# Gestion des logs
logger = logging.getLogger ('plot')
logger.setLevel (logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler (filename='log/mqttinflux.log', mode='a',
                                                     maxBytes=100000, backupCount=5,
                                                     encoding='utf8', delay=False)
file_handler.setLevel (logging.INFO)
formatter = logging.Formatter (fmt='%(asctime)s;%(name)s;%(levelname)s;%(message)s',
                               datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter (formatter)
logger.addHandler (file_handler)

if args.quiet is False:
	stream_handler = logging.StreamHandler ()
	stream_handler.setLevel (logging.DEBUG)
	logger.addHandler (stream_handler)

# mise en place call-backs MQTT Mosquito ('userdata' correspond au logger)
def on_connect (client, userdata, flags, rc):
	if rc != 0:
		userdata.critical ('MQTT connexion error: {code}'.format(code=str(rc)))
		exit (1)
	userdata.info ('MQTT connexion success')

def on_subscribe (client, userdata, mid, granted_qos):
    userdata.info ('subscribe: {q} - {m}'.format (q=str(granted_qos[0]), m=str(mid)))

def on_message (client, userdata, msg):
	userdata.info ('msg: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))
	params = {'db': 'test'}
	data = 'temp,sensor=home value={0}'.format (msg.payload)
	r = requests.post ('http://127.0.0.1:8086/write', params=params, data=data)
	print str(r.status_code) +': ' + r.text

def on_disconnect (client, userdata, rc):
	userdata.info ('deconnected: {code}'.format (code=str(rc)))
	
def on_log (client, userdata, level, buf):
    userdata.info ('MQTT log: {l}-{b}'.format (l=level, b=buf))

# création du client MQTT et mise en place du 'will'
client = mqtt.Client (client_id=args.id, clean_session=True, userdata=logger)
client.will_set (topic='monitor/mqtt2influx', payload='Aborting', qos=0, retain=True)

# mise en place des call-backs
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
if args.log is True:
	client.on_log = on_log

# création base influxdb
#params = {'q': 'CREATE DATABASE test'}
#r = requests.post ('http://127.0.0.1:8086/query', params=params)
#print str(r.status_code) + ': ' + r.text

# connection au broker MQTT
try:
	mqtt_passwd = os.environ['MQTT_PASSWD']
except KeyError as e:
	print e
	exit (1)
client.username_pw_set (username=args.user, password=mqtt_passwd)

try:
	client.connect (host=args.broker, port=args.port, keepalive=60)
except IOError as e:
	logger.critical (e)
	exit (1)

# abonnement température
client.subscribe (topic='sensors/temp', qos=0)

# boucle évènements
try:
	rc = 0
	while rc == 0:
		rc = client.loop ()
		time.sleep (0.5)
	logger.error ('broker error - {0}'.format (str(rc)))
except KeyboardInterrupt as e:
	logger.info (e)
	client.disconnect ()
	logger.info ('Ending Program')

