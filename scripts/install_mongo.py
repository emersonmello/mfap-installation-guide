# -*- coding: utf-8 -*-
'''
Script para instalação do mongodb
Autora: shirlei@gmail.com - 2018
'''

import subprocess
import sys


def install_mongodb():
    result = subprocess.run(["sudo","apt-get","install", "mongodb", "-y"])
    if result.returncode == 0:
        try:
            retcode = subprocess.call("systemctl status mongodb", shell=True)
            if retcode != 0 :
                print ("O mongodb não está rodando")
            else:
                print ("O mongodb está rodando, prosseguindo com a instalação")
                retcode = subprocess.call("mongo < scriptMongo.js", shell=True)
                if retcode == 0: # usuario foi criado
                    res = subprocess.run(["sudo", "sed", "-i", "s/#auth = true/auth = true/g", "/etc/mongodb.conf"])
                    if res.returncode == 0: 
                        runmongo = subprocess.call("systemctl restart mongodb", shell=True)
                        if runmongo != 0:
                            return False
                else:
                    print("Houve algum erro na criação do usuario do mongo")
                    return False

        except OSError as e:
            print ("Houve um erro ao verificar se o mongo está rodando: ", e)
            return False
    return True

def main():
    if sys.version_info[0] != 3:
        print("Este script requer python3")
        exit()

    mongo_installed = install_mongodb()
    if mongo_installed:
        print("Mongo instalado e configurado com sucesso!")

if __name__ == "__main__":
    main()
