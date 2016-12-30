#!/usr/bin/env python
#coding: utf-8
# -*- coding: utf-8 -*-
import sys, os, platform, argparse
import logging, logging.handlers
sys.path.remove (os.getcwd())	# pour pb import serial sous Centos 6.x python 2.6

try:
	import serial
	import paho.mqtt.client as mqtt
except ImportError as e:
	print (str(e).encode('utf8'))
	exit (1)

# gestion des options en ligne de commande
parser = argparse.ArgumentParser (description='Interface carte Arduino et broker MQTT',
								   epilog='port série COM4 si Windows - /dev/ttyACM0 si Linux')
parser.add_argument ('--broker', '-b', default='127.0.0.1', help='MQTT broker address - default to localhost')
parser.add_argument ('--port', '-p', default=1883, type=int, help='MQTT broker port - default to 1883')
parser.add_argument ('--id', '-i', default='arduino', help='Id of MQTT client - default to Arduino')
parser.add_argument ('--log', '-l', action='store_true', help='Enable MQTT tracing')
parser.add_argument ('--quiet', '-q', action='store_true', help='Disable console tracing')

args = parser.parse_args ()
print args

# Gestion des logs
logging.basicConfig (level=logging.DEBUG)
logger = logging.getLogger ('getdata')
file_handler = logging.handlers.RotatingFileHandler (filename='log/getdata.log', mode='a',
													 maxBytes=10000, backupCount=5,
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

# création objet Serial pour utilisation call-back MQTT
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

# mise en place call-backs MQTT Mosquito ('userdata' correspond au logger)
def on_connect (client, userdata, flags, rc):
	if rc != 0:
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

# création du client MQTT et mise en place du 'will'
client = mqtt.Client (client_id=args.id, clean_session=True, userdata=logger)
client.will_set (topic='monitor/arduino', payload='Aborting', qos=0, retain=True)

# mise en place des call-backs
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
if args.log is True:
	client.on_log = on_log

# tentative connection au broker MQTT
try:
    client.connect (host=args.broker, port=args.port, keepalive=60)
except IOError as e:
	logger.critical (e.strerror.decode ('latin_1'))
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
			client.publish (topic='sensors/temp', payload=float(data[1]), qos=0, retain=False)
		elif msg[0] == 'p':
			data = msg.split (':')
			logger.info ('potentiometer: {p}'.format (p=int(data[1])))
			client.publish (topic='sensors/pot', payload=int(data[1]), qos=0, retain=False)
		else:
			logger.warning ('unexpected message from Arduino: {0}'.format (msg))
except KeyboardInterrupt as e:
	logger.info (e)
	ser.close ()
	client.disconnect ()
	logger.info ('Ending Program')

