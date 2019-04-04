# Manual de como montar localmente um ambiente de DEV para o MFaP

## Para quem se destina este tutorial
> Instituições que desejam desenvolver novos fatores de autenticação e que já possuam um servidor IdP com MFaP funcionando corretamente.

## Pré-requisitos

* Eclipse IDE (com plugin Buildship Gradle Integration)
* MongoDB
* Ter um IdP Shibboleth v3.3 (com MFaProvider) remoto operacional, por exemplo, o IdP que está na federação CAFe.

### Importando projeto no Eclipse
1. Faça o download do projeto MfaProvider para o diretório de sua preferência (**ATENÇÃO:**  não deve colocar tal diretório dentro do workspace do Eclipse).

```bash
$ git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git
```

2. No eclipse, importe o MfaProvider como projeto Gradle. 

3. Na máquina onde está instalado o IdP, copiar o arquivo `/opt/shibboleth-idp/metadata/idp-metadata.xml `  para seu computador e salve em um diretório de sua preferência. Por exemplo: `/home/user/mfap-dev/`.

4. No diretório onde você baixou o projeto (ex: `MfaProvider/`), edite o arquivo `./src/main/resources/sp.properties` e altere os campos conforme exemplo:

	* **Obs.:** O campo `idp.metadata` deve ser alterado para o caminho onde foi copiado o arquivo do item 3. Também é necessário substituir os `####` dos campos `restsecurity.user` e `restsecurity.password` por usuário e senha de sua preferência. 

```properties
host.name=https://localhost:9443/conta 
idp.metadata=/home/user/mfap-dev/idp-metadata.xml

restsecurity.user=####
restsecurity.password=####

```

5. Para executar a aplicação clique no menu/aba: `Gradle Tasks > conta > gretty > tomcatStart`

6. Com a aplicação rodando, gere o arquivo com metadata do SP através da seguinte URL `https://localhost:9443/conta/saml/web/metadata/getNewMetaData`, usando o comando `curl` por exemplo: `curl -X GET --user '%s:%s' https://localhost:9443/conta/saml/web/metadata/getNewMetaData --insecure > sp-metadata.xml`

	* **Obs.:** Altere `%user` e `%password`  para os valores configurados nos campos `restsecurity.user` e `restsecurity.password` do  arquivo `sp.properties` editado no item 4. 

7. Substituir o arquivo `MfaProvider/src/main/resources/metadata/sp-metadata.xml` pelo arquivo gerado no item anterior.

### Configuração do MongoDB

1. Verifique se o serviço do MongoDB está rodando `$ sudo service mongodb status`

	* **Obs.:** Caso não estiver, execute `$ sudo service mongodb start`

2. No diretório do projeto (ex: `MfaProvider/`), edite o arquivo `scriptMongo.js`, altere os valores dos campos `user` e `pwd` de acordo com o desejado e salve o arquivo.

3. Ainda no diretório do projeto, realize a criação do usuário executando:
   ```bash
   $ mongo < scriptMongo.js
   ```

### Configuração do Servidor IdP

1. Copiar o arquivo com o metadata gerado no item 6 da seção [Importando projeto no Eclipse](###importando-projeto-no-eclipse) para `/opt/shibboleth-idp/metadata/mfapdev-metadata.xml` na máquina onde está o IdP
2. Ainda na máquina do IdP, Editar o arquivo `/opt/shibboleth-idp/conf/metadata-provider.xml` e inserir uma entrada, conforme exemplo, apontando para o arquivo copiado no item anterior;
```xml
<MetadataProvider id="mfapdev" metadataFile="/opt/shibboleth-idp/metadata/mfapdev-metadata.xml" xsi:type="FilesystemMetadataProvider" />
```


3. Execute o script `build.sh` do IdP para aplicar as alterações realizadas.
```bash
/opt/shibboleth-idp/bin/build.sh
```

### Teste

> Com a aplicação em execução (item 5 da seção [Importando projeto no Eclipse](###importando-projeto-no-eclipse)), acesse a URL `https://localhost:9443/conta` pelo navegador. 
>
> A página de login do IdP será apresentada e após a autenticação o navegador será redirecionado para a URL `https://localhost:9443/conta/mfa/cadastrar/dashboard` listando as opções de segundo fator.