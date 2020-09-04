# Multi-factor installation guide

This repository presents a guide to install a comprehensive and open source solution to offer multi-factor authentication for Shibboleth Identity Providers (version 3.3.1).

Based on the [Multi-factor Authentication Profile standard (REFEDS MFA Profile)](https://refeds.org/profile/mfa), our solution provides three extra second factors:

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

## Manuais em Português

- [Principal roteiro de instalação da solução multi-fator (IdP e MfaProvider)](doc/pt_BR/Readme.md)
  - [Como verificar os *logs* gerados pela solução](doc/pt_BR/Logs.md)
  - [Como remover o segundo fator associado a conta de um usuário](doc/pt_BR/Implementacao-remover-fator.md)
  - [Como montar um ambiente local de desenvolvimento para o MFaP](doc/pt_BR/Ambiente-DEV-local-MFaP.md)
    - [Como desenvolver o novo fator de autenticação](doc/pt_BR/Novo-fator.md)
