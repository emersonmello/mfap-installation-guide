# Roteiro de instalação completo da solução multifator (IdP e MfaProvider).

Este roteiro está dividido em 3 partes:

1. Roteiro de instalação da aplicação MfaProvider.
2. Roteiro de configuração para utilização da solução de multi-fator em um IdP Shibboleth.
3. (Extras) Utilitários para Administrador.

# Roteiro de instalação da aplicação MfaProvider

## Baixar o projeto MfaProvider do git

Faça o download do projeto MfaProvider para o diretório de sua preferência.

```bash
git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git
```

## Configuração do Tomcat/Apache para funcionamento do MfaP.


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
* Obs: Caso utilizar outro  pathname, alterar `/conta` para o nome desejado.

- Reiniciar o serviço do Apache

```bash
sudo systemctl restart apache2 
```

## Instalação e configuração do banco de dados MongoDB

Baixe e instale o mongo de acordo com a versão do sistema operacional, conforme orientação do manual oficial 
https://docs.mongodb.com/manual/tutorial/

Após instalado, é necessário configurar a autenticação do banco.

- Crie o diretório a ser utilizado para salvar os dados do MongoDB:

```bash
sudo mkdir /data & mkdir /data/db
```

* Obs: Caso deseje utilizar outro diretório, é necessário passar o parâmetro `--dbpath /diretoriodesejado` ao iniciar o serviço.

- Inicie o serviço do MongoDB.

```bash
sudo mongod &
```

* Obs: Ao iniciar o serviço, por padrão o mongo tentará utilizar o caminho `/data/db` para armazenamento de dados, caso o diretório não existir, irá apresentar erro na inicialização do serviço. Para resolução, crie o diretório ou utilize o comando especificando outro diretório, ex: 

```bash 
mongod --dbpath /data/mongodb
```

- No diretório que foi realizado o download do projeto MfaProvider, edite o arquivo `scriptMongo.js` e altere os valores de `user` e `pwd` de acordo com o desejado e salve o arquivo.

- Após, execute o script para criar o usuário:

```bash 
mongo < scritpMongo.js
```

- Inicie o Mongo com a opção --auth

```bash
sudo mongod --auth &`
```


## Configurações FCM para Diálogo de Confirmação 

Para funcionamento da opção multi-fator de diálogo de confirmação, é necessário possuir uma conta Google com o projeto FCM configurado. Siga os passos a seguir:

- Acesse a pagina de console do FCM e faça login com a conta google: https://console.firebase.google.com/
- Clique em `Adicionar Projeto`.
- Digite um nome para o projeto, e clique em `Criar projeto`.
- Clique em adicionar o Firebase ao app para Android.
- Informe no campo *Nome do pacote Android*: `br.gtampto.app2ampto` e clique em `Registrar APP`.
- Nas etapas: *Fazer o download do arquivo de configuração* e *Adicionar o SDK do Firebase*, clique em `Próxima`.
- Em *Execute seu app para verificar a instalação*, o FCM irá tentar conectar no aplicativo, como ele ja foi configurado previamente, esta etapa pode ser ignora, clique em `Pular esta etapa`.

Após criar conta FCM e registrar o app seguindo as instruções, Clique em Configurações do Projeto e na aba Cloud Messaging, anote os valores dos atributos: 
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

Edite o arquivo  `src/main/resources/sp.properties` e configure conforme explicação abaixo:

```xml
##Caminho completo do idp com o pathname
host.name=https://endereco-idp/pathname

##Caminho completo para o metadata do idp
idp.metadata=/opt/shibboleth-idp/metadata/idp-metadata.xml

##Defina um usuario e senha para proteção dos recursos rest
restsecurity.user=xxxxxxx
restsecurity.password=xxxxxxxx

##Defina um usuario e senha para administrador do IdP
admin.user=xxx
admin.password=admin
```

* Os valores definidos neste momento para credenciais rest serão utilizados posteriormente na configuração de autenticação do IdP.

### SP Metadata

Para gerar metadados para o SP, no diretório do projeto MfaProvider execute o script para realizar o deploy da aplicação para configuraçaõ dos metadados:

```bash
./deploy.sh
```

Após, siga os procedimentos abaixo:

- Acesse o endereço `https://endereco-idp/pathname/saml/web/metadata`.
- Entre com o usuário e senha configurado para o administrador do IdP.
- Clique em `Gerar novo arquivo de metadados`
- Deixe os dados setados automaticamente e clique em `gerar metadados`
- Baixe o arquivo gerado ou copie o coteúdo, e sobrescreva o arquivo `src/main/resources/metadata/sp-metadata.xml`.

### Configurar SP Metadata no IdP

Os metadados do SP recém-gerados precisam ser carregados pelo IdP, copie o arquivo `sp-metadata.xml` para o diretório "metadata" no IdP (`/opt/shibboleth-idp/metadata`) e referencie, também no IdP, o path no arquivo `/conf/metadata-providers.xml`. 
Por exemplo:

```xml
<MetadataProvider id="LocalMetadata"  xsi:type="FilesystemMetadataProvider" 
      metadataFile="/opt/shibboleth-idp/metadata/sp-metadata.xml"/>
```

Após, entre no diretório `/opt/shibboleth-idp/bin` e realize p build do IdP para utilizar as novas configurações:
```bash
./build.sh
```

## Deploy

Execute o script de deploy da aplicação novamente para utilização das novas configurações: 
```bash
./deploy.sh
```

## Configurações do Shibboleth IdP para MultiFator

Não é possível testar a aplicação antes de realizar as configurações no IdP.
Siga os próximos passos para relizar a configuração no IdP.

# Roteiro de configuração para utilização da solução de multi-fator em um IdP Shibboleth

## Pré-requisitos:

 * Idp Shibboleth v3.3 em funcionamento;
 * Servidor de aplicação Tomcat (versão 8 ou mais atual);
 * Aplicação MfaProvider configurada.
   
## Procedimento para configuração de um IdP v3.3 existente:

* Observações: 

  * Todos os arquivos indicados no tutorial, para copiar/usar como base na configuração do IdP, estão no diretório "alteracoes" do projeto baixado do git.
  * $IDP_HOME = Local onde está configurado o IdP, por padrão: "/opt/shibboleth-idp";

1. fazer o download dos fontes do projeto IdPCustomizado, disponível em https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto, por exemplo, para o diretório home do usuário.

2. Alterações no arquivo `$IDP_HOME/conf/idp.properties` 

    2.1 Localizar a linha com a entrada  `idp.authn.flows` e alterar o controle de fluxo para utilizar o controle de fluxo pelo mfa-auth-config:

    `idp.authn.flows= MFA`;

    2.2 Localizar a linha com a entrada`idp.additionalProperties` e acrescentar ao final da linha /conf/authn/mfaprovider.properties. Deve ficar sim similar ao listado abaixo:

    `idp.additionalProperties= /conf/ldap.properties, /conf/saml-nameid.properties, /conf/services.properties, /conf/authn/duo.properties, /conf/authn/mfaprovider.properties `

3. A partir do projeto baixado do git, copie o arquivo `alteracoes/conf/authn/mfaprovider.properties` para `$IDP_HOME/conf/authn/` e altere as propriedades apresentadas abaixo: 
    ```xml
    ## Enredeço do MfaProvider Ex: idp.mfaprovider.apiHost  = https://exemploidp.br/conta/
    idp.mfaprovider.apiHost  = https://idp2ampto.cafeexpresso.rnp.br/conta/
    ## Usuário e senha para autenticação REST configurado no properties no projeto do MfaProvider (<diretorio_git_MfaProvider>src/main/resources/sp.properties)
    idp.mfaprovider.username  = usuario
    idp.mfaprovider.password  = senha
    ```

4. Edite o arquivo `$IDP_HOME/conf/relying-party.xml` e configure conforme instruções comentadas no arquivo `alteracoes/conf/relying-party.xml` do projeto.

5. Configure as permissões para atributos do MfaProvider no `$IDP_HOME/conf/attribute-filter.xml` alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/attribute-filter.xml` do projeto  (diretório alteracoes, disponivel no projeto do IdP Customizado baixado do do git).

6. Copie `alteracoes/conf/authn/mfa-authn-config.xml` para `$IDP_HOME/conf/authn/` sobrescrevendo o arquivo existente;

7. Edite o arquivo `$IDP_HOME/conf/authn/general-authn.xml` alterando as propriedades conforme instruções comentadas no arquivo `alteracoes/conf/authn/general-authn.xml` do proejto.

8. Copie o conteúdo do diretório `alteracoes/flows/authn` para  `$IDP_HOME/flows/authn`;

9. Edite o arquivo `$IDP_HOME/messages/messages.properties` e configure conforme instruções comentadas no arquivo `alteracoes/messages/messages.properties` do projeto.

10. Copiar o diretório `alteracoes/views` para  `$IDP_HOME/views`;

11. Copiar conteúdo do diretório `alteracoes/webapp/images` para  `$IDP_HOME/webapp/images`;

12. Copiar conteúdo do diretório `alteracoes/webapp/WEB-INF/lib` para  `$IDP_HOME/webapp/WEB-INF/lib`.
    * Observação: As dependências contidas neste ditetório foram geradas a partir do projeto: [https://git.rnp.br/GT-AMPTo/mfadialogo](https://git.rnp.br/GT-AMPTo/mfadialogo). 
    Em caso de não funcionamento, copiar o conteúdo do diretório dependency-jar diretamente para o diretório $IDP_HOME/webapp/WEB-INF/lib (raiz) no IdP, comportamento este atrelado a configuração de cada IdP. 

13. Ao final, executar rebuild no war do IdP em `$IDP_HOME/bin/build.sh`:

    ```bash
    ./build.sh
    ```

14. Teste
- A aplicação será disponibilizada no endereço configurado, ex: `https://endereco-idp/conta`.
- Faça a autentiicação no IdP e verifique o auxílio da página para cadastrar e utilizar o segundo fator.


# (Extras) Utilitários para Administrador:

#### Remover segundo fator de determinado usuário:

Na pasta do projeto do MfaProvider,  utilize o script abaixo e informe o login do usuário para remover as configurações de segundo fator

```bash
./removeSecondFactor.sh
```

#### Habilitar e desabilitar métodos de segundo fator:

Na pasta do projeto do MfaProvider, edite o arquivo  `src/main/resource/factor.properties` e utilize `true` para habilitar ou `false` para desabilitar o fator desejado.