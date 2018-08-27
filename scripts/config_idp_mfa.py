# -*- coding: utf-8 -*-
'''
Script para instalação do mongodb
Autora: shirlei@gmail.com - 2018
'''

import subprocess
import sys

def edit_idp_properties():
    res = subprocess.call("sudo sed -i 's/idp.authn.flows=.*/idp.authn.flows= MFA/g' /opt/shibboleth-idp/conf/idp.properties",shell=True)
    if res != 0:
        print ("Não foi possível editar o arquivo idp.properties com as configurações = MFA")
        return False
    res = subprocess.call("sudo sed -i 's/idp.additionalProperties=.*/& ,\/conf\/authn\/mfaprovider.properties/' /opt/shibboleth-idp/conf/idp.properties",shell=True)
    if res != 0:
        print ("Não foi possível editar o arquivo idp.properties com as configurações do mfaprovider.properties")
        return False
    return True

def config_mfa_properties(apiHost, user, password, idp_dir):
    try:
        with open(idp_dir + 'conf/authn/mfaprovider.properties', 'w+') as mfap:
            mfap.write("## Endereço do MfaProvider\n")
            mfap.write("idp.mfaprovider.apiHost=" + apiHost + "\n")
            mfap.write("## Usuário e senha para autenticação REST \n")
            mfap.write("## configurado no sp.properties do projeto MfaProvider\n")
            mfap.write("idp.mfaprovider.username=" + user + "\n")
            mfap.write("idp.mfaprovider.password=" + password + "\n")
    except IOError as err:
        print("Erro ao escrever arquivo mfaprovider.properties")
        print ("IOError: ", err)

    return True



def main():
    if sys.version_info[0] != 2:
        print("Este script requer python2 e pode nao funcionar adequadamento no 3")
    edit_idp_properties()

if __name__ == "__main__":
    main()
