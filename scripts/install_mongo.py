# -*- coding: utf-8 -*-
'''
Script para instalação do mongodb
Autora: shirlei@gmail.com - 2018
'''

import subprocess
import sys

import utils

required_variables = ['mongo_admin_user', 'mongo_admin_password']
required_variables += ['mongo_db']

def install_mongodb(db, admin_user, admin_pwd):
    with open('scriptMongo.js', 'w') as sm:
        script_text = """
        use %s
        db.createUser(
            {
                user:"%s",
                pwd:"%s",
                roles: ["readWrite","dbAdmin"]
            }
        )
        """ % (db, admin_user, admin_pwd)
        sm.write(script_text)

    retcode_install_mongo = subprocess.call(["sudo","apt-get","install", "mongodb", "-y"])
    if retcode_install_mongo == 0: # serve para instalaçao recem realizada e já instalado
        try:
            retcode_mongo_status = subprocess.call("systemctl status mongodb", shell=True)
            if retcode_mongo_status != 0 :
                print ("O mongodb não está rodando")
                retcode_start_mongo = subprocess.call("systemctl start mongodb", shell=True)
                if retcode_start_mongo != 0:
                    print("Não foi possível iniciar o mongodb.")
                    print("Por favor, corrija manualmente esta questão e volte a executar \
                            este script.")
                    return False
            
            retcode_config_mongo = subprocess.call("mongo < scriptMongo.js", shell=True)
            if retcode_config_mongo == 0: # usuario foi criado
                retcode_edit_config = subprocess.call(["sudo", "sed", "-i", "s/#auth = true/auth = true/g", "/etc/mongodb.conf"])
                if retcode_edit_config == 0: 
                    retcode_run_mongo = subprocess.call("systemctl restart mongodb", shell=True)
                    if retcode_run_mongo != 0:
                        return False
            else:
                print("Houve algum erro na criação do usuario do mongodb.")
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
