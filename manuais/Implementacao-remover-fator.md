## Introdução

Existe um serviço no MfaProvider que pode ser consumido por outra aplicação para remover o segundo fator de um usuário.
Este serviço atualmente é consumido pelo script /opt/mfaprovider/removeSecondFactor.sh 

Caso desejar implementar um gerenciamento administrativo em outro sistema e consumir este serviço, siga as instruções abaixo

## Endpoint removeSecondFactor

Para consumir o serviço, é necessário acessar por meio de "GET".
O protocolo de segurança utilizado é do tipo Basic, sendo necessário informar o usuário e senha para proteção dos recursos rest informado durante a execução do script de instalação .

O endereço do endpoint responsável é: ```$host/mfa/resource/remove/$username```

Onde: 
$host = caminho do MfaProvider, ex: https://idp.edu.br/conta
$username = usuário que deseja remover o fator

Exemplo utilizando curl: 
  ```bash
  curl -X GET -H "Authorization: Basic `echo -n usuario:senha | base64`" https://devampto.cafeexpresso.rnp.br/conta/mfa/resource/remove/aluno
  ```

## Conclusão

Após o consumo do serviço, o MfaProvider irá retornar uma mensagem informando o sucesso ou não na remoção do segundo fator para o usuário informado.

