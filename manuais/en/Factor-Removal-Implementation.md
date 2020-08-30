## Introduction

The MfaProvider has a service responsible for removing the second factor from a user.
This service currently is consumed by the script `/opt/mfaprovider/removeSecondFactor.sh`

If you want to consume that service from another application (a web admin interface, for example), follow the instructions provided in the next section.

## Endpoint removeSecondFactor

To consume the service, a GET request is needed. The authentication protocol used is of the type "Basic", so you need to provide a username and password. They are the same you provided when installing the MfaProvider (username and password for the REST endpoints).

The endpoint address is: ```$host/mfa/resource/remove/$username```

Where: 

```
$host = MfaProvider path, ex: https://idp.edu.br/conta
$username = user from which the second factor will be removed
```

Example using curl: 
```bash
curl -X GET -H "Authorization: Basic `echo -n username:password | base64`" https://devampto.cafeexpresso.rnp.br/conta/mfa/resource/remove/aluno
```

After consuming the service, the MfaProvider will present a message informing if the second factor removal was successful or not.
