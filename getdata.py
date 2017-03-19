#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, platform, argparse
from util import util
sys.path.remove (os.getcwd())	# pour pb import serial sous Centos 6.x python 2.6

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description='Interface carte Arduino et broker MQTT',
                                  epilog='port série COM4 si Windows - /dev/ttyACM0 si Linux')
parser.add_argument ('--broker', '-b', default='127.0.0.1', help='MQTT broker address - default to localhost')
parser.add_argument ('--port', '-p', default=1883, type=int, help='MQTT broker port - default to 1883')
parser.add_argument ('--id', '-i', default='arduino', help='Id of MQTT client - default to Arduino')
parser.add_argument ('--user', '-u', default='arduino', help='username to log to MQTT broker')
parser.add_argument ('--debug', '-d', action='store_true', help='Enable MQTT tracing')
parser.add_argument ('--quiet', '-q', action='store_true', help='Disable console tracing')

args = parser.parse_args ()

# Gestion des logs
logger = util.init_log ('getdata', args.quiet)

# récupération mot de passe pour connexion MQTT broker
try:
	mqtt_passwd = os.environ['MQTT_PASSWD']
except KeyError as e:
	logger.error ('Please set MQTT_PASSWD environment variable')
	exit (1)
	
# import des librairies 
try:
	import serial
	import paho.mqtt.client as mqtt
except ImportError as e:
	logger.critical (e)
	exit (1)

# création objet Serial
ser = serial.Serial ()
ser.baudrate = 9600
ser.timeout = 10

# vérification OS pour nommage driver port série
platform_name = platform.system ()
if platform_name == 'Windows':
	ser.port = 'COM4'
elif platform_name == 'Linux':
	ser.port = '/dev/ttyACM0'
else:
	logger.critical ('Unsupported platform: {0}'.format (platform_name))
	exit (1)

logger.info ('Starting program - running on: {0}'.format (platform_name))

# définition call-backs MQTT Mosquito ('userdata' correspond au logger)
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
	userdata.warning ('unexpected MQTT msg: {t}:{p}'.format (t=msg.topic, p=str(msg.payload)))

def on_red (client, userdata, msg):
	userdata.info ('red led - action: {a}'.format (a=str(msg.payload)))
	ser.write ('R'+str(msg.payload)+'\n')
	
def on_blue (client, userdata, msg):
	userdata.info ('blue led - action: {a}'.format (a=str(msg.payload)))
	ser.write ('B'+str(msg.payload)+'\n')
	
def on_white (client, userdata, msg):
	userdata.info ('white led - action: {a}'.format (a=str(msg.payload)))
	ser.write ('W'+str(msg.payload)+'\n')
	
def on_tone (client, userdate, msg):
	userdata.info ('tone - action: {a}'.format (a=str(msg.payload)))
	ser.write ('P'+str(msg.payload)+'\n')
	
def on_disconnect (client, userdata, rc):
    userdata.info ('deconnected: {code}'.format (code=str(rc)))

def on_log (client, userdata, level, buf):
    userdata.info ('MQTT log: {l}-{b}'.format (l=level, b=buf))

# création du client MQTT, mise en place du 'will' et infos de connexion
client = mqtt.Client (client_id=args.id, clean_session=True, userdata=logger)
client.will_set (topic='monitor/arduino', payload='Aborting', qos=0, retain=True)
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

# démarrage boucle évènements MQTT
client.loop_start ()

# mise en place des abonnements et des callbacks associés
client.subscribe (topic='led/+', qos=0)
client.subscribe (topic='tone', qos=0)

client.message_callback_add (sub='led/red', callback=on_red)
client.message_callback_add (sub='led/blue', callback=on_blue)
client.message_callback_add (sub='led/white', callback=on_white)
client.message_callback_add (sub='tone', callback=on_tone)

# ouverture port série pour communication Arduino
try:
	ser.open()
except serial.SerialException as e:
	logger.critical (e)
	client.disconnect ()
	exit (1)
	
# boucle principale de traitement des messages sur ligne série Arduino
try:
	ser.flushInput ()
	ser.readline ()	# 1er buffer ignoré
	while True:
		msg = ser.readline ()
		if msg[0] == 't':
			data = msg.split (':')
			logger.info ('temperature: {t}'.format (t=float(data[1])))
			(rc, mid) = client.publish (topic='sensors/temp', payload=float(data[1]), qos=0, retain=False)
		elif msg[0] == 'p':
			data = msg.split (':')
			logger.info ('potentiometer: {p}'.format (p=int(data[1])))
			(rc, mid) = client.publish (topic='sensors/pot', payload=int(data[1]), qos=0, retain=False)
		else:
			logger.warning ('unexpected message from Arduino: {0}'.format (msg))
except KeyboardInterrupt as e:
	logger.info (e)
	ser.close ()
	client.disconnect ()
	logger.info ('Ending Program')

