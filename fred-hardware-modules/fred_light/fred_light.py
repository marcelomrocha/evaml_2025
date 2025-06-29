# Software developed by Marcelo Marques da Rocha
# MidiaCom Laboratory - Universidade Federal Fluminense
# This work was funded by CAPES and Google Research

# From time to time, it appears that the lamp disconnects and does not respond to a command, failing...
# Just responding to the following command...
# It seems to me that it is a problem with the lamp and not this software...

import socket
from paho.mqtt import client as mqtt_client
import time

import sys
import os

# # Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import config # Module with network device configurations.
import robot_profile

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = robot_profile.ROBOT_TOPIC_BASE

SMARTBULB_IP = config.SMART_BULB_IP_ADRESS
SMARTBULB_PORT = config.SMART_BULB_PORT

COLOR_TABLE = {
    "RED"   : "FF0000",
    "GREEN" : "00FF00",
    "BLUE"  : "0000FF",
    "YELLOW": "FFFF00",
    "PINK"  : "FF00FF",
    "WHITE" : "FFFFFF",
    "BLACK" : "000000"
}


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(topic_base + '/light', 1), ])
    print("Smart Bulb Module - Connected.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SMARTBULB_IP, SMARTBULB_PORT))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    bulb_color = ""
    if msg.topic == topic_base + '/light':
        client.publish(topic_base + '/syslog', 'Controlling the Smart Bulb (color|state): ' + msg.payload.decode())
        color = msg.payload.decode().split("|")[0]
        if color == "": color = "000000"
        state = msg.payload.decode().split("|")[1]

        if color in COLOR_TABLE:
            bulb_color = str(int(COLOR_TABLE[color], 16))
        else:
            bulb_color = str(int(color, 16))
            
        if state == "OFF":
            # off command
            s.sendall('{"id":1, "method":"set_power","params":["off", "smooth", 0]}\r\n'.encode())
        elif state == "ON":
            # on command
            s.sendall('{"id":1, "method":"set_power","params":["on", "smooth", 0]}\r\n'.encode())
            time.sleep(0.1) # parece precisar de um tempo para enviar os dois comandos seguidos
            s.sendall(('{"id":1,"method":"set_rgb","params":[' + bulb_color + ', "smooth", 0]}\r\n').encode())

                
        

# Run the MQTT client thread.
client = mqtt_client.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect(broker, port)
except:
    print ("Unable to connect to Broker.")
    exit(1)

client.loop_forever()
