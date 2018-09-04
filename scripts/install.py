# -*- coding: utf-8 -*-
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import shutil
import subprocess
from urllib2 import urlopen

import utils
from utils import CommentedTreeBuilder

from config_idp_mfa import edit_idp_properties, config_mfa_properties
from config_xml_files import config_relying_party, config_metadata_provider
from config_xml_files import config_attribute_filters
from generate_metadata import generate_metadata

import ConfigParser
config = ConfigParser.ConfigParser()

# Lê as variáveis
config.read('config.ini')

def config_mfa_idp():
    # Alteração do fluxo principal para multifator
    if not edit_idp_properties():
        msg = """
        Não foi possível editar o arquivo idp.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # Configuração Rest do MfaProvider
    if not config_mfa_properties(config.get('mfap','idp.mfaprovider.apiHost'),
        config.get('mfap','restsecurity.user'),
        config.get('mfap','restsecurity.password'),
        config.get('idp','dir_base_idp_shibboleth')):
        msg = """
        Não foi possível editar o arquivo mfaprovider.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # Configurações gerais, flows, views, properties,
    # libs e arquivos necessários:
    # 1. relying-party.xml
    #if not config_relying_party(config.get(idp,dir_base_idp_shibboleth)):
    #    msg = """
    #   Não foi possível editar o arquivo relying-party.xml.
    #    Por favor,edite manualmente conforme tutorial.
    #    """
    #    print(msg)

    # 2. attribute-filter.xml
    if not config_attribute_filters(config.get('idp','dir_base_idp_shibboleth')):
        msg = """
        Não foi possível editar o arquivo attribute-filter.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # 3. general-authn.xml
    
    # 4 messages.properties
    if not  write_messages_idp_properties():
        msg = """
        Não foi possível editar o arquivo messages.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)
    # 5. Copie o arquivo alteracoes/conf/authn/mfa-authn-config.xml para /opt/shibboleth-idp/conf/authn/
    # sudo cp alteracoes/conf/authn/mfa-authn-config.xml /opt/shibboleth-idp/conf/authn/

    # 6 Copie o conteúdo do diretório alteracoes/flows/authn para  /opt/shibboleth-idp/flows/authn
    # sudo cp -R alteracoes/flows/authn/* /opt/shibboleth-idp/flows/authn/

    # 7 Copie o conteúdo do diretório alteracoes/views para  /opt/shibboleth-idp/views;
    # sudo cp alteracoes/views/* /opt/shibboleth-idp/views/

    # 8 Copie o conteúdo do diretório alteracoes/webapp/images para  /opt/shibboleth-idp/webapp/images;
    # sudo cp alteracoes/webapp/images/* /opt/shibboleth-idp/webapp/images/

    # 9 Copie o conteúdo do diretório alteracoes/webapp/WEB-INF/lib para /opt/shibboleth-idp/webapp/WEB-INF/lib
    #sudo cp alteracoes/webapp/WEB-INF/lib/* /opt/shibboleth-idp/webapp/WEB-INF/lib/

    # build do idp 
    # cd /opt/shibboleth-idp/
    # ./bin/build.sh

def config_tomcat():
    '''
    O caminho docBase está definido também no script 
    de deploy da aplicação.
    '''
    filename = config.get('tomcat','dir_tomcat_app_config') + config.get('mfap','mfapbasepath') + '.xml'
    try:
        with open(filename, 'w+') as fh:
            fh.write('<Context docBase="%s"\n' % config.get('tomcat','docBase'))
            fh.write('unpackWAR="true"\n')
            fh.write('swallowOutput="true">\n')
            fh.write('<Manager pathname="" />\n')
            fh.write('</Context>')
    except OSError as err:
        print("Erro ao escrever arquivo " + config.get('tomcat','docBase'))
        print ("IOError: ", err)
        return False

    utils.backup_original_file(config.get('tomcat','tomcat_server_config'))
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(config.get('tomcat','tomcat_server_config'), parser)
    root = tree.getroot()
    service_catalina = root.find('Service/[@name="Catalina"]')
    for child in service_catalina:
        if child.tag == 'Connector' and 'port' in child.attrib:
            if child.attrib['port'] == '9443':
                service_catalina.remove(child)
    ET.SubElement(service_catalina, 'Connector', {'port': '9443', 'address': '127.0.0.1',
        'protocol': 'AJP/1.3'})
    utils.indent(root)
    tree.write(config.get('tomcat','tomcat_server_config'))
    return True

def config_sp_properties():
    file_contents = """
 ##Caminho completo do idp com o pathname
 host.name=%s

 ##Caminho completo para o metadata do idp
 idp.metadata=%s

 ##Defina um usuario e senha para proteção dos recursos rest
 restsecurity.user=%s
 restsecurity.password=%s

 ##Defina um usuario e senha para administrador do IdP
 admin.user=%s
 admin.password=%s
    """ % (config.get('mfap','host.name') + config.get('mfap','mfapbasepath'), 
            config.get('idp','idp.metadata'), config.get('mfap','restsecurity.user'), 
            config.get('mfap','restsecurity.password'),
            config.get('idp','admin.user'), config.get('idp','admin.password'))
    try:
        with open('MfaProvider/src/main/resources/sp.properties', 'w+') as fp:
            fp.write(file_contents)
    except OSError as err:
        print("Nao foi possível escrever o arquivo sp.properties")
        return False
    return True

def config_mfaprovider_properties():
    file_contents = """
##substitua por chave herdada do servidor FCM
br.rnp.xmpp.serverKey=%s

##substitua por codigo do remetente FCM
br.rnp.xmpp.senderId=%s

#substitua somente se utilizar um pathname diferente do padr�o conta
mfapbasepath=%s

#substitua o idphost com o caminho completo do idp para obter o logo ex: https://insituicao.edu.br/idp/images/logo-instituicao.png
idplogo=%s
    """ % (config.get('fcm','br.rnp.xmpp.serverKey'), 
            config.get('fcm','br.rnp.xmpp.senderId'), 
            config.get('mfap','mfapbasepath'), 
            config.get('idp','idp_logo'))
    try:
        with open('MfaProvider/src/main/resources/mfaprovider.properties', 'w+') as fp:
            fp.write(file_contents)
    except OSError as err:
        print("Nao foi possível escrever o arquivo sp.properties")
        return False
    return True


def config_apache():
    apache_conf_file = config.get('apache','apache_conf_file')
    if os.path.exists(apache_conf_file):
        utils.backup_original_file(apache_conf_file)
        try:
            with open('insert_apache.txt', 'w+') as fp:
                fp.write('\n    ProxyPass /%s ajp://localhost:9443/%s retry=5 \n' 
                        % (config.get('mfap','mfapbasepath'), config.get('mfap','mfapbasepath')))
                fp.write('  <Proxy ajp://localhost:9443>\n')
                fp.write('      Require all granted\n')
                fp.write('  </Proxy>\n')
        except IOError as err:
            print("Erro ao escrever arquivo " + apache_conf_file)
            print ("IOError: ", err)
            return False
        retcode = subprocess.call("sed -i '/<\/Proxy>/r insert_apache.txt' %s" % apache_conf_file, shell=True)
        if retcode == 0:
            print ("Reiniciando apache..." )
            retcode_restart_apache = subprocess.call('systemctl restart apache2', shell=True)
            if retcode_restart_apache == 0:
                print("Apache reiniciado com sucesso!")
                return True
            else:
                print("Nao foi possivel reiniciar o apache")
    else:
        print ("Arquivo " + config.get('apache','apache_conf_file') + " de configuração do apache não encontrado!")

    return False

def write_mongo_properties():
    try:
        # codigo fonte clonado em MfaProvider, a partir do diretorio
        # deste script
        with open('MfaProvider/src/main/resources/mongo.properties', 'w+') as fmp:
            fmp.write('mongo.user=' + config.get('mongo','user')+"\n")
            fmp.write('mongo.pass=' + config.get('mongo','password')+"\n")
            fmp.write('mongo.host=' + config.get('mongo','host')+"\n")
            fmp.write('mongo.db=' + config.get('mongo','db'))
    except OSError as err:
        print("Não foi possível escrever o arquivo mongo.properties. Erro: " + err)
        return False
    return True

def write_messages_idp_properties():
    try:
        # messages.properties a partir do diretorio do Idp
        # deste script
        with open('alteracoes/messages/messages.properties', 'w+') as fmp:
            fmp.write('mfaprovider.host=' + config.get('mfap','host.name') + config.get('mfap','mfapbasepath'))
    except OSError as err:
        print("Não foi possível escrever o arquivo messages.properties. Erro: " + err)
        return False
    return True


def main():
    ##
    #   1. Roteiro de instalação da aplicação MfaProvider
    ##
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
    else:
        write_mongo_properties()

    # configuração do Tomcat 8 para servir o SP MfaProvider
    config_tomcat()

    # Configuração apache
    config_apache()
    
    config_mfaprovider_properties()

    ## Configuração do MfaP como Service Provider:
    if config_sp_properties():
        try:
            retcode_deploy = subprocess.call('cd MfaProvider && ./deploy.sh', shell=True)
        except IOError as fne:
            print("O arquivo de deploy não foi encontrado")
            exit()
    # Gerar SP Metadata
    metadatafile = 'MfaProvider/src/main/resources/metadata/sp-metadata.xml'
    if retcode_deploy == 0:
        generate_metadata(config.get('mfap','restsecurity.user'),
                config.get('mfap','restsecurity.password'),
                config.get('mfap','host.name') + config.get('mfap', 'mfapbasepath'),
                metadatafile)
    else:
        print("Não foi possível gerar metadados do MfaProvider")
        exit()

    # Configurar SP Metadata no IdP
    ## 1. Copiar metadata do sp
    metadatadest = config.get('idp', 'dir_base_idp_shibboleth') + '/metadata/' + 'mfaprovider-metadata.xml' 
    shutil.copyfile(metadatafile, metadatadest)

    ## 2. Editar metadata-providers.xml
    if not config_metadata_provider(config.get('idp','dir_base_idp_shibboleth')):
        msg = """
        Não foi possível editar o arquivo metadata-providers.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    ## 3. Deploy do sp
    try:
        retcode_deploy = subprocess.call('cd MfaProvider && ./deploy.sh', shell=True)
    except IOError as fne:
        print("O arquivo de deploy não foi encontrado")
        exit()


    ##
    #   2. Roteiro de configuração para solução de multifator no Shibboleth IdP
    ##

    # Download do projeto:
    # git clone https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto.git

    config_mfa_idp()
    # chamar script de cópias
    try:
        retcode_copy =  subprocess.call('./implantacao_mfa_idpv3.sh', shell=True)
    except IOError as fne:
        print("O script implantacao_mfa_idpv3.sh não foi encontrado")
        if retcode_copy == 0:
             print("Script finalizado com sucesso")
        exit()

if __name__ == '__main__':
    #TODO : avisar que o script faz backup, mas sugerir backup
    # prévio de alguns arquivos, ainda a listar
   #config_mfa_idp()
   main()
