# -*- coding: utf-8 -*-
"""
    Este script realiza a atualização da aplicação multifator MfaProvider.
    O código fonte é baixado do repositório git e na sequência um pacote
    via gradlew é gerado. Se essa geração for bem sucedida, o tomcat8 é reiniciado.
    
    Autora: shirlei@gmail.com - GTAMPTo - 2018
    Versão: 1.0

"""
from datetime import datetime
import os, shutil, subprocess

import utils

import ConfigParser
config = ConfigParser.ConfigParser()
# Lê as variáveis de configuração
config.read('config.ini')

def set_value(group,field,message):
    variable = raw_input(message)
    while variable == '':
        variable = raw_input('O valor para %s não pode ser nulo, digite novamente: ' % field)
    config.set(group,field,variable)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    return variable

def verify_existing_variable(section,variable):
    variable_value = config.get(section, variable) 
    if variable_value != '' :
        choice = raw_input('Um valor para a variável %s está definido em config.ini. Deseja utilizá-lo? (s,N)' % variable)
        if (choice not in ('S','s')):
            message  = "Informe o valor para %s " % variable
            variable= set_value(section, variable, message)
    return variable

def deploy():
    ## Alterar a variável SP_DIR para o diretório que está configurado no servidor de aplicação apache  ##
    sp_dir= verify_existing_variable('apache', 'sp_dir')
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
    ##
    #   1. Roteiro de instalação da aplicação MfaProvider
    ##
    print("\n=== Clonando o repositório do projeto MfaProvider ===\n")
    print("Você será solicitado a informar seu usuário e senha do git\n")
    # clone repositório MFAProvider
    mfaprovider_repo = config.get('mfap','repositorio')
    # Esta configuração já vai informada por padrão, se não existir, houve algum 
    # problema e deve ser solicitada. Senão, o usuário não precisa tomar conhecimento.
    if mfaprovider_repo is None or mfaprovider_repo == '':
        msg = """
        Não foi encontrado o endereço do repositório do código fonte do MfaProvider
        em config.ini. Por favor, informe manualmente abaixo.
        """
        print msg
        mfaprovider_repo = set_value('mfap','repositorio')

    if os.path.exists('MfaProvider'):
        print("Diretorio MfaProvider existe, fazendo backup")
        dt = datetime.now()
        shutil.move('MfaProvider','MfaProvider.orig.%s' % dt.strftime("%d%m%Y%H%M%S"))
    retcode_gitclone = subprocess.call("git -c http.sslVerify=false clone %s" % mfaprovider_repo, 
        shell=True)
    retcode_gitclone = 0
    if retcode_gitclone != 0:
        msg = """
        Não foi possível clonar o diretório do projeto MfaProvider.
        Por favor, corrija o problema indicado e tente novamente.
        """
        print(msg)
        exit()
    else:
        ## Realiza (re)deploy do MfaProvider
        deploy()



if __name__ == '__main__':
    #TODO : avisar que o script faz backup, mas sugerir backup
    # prévio de alguns arquivos, ainda a listar
   #config_mfa_idp()
   main()
