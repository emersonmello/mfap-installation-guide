# -*- coding: utf-8 -*-
'''
Script para geração do metadata
Autor: bristot@gmail.com - 2018
'''
import subprocess
import sys
import base64
try:
    # For Python 3.0 and later
    import urllib.request as urllib2
except ImportError:
    # Fall back to Python 2's urllib2
    import urllib2
import utils

try:
    import configparser
    config = configparser.ConfigParser()
except ImportError:
    import ConfigParser
    config = ConfigParser.ConfigParser()

config.read('config.ini')

def generate_metadata(user, password, host, destdir):
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, host, user, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    pagehandler = urllib2.urlopen(host+"/saml/web/metadata/getNewMetaData")
    if pagehandler.code == 200:   
        try:
            with open(destdir, 'wb+') as fh:
                fh.write(pagehandler.read())
        except OSError as err:
            print("Náo foi possível salvar o metadata")
    else:
        print("Não foi possível acessar os metadados do mfaprovider")

    return True

def main():
    if sys.version_info[0] != 2:
        print("Este script requer python2 e pode não funcionar com outra versão!")
    
    metadata_generated = generate_metadata(config.get('idp','restsecurity.user'),
            config.get('idp','restsecurity.password'),
            config.get('mfap','host.name') + config.get('mfap', 'mfapbasepath'), 
            'MfaProvider/src/main/resources/metadata/sp-metadata.xml')
    if metadata_generated:
        print("o metadado foi configurado com sucesso!")
    else:
        print("Não foi possível configurar o metadata... Encerrando...")


if __name__ == "__main__":
    main()
