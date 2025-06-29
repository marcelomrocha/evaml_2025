from paho.mqtt import client as mqtt_client

import tkinter as tk
from tkinter import messagebox
from tkinter import *

import sys

import platform 

import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # Module with network device configurations.

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = config.SIMULATOR_TOPIC_BASE


# Cria a janela do módulo
janela = Tk()
janela.title("TTS Msg")
janela.geometry('193x65')
#fotofundo
back = Label(janela)
back.la = PhotoImage(file = 'sim_tts_msg/images/tts_msgbox.png')
back['image'] = back.la
back.place(x=0,y=0)


# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    client.subscribe(topic=[(topic_base + '/talk', 1), ])
    print("SIM - TTS - MsgBox - Connected.")
            

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    text = msg.payload.decode().split("|")[1]

    
    messagebox.showinfo("The robot is speaking...", text)
    client.publish(topic_base + "/robot_response", "state|free", qos=2) # Libera o robô.





# Run the MQTT client thread.
client = mqtt_client.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect(broker, port)
except:
    print ("Unable to connect to Broker.")
    exit(1)

# You cannot use the "forever" method (as in other modules) because it blocks not allowing
# for the graphical interface thread loop to execute.
client.loop_start()

janela.mainloop()
