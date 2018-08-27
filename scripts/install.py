# -*- coding: utf-8 -*-
from datetime import datetime
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


    # configuração para solução de multifator no Shibboleth IdP
    config_mfa_idp(config_variables)


if __name__ == '__main__':
   main()
