# -*- coding: utf-8 -*-
'''
Script para geração do metadata
Autor: bristot@gmail.com - 2018
'''
import subprocess
import sys
import base64
import utils

required_variables = ['restsecurity.user', 'restsecurity.password']
required_variables += ['host.name']

def generate_metadata(user, password, host):
    userbase64 = base64.b64encode(user+':'+password)
    destdir = 'MfaProvider/src/main/resources/metadata/sp-metadata.xml'
    resultrest = subprocess.call("$(curl","-X","GET","-H","'Authorization: Basic",userbase64,"'",host,"/saml/web/metadata/getNewMetaData)",shell=True)
    
    if resultrest != 0:
        
	try:
            save_file = subprocess.call("echo",resultrest,">",destdir, shell=True)
            if save_file == 0: # arquivo foi criado
                 return True
            else:
                print("Houve algum erro na criação do arquivo.")
                return False

        except OSError as e:
            print ("OSError ao executar a instalação e configuração do mongodb: ", e)
            return False
    else:
        return False
    return True

def main():
    if sys.version_info[0] != 2:
        print("Este script requer python2 e pode não funcionar com outra versão!")
    
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

    mongo_installed = install_mongodb(config_variables['mongo_db'],
            config_variables['mongo_admin_user'],
            config_variables['mongo_admin_password'])
    if mongo_installed:
        print("Mongo instalado e configurado com sucesso!")
    else:
        print("Não foi possível instalar e/ou configurar o mongodb... Encerrando...")


if __name__ == "__main__":
    main()
