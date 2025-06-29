# Embodied Voice Assistant Markup Language (2025)


#### Todo elemento XML deve ter um módulo python associado, a fim de processá-lo.
#### O módulo deve ter o nome definido com o nome do elemento XML (com todos os caracteres minúsculos) concatenado a um "_" mais a palavra "module".
#### Ele também deve estar dentro de uma pasta como o mesmo nome, no mesmo diretório do script_player
#### O módulo deve definir a função node_processing(node, memory) e deve retornar um nó, que normalmente é o próprio node, com exceção do <goto> que retorna o nó "target".

Exemplos:

Elemento: **light**

Nome da pasta: **light_module**

Nome do módulo Python: **light_module.py**

Elemento: **evaEmotion**

Nome da pasta: **evaemotion_module**

Nome do módulo Python: **evaemotion_module.py**



Bibliotecas utilizadas:

**Rich** - Colorização dos textos do terminal.

pip install rich

**lxml** - Biblioteca externa mais avançada e eficiente para manipulação de arquivos XML.

pip install lxml