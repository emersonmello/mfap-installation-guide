#!/bin/bash 
#Objetivo: Implantação das configuração do MfaProvider no ambiente IDPv3
#Autor: Samuel Bristot Loli

VAR_HOME_IDP_V3="/opt/shibboleth-idp"

echo "Verificando se existe o diretório IDP nesta maquina"

if [ -d "${VAR_HOME_IDP_V3}" ]
then
	 echo "Diretório IDP encontrado"
else
	 echo "Diretorio IDP não encontrado. Finalizando implantação....." 
	 exit 2
fi

echo "Alterando permissoes dos arquivos para o tomcat"
chown -hR tomcat8:tomcat8 /opt/shibboleth-idp/

echo "Executando build do IDP"
sudo /opt/shibboleth-idp/bin/build.sh -Didp.target.dir=/opt/shibboleth-idp
echo "Build executado com sucesso"


echo "Reiniciando o tomcat8"
systemctl restart tomcat8
echo "Server Reiniciando"

echo "Script finalizado"
