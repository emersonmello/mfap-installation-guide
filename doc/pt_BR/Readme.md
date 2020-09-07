# Roteiro de instalação completo da solução multi-fator (IdP e MfaProvider).

- [Roteiro de instalação completo da solução multi-fator (IdP e MfaProvider).](#roteiro-de-instalação-completo-da-solução-multi-fator-idp-e-mfaprovider)
  - [Primeira Instalação](#primeira-instalação)
    - [Pré-requisitos](#pré-requisitos)
    - [Configurações FCM para Diálogo de Confirmação](#configurações-fcm-para-diálogo-de-confirmação)
    - [Ajustes de configuração da máquina](#ajustes-de-configuração-da-máquina)
    - [Certificado auto-assinado](#certificado-auto-assinado)
    - [Instalação do banco de dados MongoDB](#instalação-do-banco-de-dados-mongodb)
    - [Instalação da aplicação MfaProvider e configuração da solução de multi-fator no Shibboleth IdP.](#instalação-da-aplicação-mfaprovider-e-configuração-da-solução-de-multi-fator-no-shibboleth-idp)
    - [Instalação Básica](#instalação-básica)
    - [Instalação Avançada](#instalação-avançada)
    - [Testes para verificar se a instalação foi feita com sucesso](#testes-para-verificar-se-a-instalação-foi-feita-com-sucesso)
  - [Atualização da aplicação MFaP já instalada](#atualização-da-aplicação-mfap-já-instalada)
    - [Atualização da aplicação multi-fator MfaProvider](#atualização-da-aplicação-multi-fator-mfaprovider)
  - [Utilitários para Administrador](#utilitários-para-administrador)
    - [Remover segundo fator de determinado usuário](#remover-segundo-fator-de-determinado-usuário)
    - [Habilitar e desabilitar métodos de segundo fator](#habilitar-e-desabilitar-métodos-de-segundo-fator)


## Primeira Instalação

### Pré-requisitos

* IdP Shibboleth v3.3, Apache Tomcat 8 e Apache HTTPd 2 instalados.

### Configurações FCM para Diálogo de Confirmação 

Para funcionamento da opção multi-fator com diálogo de confirmação, é necessário utilizar o servidor de fila de mensagens FCM do Google. 
Siga os passos a seguir para configurar o FCM:

1.   Crie uma conta google para a instituição (caso já possuir, ignorar esta etapa): https://accounts.google.com/SignUp?hl=pt
2.   Acesse a página de console do FCM e faça login com a conta google: https://console.firebase.google.com/
3.   Clique em `Adicionar Projeto`.
4.   Digite um nome para o projeto (ignore os demais campos), marque a opção "Aceito os termos.." e clique em `Criar projeto`.
5.   Clique no ícone do Android para adicionar o Firebase ao app para Android, conforme imagem abaixo:

![](../images/addapp.png)

6.  Informe no campo *Nome do pacote Android*: `br.edu.ifsc.sj.gtampto` e clique em `Registrar APP`.

7.   Na etapa: *Fazer o download do arquivo de configuração* , clique em `Próxima`.

8.   Na etapa: *Adicionar o SDK do Firebase*, clique em `Próxima`.

9.   Em *Execute seu app para verificar a instalação*, o FCM irá tentar conectar no aplicativo, como ele já é configurado previamente, esta etapa pode ser ignorada, clique em `Pular esta etapa`.

10.  Após criar conta FCM e registrar o app seguindo as instruções, clique em configurações conforme imagem abaixo:

![](../images/confcm.png)

11.  Clique em `Configurações do Projeto` e na aba Cloud Messaging, anote os valores dos atributos `chave herdada do servidor` e `código do remetente` que serão solicitados pelo script de instalação.  
Segue imagem exemplificando o local dos atributos:

![](../images/confcm2.png)

### Ajustes de configuração da máquina 

Para que o IdP consiga realizar requisições para seu próprio endereço, é necessário um ajuste na configuração do `/etc/hosts`

1.  Edite o arquivo `/etc/hosts`:

     ```bash
     sudo vi /etc/hosts
     ```
2.  Apague a linha que contém o endereço `127.0.1.1`. O arquivo deverá ficará semelhante ao exemplo abaixo:

    ```config
    127.0.0.1       localhost
    #Endereço de Ip e Host
    191.36.8.39     idpexemplo.idp.edu.br idpexemplo
    ```
3.  Reinicie o serviço de rede para aplicação da nova configuração:
    
    ```bash
    sudo systemctl restart networking.service
    ```

### Certificado auto-assinado

A comunicação IdP - MfaProvider se dá utilizando requisições via HTTPS, as quais necessitam que a Java Virtual Machine (JVM) confie no certificado utilizado.
Caso o certificado ssl do IdP for um certificado do tipo auto-assinado, deve ser importado para a JVM usando o seguinte comando:

```<JAVA_HOME>/bin/keytool -import -alias <server_name> -keystore <JAVA_HOME>/jre/lib/security/cacerts -file public.crt```

Caso não saiba qual é o certificado ssl a ser importado, execute o comando abaixo para exibir o caminho do arquivo:

```cat /etc/apache2/sites-enabled/01-idp.conf | grep SSLCertificateFile```

Supondo que `JAVA_HOME` seja `/usr/lib/jvm/java-8-oracle` e que o certificado ssl utilizado esteja no caminho `/etc/ssl/certs/server.crt`, 
e que o server_name seja `idp.rnp.br`, o comando final ficaria da seguinte forma:

```/usr/lib/jvm/java-8-oracle/bin/keytool -import -alias idp.rnp.br -keystore /usr/lib/jvm/java-8-oracle/jre/lib/security/cacerts -file /etc/ssl/certs/server.crt```

**Atenção**: A senha de administração da keystore da JVM vai ser solicitada. A senha padrão, caso não tenha sido mudada, é *changeit*. Esse procedimento deve ser repetido sempre que o certificado for trocado.

Após, reinicie o Tomcat: `sudo systemctl restart tomcat8`


### Instalação do banco de dados MongoDB

1. Baixe e instale o MongoDB pelo gerenciador de pacotes:
    ```bash
    sudo apt-get install mongodb
    ```
   - **Observação**: Ao término da instalação, o serviço do MongoDB será instanciado automaticamente, o qual pode ser conferido pelo comando `sudo systemctl status mongodb.service` (caso não estiver iniciado, utilize o comando `sudo systemctl start mongodb`).
    
### Instalação da aplicação [MfaProvider](https://git.rnp.br/GT-AMPTo/MfaProvider) e configuração da solução de multi-fator no Shibboleth IdP.

**Observação:** executar todos os comandos como root

1. Faça o download do projeto `roteiro-instalacao` para o diretório de sua preferência. Pode ser utilizado o diretório home do usuário por exemplo.
    ```bash
    git clone https://git.rnp.br/GT-AMPTo/roteiro-instalacao.git
    ```
    - **Observação:** Em caso de problemas com certificado, utilize o comando:
      -  `git -c http.sslVerify=false clone https://git.rnp.br/GT-AMPTo/roteiro-instalacao.git`  
1. Dentro do diretório baixado do git,  acesse o diretório `scripts`. Este será nosso diretório base para execução dos próximos passos.
    ```bash
    cd scripts
    ```

Há duas formas de realizar a instalação, de forma básica ou de forma avançada.

- Na instalação básica, o script irá questionar os valores das variáveis básicas para funcionamento padrão da solução de multi-fator.
- A instalação avançada é recomendada caso queira alterar o pathname padrão do `MfaProvider` (`idp.instituicao.edu.br/conta`) ou tenha algum problema na instalação básica devido a locais e diretórios diferente do padrão.

### Instalação Básica

1. No diretório scripts, execute o script `install.py` 
    ```bash
    python2 install.py
    ```
Serão realizados questionamentos durante a instalação, tais como:

 - Definição de usuário e senha do banco de dados;
 - Definição de usuário e senha para proteção dos recursos rest;
 - Endereço do IdP sem https, ex:  `idp.instituicao.edu.br`.

Após processo de instalação concluído, verificar a seção [Testes](#testes) para verificar o funcionamento da aplicação.

### Instalação Avançada

1. No diretório `scripts`, edite o arquivo `config.ini` conforme abaixo:
   1. Caso deseje alterar o caminho dos diretórios:
      - Endereço do metadata:
    alterar o atributo: `idp.metadata=/opt/shibboleth-idp/metadata/idp-metadata.xml`
      - Diretório base do Idp: alterar o atributo: `dir_base_idp_shibboleth=/opt/shibboleth-idp`
      - Endereço do server.xml do tomcat: alterar o atributo: `tomcat_server_config=/etc/tomcat8/server.xml`
      - Endereço do arquivo de configuração do site do idp no apache: alterar o atributo: `apache_conf_file=/etc/apache2/sites-enabled/01-idp.conf`
   1. Caso desejar alterar o `pathname`  (nome a ser acessado pelo usuário para acessar o MfaProvider no Idp) :
      - Endereço do pathname: alterar o atributo `mfapbasepath=conta`

**Os demais atributos não devem ser alterados, os que estão sem informação o script de instalação irá solicitar durante o processo.**

Por fim, no diretório scripts, execute o script `install.py`

```bash
python2 install.py
```

Após processo de instalação concluído, verificar a seção [Testes](#testes) para verificar o funcionamento da aplicação.

### Testes para verificar se a instalação foi feita com sucesso

- A aplicação será disponibilizada no endereço configurado, ex: `https://idp.instituicao.edu.br/conta`.

Ao acessar o endereço, caso apresentar a mensagem "Sua conexão não é segura" ou "Sua conexão não é particular" (dependendo do navegador), isto pode indicar que você possui um certificado auto-assinado e será necessário realizar o processo descrito na seção [Certificado auto-assinado](#certificado-auto-assinado)
 Utilitários para Administrador > Uso de certificado auto-assinado ou expiração de certificado. **Este processo evitará erro após processo de login.**

- Faça a autenticação e verifique o auxílio da página para cadastrar e utilizar o segundo fator.

## Atualização da aplicação MFaP já instalada

### Atualização da aplicação multi-fator MfaProvider

Eventualmente pode ser necessário atualizar a aplicação multi-fator MfaProvider e esse procedimento pode ser feito separadamente.

Para isso, no diretório do roteiro de instalação, que foi baixado conforme passo [Instalação da aplicação MfaProvider e configuração da solução de multi-fator no Shibboleth IdP](#instalação-da-aplicação-mfaProvider-e-configuração-da-solução-de-multifator-no-shibboleth-idP) da instalação inicial, execute o seguinte comando:

```bash
python update_mfaprovider.py
```
    
O script acima irá realizar a atualização da aplicação multi-fator MfaProvider, baixando o código fonte do repositório git, gerando o pacote necessário para implantação no tomcat8, e reiniciando-o.

## Utilitários para Administrador

### Remover segundo fator de determinado usuário

- No diretório `/opt/mfaprovider`,  utilize o script abaixo e informe o login do usuário para remover as configurações de segundo fator

```bash
./removeSecondFactor.sh
```

### Habilitar e desabilitar métodos de segundo fator

- Na pasta do projeto `scripts/MfaProvider`, edite o arquivo  `src/main/resource/factor.properties` e utilize `true` para habilitar ou `false` para desabilitar o fator desejado. Após, ainda no diretório `scripts/MfaProvider`, execute o deploy da aplicação, através do comando:

```bash
./deploy.sh
```