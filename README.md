# Roteiro de instalação completo da solução multifator (IdP e MfaProvider).

## Pré-requisitos

 * IdP Shibboleth v3.3, tomcat 8 e apache 2 instalados.

## Organização do roteiro

Este roteiro está dividido em 3 partes:

1. Configuração do FCM (Console)
1. Configurações de variáveis para utilização nos scritps
1. Instalação do Mongo
1. Roteiro de instalação da aplicação MfaProvider.
2. Roteiro de configuração para solução de multifator no Shibboleth IdP.
3. (Extras) Utilitários para Administrador.

# Configurações FCM para Diálogo de Confirmação 

Para funcionamento da opção multi-fator de diálogo de confirmação, é necessário possuir uma conta Google com o projeto FCM configurado. Siga os passos a seguir:

1.   Acesse a página de console do FCM e faça login com a conta google: https://console.firebase.google.com/

2.   Clique em `Adicionar Projeto`.

3.   Digite um nome para o projeto (ingnore os demais campos), marque a opção "Aceito os termos.." e clique em `Criar projeto`.

4.   Clique no ícone do Android para adicionar o Firebase ao app para Android, conforme imagem abaixo:

     ![](./images/addapp.png)

5.  Informe no campo *Nome do pacote Android*: `br.gtampto.app2ampto` e clique em `Registrar APP`.

6.   Nas etapas: *Fazer o download do arquivo de configuração* e *Adicionar o SDK do Firebase*, clique em `Próxima`.

7.   Em *Execute seu app para verificar a instalação*, o FCM irá tentar conectar no aplicativo, como ele já foi configurado previamente, esta etapa pode ser ignora, clique em `Pular esta etapa`.

8.   Após criar conta FCM e registrar o app seguindo as instruções, clique em configurações conforme imagem abaixo:

     ![](./images/confcm.png)

9.   Clique em `Configurações do Projeto` e na aba Cloud Messaging, anote os valores dos atributos `chave herdada do servidor` e `código do remetente` .  Segue imagem exemplificando o local dos atributos:

     ![](./images/confcm2.png)

# Configuração de variáveis

1.   Editar o arquivo config.ini e ajustar os valores conforme comentários.


# Roteiro de instalação da aplicação MfaProvider

1.   Executar o script

# Roteiro de instalação da aplicação MfaProvider

## Baixar o projeto MfaProvider do git

O MfaProvider será a aplicação dentro do IdP responsável por gerenciar o segundo fator do usuário.

1.   Faça o download do projeto MfaProvider para o diretório de sua preferência. Pode ser utilizado o diretório home do usuário por exemplo.

     ```bash
     git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git
     ```

## Configuração do Tomcat/Apache para funcionamento do MfaProvider.

*Obs: o roteiro foi desenvolvido considerando o servidor de aplicação tomcat na versão 8.*

### Arquivo de configuração da aplicação no Tomcat:

1.   Edite o arquivo `01-idp.conf`:

     ```bash
     sudo vi /etc/apache2/sites-enabled/01-idp.conf
     ```

    Localize no arquivo, a tag: `<VirtualHost *:443>` e adicione dentro desta tag (abaixo do mesmo trecho de configuração de ProxyPass /idp) o seguinte conteúdo:
    *Obs: Caso utilizar outro  pathname, alterar `/conta` para o nome desejado.*

    ```xml
    ProxyPass /conta ajp://localhost:9443/conta retry=5
     <Proxy ajp://localhost:9443>
       Require all granted
     </Proxy>
    ```
2.   Execute o scrip install.py

TODO: passo 10 do fcm, escrever mfaprovider.properties

## Configuração do MfaP como Service Provider:

1.   No dirtório do projeto MfaProvider, edite o arquivo  `sp.properties`:

     ```bash
     sudo vi src/main/resources/sp.properties
     ```

    Configure o arquivo conforme explicação nos comentários abaixo:

     ```properties
     ##Caminho completo do idp com o pathname ex: https://insituicao.edu.br/conta
     host.name=https://idphost/pathname
     
     ##Caminho completo para o metadata do idp
     idp.metadata=/opt/shibboleth-idp/metadata/idp-metadata.xml
     
     ##Defina um usuario e senha para proteção dos recursos rest
     restsecurity.user=xxx
     restsecurity.password=xxx
     
     ##Defina um usuario e senha para administrador do IdP
     admin.user=xxx
     admin.password=xxx
     ```

    *Obs: Os valores definidos neste momento para credenciais rest serão utilizados posteriormente na configuração de autenticação do IdP. Não utilizar o mesmo usuário e senha para admin e restsecurity*

### Configurar SP Metadata no IdP

1.   Referencie, também no IdP, o path do arquivo. Para isso, altere o arquivo `metadata-providers.xml`. 
     
     ```bash
     sudo vi /opt/shibboleth-idp/conf/metadata-providers.xml
     ```
     
    Localize a tag `<MetadataProvider id="ShibbolethMetadata"...../>` e adicione o seguinte conteúdo abaixo desta tag:

     ```xml
     <MetadataProvider id="LocalMetadata"  xsi:type="FilesystemMetadataProvider" 
       metadataFile="/opt/shibboleth-idp/metadata/sp-metadata.xml"/>
     ```
     Ficará desta forma, por exemplo:

     ```xml
     <MetadataProvider id="ShibbolethMetadata" xsi:type="ChainingMetadataProvider"
        xmlns="urn:mace:shibboleth:2.0:metadata"
        xmlns:resource="urn:mace:shibboleth:2.0:resource"
        xmlns:security="urn:mace:shibboleth:2.0:security"
        xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="urn:mace:shibboleth:2.0:metadata http://shibboleth.net/schema/idp/shibboleth-metadata.xsd
                            urn:mace:shibboleth:2.0:resource http://shibboleth.net/schema/idp/shibboleth-resource.xsd 
                            urn:mace:shibboleth:2.0:security http://shibboleth.net/schema/idp/shibboleth-security.xsd
                            urn:oasis:names:tc:SAML:2.0:metadata http://docs.oasis-open.org/security/saml/v2.0/saml-schema-metadata-2.0.xsd">

     <MetadataProvider id="LocalMetadata"  xsi:type="FilesystemMetadataProvider" 
         metadataFile="/opt/shibboleth-idp/metadata/sp-metadata.xml"/>
      
     #continuação arquivo........
     ```

3.  No diretório do projeto MfaProvider e execute o script de deploy da aplicação novamente para utilização das novas configurações: 

     ```bash
     ./deploy.sh
     ```

Siga os próximos passos para relizar a configuração no IdP.

# Roteiro de configuração para solução de multifator no Shibboleth IdP

* Observações: 

  * Todos os arquivos indicados no tutorial, para copiar/utilizar como base na configuração do IdP, estão no diretório "alteracoes" do projeto baixado do git.

## Download do projeto:

1. Faça o download dos fontes do projeto IdP-Customizado-GtAmpto, por exemplo, para o diretório home do usuário.

     ```bash
     git clone https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto.git
     ```

## Alteração do fluxo principal para Multifator:

1.   Edite o arquivo idp.properties `sudo vi /opt/shibboleth-idp/conf/idp.properties` e altere conforme explicação:

     1.1.   Localize a linha com a entrada `idp.authn.flows` e altere o controle de fluxo para utilizar MFA:
        
        idp.authn.flows= MFA
            

     1.2.   Localize a linha com a entrada `idp.additionalProperties` e acrescente ao final da linha: `/conf/authn/mfaprovider.properties`. Deve ficar similar ao listado abaixo:
        
        idp.additionalProperties= /conf/ldap.properties, /conf/saml-nameid.properties, /conf/services.properties, /conf/authn/duo.properties, /conf/authn/mfaprovider.properties
            
## Configuração Rest do MfaProvider:

1.   A partir do diretório do projeto IdP-Customizado-GtAmpto baixado no git, edite o arquivo mfaprovider.properties `mfaprovider.properties` altererando as propriedades apresentadas abaixo: 
    
    ```bash
    sudo vi alteracoes/conf/authn/mfaprovider.properties
    ```
      
     ```properties
     ## Enredeço do MfaProvider 
     idp.mfaprovider.apiHost  = https://exemploidp.br/conta/
     ## Usuário e senha para autenticação REST configurado no sp.properties do projeto MfaProvider
     idp.mfaprovider.username  = usuario
     idp.mfaprovider.password  = senha
     ```
     

## Configurações gerais, flows, views, properties, libs e arquivos necessários:

1.   A partir do diretório IdP-Customizado-GtAmpto, execute o script `implantacao_mfa_idpv3.sh` para realizar a copia dos arquivos para o IdP. Esse script irá realizar
backup e cópia dos arquivos necessários.

     ```bash
     sudo ./implantacao_mfa_idpv3.sh
     ```

*Obs: Os trechos de código a partir deste momento estarão em arquivos de exemplo com comentários no diretório IdP-Customizado-GtAmtpo baixado do git, para facilitar a visualização do local exato onde devem ser configurados no Idp*

1.   Edite o arquivo `relying-party.xml` do IdP e configure conforme instruções comentadas no arquivo `alteracoes/conf/relying-party.xml` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/conf/relying-party.xml
    ```
    
2.   Edite o arquivo `attribute-filter.xml` do IdP alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/attribute-filter.xml` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/conf/attribute-filter.xml
    ```
    
3.   Edite o arquivo `general-authn.xml` do IdP alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/authn/general-authn.xml` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/conf/authn/general-authn.xml
    ```
    
4.   Edite o arquivo `messages.properties` do IdP e configure conforme instruções comentadas no arquivo `alteracoes/messages/messages.properties` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/messages/messages.properties
    ```
    
## Build IdP, Permissões e Reinicialização de serviços

- Execute o script para finalizar a configuração:

    ```bash
    sudo ./finaliza_configuracao.sh 
    ```
    
## Teste

- A aplicação será disponibilizada no endereço configurado, ex: `https://endereco-idp/conta`.
- Faça a autenticação e verifique o auxílio da página para cadastrar e utilizar o segundo fator.


# (Extras) Utilitários para Administrador:

#### Remover segundo fator de determinado usuário:

- Na pasta do projeto do MfaProvider,  utilize o script abaixo e informe o login do usuário para remover as configurações de segundo fator

     ```bash
     ./removeSecondFactor.sh
     ```

#### Habilitar e desabilitar métodos de segundo fator:

- Na pasta do projeto do MfaProvider, edite o arquivo  `src/main/resource/factor.properties` e utilize `true` para habilitar ou `false` para desabilitar o fator desejado.