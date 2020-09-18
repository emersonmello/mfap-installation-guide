# How to configure Service Providers (SP) to require Multi-Factor from the Identity Provider (IdP)
This guide presents how to enable the SP Shibboleth request to require MFA from the IdP. That is, the SP will only accept users that have authenticated with multi-factor.


## Prerequisites
* A working installation of the Shibboleth Service Provider (SP) 2.6
* A working installation of the Shibboleth Identity Provider (IdP) 3.3.1 with the MFaP application installed as indicated in the [Main multi-factor installation guide (IdP and MfaProvider)](doc/en/Readme.md)
 

### Changing SAML requests

When requesting a SAML authentication, if MFA profile is wanted, it is necessary to list the authentication value that your SP is willing to accept in `<RequestedAuthnContext>`.
Modify the file in which the SAML authentication request is defined, like the example below:

```xml
<samlp:RequestedAuthnContext Comparison="exact">
    <saml:AuthnContextClassRef> http://id.incommon.org/assurance/mfa </saml:AuthnContextClassRef>
</samlp:RequestedAuthnContext>
```

The configuration to be made is dependant on the way each SP is organized.
For instance, in the Shibboleth SP2 the changes have to be made in the file `/etc/shibboleth/shibboleth2.xml`, for the standard installation, or in `/opt/shibboleth-sp/etc/shibboleth/shibboleth2.xml`. 
In that file, you have to change the `SessionInitiator` element. After editing it, it should look like the following:

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

That way, the MFA is the only value requested. Even if an IdP supports the [MFA Profile](https://refeds.org/profile/mfa), it will only be able to successfully respond to an authentication request if MFA is performed.
