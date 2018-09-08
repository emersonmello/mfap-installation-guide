rm -rf MfaProvider
cd /etc/apache2/sites-enabled/
git checkout .
git clean -f
cd /etc/tomcat8/
git checkout .
git clean -f
cd /etc/tomcat8/Catalina/localhost/
git checkout .
git clean -f
cd /opt/shibboleth-idp/
git checkout .
git clean -f
rm -rf flows/authn/fido-ecp-flow/
rm -rf flows/authn/mfa-failure-request-flow/
rm -rf flows/authn/mfa-provider-flow/

cd ~/git/roteiro-instalacao
rm -rf scripts/backup/opt/
rm -rf scripts/insert_apache.txt
rm -rf scripts/scriptMongo.js
rm -rf scripts/MfaProvider*
git checkout scripts/alteracoes/messages/messages.properties
