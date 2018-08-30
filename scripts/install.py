# -*- coding: utf-8 -*-
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import shutil
import subprocess

import utils

from config_idp_mfa import edit_idp_properties, config_mfa_properties
from config_xml_files import config_relying_party, config_metadata_provider

required_variables = ['host.name', 'idp.metadata', 'restsecurity.user']
required_variables += ['restsecurity.password', 'admin.user', 'admin.password']
# config rest mfaprovider:
required_variables += ['idp.mfaprovider.apiHost','idp.mfaprovider.username',
        'idp.mfaprovider.password']
required_variables += ['dir_base_idp_shibboleth']
required_variables += ['mfapbasepath','docBase','dir_tomcat_app_config']
required_variables += ['tomcat_server_config', 'apache_conf_file']

# mongo
required_variables += ['mongo.user', 'mongo.pass', 'mongo.host',
        'mongo.db', 'mongo.port']


def config_mfa_idp(cfg):
    # Alteração do fluxo principal para multifator
    if not edit_idp_properties():
        msg = """
        Não foi possível editar o arquivo idp.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # Configuração Rest do MfaProvider
    if not config_mfa_properties(cfg['idp.mfaprovider.apiHost'],
        cfg['idp.mfaprovider.username'],
        cfg['idp.mfaprovider.password'],
        cfg['dir_base_idp_shibboleth']):
        msg = """
        Não foi possível editar o arquivo mfaprovider.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # Configurações gerais, flows, views, properties,
    # libs e arquivos necessários:
    # 1. relying-party.xml
    if not config_relying_party(cfg['dir_base_idp_shibboleth']):
        msg = """
        Não foi possível editar o arquivo relying-party.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # 2. attribute-filter.xml
    if not config_attribute_filters(cfg['dir_base_idp_shibboleth']):
        msg = """
        Não foi possível editar o arquivo attribute-filter.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # 3. general-authn.xml
    
    # 4 messages.properties

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

def config_tomcat(dir_tomcat, mfapbasepath, docBase, server_file):
    '''
    O caminho docBase está definido também no script 
    de deploy da aplicação.
    '''
    filename = dir_tomcat + mfapbasepath + '.xml'
    try:
        with open(filename, 'w+') as fh:
            fh.write('<Context docBase="%s"\n' % docBase)
            fh.write('unpackWAR="true"\n')
            fh.write('swallowOutput="true">\n')
            fh.write('<Manager pathname="" />\n')
            fh.write('</Context>')
    except IOError as err:
        print("Erro ao escrever arquivo " + docBase)
        print ("IOError: ", err)
        return False
    utils.backup_original_file(server_file)
    tree = ET.parse(server_file, utils.parser)
    root = tree.getroot()
    service_catalina = root.find('Service/[@name="Catalina"]')
    for child in service_catalina:
        if child.tag == 'Connector' and 'port' in child.attrib:
            if child.attrib['port'] == '9443':
                service_catalina.remove(child)
    ET.SubElement(service_catalina, 'Connector', {'port': '9443', 'address': '127.0.0.1',
        'protocol': 'AJP/1.3'})
    utils.indent(root)
    tree.write(server_file)
    return True

def config_sp_properties(idp_address, metadata, rest_user, rest_pwd,
        admin_user, admin_pwd):
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
    """ % (idp_address, metadata, rest_user, rest_pwd, admin_user, admin_pwd)
    try:
        with open('MfaProvider/src/main/resources/sp.properties', 'w+') as fp:
            fp.write(file_contents)
    except OSError as err:
        print("Nao foi possível escrever o arquivo sp.properties")
        return False
    return True

def config_apache(apache_conf_file):
    if os.path.exists(apache_conf_file):
        utils.backup_original_file(apache_conf_file)
        try:
            #TODO

        except IOError as err:
            print("Erro ao escrever arquivo " + apache_conf_file)
            print ("IOError: ", err)
            return False

        print ("Reiniciando apache..." )
        retcode_restart_apache = subprocess.call('systemctl restart apache2', shell=True)
        if retcode_restart_apache == 0:
            print("Apache reiniciado com sucesso!")
            return True
        else:
        print("Nao foi possivel reiniciar o apache")
    else:
        print ("Arquivo " + apache_conf_file + " de configuração do apache não encontrado!")

    return False

def write_mongo_properties(user, pwd, host, port, db):
    try:
        # codigo fonte clonado em MfaProvider, a partir do diretorio
        # deste script
        with open('MfaProvider/src/main/resources/mongo.properties', 'w+') as fmp:
            fmp.write('mongo.user=' + user)
            fmp.write('mongo.pass=' + pwd)
            fmp.write('mongo.host=' + host)
            fmp.write('mongo.port=' + port)
            fmp.write('mongo.db=' + db)
    except OSError as err:
        print("Não foi possível escrever o arquivo mongo.properties")
        return False
    return True


def main():
    # lê variáveis de configuração
    cfg = utils.read_cfg()
    if cfg and len(cfg) == 0:
        msg = """
        As variaveis de configuraçao necessárias nao foram adquiridas
        Por favor, verifique o arquivo variaveis_configuracao.txt
        """
        print(msg)
    if utils.check_missing_variables(cfg, required_variables):
        print("Corrija as variáveis faltantes e reinicie a execução")
        exit()

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
        write_mongo_properties(cfg['mongo.user'], cfg['mongo.pass'],
                cfg['mongo.host'], cfg['mongo.port'], cfg['mongo.db'])

    # configuração do Tomcat 8 para servir o SP MfaProvider
    config_tomcat(cfg['dir_tomcat_app_config'],
            cfg['mfapbasepath'], cfg['docBase'],
            cfg['tomcat_server_config'])

    # Configuração apache
    config_apache(cfg['apache_conf_file'])

    ## Configuração do MfaP como Service Provider:
    if (config_sp_properties(config_variables['host.name'], cfg['idp.metadata'],
            cfg['restsecurity.user'], cfg['restsecurity.password'],
            cfg['admin.user'], cfg['admin.password'])):
        retcode_deploy = subprocess.call('./deploy.sh')

    # Gerar SP Metadata

    # Configurar SP Metadata no IdP
    ## 1. Copiar metadata do sp

    ## 2. Editar metadata-providers.xml
    if not config_metadata_provider(cfg['dir_base_idp_shibboleth']):
        msg = """
        Não foi possível editar o arquivo metadata-providers.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    ## 3. Deploy do sp

    ## 4. Build do IdP

    ##
    #   2. Roteiro de configuração para solução de multifator no Shibboleth IdP
    ##

    # Download do projeto:
    # git clone https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto.git

    config_mfa_idp(cfg)

if __name__ == '__main__':
    #TODO : avisar que o script faz backup, mas sugerir backup
    # prévio de alguns arquivos, ainda a listar
   main()
