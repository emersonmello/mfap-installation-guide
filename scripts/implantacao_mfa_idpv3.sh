#!/bin/bash 
#Objetivo: Implantação das configuração do MfaProvider no ambiente IDPv3
#Autor: Samuel Bristot Loli

VAR_HOME_IDP_V3="/opt/shibboleth-idp"

echo "Iniciando script de implantação do MfaProvider no IDP"

echo "Verificando se existe o diretório IDP nesta maquina"


if [ -d "${VAR_HOME_IDP_V3}" ]
then
	 echo "Diretório IDP encontrado"
else
	 echo "Diretorio IDP não encontrado. Finalizando implantação....." 
	 exit 2
fi

echo "Realizando backups dos arquivos do script"

cp -r --parents  "${VAR_HOME_IDP_V3}"/conf/relying-party.xml "${VAR_HOME_IDP_V3}"/conf/relying-party.xml.orig 
cp -r --parents  "${VAR_HOME_IDP_V3}"/conf/attribute-filter.xml "${VAR_HOME_IDP_V3}"/conf/attribute-filter.xml.orig
cp -r --parents  "${VAR_HOME_IDP_V3}"/conf/authn/general-authn.xml "${VAR_HOME_IDP_V3}"/conf/authn/general-authn.xml.orig
cp -r --parents  "${VAR_HOME_IDP_V3}"/conf/authn/mfa-authn-config.xml "${VAR_HOME_IDP_V3}"/conf/authn/mfa-authn-config.xml.orig
cp -r --parents  "${VAR_HOME_IDP_V3}"/flows/authn/* backup
cp -r --parents  "${VAR_HOME_IDP_V3}"/views/* backup
cp -r --parents  "${VAR_HOME_IDP_V3}"/webapp/images/* backup
cp -r --parents  "${VAR_HOME_IDP_V3}"/webapp/WEB-INF/lib/* backup
cp -r --parents  "${VAR_HOME_IDP_V3}"/webapp/images/* backup


echo "Fim do processo de backup"

echo "Fazendo as copias dos arquivos para o IDP"

cp alteracoes/messages/messages.properties "${VAR_HOME_IDP_V3}"/messages/messages.properties
cp alteracoes/conf/authn/mfa-authn-config.xml "${VAR_HOME_IDP_V3}"/conf/authn/
cp -R alteracoes/flows/authn/* "${VAR_HOME_IDP_V3}"/flows/authn/
cp alteracoes/views/* "${VAR_HOME_IDP_V3}"/views/
cp alteracoes/webapp/images/* "${VAR_HOME_IDP_V3}"/webapp/images/
cp alteracoes/webapp/WEB-INF/lib/* "${VAR_HOME_IDP_V3}"/webapp/WEB-INF/lib/
echo "Fim do processo de copia"

echo "Alterando permissoes dos arquivos para o tomcat"
chown -hR tomcat8:tomcat8 /opt/shibboleth-idp/


echo "Executando build do IDP"
sudo /opt/shibboleth-idp/bin/build.sh -Didp.target.dir=/opt/shibboleth-idp
echo "Build executado com sucesso"

echo "Script finalizado"
