# Log Management Manual

The MfaProvider allows log tracking to identify actions related to registration, what factor was used during the authentication, and other relevant information. 
Below is the relevant information for consulting the logs.

## MfaProvider module - IdP

In this context, the logged info will be related to the checks made regarding the multi-factor authentication in the IdP, such as requests to the MfaProvider about user extra authentication factors, authentication and authentication type requested to the MfaProvider, as well as the authentication response.

Those logs are generated together with the Shibboleth IdP log, in the `/opt/shibboleth-idp/logs/idp-process.log` file.
To filter the MfaProvider logs, you can use the keyword `GTAMPTO`.
For instance: `less /opt/shibboleth-idp/logs/idp-process.log | grep GTAMPTO`


## MfaProvider Application

In this context, logs will be presented regarding the registration of extra factors, authentication requests from the Idp, request responses to the IdP, among other information such as FCM server execution data.

Such logs are genereated in the Tomcat logs dir, for instance`/var/lib/tomcat8/logs`, with the name`logMfaProvider-<currentdate>.log`.

> Obs.: The logs path can be changed. To do so, edit the file `scripts/MfaProvider/src/main/resources/logback.xml`, change to the path you want and in `scripts/MfaProvider` run the `./build.sh` to update the MfaProvider.




