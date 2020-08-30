## Introduction

The MfaProvider development aimed to be extensible and low coupled. To add a new authentication factor, the developer should have prior experience with *Java*, *Spring MVC* and *Apache Velocity*.

This guide will present how to implement a new factor according to the current architecture, using as an example the TOTP implementation (*time-based one-time password*).
In order to implement a new factor, it is necessary to make changes in the MfaProvider and in some Shibboleth Idp v3 files, as follows:

## MfaProvider

1) Create a model class for the new Factor, with the necessary attributes to be stored in the database.
   
     - The class has to be created in the ``br.rnp.factor`` package
       <br> ex: ``br.rnp.factor.TOTPFactor.java``

2) Edit the enum: ``br.rnp.modelo.enumerations.TipoAutenticacao.java`` and add a new entry containing the information of the new factor.

3) Create a service class that will be responsible for the logic of the new authentication factor (ex: ``br.rnp.service.factorService.TOTPService.java``)
    - Implement the interface - ``br.rnp.service.factorService``
    - Implement the required methods by the interface responsible for the authentication logic:

    ```java
    public AuthenticationResponseDTO authenticates(AuthenticationRequestDTO aut)
    ``` 

    >Obs: ``AuthenticationRequestDTO`` is the DTO (Data Transfer Object) coming from the IdP, requiring authentication; ``AuthenticationResponseDTO`` is the DTO answering the IdP, confirming or denying the authentication.

4) Modify the class ``br.rnp.service.factorService.factor.FactorFactory.java``, adding the new factor to the *factory* pattern (responsible for instantiating service layer classes from the factor selected by the user in the IdP). Use as example the factors already present in that class, as the TOTPService.

5) Modify the class ``br.rnp.controller.RegistrationController.java``, implementing the methods related to the new factor (for example, the registration method that will be invoked from the view layer and will interact with the service layer) Ex: methods related to the TOTP:

    ```java
    public registerTOTP(HttpSession session);  
    public finishTOTPRegister(@RequestParam("totpCode") String totpCode, HttpSession session).
    ```

6) Create a page for the new factor

    - Create a .jsp file for the new factor in the webapp dir, so the user can interact to enable that factor in his/her account. Ex: ``src/main/webapp/cadastrototp.jsp``

5) Add an entry for the new factor in the ``factor.properties`` file to enable it in the MfaProvider dashboard. Set it to true to be enabled (it will be presented to the user in the MfaProvider dashboard) and to false to be disabled (won't be available in the user dashboard).

## Shibboleth IdP

1) Edit the ``/opt/shibboleth-idp/view/loginMfaProvider.vm`` file and add an entry with the new factor code (the one you provided in step 2)
 
Ex: Entry related to the TOTP, which was registered with the code 503:

```velocity
#elseif ($fator.getFatorPreferencial()=="503")
        ###implementação...
#end
```

2)In more complex cases, where interaction with shibboleth-idp objects is needed in the backend, there is a repository with a project that allows you to build a *jar* to add to the IdP. In this case, you can create or change objects in that project [MfaProviderIdp](https://git.rnp.br/GT-AMPTo/mfadialogo) and follow the instructions on the README available in the repository.

## Conclusion

Once you finish adding the new factor according to the instructions provided in this tutorial, you have to re-deploy the MfaProvider, following the instructions in the [README](README.md) file and restarting the IdP.




