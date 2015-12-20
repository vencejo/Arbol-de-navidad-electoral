#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  arbolDeNavidadElectoral.py
#  
#  Copyright 2015  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


from bibliopixel.drivers.serial_driver import *
from bibliopixel.led import *
import bibliopixel.colors as colors
import time
import collections
import datetime
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('datosCuentaTwitter.ini')

APP_KEY = config.get('DatosTwitter','APP_KEY')
APP_SECRET = config.get('DatosTwitter','APP_SECRET')
OAUTH_TOKEN = config.get('DatosTwitter','OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = config.get('DatosTwitter','OAUTH_TOKEN_SECRET')

terminosDeBusqueda = 'pp,psoe,podemos,ciudadanos'
tweets = collections.Counter({'psoe':0, 'pp':0, 'podemos':0,'ciudadanos':0})
color = {"psoe":colors.Red, "ciudadanos":colors.Orange, "pp":colors.Blue, "podemos":colors.Purple}
tiempoIluminacion = {"psoe":6, "ciudadanos":6, "pp":1, "podemos":1}

intervaloIluminacion = 16 #Segundos
inicioAnalisis = datetime.datetime.now()
intervaloAnalisis = datetime.timedelta(minutes=59) 

class MyListener(StreamListener):
 
    def on_status(self, tweet):
        tweetConjunto = set(tweet.text.lower().split(" "))
        conjuntoTerminosDeBusqueda = set(terminosDeBusqueda.split(","))
        interseccion = tweetConjunto & conjuntoTerminosDeBusqueda
        tweets.update(interseccion)
        
            
    def on_error(self, status_code):
        if status_code == 420:
            return False


auth = tweepy.OAuthHandler(APP_KEY, APP_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    
twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=[terminosDeBusqueda], async=True )

driver = DriverSerial(num = 50, type = LEDTYPE.WS2811_400)
led = LEDStrip(driver)
led.setMasterBrightness(225)


while True:
	# Reinicio del analisis de Twitter cada x minutos (59 en el ejemplo)
    ahora = datetime.datetime.now()
    tiempoTranscurrido = ahora - inicioAnalisis
    if tiempoTranscurrido > intervaloAnalisis: # Vuelvo a comenzar otro analisis de 59 min
		inicioAnalisis = datetime.datetime.now()
		tweets.clear() 

	# Impresion de los datos en el terminal
    print("")
    print("*"*72)
    print "Tiempo transcurrido en el analisis: "+str(tiempoTranscurrido)[:7]
    print("")
    print "Tweets: "
    print tweets
    print("")
    print "Tiempos de iluminacion (seg): "
    print tiempoIluminacion
    print("*"*72)
    print("")

    # Calculo de los tiempos de iluminacion correspondientes por partido
    tweetsTotales = sum(tweets.values())
    if tweetsTotales == 0:
		continue
		
    for partido in color.keys():
		tiempoIluminacion[partido] = (tweets[partido]*1.0/(tweetsTotales))*intervaloIluminacion

    # Iluminacion de la matriz de leds
    for partido in color.keys():
			led.fillRGB(*color[partido]) #Hay que extender la tupla con *
			led.update()
			time.sleep(tiempoIluminacion[partido])
			
    
    


	
			
		
