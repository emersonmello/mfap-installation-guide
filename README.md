# Roteiro de instalação completo da solução multifator (IdP e MfaProvider).

## Pré-requisitos

 * IdP Shibboleth v3.3, tomcat 8 e apache 2 instalados.

## Organização do roteiro

Este roteiro está dividido em:

1. Configuração do FCM
2. Configurações de variáveis para utilização nos scritps
3. Instalação do Mongo
4. Instalação da aplicação MfaProvider e configuração da solução de multifator no Shibboleth IdP.
5. (Extras) Utilitários para Administrador.

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

# Configurações das variáveis

*Obs: executar todos os comandos como root*

1.   Faça o download do projeto `roterio-instalacao` para o diretório de sua preferência. Pode ser utilizado o diretório home do usuário por exemplo.

     ```bash
     git clone https://git.rnp.br/GT-AMPTo/roteiro-instalacao.git
     ```

1.   Dentro do diretório baixado do git,  acesse o diretório `scripts`. Este será nosso diretório base para execução dos próximos passos.

      ```bash
     cd scripts
     ```

2.   No diretório scripts, edite o arquivo `config.ini` e ajuste os valores conforme comentários do próprio arquivo.

     ```bash
     vi config.ini
     ```

# Instalação do MongoDB

1.   No diretório scripts, execute o script `install_mongo.py`

      ```bash
      python2 install_mongo.py
      ```

# Instalação da aplicação MfaProvider e configuração da solução de multifator no Shibboleth IdP.

*Obs: O script irá realizar o backup e cópia dos arquivos originais do IdP para o diretório Backup.*

1.  No diretório scripts, execute o script `install.py`
    
     ```bash
     python2 install.py
     ```

*Obs: Os trechos de código a partir deste momento estarão em arquivos de exemplo com comentários no diretório scripts/alteracoes, para facilitar a visualização do local exato onde devem ser configurados no Idp*

1.   Edite o arquivo `relying-party.xml` do IdP e configure conforme instruções comentadas no arquivo `scripts/alteracoes/conf/relying-party.xml` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/conf/relying-party.xml
    ```
    
3.   Edite o arquivo `general-authn.xml` do IdP alterando as propriedades conforme instruções comentadas no arquivo `scripts/alteracoes/conf/authn/general-authn.xml` do projeto.
    
    ```bash
    sudo vi /opt/shibboleth-idp/conf/authn/general-authn.xml
    ```
 ## Build IdP, Permissões e Reinicialização de serviços

- No diretório roteiro-instalacao/scripts, execute o script para finalizar a configuração:

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