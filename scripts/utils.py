# -*- coding: utf-8 -*-

def read_config_variables():
    config_variables = {}
    with open('variaveis_configuracao.txt', 'r') as vc:
        try:
            for line in vc:
                config_line = line.strip().split('=')
                if len(config_line) == 2:
                    config_variables[config_line[0].strip()] = config_line[1].strip()
        except ValueError:
            msg = """
            O arquivo de configuração deve ter o formato:
            var1=valor1
            var2=valor2
            Sendo uma variável por linha, sem linhas em branco.
            Por favor, ajuste o arquivo e repita a operação.
            """
    return config_variables

def check_missing_variables(config_variables, required_variables):
    missing_variable = False
    for required_variable in required_variables:
        if required_variable not in config_variables.keys():
            msg = """
            A variavel %s está faltando.
            Edite o arquivo variaveis_configuracao.txt e insira-a na forma
            %s=valor
            """ % (required_variable, required_variable)
            print(msg)
            missing_variable = True
    return missing_variable
