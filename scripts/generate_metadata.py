# -*- coding: utf-8 -*-
'''
Script para geração do metadata
Autor: bristot@gmail.com - 2018
'''
import ssl
import subprocess
import sys
import base64
import urllib2

import ConfigParser
config = ConfigParser.ConfigParser()

config.read('config.ini')

def generate_metadata(user, password, host, destdir, autoassinado=True):
    # verifica se usa certificado autoassinado, o que pelo comportamento 
    # padrão do python lança o erro :
    # SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)
    # Como a imagem do IdP liberada pelas instituições pela RNP utiliza certificado
    # autoassinado (gerado no seu script de instalação firstboot.sh), esta opção
    # vai ficar como configuração padrão na instalação do MfaProvider, para que,
    # na instalação avançada, caso a instituição não queira deixar essa opção
    # por não utilizar certificado autoassinado
    if autoassinado:
        context = ssl._create_unverified_context()
    else:
        context = ssl._create_default_https_context()
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, host, user, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    try:
        pagehandler = urllib2.urlopen(host+"/saml/web/metadata/getNewMetaData", context=context)
        if pagehandler.code == 200:
            try:
                with open(destdir, 'wb+') as fh:
                    fh.write(pagehandler.read())
            except OSError as err:
                print("Não foi possível salvar o metadata")
                return False
        else:
            print "Não foi possível acessar os metadados do mfaprovider"
            print "Código http obtido: %s \n"   % pagehandler.code
    except urllib2.URLError as e:
        print "Não foi possível acessar a url para obter o arquivo de metadata do SP \n"
        print "Erro obtido:"
        print e
        return False
    return True

#def generate_metadata(user, password, host, destdir):
#    pagehandler = subprocess.call("curl -X GET --user %s:%s %s/saml/web/metadata/getNewMetaData --insecure > %s" % (user, password, host, destdir), shell=True)
    #subprocess.call("wget -O %s --user %s --password %s %s/saml/web/metadata/getNewMetaData --no-check-certificate" % (destdir, user, password, host), shell=True)
#    if pagehandler == 0:
#        return True
#    else:
        #        print("Ocorreu um erro ao gerar o MetaData")
#        return False
#

def main():
    if sys.version_info[0] != 2:
        print("Este script requer python2 e pode não funcionar com outra versão!")
    
    metadata_generated = generate_metadata(config.get('mfap','restsecurity.user'),
            config.get('mfap','restsecurity.password'),
            "https://" + config.get('default','uri') + "/" + config.get('mfap', 'mfapbasepath'),
            'MfaProvider/src/main/resources/metadata/sp-metadata.xml',
            config.get('apache', 'certificado_autoassinado'))
    if metadata_generated:
        print("o metadado foi configurado com sucesso!")
    else:
        print("Não foi possível configurar o metadata... Encerrando...")


if __name__ == "__main__":
    main()
