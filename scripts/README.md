# IdP Personalizado MFA GtAmpto

#### Modificações necessárias para utilização de multi-fator de autenticação no IdP Shibboleth 

#### Pré-requisitos:

 * Idp Shibboleth v3.3 em funcionamento;
 * Servidor de aplicação Tomcat (versão 8 ou mais atual);
 * Aplicação MfaProvider configurada: [https://git.rnp.br/GT-AMPTo/MfaProvider](https://git.rnp.br/GT-AMPTo/MfaProvider). 
   
#### Procedimento para configuração de um IdP v3.3 existente:

* Observações: 

  * Todos os arquivos indicados no tutorial, para copiar/usar como base na configuração do IdP, estão no diretório "alteracoes" do projeto baixado do git, conforme passo 1 abaixo.

  * $IDP_HOME = Local onde está configurado o IdP, por padrão: "/opt/shibboleth-idp";


1. Baixar o fonte do projeto do IdPCustomizado, disponível em https://git.rnp.br/GT-AMPTo/IdP-Customizado-GtAmpto, por exemplo, para o diretório home do usuário.

2. Alterações no arquivo `$IDP_HOME/conf/idp.properties` 

    1.1 Localizar a linha com a entrada  `idp.authn.flows` e alterar o controle de fluxo para utilizar o controle de fluxo pelo mfa-auth-config:

    `idp.authn.flows= MFA`;

    1.2 Localizar a linha com a entrada`idp.additionalProperties` e acrescentar ao final da linha /conf/authn/mfaprovider.properties. Deve ficar sim similar ao listado abaixo:

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
- Faça a autentiicação no IdP com um usuário e verifique o auxílio da página para cadastrar o segundo fator.
- Após cadastro, realize novamente a autenticação
- Em caso de sucesso, o serviço de multi-fator foi configurado com sucesso em seu IdP.
