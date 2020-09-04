# Como desenvolver o novo fator de autenticação

O MfaProvider foi desenvolvido de forma a ser extensível e com baixo acoplamento, para adicionar um nova tecnologia como fator de autenticação (novo fator), como pré-requisito é necessário ao desenvolvedor conhecimentos em *Java*, *Spring MVC* e *Apache Velocity*.

Neste guia será apresentado como implementar um novo fator seguindo a arquitetura do projeto atual, citando como exemplo a implementação do TOTP (*time-based one-time password*). 

Para implementação do novo fator, é necessário alterações no MfaProvider e em arquivos do Shibboleth Idp v3, conforme segue abaixo:

## MfaProvider

1. Criar uma classe de modelo para o novo fator com os atributos desejados para armazenamento em banco: 
   - A classe deve estar dentro do pacote: ``br.rnp.factor``
   - Exemplo: ``br.rnp.factor.TOTPFactor.java``
2. Editar o enum: ``br.rnp.modelo.enumerations.TipoAutenticacao.java`` e adicionar um novo registro com as informações do novo fator
   - Exemplo: Informações do TOTP no próprio arquivo). 
3. Criar uma classe na camada de serviço que ficará responsável pela lógica do novo fator de autenticação (ex: ``br.rnp.service.factorService.TOTPService.java``)
   - Implementar a interface - ``br.rnp.service.factorService``
   - Implementar os método exigido exigido pela interface que será responsável pela lógica de autenticação: 
    ```java
    public AuthenticationResponseDTO authenticates(AuthenticationRequestDTO aut)
    ``` 
   - **Observação**: ``AuthenticationRequestDTO`` é o DTO (*data transfer object*) oriundo do IdP, solicitando autenticação. O ``AuthenticationResponseDTO`` é o DTO de resposta ao IdP confirmando ou negando a autenticação.
4. Modificar o arquivo ``br.rnp.service.factorService.factor.FactorFactory.java``. Adicionar a nova classe ao padrão *factory* (responsável por instanciar classes da camada de serviço a partir do fator selecionado pelo usuário no IdP). Vide exemplo no próprio arquivo referente ao objeto TOTPService.
5. Modificar o arquivo ``br.rnp.controller.RegistrationController.java`` e implementar métodos referente ao registro que serão chamados pela camada de visão e irão interagir com a camada de serviço. 
   - Exemplo: métodos referentes ao TOTP no arquivo: 
    ```java
    public registerTOTP(HttpSession session);  
    public finishTOTPRegister(@RequestParam("totpCode") String totpCode, HttpSession session).
    ```
6. Criar objetos na camada de visão
   - Criar um arquivo `.jsp` referente ao cadastro específico do novo fator no diretório webapp. Ex: ``src/main/webapp/cadastrototp.jsp``
7. Adicionar uma entrada para o novo fator no arquivo ``factor.properties`` para habilitar o fator na pagina principal.

## Shibboleth IdP

1. Editar o arquivo ``/opt/shibboleth-idp/view/loginMfaProvider.vm`` e acrescentar uma verificação com o código do fator cadastrado no enum anteriormente e sua implementação. 
   - Exemplo: Entrada referente ao TOTP 
    ```velocity
    #elseif ($fator.getFatorPreferencial()=="503")
         ###implementação...
    #end
    ```
2. Em casos mais complexos, onde é necessário interações com objetos do shibboleth-idp no backend, possuímos um projeto que ao final é gerado um *jar* e disponibilizado como uma *lib* do Idp. Neste caso pode ser criado/alterado objetos no projeto [MfaProviderIdp](https://git.rnp.br/GT-AMPTo/mfadialogo). Após alterações, seguir o Readme.md do referido projeto.

## Conclusão

Para que as alterações tenham efetividade, é necessário realizar deploy do MfaProvider (Seguir instruções no [Roteiro de instalação completo da solução multi-fator (IdP e MfaProvider)](Readme.md) contido neste projeto) e também reiniciar o Tomcat do IdP.


