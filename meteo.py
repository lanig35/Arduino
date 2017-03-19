#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os, platform, time, argparse
import xml.dom.minidom as xml

# recupération arguments ligne de commande
parser = argparse.ArgumentParser (description=u'Interface Station Météo')
parser.add_argument ('--delai', metavar='d', default=120, type=int, help=u'délai entre 2 consultations du site météo')

args = parser.parse_args ()

# import librairies specifiques
try:
    import serial
    import requests
except ImportError as e:
    print (e)
    exit (1)

# creation objet Serial pour dialogue Arduino
ser = serial.Serial ()
ser.baudrate = 9600

# verification plate-forme
platform_name = platform.system ()
if platform_name == 'Windows':
    ser.port = 'COM4'
elif platform_name == 'Linux':
    ser.port = '/dev/ttyACM0'
else:
    print ('Platforme {0} non supportée'.format (platform_name))
    exit (1)

# ouverture port série et attent 5 Secondes car provoque reset carte Arduino
try:
    ser.open ()
    time.sleep (5)
except serial.SerialException as e:
    print (e)
    exit (1)

# recuperation meteo de Rennes
rennes = 'http://www.infoclimat.fr/public-api/gfs/xml?_ll=48.11198,-1.67429&_auth=AhgDFAR6UHJXelViVCJSe1U9DzpbLQMkUy8EZ1o%2FXyIJa186VTdcNwViWicFKgsiUGIHeQA5BDtTNFYzDWkDfwJ%2BA2UEblA6VztVPlRtUmZVeQ9wW3kDOlMvBHxaPl8%2BCXRfOlU1XDcFdFo5BTwLN1B9B2YAOwQ4Uy9WLg1hA2QCaQNuBGJQNVc8VTBUZlJnVXkPcFthAzNTYwRqWjZfbgluXzpVZFw2BW9aMQVgCz5QfQdnADYEOVM5VjENaQNhAmADeAR4UEtXS1UqVCRSJFUzDylbeQNuU24ENw%3D%3D&_c=f65c235031630e0ab549b3f92326c4cb'

#proxies = {
#        'http': '135.245.192.7:8000',
#        'https': '135.245.192.7:8000'
#        }

try:
    while True:
        # interrogation site méteo
        # r = requests.get (rennes, proxies=proxies)
        r = requests.get (rennes)

        if r.status_code != 200:
            print (r.text)
        else:
            # TODO: analyse code requete XML

            # sauvegarde donnees XML dans un fichier
            with open ('data.xml', 'w') as f:
                f.write (r.content)
                f.close ()

            # analyse XML
            DomTree = xml.parse ('data.xml')
            previsions = DomTree.documentElement

            temperature = 0.0
            pluie = 0.0

            # parcours structure XML
            echeances = previsions.getElementsByTagName ('echeance')
            for item in echeances:
                if item.getAttribute ('hour') == '24':
                    temp = item.getElementsByTagName ('temperature')[0]
                    levels = temp.getElementsByTagName ('level')
                    for level in levels:
                        if level.getAttribute ('val') == '2m':
                            temperature = float(level.childNodes[0].data) - 273.15
                    eau = item.getElementsByTagName ('pluie')[0]
                    if eau.getAttribute ('interval') == '3h':
                        pluie = float (eau.childNodes[0].data)
    
            print ('T: {0} - P: {1}'.format (str(temperature), str(pluie)))
            
            # ecriture donnees liaison série Arduino
            ser.write (bytes(temperature))
            ser.write (':')
            ser.write (bytes(pluie))

        # attente entre 2 consultations site météo
        time.sleep (args.delai)

except KeyboardInterrupt as e:
    ser.close ()
    print ('Fin du programme')

