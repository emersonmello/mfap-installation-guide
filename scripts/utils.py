# -*- coding: utf-8 -*-
from shutil import copyfile
import xml.etree.ElementTree as ET

class CommentedTreeBuilder(ET.TreeBuilder):
    def __init__(self, *args, **kwargs):
        super(CommentedTreeBuilder, self).__init__(*args, **kwargs)

    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)

parser = ET.XMLParser(target=CommentedTreeBuilder())

def read_config_variables():
    config_variables = {}
    with open('variaveis_configuracao.txt', 'r') as vc:
        try:
            for line in vc:
                if line.startswith('#'): # para permitir comentários no txt
                    next
                config_line = line.strip().split('=')
                if len(config_line) == 2:
                    config_variables[config_line[0].strip()] = config_line[1].strip()
        except ValueError:
            msg = """
            O arquivo de configuração deve ter o formato:
            var1=valor1
            var2=valor2
            Sendo uma variável por linha, sem linhas em branco.
            Por favor, ajuste o arquivo e repita a operação.
            """
    return config_variables

def check_missing_variables(config_variables, required_variables):
    missing_variable = False
    for required_variable in required_variables:
        if required_variable not in config_variables.keys():
            msg = """
            A variavel %s está faltando.
            Edite o arquivo variaveis_configuracao.txt e insira-a na forma
            %s=valor
            """ % (required_variable, required_variable)
            print(msg)
            missing_variable = True
    return missing_variable

def backup_original_file(filename):
    print("Fazendo backup de "  + filename)
    try:
        copyfile(filename, filename + ".orig")
    except IOError as io:
        print("Erro ao fazer backup do arquivo", filename)
        print("Error ", io)


def indent(elem, level=0):
    '''
    Identa a árvore xml resultante, antes de escrever novamente
    o arquivo.
    Obtido de:
        - https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python e
        - http://effbot.org/zone/element-lib.htm#prettyprint
    '''
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

if __name__ == "__main__":
    read_config_variables()
