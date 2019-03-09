# Manual de gerenciamento de logs

A solução multi-fator MfaProvider permite o acompanhamento de logs para indentificar ações de cadastro, 
autenticação, qual fator utilizado, entre outras informações relevantes.
Uma parte desta solução está como um módulo dentro do contexto da aplicação Shibboleth-Idp e outra parte está
em um contexto próprio da aplicação MfaProvider. Segue abaixo, os procedimentos e locais para consulta aos logs da solução.

## Módulo MfaProvider - IdP

Neste contexto serão apresentado os logs das verificações feitas referente a autenticação multifator no IdP, como verificações solicitadas ao
mfaprovider para verificação de fatores extras do usuário, autenticação e tipo de autenticação solicitada ao mfaprovider 
bem como o retorno desta autenticação .

Os logs do móludo MfaProvider no IdP são gerados junto com os logs do próprio Shibboleth Idp em: `/opt/shibboleth-idp/logs/idp-process.log`.
Para filtrar os logs referente ao MfaProvider, pode ser utilizada a palavra chave: `GTAMPTO`.
Exemplo: `less /opt/shibboleth-idp/logs/idp-process.log | grep GTAMPTO`



## aplicação MfaProvider

Neste contexto serão apresentados logs referente ao registro de fatores extras, autenticação após pedido oriundo do Idp, retorno encaminhado ao Idp,
além de outras informações como dados de execução do servidor FCM. 

Os logs referente a aplicação do Mfaprovider são gerados no diretório `/opt/mfaprovider` com o nome: `logMfaProvider-datadodia.log`.
Para filtrar os logs, é possível utilizar a palavra chave: `GTAMPTO`. 
Exemplo: `less /opt/mfaprovider/logMfaProvider-2019-01-01.log | grep GTAMPTO`




