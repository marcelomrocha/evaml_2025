# Is equivalent to the $ of the original Eva software
# Is a list of results
var_dolar = []

# Pilha de nós de retorno, usados na execução do script
node_stack = []

# Contém os resultado de uma comparação com o <case>. Pode ser> True, False ou None.
flag_case = None

# Operador do elemento <switch>
op_switch = None

# Eva ram (a key/value dictionary)
vars = {}

# Contem a associação entre os nomes dos elementos e seus módulos.
# A chave é a tag do elemento e o valor é uma lista com 2 elementos:
# 1) o número de ocorrências do elemento no script.
# 2) o objeto que aponta para o módulo importado..
tab_modules = {}

# Esta tabela deve conter todos os elementos com "id", ou seja, aqueles que podem ser chamados por um <goto> ou por um <useMacro>.
tab_ids = {}

# Esta tabela armazena a contagem dos números de sequência dos "logs" de eventos.
log_seq_numbers = {}

# Modo de execução do script_player (default = terminal).
running_mode = 'terminal'

# Armazena uma resposta do robô físico. Pode ser um texto do STT, um expressão etc.
robot_response = None

# Armazena o estado do robô físico.
robot_state = "free"

# Tipo de voz padrão
default_voice = None
default_voice_pitch_shift = None