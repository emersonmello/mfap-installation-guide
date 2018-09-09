Os arquivos xml presentes nesta seção são os arquivos presentes no IdP V3,
copiados logo após a execução dos procedimentos descritos na atividade 2 do
roteiro disponível em:

https://wiki.rnp.br/display/cafewebsite/Roteiro+de+Atividades+para+Entrada+de+um+IDP

Esses arquivos estão aqui disponibilizados para servirem de documentação e referência futura
dos arquivos bases que foram utilizados para implementação dos scripts de escrita
nesses arquivos, especificamente os disponíveis em scripts/config_xml_files.py



Uma breve descrição de cada arquivo e sua relação com o MfaProvider:

* /opt/shibboleth-idp/conf/attribute-filter.xml

  Configura  os atributos que serão disponibilizados para o SP MfaProvider

* /opt/shibboleth-idp/conf/metatadata-providers.xml

  Configura o endereço local do arquivo de metadados do SP MfaProvider

* /opt/shibboleth-idp/conf/relying-party.xml

  Configura os fluxos de autenticação disponíveis

* /opt/shibboleth-idp/conf/authn/general-authn.xml


