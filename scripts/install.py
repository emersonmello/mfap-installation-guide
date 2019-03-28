# -*- coding: utf-8 -*-
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import re
import shutil
import subprocess

import utils
from utils import CommentedTreeBuilder

from config_idp_mfa import edit_idp_properties, config_mfa_properties
from config_xml_files import config_relying_party, config_metadata_provider
from config_xml_files import config_attribute_filters, config_general_authn
from generate_metadata import generate_metadata


import ConfigParser
config = ConfigParser.ConfigParser()
editVariables = True
# Lê as variáveis
config.read('config.ini')

def set_value(group,field,message):
    variable = config.get(group,field) 
    if variable =='' or editVariables:
        variable = raw_input(message)
        while variable =='':
            variable = raw_input('valor não pode ser nulo, digite novamente: ')
        config.set(group,field,variable)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    return variable

def set_value_without_ask(group,field,value):
    variable = config.get(group,field) 
    if variable =='' or editVariables:
        config.set(group,field,value)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    return variable 

def verify_edit_variables():
    mongouser = config.get('mongo','user') 
    if mongouser !='' :
        choise = raw_input('Você já tentou realizar uma instalação anteriormente, continuar utilizando os mesmos dados informados? (N,s)')
        if (choise in ('S','s')):
            return False
    return True

def set_auth_mongoconf():
    retcode_edit_config = subprocess.call(["sudo", "sed", "-i", "s/#auth = true/auth = true/g", "/etc/mongodb.conf"])
    if retcode_edit_config == 0: 
        retcode_run_mongo = subprocess.call("systemctl restart mongodb", shell=True)
        if retcode_run_mongo != 0:
            return False
        else :
            return True
    return True

def set_noauth_mongoconf():
    retcode_edit_config = subprocess.call(["sudo", "sed", "-i", "s/auth = true/#auth = true/g", "/etc/mongodb.conf"])
    if retcode_edit_config == 0: 
       retcode_run_mongo = subprocess.call("systemctl restart mongodb", shell=True)
       if retcode_run_mongo != 0:
            return False
       else :
            return True
    return True

def install_mongodb():
    mongouser = set_value('mongo','user','Informe um nome de usuário para ser utilizado como administrador do banco de dados:') 
    mongopass = set_value('mongo','password','Defina uma senha para o usuário ' + mongouser+ ': ')
    with open('scriptMongo.js', 'w') as sm:
        mongouser = config.get('mongo','user') 
        script_text = """
        use %s
        db.createUser(
            {
                user:"%s",
                pwd:"%s",
                roles: ["readWrite","dbAdmin"]
            }
        )
        """ % (config.get('mongo','db'), mongouser, mongopass)
        sm.write(script_text)

    #retcode_install_mongo = subprocess.call(["sudo","apt-get","install", "mongodb", "-y"])
    #if retcode_install_mongo == 0: # serve para instalaçao recem realizada e já instalado
    try:
        retcode_config_mongo = subprocess.call("mongo < scriptMongo.js", shell=True)
        if retcode_config_mongo == 0: # usuario foi criado
            set_auth_mongoconf()
        else:
            print("Houve algum erro na criação do usuario do mongodb.")
            return False

    except OSError as e:
        print ("Error ao executar a instalação e configuração do mongodb: ", e)
        return False
    return True

def config_mfa_idp():
    # Alteração do fluxo principal para multifator
    apiHost = set_value_without_ask('mfap','idp.mfaprovider.apiHost',config.get('mfap','host.name')+config.get('mfap','mfapbasepath'))
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
    if not config_relying_party(config.get('idp','dir_base_idp_shibboleth')):
        msg = """
       Não foi possível editar o arquivo relying-party.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # 2. attribute-filter.xml
    if not config_attribute_filters(config.get('idp','dir_base_idp_shibboleth'),config.get('default','uri')):
        msg = """
        Não foi possível editar o arquivo attribute-filter.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

    # 3. general-authn.xml
    if not config_general_authn(config.get('idp','dir_base_idp_shibboleth')):
        msg = """
        Não foi possível editar o arquivo general-authn.xml.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)
    
    # 4 messages.properties
    if not  write_messages_idp_properties():
        msg = """
        Não foi possível editar o arquivo messages.properties.
        Por favor,edite manualmente conforme tutorial.
        """
        print(msg)

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
        print("verifique se a propriedade dir_tomcat_app_config no config.ini esta com o caminho correto do tomcat ")
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
    uri_idp = set_value('default','uri','Informe o endereço do IdP, sem o https ex: idp.instituicao.edu.br: ')
    host_name = set_value_without_ask('mfap','host.name','https://'+uri_idp+'/')
    user_rest_mfa = set_value('mfap','restsecurity.user','Defina um usuário para proteção dos recursos rest: ') 
    pass_rest_mfa = set_value('mfap','restsecurity.password','Defina uma senha: ')
    file_contents = """

 ##Caminho completo do idp com o pathname
 host.name=%s

 ##Nome do host do idp sem o pathname e htpps ex: insituicao.edu.br
 entity.id=%s

 ##Caminho completo para o metadata do idp
 idp.metadata=%s

 ##Defina um usuario e senha para proteção dos recursos rest
 restsecurity.user=%s
 restsecurity.password=%s
    """ % ((config.get('mfap','host.name') + config.get('mfap','mfapbasepath')), 
            uri_idp, 
            config.get('idp','idp.metadata'), 
            user_rest_mfa, 
            pass_rest_mfa)
    try:
        with open('MfaProvider/src/main/resources/sp.properties', 'w+') as fp:
            fp.write(file_contents)
    except OSError as err:
        print("Nao foi possível escrever o arquivo sp.properties")
        return False
    return True

def config_mfaprovider_properties():
    print("Informações geradas conforme item 9 do Readme.md (seção: configurações FCM para Diálogo de Confirmação)")
    set_value('fcm','br.rnp.xmpp.serverKey','Informe a chave herdada do servidor FCM: ')
    set_value('fcm','br.rnp.xmpp.senderId','Informe o codigo do remetente do servidor FCM: ')
    set_value_without_ask('idp','idp_logo',config.get('mfap','host.name')+'idp/images/logo-instituicao.png')
    file_contents = """
##substitua por chave herdada do servidor FCM
br.rnp.xmpp.serverKey=%s

##substitua por codigo do remetente FCM
br.rnp.xmpp.senderId=%s

#substitua somente se utilizar um pathname diferente do padr�o conta
mfapbasepath=%s

#substitua o idphost com o caminho completo do idp para obter o logo ex: https://insituicao.edu.br/idp/images/logo-instituicao.png
idplogo=%s

hostmfap=%s
    """ % (config.get('fcm','br.rnp.xmpp.serverKey'), 
            config.get('fcm','br.rnp.xmpp.senderId'), 
            config.get('mfap','mfapbasepath'), 
            config.get('idp','idp_logo'),
            config.get('default','uri'))
    try:
        with open('MfaProvider/src/main/resources/mfaprovider.properties', 'w+') as fp:
            fp.write(file_contents)
    except OSError as err:
        print("Nao foi possível escrever o arquivo mfaprovider.properties")
        return False
    return True


def config_apache():
    apache_conf_file = config.get('apache','apache_conf_file')
    insert_apache_str = """
        ProxyPass /%s ajp://localhost:9443/%s retry=5
        <Proxy ajp://localhost:9443>
            Require all granted
        </Proxy>
    """ % (config.get('mfap','mfapbasepath'), config.get('mfap','mfapbasepath'))

    if os.path.exists(apache_conf_file):
        utils.backup_original_file(apache_conf_file)
        # Verifica se o conteudo de insert_apache_str já foi adicionado anteriormente e apaga
        vhost_contents = ''
        try:
            with open(apache_conf_file, 'r') as fh:
                vhost_contents = fh.read()
        except IOError as e:
            print "Houve um erro ao abrir %s para leitura" % apache_conf_file
            print "Erro:  %s " % err
        if re.findall(insert_apache_str, vhost_contents, re.M):
            msg = """
                Foi encontrada uma configuração idêntica do MfaProvider no apache, em
                em %s. Portanto, esse passo não será executado.
                Configuração que seria adicionada por este script, e que já existia:
                %s
            """ % (apache_conf_file, insert_apache_str)
            print msg
        else:
            try:
                with open('insert_apache.txt', 'w+') as fp:
                    fp.write(insert_apache_str)
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
            fmp.write('mfaprovider.host=' + config.get('mfap','host.name') + config.get('mfap','mfapbasepath')+"\n")
            fmp.write('# Os demais não precisam ser alterados, mas podem caso desejar customizar as mensagens.'+"\n")
            fmp.write('mfaprovider.animation.alt-text = Autenticação MFA'+"\n")
            fmp.write('mfaprovider.animation = /images/dialogo.gif'+"\n")
            fmp.write('mfaprovider.information = Confirme a autenticação no dispositivo'+"\n")
            fmp.write('idp.logo.alt-text = MfaProvider'+"\n")

    except OSError as err:
        print("Não foi possível escrever o arquivo messages.properties. Erro: " + err)
        return False
    return True

def deploy():
    ## Alterar a variável SP_DIR para o diretório que está configurado no servidor de aplicação apache  ##
    sp_dir=config.get('apache', 'sp_dir')
    try:
        if not os.path.exists(sp_dir):
            os.makedirs(sp_dir)
        os.chdir('./MfaProvider')
        retcode_gradle_clean = subprocess.call('./gradlew clean', shell=True)
        if retcode_gradle_clean == 0:
            retcode_gradle_build = subprocess.call('./gradlew build', shell=True)
            if retcode_gradle_build == 0:
                retcode_gradle_war = subprocess.call('./gradlew war', shell=True)
                if retcode_gradle_war == 0:
                    try:
                        if os.path.exists(sp_dir + '/mfaprovider.war'):
                            os.remove(sp_dir + '/mfaprovider.war')
                        shutil.copyfile('./build/libs/mfaprovider.war', sp_dir + '/mfaprovider.war')
                    except IOError as e:
                        print ("Não foi possível copiar o arquivo mfaprovider.war")
                        print ("Erro: ", e)

        retcode_restart_tomcat = subprocess.call('sudo systemctl restart tomcat8', shell=True)
        try:
            os.remove('./build/')
        except Exception as e:
            pass
        if retcode_restart_tomcat != 0:
            print ("Não foi possível reiniciar o tomcat após o deploy")
            return False
        try:
            os.remove('./build')
        except Exception as e:
            # nao vamos parar o processo se nao conseguir remover, o clean
            # deve dar conta 
            pass
    except OSError as ose:
        print ("Erro ao fazer o deploy ", ose)
        return False
    except Exception as e:
        print e
    os.chdir('..')
    return True


def main():
    ## Verifica se houve tentativa de instalação anterior
    global editVariables
    editVariables = verify_edit_variables()
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
    retcode_gitclone = subprocess.call("git -c http.sslVerify=false clone https://git.rnp.br/GT-AMPTo/MfaProvider.git", 
        shell=True)
    if retcode_gitclone != 0:
        msg = """
        Não foi possível clonar o diretório do projeto MfaProvider.
        Por favor, corrija o problema indicado e tente novamente.
        """
        print(msg)
        utils.revert_backup_files()
        exit()
    else:
        ## Adiciona segurança ao Mongo DB
        install_mongodb()
        write_mongo_properties()

    # configuração do Tomcat 8 para servir o SP MfaProvider
    config_tomcat()

    # Configuração apache
    config_apache()

    ## Configuração do MfaP como Service Provider:
    if config_sp_properties():
        config_mfaprovider_properties()
    if deploy():
        # Gerar SP Metadata
        metadatafile = 'MfaProvider/src/main/resources/metadata/sp-metadata.xml'
        if generate_metadata(config.get('mfap','restsecurity.user'),
                config.get('mfap','restsecurity.password'),
                config.get('mfap','host.name')+config.get('mfap', 'mfapbasepath'),
                metadatafile):
            metadatadest = config.get('idp', 'dir_base_idp_shibboleth') + '/metadata/' + 'mfaprovider-metadata.xml' 
            shutil.copyfile(metadatafile, metadatadest)
            print ("Metadados configurado com sucesso")
        else:
            print("Não foi possível gerar metadados do MfaProvider")
            utils.revert_backup_files()
            exit()    

        # Configurar SP Metadata no IdP
        ## 1. Copiar metadata do sp
        
        ## 2. Editar metadata-providers.xml
        if not config_metadata_provider(config.get('idp','dir_base_idp_shibboleth')):
            msg = """
            Não foi possível editar o arquivo metadata-providers.xml.
            Por favor,edite manualmente conforme tutorial.
            """
            print(msg)

        ## 3. Deploy do sp
        if deploy():
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
                utils.revert_backup_files()
                exit()

if __name__ == '__main__':
    #TODO : avisar que o script faz backup, mas sugerir backup
    # prévio de alguns arquivos, ainda a listar
   #config_mfa_idp()
   main()
