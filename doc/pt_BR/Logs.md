# Manual de gerenciamento de logs

A solução multi-fator `MfaProvider` permite o acompanhamento de logs para identificar ações de cadastro, 
autenticação, qual fator utilizado, entre outras informações relevantes.
Uma parte desta solução está como um módulo dentro do contexto da aplicação Shibboleth-Idp e outra parte está
em um contexto próprio da aplicação `MfaProvider`. Segue abaixo, os procedimentos e locais para consulta aos logs da solução.

## Módulo MfaProvider - IdP

Neste contexto serão apresentado os logs das verificações feitas referente a autenticação multi-fator no IdP, como verificações solicitadas ao
`mfaprovider` para verificação de fatores extras do usuário, autenticação e tipo de autenticação solicitada ao `mfaprovider` 
bem como o retorno desta autenticação .

Os logs do módulo `MfaProvider` no IdP são gerados junto com os logs do próprio Shibboleth Idp em: `/opt/shibboleth-idp/logs/idp-process.log`.
Para filtrar os logs referente ao `MfaProvider`, pode ser utilizada a palavra chave: `GTAMPTO`.

Exemplo: 
```bash
less /opt/shibboleth-idp/logs/idp-process.log | grep GTAMPTO
```



## Aplicação MfaProvider

Neste contexto serão apresentados logs referente ao registro de fatores extras, autenticação após pedido oriundo do Idp, retorno encaminhado ao Idp,
além de outras informações como dados de execução do servidor FCM. 

Os logs referente a aplicação do `MfaProvider` são gerados no diretório de logs do Tomcat ex:`/var/lib/tomcat8/logs` com o nome: `logMfaProvider-datadodia.log`.

**Observação**: este caminho pode ser alterado caso desejado. Para isto, basta editar o arquivo `roteiro-instalação/scripts/MfaProvider/src/main/resources/logback.xml`, alterar para o caminho desejado e em `roteiro-instalação/scripts/MfaProvider` executar o comando `./build.sh` para atualizar a aplicação.




