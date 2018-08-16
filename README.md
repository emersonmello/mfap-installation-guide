# Roteiro de instalação completo da solução multifator (IdP e MfaProvider).

## Pré-requisitos

 * IdP Shibboleth v3.3.

## Organização do roteiro

Este roteiro está dividido em 3 partes:

1. Roteiro de instalação da aplicação MfaProvider.
2. Roteiro de configuração para solução de multifator no Shibboleth IdP.
3. (Extras) Utilitários para Administrador.


# Roteiro de instalação da aplicação MfaProvider

## Baixar o projeto MfaProvider do git

- Faça o download do projeto MfaProvider para o diretório de sua preferência.

```bash
git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git
```

## Configuração do Tomcat/Apache para funcionamento do MfaP.

*Obs: o roteiro foi desenvolvido considerando o servidor de aplicação tomcat na versão 8.*

- Crie um arquivo xml com o pathname desejado (caminho a ser acessado pelo usuário para acessar o MfaP).
Por padrão, o MfaP é configurado em `https://endereco-idp/conta`. Caso desejar utilizar outro pathname, alterar `conta` para o nome desejado.

```bash
sudo vi /etc/tomcat8/Catalina/localhost/conta.xml 
```

- Insira o seguinte conteúdo dentro do arquivo: 

```xml
<Context docBase="/opt/mfaprovider/mfaprovider.war"
    unpackWAR="true"
    swallowOutput="true">
    <Manager pathname="" />
</Context>
```

- Edite o arquivo `/etc/tomcat8/server.xml` para configuração de porta e adicione:

```xml
<Connector port="9443" address="127.0.0.1" protocol="AJP/1.3" />
```

- Edite o arquivo `etc/apache2/sistes-enable/01-idp.conf` e adicione o seguinte conteúdo:

```xml
 ProxyPass /conta ajp://localhost:9443/conta retry=5
  <Proxy ajp://localhost:9443>
    Require all granted
  </Proxy>
```
*Obs: Caso utilizar outro  pathname, alterar `/conta` para o nome desejado.*

- Reinicie o serviço do Apache:

```bash
sudo systemctl restart apache2 
```

## Instalação e configuração do banco de dados MongoDB

Baixe e instale o mongo de acordo com a versão do sistema operacional, conforme orientação do manual oficial 
[Manual de instalação do mongo](https://docs.mongodb.com/manual/tutorial/). Após instação, é necessário configurar a autenticação do banco.

- Crie o diretório a ser utilizado para salvar os dados do MongoDB:

```bash
sudo mkdir /data & mkdir /data/db
```

*Obs: Caso deseje utilizar outro diretório, é necessário passar o parâmetro `--dbpath /diretoriodesejado` ao iniciar o serviço.*

- Inicie o serviço do MongoDB.

```bash
sudo mongod --quiet &
```

- No diretório que foi realizado o download do projeto MfaProvider, edite o arquivo `scriptMongo.js` e defina os valores de `user` e `pwd` (usuário e senha) para segurança do banco e salve o arquivo:

```js
use mfaprovider
db.createUser(
   {
     user:"VALORDEFINIDO",
     pwd:"VALORDEFINIDO",
     roles: ["readWrite","dbAdmin"]
   }
)
```

- Após, execute o script para criar o usuário:

```bash 
mongo < scritpMongo.js
```

- Altere no arquivo `src/main/resources/mongo.properties` as propriedades `mongo.user` e `mongo.pass` com usuário e senha definidos para o banco anteriormente:

```xml
mongo.host=localhost:27017
mongo.port=27017
mongo.db=mfaprovider
mongo.user=VALORDEFINIDO
mongo.pass=VALORDEFINIDO

```

- Inicie o Mongo com a opção --auth

```bash
sudo mongod --quiet --auth &`
```

## Configurações FCM para Diálogo de Confirmação 

Para funcionamento da opção multi-fator de diálogo de confirmação, é necessário possuir uma conta Google com o projeto FCM configurado. Siga os passos a seguir:

1. Acesse a pagina de console do FCM e faça login com a conta google: https://console.firebase.google.com/
2. Clique em `Adicionar Projeto`.
3. Digite um nome para o projeto, e clique em `Criar projeto`.
4. Clique em adicionar o Firebase ao app para Android.
5. Informe no campo *Nome do pacote Android*: `br.gtampto.app2ampto` e clique em `Registrar APP`.
6. Nas etapas: *Fazer o download do arquivo de configuração* e *Adicionar o SDK do Firebase*, clique em `Próxima`.
7. Em *Execute seu app para verificar a instalação*, o FCM irá tentar conectar no aplicativo, como ele ja foi configurado previamente, esta etapa pode ser ignora, clique em `Pular esta etapa`.

- Após criar conta FCM e registrar o app seguindo as instruções, Clique em Configurações do Projeto e na aba Cloud Messaging, anote os valores dos atributos: 
`chave herdada do servidor` e `código do remetente`.

- No diretório do projeto MfaProvider, altere no arquivo `src/main/resources/mfaprovider.properties` as propriedades:

```xml
##substitua por chave herdada do servidor FCM
br.rnp.xmpp.serverKey= XXXX

##substitua por código do remetente FCM
br.rnp.xmpp.senderId= XXXXX

#Substituir somente se utilizar um pathname diferente do padrão conta
mfapbasepath=conta
```


## Configuração do MfaP como Service Provider:

- Edite o arquivo  `src/main/resources/sp.properties` e configure conforme explicação abaixo:

```xml
##Caminho completo do idp com o pathname
host.name=https://endereco-idp/pathname

##Caminho completo para o metadata do idp
idp.metadata=/opt/shibboleth-idp/metadata/idp-metadata.xml

##Defina um usuario e senha para proteção dos recursos rest
restsecurity.user=xxx
restsecurity.password=xxx

##Defina um usuario e senha para administrador do IdP
admin.user=xxx
admin.password=xxx
```

*Obs: Os valores definidos neste momento para credenciais rest serão utilizados posteriormente na configuração de autenticação do IdP.*

### SP Metadata

- No diretório do projeto MfaProvider execute o script para realizar o deploy da aplicação para configuraçaõ dos metadados.

```bash
./deploy.sh
```

- Após, siga os procedimentos abaixo para gerar os metadados do MfaProvider:

1. Acesse o endereço `https://endereco-idp/pathname/saml/web/metadata`.
2. Entre com o usuário e senha configurado para o administrador do IdP.
3. Clique em `Gerar novo arquivo de metadados`
4. Deixe os dados setados automaticamente e clique em `gerar metadados`
5. Baixe o arquivo gerado ou copie o coteúdo, e sobrescreva o arquivo `src/main/resources/metadata/sp-metadata.xml`.

### Configurar SP Metadata no IdP

- Os metadados do MfaProvider recém-gerados precisam ser carregados pelo IdP, copie o arquivo `sp-metadata.xml` para o diretório "metadata" no IdP (`/opt/shibboleth-idp/metadata`) e referencie, também no IdP, o path no arquivo `/conf/metadata-providers.xml`. 
Por exemplo:

```xml
<MetadataProvider id="LocalMetadata"  xsi:type="FilesystemMetadataProvider" 
      metadataFile="/opt/shibboleth-idp/metadata/sp-metadata.xml"/>
```

- Entre no diretório `/opt/shibboleth-idp/bin` e realize p build do IdP para utilizar as novas configurações:

```bash
./build.sh
```

## Deploy

- Execute o script de deploy da aplicação novamente para utilização das novas configurações: 

```bash
./deploy.sh
```
*Obs: Não é possível testar a aplicação antes de realizar as configurações no IdP.*

Siga os próximos passos para relizar a configuração no IdP.

# Roteiro de configuração para solução de multifator no Shibboleth IdP

* Observações: 

  * Todos os arquivos indicados no tutorial, para copiar/usar como base na configuração do IdP, estão no diretório "alteracoes" do projeto baixado do git.
  * $IDP_HOME = Local onde está configurado o IdP, por padrão: "/opt/shibboleth-idp";
   
## Download do projeto:

- Faça o download dos fontes do projeto IdP-Customizado-GtAmpto, por exemplo, para o diretório home do usuário.

```bash
git clone https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto.git
```

## Alteração do fluxo principal para Multifator:

- Edite o arquivo `$IDP_HOME/conf/idp.properties` e altere conforme explicação:

1. Localize a linha com a entrada  `idp.authn.flows` e altere o controle de fluxo para utilizar MFA:
    `idp.authn.flows= MFA`;
2. Localize a linha com a entrada `idp.additionalProperties` e acrescente ao final da linha: `/conf/authn/mfaprovider.properties`. Deve ficar similar ao listado abaixo:
    `idp.additionalProperties= /conf/ldap.properties, /conf/saml-nameid.properties, /conf/services.properties, /conf/authn/duo.properties, /conf/authn/mfaprovider.properties `

## Configurações gerais, flows, views, properties, libs e arquivos necessários:

- A partir do diretório do projeto baixado no git, copie o arquivo `alteracoes/conf/authn/mfaprovider.properties` para `$IDP_HOME/conf/authn/` e altere as propriedades apresentadas abaixo: 
    
```xml
## Enredeço do MfaProvider 
idp.mfaprovider.apiHost  = https://exemploidp.br/conta/
## Usuário e senha para autenticação REST configurado no sp.properties do projeto MfaProvider (<diretorio_git_MfaProvider>src/main/resources/sp.properties)
idp.mfaprovider.username  = usuario
idp.mfaprovider.password  = senha
```

1. Edite o arquivo `$IDP_HOME/conf/relying-party.xml` e configure conforme instruções comentadas no arquivo `alteracoes/conf/relying-party.xml` do projeto.

2. Configure as permissões para atributos do MfaProvider no `$IDP_HOME/conf/attribute-filter.xml` alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/attribute-filter.xml` do projeto.

3. Edite o arquivo `$IDP_HOME/conf/authn/general-authn.xml` alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/authn/general-authn.xml` do projeto.

4. Edite o arquivo `$IDP_HOME/messages/messages.properties` e configure conforme instruções comentadas no arquivo `alteracoes/messages/messages.properties` do projeto.

5. Copie o arquivo `alteracoes/conf/authn/mfa-authn-config.xml` para `$IDP_HOME/conf/authn/` sobrescrevendo o existente;

6. Copie o conteúdo do diretório `alteracoes/flows/authn` para  `$IDP_HOME/flows/authn`;

7. Copie o conteúdo do diretório `alteracoes/views` para  `$IDP_HOME/views`;

8. Copie o conteúdo do diretório `alteracoes/webapp/images` para  `$IDP_HOME/webapp/images`;

9. Copie o conteúdo do diretório `alteracoes/webapp/WEB-INF/lib` para `$IDP_HOME/webapp/WEB-INF/lib`.
    * Observação: As dependências contidas neste ditetório foram geradas a partir do projeto: [MfaProviderIdp](https://git.rnp.br/GT-AMPTo/mfadialogo). 
    
## Build IdP

- Execute o build do IdP em `$IDP_HOME/bin/build.sh`:

    ```bash
    ./build.sh
    ```

## Teste

- A aplicação será disponibilizada no endereço configurado, ex: `https://endereco-idp/conta`.
- Faça a autentiicação no IdP e verifique o auxílio da página para cadastrar e utilizar o segundo fator.


# (Extras) Utilitários para Administrador:

#### Remover segundo fator de determinado usuário:

- Na pasta do projeto do MfaProvider,  utilize o script abaixo e informe o login do usuário para remover as configurações de segundo fator

```bash
./removeSecondFactor.sh
```

#### Habilitar e desabilitar métodos de segundo fator:

- Na pasta do projeto do MfaProvider, edite o arquivo  `src/main/resource/factor.properties` e utilize `true` para habilitar ou `false` para desabilitar o fator desejado.