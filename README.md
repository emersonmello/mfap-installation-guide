# Multi-factor installation guide

This repository presents a guide to install a comprehensive and open source solution (available at https://git.rnp.br/GT-AMPTo/MfaProvider) to offer multi-factor authentication for Shibboleth Identity Providers (version 3.3.1).

Based on the [Multi-factor Authentication Profile standard (REFEDS MFA Profile)](https://refeds.org/profile/mfa), our solution [(MFaProvider)](https://git.rnp.br/GT-AMPTo/MfaProvider) provides three extra second factors:

- One-Time Password - TOTP standard 
  - you can use Google Authenticator
- FIDO2 (WebAuthN)
  - you can use physical token such as Yubikey
- Phone Prompt - Mobile App developed by us
  - [Android source code](https://git.rnp.br/GT-AMPTo/App2Ampto) 
  - [iOS source code](https://git.rnp.br/GT-AMPTo/amptoios)

## Manuals in English

- [Main multi-factor installation guide (IdP and MfaProvider)](doc/en/Readme.md)
  - [Log management manual](doc/en/Logs.md) 
  - [Removing the second factor from a user](doc/en/Factor-Removal-Implementation.md)
  - [How to setup a local development environment](doc/en/setup-local-dev.md)
    - [How to implement a new factor according to the current architecture](doc/en/New-Factor.md)
  - How to configure Service Provider to request that Identity Providers perform MFA

## Manuais em Português

- [Principal roteiro de instalação da solução multi-fator (IdP e MfaProvider)](doc/pt_BR/Readme.md)
  - [Como verificar os *logs* gerados pela solução](doc/pt_BR/Logs.md)
  - [Como remover o segundo fator associado a conta de um usuário](doc/pt_BR/Implementacao-remover-fator.md)
  - [Como montar um ambiente local de desenvolvimento para o MFaP](doc/pt_BR/Ambiente-DEV-local-MFaP.md)
    - [Como desenvolver o novo fator de autenticação](doc/pt_BR/Novo-fator.md)
  - [Como configurar provedores de serviços (SP) para solicitar que os provedores de identidade (IdPs) realizem MFA](doc/pt_BR/sp-mfa.md)

## Organization of the GT-AMPTo's repositories

- **Multi-factor installation guide**
  - https://git.rnp.br/GT-AMPTo/roteiro-instalacao
  - Use this repository to perform the automated installation of the MFaP solution at the Identity Provider. The script will download codes from [MFaProvider](https://git.rnp.br/GT-AMPTo/MfaProvider) and [MfaProviderIdp](https://git.rnp.br/GT-AMPTo/mfadialogo) repositories
- **MFaProvider**
  - https://git.rnp.br/GT-AMPTo/MfaProvider
  - Application responsible for performing MFA authentication of users and which presents a dashboard for users to enable their authentication factors
- **MFaP library for the IdP**
  - https://git.rnp.br/GT-AMPTo/mfadialogo
  - Library to be invoked by the IdP's `AuthFlow`(in the `.xml` file) and that will allow to interact with the [MFaProvider](https://git.rnp.br/GT-AMPTo/MfaProvider)
- **Mobile applications specific for Phone Prompt** 
  - https://git.rnp.br/GT-AMPTo/App2Ampto - Android version
  - https://git.rnp.br/GT-AMPTo/amptoios - iOS version
  - Required if you want to use the Phone Prompt as a second authentication factor



## Authors
- [Emerson Ribeiro de Mello](https://github.com/emersonmello) - Federal Institute of Santa Catarina (IFSC)
- [Carlos Eduardo da Silva](https://www.researchgate.net/profile/Carlos_Da_Silva6) - Sheffield Hallam University
- [Michelle Silva Wangham](https://www.researchgate.net/profile/Michelle_Wangham)  - Universidade do Vale do Itajaí (UNIVALI)
- Samuel Bristot Loli - Federal Institute of Santa Catarina (IFSC)
- [Shirlei Aparecida Chaves](https://github.com/shirlei) - Federal Institute of Santa Catarina (IFSC)
- [Gabriela Cavalcanti da Silva](https://github.com/gabicavalcante) - Federal University of Rio Grande do Norte
- Bruno Bristot Loli - CIASC