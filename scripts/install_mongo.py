# -*- coding: utf-8 -*-
'''
Script para instalação do mongodb
Autora: shirlei@gmail.com - 2018
'''

import subprocess
import sys

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
        print("Este script requer python2")
        exit()

    mongo_installed = install_mongodb()
    if mongo_installed:
        print("Mongo instalado e configurado com sucesso!")


if __name__ == "__main__":
    main()
