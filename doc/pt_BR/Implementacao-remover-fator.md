# Como remover o segundo fator associado a conta de um usuário

O MfaProvider possui um serviço responsável por remover o segundo fator de um usuário.
Este serviço atualmente é consumido pelo script `/opt/mfaprovider/removeSecondFactor.sh`

Caso desejar implementar um gerenciamento administrativo em outro sistema e consumir este serviço, siga as instruções a seguir.

## Endpoint `removeSecondFactor`

Para realizar o consumo do serviço serviço, é necessário acessar por meio de "`GET`".
A autenticação utilizada utilizado é do tipo "`HTTP Basic`", sendo necessário informar o usuário e senha para consumir o recurso REST, o mesmo informado durante a execução do script de instalação.

O endereço do endpoint responsável é: ```$host/mfa/resource/remove/$username```

Onde: 

```
$host = caminho do MfaProvider, ex: https://idp.edu.br/conta
$username = usuário que deseja remover o fator
```

Exemplo utilizando curl com o host de exemplo `devampto.cafeexpresso.rnp.br`: 
  ```bash
  curl -X GET -H "Authorization: Basic `echo -n usuario:senha | base64`" https://devampto.cafeexpresso.rnp.br/conta/mfa/resource/remove/aluno
  ```

## Conclusão

Após consumir o serviço, o MfaProvider irá apresentar uma mensagem informando o sucesso ou não na remoção do segundo fator para o usuário informado.

