# -*- coding: utf-8 -*-
'''
Script para geração do metadata
Autor: bristot@gmail.com - 2018
'''
import subprocess
import sys
import base64

try:
    import configparser
    config = configparser.ConfigParser()
except ImportError:
    import ConfigParser
    config = ConfigParser.ConfigParser()

config.read('config.ini')

def generate_metadata(user, password, host, destdir):
    pagehandler = subprocess.call("wget -O %s --user %s --password %s %s/saml/web/metadata/getNewMetaData --no-check-certificate" % (destdir, user, password, host), shell=True)
    return True

def main():
    if sys.version_info[0] != 2:
        print("Este script requer python2 e pode não funcionar com outra versão!")
    
    metadata_generated = generate_metadata(config.get('mfap','restsecurity.user'),
            config.get('mfap','restsecurity.password'),
            config.get('mfap','host.name') + config.get('mfap', 'mfapbasepath'), 
            'MfaProvider/src/main/resources/metadata/sp-metadata.xml')
    if metadata_generated:
        print("o metadado foi configurado com sucesso!")
    else:
        print("Não foi possível configurar o metadata... Encerrando...")


if __name__ == "__main__":
    main()
