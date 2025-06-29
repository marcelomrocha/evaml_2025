# Este módulo define duas funções.
# Uma função para a identificação dos elementos usados no script.
# Uma função para a importação dos módulos associados a cada um desses elementos.
# A função de importação retorna uma tabela que associa os nomes (tags) dos elementos com os objetos dos módulos importados.

import sys
import os

import importlib

from rich import print, box
from rich.console import Console
from rich.table import Table

import config

console = Console()


def identify_targets(xml_root, verbose_mode=False):
    tab_ids = {}
    for element in xml_root.iter():
        # If element.get("id") and element.tag != "macro": # Cria a tabela com os elementos que possuem o atributo "id" excluindo as macros.
        if element.get("id"):
            tab_ids[element.get("id")] = [element.tag, element]
    if verbose_mode:
        print("")
        table = Table(title="[b]Table: Element identifiers[/]")
        table.add_column("Identifier")
        table.add_column("Element type")
        for item in sorted(tab_ids):
            table.add_row("[bold yellow]" + tab_ids[item][1].get("id"), "[bold cyan ]" + str(tab_ids[item][0]))
        console.print(table)
    return tab_ids


def identify_elements(xml_root, verbose_mode=False):
    """Percorre toda a seção de script identificando os elementos utilizados."""
    if verbose_mode:
        # Rich tem um método para limpar a tela
        console.clear()
        print("[bold underline green]Identificando os elementos do script.[/]")
    tab_modules = {}
    for element in xml_root.iter():
        if element.tag in tab_modules:
            tab_modules[element.tag][0] = tab_modules[element.tag][0] + 1
        else:
            tab_modules[element.tag] = [1]
            if element.getparent() == None: # It is the root element (EvaML).
                tab_modules[element.tag].append("[b white]Root element[/]")
            elif element.getparent().tag == "evaml": # Its is an EvaML section.
                tab_modules[element.tag].append("[b magenta]Section <" +  element.tag + ">[/]")
    if verbose_mode:
        print("[white]O script utiliza [bold]" + str(sum(1 for _ in xml_root.iter()) - 1) + " elemento(s).")
    
    return tab_modules # Retorna uma tabela com os elmentos utilizados no script.


def import_modules(xml_root, verbose_mode=False):
    """Importa os módulos associados a cada um dos elementos do script."""

    # At this moment, the tab_modules structure is: {elem.tag: [occurrences]}
    tab_modules = identify_elements(xml_root, verbose_mode)
    # From here, the tab_modules will have its structure modified. New information will be added to its value (list).
    for element_tag in tab_modules:
        module_name = element_tag.lower() + "_module" # Nome padrão para pastas dos módulos
        diretorio = os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/" + module_name #os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/" + module_name + "/"
        sys.path.insert(0, diretorio) # Coloca o diretório do módulo no path.
        try:
            mod = importlib.import_module(module_name) # importa o módulo
            tab_modules[element_tag].append(module_name + ".py")
            tab_modules[element_tag].append(mod)
        except Exception as e:
            tab_modules[element_tag].append("Not imported")
            tab_modules[element_tag].append(None)

    if verbose_mode:
        print("")
        table = Table(title="[bold]Table: XML Elements and Modules", box=box.DOUBLE_EDGE) # show_header=False, box=None (Algumas opções)
        table.add_column("XML Element")
        table.add_column("Occurrence", justify='center')
        table.add_column("Associated Module")
        # At this moment, the tab_modules structure is: {elem.tag: [occurrences, dir. do módulo, module obj]}
        for key, value in tab_modules.items():
            if value[2]: # not None
                table.add_row("[bold yellow]" + key, "[bold cyan ]" + str(value[0]), "[bold green]" + value[1])
            else:
                table.add_row("[bold yellow]" + key, "[bold cyan ]" + str(value[0]), "[bold red]" + value[1])
        console.print(table)
    
    return tab_modules


    
