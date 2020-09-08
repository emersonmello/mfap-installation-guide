# Como configurar provedores de serviços (SP) para solicitar que os provedores de identidade (IdPs) realizem MFA

Este guia apresenta como habilitar a requisição do SP Shibboleth para solicitar
MFA no IdP. Ou seja, o SP só aceitará usuários que autenticaram com múltiplos-fatores.

## Pré-requisitos:
* Shibboleth Service Provider (SP) 2.6 em funcionamento;
* Shibboleth Identity Provider (IdP) 3.3.1 com a solução MFaP instalada conforme indicado no roteiro [Principal roteiro de instalação da solução multi-fator (IdP e MfaProvider)](Readme.md)
 

### Modificando solicitações SAML

Ao gerar um pedido de autenticação SAML, onde o MFA é o perfil desejado, explicitamente é necessário listar o valor de autenticação que seu SP está disposto a aceitar em `<RequestedAuthnContext>`.
De forma geral, deve ser modificado no arquivo de configuração em que é definido o pedido de autenticação SAML:

```xml
<samlp:RequestedAuthnContext Comparison="exact">
    <saml:AuthnContextClassRef> http://id.incommon.org/assurance/mfa </saml:AuthnContextClassRef>
</samlp:RequestedAuthnContext>
```

A configuração a ser feita depende da forma que cada SP está estruturado.
Por exemplo, no Shibboleth SP2 a modificação deve ser feita apenas no arquivo `/etc/shibboleth/shibboleth2.xml` para a instalação padrão, ou em
`/opt/shibboleth-sp/etc/shibboleth/shibboleth2.xml`. Neste contexto, a configuração a ser feita é dentro do
elemento `SessionInitiator`. O arquivo ficaria da seguinte forma:

```xml
<SessionInitiator type="Chaining" Location="/DS" id="DS" relayState="cookie">
    <SessionInitiator type="SAML2" acsIndex="1" acsByIndex="false" template="bindingTemplate.html" authnContextClassRef="http://id.incommon.org/assurance/mfa" forceAuthn="true">
            <samlp:RequestedAuthnContext Comparison="exact" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
                    <saml:AuthnContextClassRef>http://id.incommon.org/assurance/mfa</saml:AuthnContextClassRef>
            </samlp:RequestedAuthnContext>
    </SessionInitiator>
    <SessionInitiator type="Shib1" acsIndex="5"/>
    <SessionInitiator type="SAMLDS" URL="https://ds.cafeexpresso.rnp.br/WAYF.php"/>
</SessionInitiator>
```

Desta forma, o MFA é o único valor solicitado. Mesmo que um IdP tenha suporte ao [MFA Profile](https://refeds.org/profile/mfa), ele só pode responder com sucesso a tal solicitação se o MFA for realmente realizado na autenticação.