from rich import print

import sys

sys.path.insert(0, "../")

import robot_profile  # Module with network device configurations.

robot_topic_base = robot_profile.ROBOT_TOPIC_BASE

import config


def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    if memory.running_mode == "simulator":
        topic_base = config.SIMULATOR_TOPIC_BASE
    elif memory.running_mode == "robot":
        topic_base = robot_profile.ROBOT_TOPIC_BASE
    else:
        topic_base = config.TERMINAL_TOPIC_BASE

    if node.get("emotion") == "NEUTRAL":
        emoji = " 😐"
    elif node.get("emotion") == "ANGRY":
        emoji = " 😡"
    elif node.get("emotion") == "DISGUST":
        emoji = " 😖"
    elif node.get("emotion") == "FEAR":
        emoji = " 😧"
    elif node.get("emotion") == "HAPPY":
        emoji = " 😄"
    elif node.get("emotion") == "INLOVE":
        emoji = " 🥰"
    elif node.get("emotion") == "SAD":
        emoji = " 😔"
    elif node.get("emotion") == "SURPRISE":
        emoji = " 😲"

    print("[b white]State:[/] Setting the robot [b white]expression[/] to [b white]" + node.get("emotion") + emoji + "[/].")

    if topic_base != "TERMINAL":
        message = node.get("emotion")
        topic = "evaEmotion" # Para o FRED o tópico é "expression"
        client_mqtt.publish(topic_base + '/' + topic, message)

    return node # It returns the same node

