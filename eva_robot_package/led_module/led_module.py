from paho.mqtt import client as mqtt_client

import sys

import time

from rich import print

sys.path.insert(0, "../")

import config

import robot_profile  # Module with network device configurations.

robot_topic_base = robot_profile.ROBOT_TOPIC_BASE


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """
    if memory.running_mode == "simulator":
        topic_base = config.SIMULATOR_TOPIC_BASE
    elif memory.running_mode == "robot":
        topic_base = robot_profile.ROBOT_TOPIC_BASE
    else:
        topic_base = config.TERMINAL_TOPIC_BASE
        
    print("[b white]State: Setting [/]the robot [b white]LEDs[/] to the animation/color [bold]" + node.get("animation") + "![/].")

    message = node.get("animation")
    

    if topic_base != "TERMINAL":
        client_mqtt.publish(topic_base + '/' + "leds", "STOP") # Apesar da node.tag ser "led" o tópico definido ficou "leds".
        time.sleep(0.1)
        client_mqtt.publish(topic_base + '/' + "leds", message) # Apesar da node.tag ser "led" o tópico definido ficou "leds".

    return node # It returns the same node