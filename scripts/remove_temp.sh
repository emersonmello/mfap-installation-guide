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
cd ~/git/roteiro-instalacao
