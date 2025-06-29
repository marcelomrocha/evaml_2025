import sys

import os


from rich import print
from rich.console import Console

from lxml import etree as ET

from auxiliar_module import identify_targets, import_modules

import robot_memory as memory

import config

sys.path.append(os.getcwd() + "/" + "robot_package/")

import robot_profile


console = Console()

broker = config.MQTT_BROKER_ADRESS # broker adress
port = config.MQTT_PORT # broker port


file_name  = sys.argv[1]

tree = ET.parse(sys.argv[1])  # XML code file
root = tree.getroot() # script root node
settins_node = root.find("settings")
script_node = root.find("script")



# Versão iterativa do player. Agora o XML é lido de maneira iterativa, sem recursão.
def run_script(xml_root):
    node = xml_root[0]

    while True: # Roda até ser interrompido por um break.
        if node == None: # None significa o fim de um um nível, onde não existe mais um nó irmão.
            if len(memory.node_stack) != 0: # Se tem elemento na pilha.
                node = memory.node_stack.pop()
            else:
                break

        # Processa os nós que têm filhos.
        elif len(node) > 0:
            if node.tag == "switch":
                if node.getnext() != None: # O nó "switch" tem um irmão adiante.
                    memory.node_stack.append(node.getnext()) # Nó que será executado após o retorno do <switch>.
                mod = memory.tab_modules[node.tag][2]
                node = eval('mod.node_processing')(node, memory, client_mqtt) # Executa o <switch> colocando seu operador na memória.
                node = node[0] # Primeiro <case> do <switch>

            elif node.tag == "case":
                # Um case só executa se houver um operador do switch na memória.
                if memory.op_switch != None: # Deve haver um operador do switch na memória. None indica que um case verdadeiro já ocorreu neste switch
                    mod = memory.tab_modules[node.tag][2]
                    node = eval('mod.node_processing')(node, memory, client_mqtt) # Executa o elemento <case> comparando com o operador (do switch) na memória. O result. da comparação fica em memory.flag_case.
                    if memory.flag_case == True:
                        memory.flag_case = False
                        memory.op_switch = None
                        node = node[0] # Executa o primeiro nó do elemento composto <case> (True).
                    else:
                        # Tenta buscar o case seguinte ou o default.
                        # Senão encontrar, node será None.
                        node = node.getnext() 
                else:
                    # if len(memory.node_stack) != 0:
                    node = node = node.getnext() 

            elif node.tag == "default" and memory.op_switch != None: # Se chegou aqui... então executa!
                mod = memory.tab_modules[node.tag][2]
                node = eval('mod.node_processing')(node, memory, client_mqtt)
                node = node[0] # Primeiro nó do <Default>
            
            else:
                node = node.getnext()

        else: # Execução de nós comuns.
            # Alguns casos de nós especiais.
            if node.tag == "goto":
                mod = memory.tab_modules[node.tag][2]
                node = eval('mod.node_processing')(node, memory, client_mqtt) # Executa o <goto> que retorna o nó destino (target).
                node_target = node # Armazena o target do goto.
                # Com a execução sendo direcionada para o nó "target" do <goto>
                # Os nós na pilha de endereços de retorno podem perder o significado, caso o goto direcione
                # a execução para um nó destino que pertence a um outro pai, dieferente do pai do goto.
                # É preciso zerar a pilha e inserir novos nó que são os pais do nó "target"?.
                memory.node_stack = []

                # Primeiro elemento da node_stack deve ser o próprio node target.
                memory.node_stack.append(node_target)
                node = node_target.getparent()

                # Busca pelos pais do node target.
                # Cases não são considerados, pois para se executar um case é preciso ter informação do switch que seria o pai dos cases.
                # Sendo assim, os switchs são considerados na busca pelos pais e por último o root (script).
                # As macros também são considerdas como pais dos seus grupos de comandos, mas não....
                while node.tag != "script" and node.tag != "macro":
                    if node.tag == "switch":
                        if node.getnext() == None:
                            node = node.getparent()
                        else:
                            memory.node_stack.append(node.getnext())
                            node = node.getparent()
                    else:
                        node = node.getparent()

                memory.node_stack.reverse()
                node = None # Vai forçar a leitura da node_stack.

            elif node.tag == "useMacro": # Tratando elemento <useMacro>
                if node.getnext() != None: # O nó "useMacro" tem um irmão adiante.
                    memory.node_stack.append(node.getnext()) # Nó que será executado após o retorno do <useMacro>.
                
                mod = memory.tab_modules[node.tag][2]
                node = eval('mod.node_processing')(node, memory, client_mqtt) # Executa o <useMacro> que retorna o nó "macro".
                node = node[0] # Primeiro nó  dentro da "macro"

            else:
                mod = memory.tab_modules[node.tag][2]
                node = eval('mod.node_processing')(node, memory, client_mqtt)
                if node.tag == "stop":
                    break
                node = node.getnext() # Chama o próximo irmão do no corrente.



console.clear()

# Lendo as flags da linha de comando.
if len(sys.argv) == 2: # Sem flags. Executar em modo default=sim.
    print("You didn't use any flag. Running in default (Simulator) mode.")
else:
    for flag_param in sys.argv[2:]:
        flag = flag_param.split("=")[0]
        param = flag_param.split("=")[1]
    if flag.lower() == "-r": # A flag -r define a variável RUNNING_MODE podendo assumir os valores "simulator", "terminal" ou "robot".
        if param.lower() == "simulator":
            memory.running_mode = 'simulator'
        elif param.lower() == "robot":
            memory.running_mode = 'robot'
        elif param.lower() == "terminal":
            memory.running_mode = 'terminal'
        else:
            print("[b blink reverse red] It was not possible to understand the -r option: [u]" + param + " [/]")
            exit(1)

if memory.running_mode == "simulator":
    topic_base = config.SIMULATOR_TOPIC_BASE
elif memory.running_mode == "robot":
    topic_base = robot_profile.ROBOT_TOPIC_BASE
else:
    topic_base = config.TERMINAL_TOPIC_BASE

# Esta parte é responsável por receber as respostas do robô físico através do tópico robot_response.
# O tópico recebe uma mensagem vinda do robô que tem duas partes, um tipo e uma mensagem.
# O tipo pode ser "state", com uma mensagem "free", ou um tipo "var", com um valor de retorno do robô (expressão facial, testo do STT etc). 
# Configuração do MQTT
from paho.mqtt import client as mqtt_client
# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(topic=[(topic_base + '/robot_response', 1), ])


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == topic_base + '/robot_response': # Recebe uma resposta dos módulos que controlam o hardware do robô físco.
        type, message = msg.payload.decode().split("|")
        if type == "state":
            memory.robot_state = message #
        else:
            memory.robot_response = message #
            memory.robot_state = "free"
        

# # Run the MQTT client thread.
client_mqtt = mqtt_client.Client()
client_mqtt.on_connect = on_connect
client_mqtt.on_message = on_message
try:
    client_mqtt.connect(broker, port)
except:
    print ("[b red reverse blink] Unable to connect to Broker. [/]")
    exit(1)

client_mqtt.loop_start()

# Robot memory initializing
memory.tab_modules = import_modules(root, verbose_mode=True)
memory.tab_ids = identify_targets(root, verbose_mode=True)


# Running the script
console.rule("🤖 [red reverse b]  Executing the script: " + file_name.split('/')[-1][:-4] + "  [/] 🤖")
print()

# Running the settings commands.
run_script(settins_node)

# Running the script.
run_script(script_node)

# End of script
print('[b white]State:[/] [b white]End of script![/] 🎈🥳🥳🎈')
print()
console.rule("🤖 [green reverse b]  Script finished: " + file_name.split('/')[-1][:-4] + "  [/] 🤖")
print()
client_mqtt.loop_stop()
client_mqtt.disconnect()





# Validating the script. #########################################################################
# console.clear()
# console.rule("\n🤖 [yellow reverse b]  Parsing the script: " + "file_name" + "  [/] 🤖")
# print()
# script_file = sys.argv[1]
# print("[b white reverse] STEP 1. Let's validate de script. [/]\n")
# xml_file_ok = evaml_validator(script_file)

# if not xml_file_ok:
#   print("\n[b white on red blink] VALIDATION ERROR [/]: The script [b white]" + script_file + " [/]failed the validation process with the [b white]XMLSchema[/]. Please, [b white]check[/] the info above. [blink]👆[/]\n")
#   exit(1)
# else:
#   print("   [b green reverse] The script was validated! [/]\n")


# # Parsing (Loop processing)
# print("[b white reverse] STEP 2. Parsing the file (Expanding <loop> elements). [/]\n")
# id_loop_number = 0  # id usado na criação dos ids dos loops
# root = xml_file_ok.getroot() # Evaml root node
# script_node = root.find("script")
# process_loop(script_node)

# print("[b white reverse] STEP 3. Generating the EvaML parsed file. [/]\n")
# # Gera o arquivo com as macros expandidas (caso existam) para a proxima etapa
# xml_file_ok.write("_parsed_file.xml", "UTF-8")