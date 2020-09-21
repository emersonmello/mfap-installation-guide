# How to setup a local development environment

This tutorial describes the setup for a local development environment.

## Audience

Institutions with a working IdP with the MFaProvider installed and running that want to develop a new authentication factor or maintain/debug an existing one.

## Prerequisites

* Eclipse IDE (with the plugin Buildship Gradle Integration)
* MongoDB
* A working installation of IdP Shibboleth v3.3 (with MFaProvider) like the one from CAFe Federation.

## Importing the project to Eclipse

1. Clone the MFaProvider project to the directory of your choice (DO NOT download it to the Eclipse workspace)

```bash
$ git clone https://git.rnp.br/GT-AMPTo/MfaProvider.git
```

2. In Eclipse, import the MFaProvider as a Gradle project.

3. From the host where the IdP is installed, copy the file `/opt/shibboleth-idp/metadata/idp-metadata.xml ` to a directory in your computer. For instance, `/home/user/mfap-dev/`.

4. In the directory where you've downloaded the project (e.g: `MfaProvider/`), edit the file `./src/main/resources/sp.properties` and change the fields as shown below:

    * **Obs.:** Change the field `idp.metadata` to match the path of the file you've saved in item 3. It is also necessary to replace the `####` of the fields `restsecurity.user` and `restsecurity.password` by the user and password of your choice.

```properties
host.name=https://localhost:9443/conta 
idp.metadata=/home/user/mfap-dev/idp-metadata.xml

restsecurity.user=####
restsecurity.password=####

```

5. To execute the application, click on `Gradle Tasks > conta > gretty > tomcatStart` in the menu.

6. With the application running, generate the SP metadata file by accessing the URL `https://localhost:9443/conta/saml/web/metadata/getNewMetaData`, or using `curl` in the command line: `curl -X GET --user '%s:%s' https://localhost:9443/conta/saml/web/metadata/getNewMetaData --insecure > sp-metadata.xml`

	> **Obs.:** Change `%user` and `%password` to the values configured in the fields  `restsecurity.user` and `restsecurity.password` in the file `sp.properties` that was edited in item 4. 

7. Replace the file `MfaProvider/src/main/resources/metadata/sp-metadata.xml` with the file generated in the previous step.

## MongoDB Configuration

1. Check if MongoDB is running by issuing the command `$sudo service mongodb status`

	> **Obs.:** If it isn't, run `$ sudo service mongodb start`

2. In the project dir (e.g: `MfaProvider/`), edit the file `scriptMongo.js`, change the value of the fields `user` and `pwd` to the values you want and save the file.

3. Also in the project dir, create the mongo user running the following:

   ```bash
   $ mongo < scriptMongo.js
   ```

## IdP Server Configuration

1. Copy the metadata file created in the item 6 of the section [Importing the project to Eclipse](###importing-the-project-to-eclipse) to `/opt/shibboleth-idp/metadata/mfapdev-metadata.xml` in the IdP host

2. Also in the IdP host, edit the file `/opt/shibboleth-idp/conf/metadata-provider.xml` and insert a new entry, as follows, indicating the file copied in the previous item:

```xml
<MetadataProvider id="mfapdev" metadataFile="/opt/shibboleth-idp/metadata/mfapdev-metadata.xml" xsi:type="FilesystemMetadataProvider" />
```

3. Run the script `build.sh` to apply the changes:

```bash
/opt/shibboleth-idp/bin/build.sh
```

## Test

With the application running (item 5 from the section [Importing the project to Eclipse](###importing-the-project-to-eclipse)), visit the URL `https://localhost:9443/conta` from the browser.

You'll see the IdP login page, and after authentication, you'll be redirected to the URL `https://localhost:9443/conta/mfa/cadastrar/dashboard` listing all the available options for the second factor.