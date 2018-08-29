# -*- coding: utf-8 -*-
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import shutil
import subprocess

import utils

from install_mongo import install_mongodb
from config_idp_mfa import edit_idp_properties, config_mfa_properties
from config_xml_files import config_relying_party

required_variables = ['host.name', 'idp.metadata', 'restsecurity.user']
required_variables += ['restsecurity.password', 'admin.user', 'admin.password']
# config rest mfaprovider:
required_variables += ['idp.mfaprovider.apiHost','idp.mfaprovider.username',
        'idp.mfaprovider.password']
required_variables += ['dir_base_idp_shibboleth']
required_variables += ['mfapbasepath','docBase','dir_tomcat_app_config']
required_variables += ['tomcat_server_config']

def config_mfa_idp(config_variables):
    # Alteraçao do fluxo principal para Multifator
    if not edit_idp_properties():
        msg = """
        Não foi possível editar o arquivo idp.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # Configuração Rest do MfaProvider
    if not config_mfa_properties(config_variables['idp.mfaprovider.apiHost'],
        config_variables['idp.mfaprovider.username'], 
        config_variables['idp.mfaprovider.password'],
        config_variables['dir_base_idp_shibboleth']): 
        msg = """
        Não foi possível editar o arquivo mfaprovider.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)
    
    if not config_relying_party(config_variables['dir_base_idp_shibboleth']): 
        msg = """
        Não foi possível editar o arquivo relying-party.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

def config_tomcat(dir_tomcat, mfapbasepath, docBase, server_file):
    '''
    O caminho docBase está definido também no script 
    de deploy da aplicação.
    '''
    filename = dir_tomcat + mfapbasepath + '.xml'
    try:
        with open(filename, 'w+') as fh:
            fh.write('<Context docBase="%s"\n' % docBase)
            fh.write('unpackWAR="true"\n')
            fh.write('swallowOutput="true">\n')
            fh.write('<Manager pathname="" />\n')
            fh.write('</Context>')
    except IOError as err:
        print("Erro ao escrever arquivo mfaprovider.properties")
        print ("IOError: ", err)
        return False
    utils.backup_original_file(server_file)
    tree = ET.parse(server_file, utils.parser)
    root = tree.getroot()
    service_catalina = root.find('Service/[@name="Catalina"]')
    for child in service_catalina:
        if child.tag == 'Connector' and 'port' in child.attrib:
            if child.attrib['port'] == '9443':
                service_catalina.remove(child)
    ET.SubElement(service_catalina, 'Connector', {'port': '9443', 'address': '127.0.0.1',
        'protocol': 'AJP/1.3'})
    utils.indent(root)
    tree.write(server_file)
    return True


def main():

    # lê variáveis de configuração
    config_variables = utils.read_config_variables()
    if config_variables and len(config_variables) == 0:
        msg = """
        As variaveis de configuraçao necessárias nao foram adquiridas
        Por favor, verifique o arquivo variaveis_configuracao.txt
        """
        print(msg)
    if utils.check_missing_variables(config_variables, required_variables):
        print("Corrija as variáveis faltantes e reinicie a execução")
        exit()
   
    print("\n=== Clonando o repositório do projeto MfaProvider ===\n")
    print("Você será solicitado a informar seu usuário e senha do git\n")
    # clone repositório MFAProvider
    if os.path.exists('MfaProvider'):
        print("Diretorio MfaProvider existe, fazendo backup")
        dt = datetime.now()
        shutil.move('MfaProvider','MfaProvider.orig.%s' % dt.strftime("%d%m%Y%H%M%S"))
    retcode_gitclone = subprocess.call("git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git", 
        shell=True)
    if retcode_gitclone != 0:
        msg = """
        Não foi possível clonar o diretório do projeto MfaProvider. 
        Por favor, corrija o problema indicado e tente novamente.
        """
        print(msg)
        exit()

    # configuração do Tomcat 8

    config_tomcat(config_variables['dir_tomcat_app_config'],
            config_variables['mfapbasepath'], config_variables['docBase'],
            config_variables['tomcat_server_config'])
    # configuração para solução de multifator no Shibboleth IdP
    config_mfa_idp(config_variables)



if __name__ == '__main__':
    #TODO : avisar que o script faz backup, mas sugerir backup
    # prévio de alguns arquivos, ainda a listar
   main()
