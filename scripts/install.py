# -*- coding: utf-8 -*-
from datetime import datetime
import os
import shutil
import subprocess

import utils

from install_mongo import install_mongodb

required_variables = ['host.name', 'idp.metadata', 'restsecurity.user']
required_variables += ['restsecurity.password', 'admin.user', 'admin.password']


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

    # instalação e configuração do mongo
    print("=== Instalando e configurando mongodb ===")
    mongodb_installed = install_mongodb(config_variables['mongo_db'],
            config_variables['mongo_admin_user'],
            config_variables['mongo_admin_password'])

    if not mongodb_installed:
        print("Não foi possível instalar e/ou configurar o mongodb... Encerrando...")
        exit()
if __name__ == '__main__':
   main()
