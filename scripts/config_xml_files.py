# -*- coding: utf-8 -*-
'''
Configura arquivos xml necessários para a implantação
e estabelecimento de confiança entre o SP MfaProvider
e o IdP customizado para multifator.
Autora: shirlei@gmail.com - 2018
Versão: 1.0

'''
import xml.etree.ElementTree as ET
from shutil import copyfile
from lxml import etree

import utils
required_variables = ['dir_base_idp_shibboleth', 'uri']

idp_root_dir='./'
URI = 'idp2ampto.cafeexpresso.rnp.br'
ATTRIBUTE_FILTER_FILE = '/conf/attribute-filter.xml'
MFA_FILTER_POLICY_ID = 'releaseToMfaProvider'
METADATA_PROVIDER_FILE = '/conf/metadata-providers.xml'
SP_METADATA_FILE = '/conf/spmfaprovider-metadata.xml'

def config_attribute_filters(idp_base_dir):
    filter_file = idp_base_dir + ATTRIBUTE_FILTER_FILE
    print("Fazendo backup de "  + filter_file)
    try:
        copyfile(filter_file, filter_file + ".orig")
    except FileNotFoundError as fnf:
        print("O arquivo %s não foi encontrado", filter_file)
    
    ET.register_namespace('','urn:mace:shibboleth:2.0:afp')
    # namespace for attribute filter policy.
    # See https://wiki.shibboleth.net/confluence/display/IDP30/AttributeFilterPolicyConfiguration
    ns = {"afp": "urn:mace:shibboleth:2.0:afp"} 
    tree = ET.parse(filter_file)
    root = tree.getroot()
    for child in root.findall('afp:AttributeFilterPolicy', ns):
        if child.attrib['id'] == MFA_FILTER_POLICY_ID:
            # caso já exista um AttributeFilterPolicy para o MfaProvider 
            # (este script já foi executado, por exemplo), remove.
            root.remove(child)

    filter_policy = ET.SubElement(root,'AttributeFilterPolicy', {'id': 'releaseToMfaProvider'})
    filter_policy.tail = "\n  "
    filter_policy_sub = ET.SubElement(filter_policy, 'PolicyRequirementRule', {'xsi:type':"Requester", "value": "Alterar"})

    with open('attribute_rules.txt', 'r') as fa:
        for line in fa:
            attribute=line.split(',')
            create_elem_rule(attribute, filter_policy)
    indent(root)
    tree.write(filter_file)

def create_elem_rule(attribute, root):
    elem = ET.SubElement(root, 'AttributeRule', {'attributeID':attribute[0].strip()})
    elem.tail = "\n  "
    elem_rule = ET.SubElement(elem,'PermitValueRule', {'xsi:type': attribute[1].strip()})
    elem_rule.tail = "\n    "

def config_metadata_provider(idp_base_dir):
    metadata_file = idp_base_dir + METADATA_PROVIDER_FILE
    sp_file = idp_base_dir + SP_METADATA_FILE
    print("Fazendo backup de "  + metadata_file)
    try:
        copyfile(metadata_file, metadata_file + ".orig")
    except FileNotFoundError as fnf:
        print("O arquivo %s não foi encontrado", metadata_file)
    # namespace for Metadata Provider.
    # https://wiki.shibboleth.net/confluence/display/IDP30/MetadataConfiguration
    ET.register_namespace('','urn:mace:shibboleth:2.0:metadata')
    ns = {"mdp": "urn:mace:shibboleth:2.0:metadata", "xsitype": "http://www.w3.org/2001/XMLSchema-instance"} 
    tree = ET.parse(metadata_file)
    root = tree.getroot()
    for child in root.findall('./mdp:MetadataProvider', ns):
        if child.attrib['id'] == 'MfaProviderMetadata':
            # caso já exista um AttributeFilterPolicy para o MfaProvider 
            # (este script já foi executado, por exemplo), remove.
            root.remove(child)
    metadata_details = {'id': 'MfaProviderMetadata', 'xsi:type': 'FilesystemMetadataProvider',
            'metadataFile': sp_file}
    ET.SubElement(root,'MetadataProvider', metadata_details)
    indent(root)
    tree.write(metadata_file)

def main():
    # lê variáveis de configuração
    config_variables = utils.read_config_variables()
    if config_variables and len(config_variables) == 0:
        msg = """
        As variaveis de configuraçao necessárias nao foram adquiridas
        Por favor, verifique o arquivo variaveis_configuracao.txt
        """
        print(msg)
    if utils.check_missing_variables(config_variables, required_variables):
        print("Corrija as variáveis faltantes e reinicie a execução")
        exit()
    config_attribute_filters(config_variables['dir_base_idp_shibboleth'])
    config_metadata_provider(config_variables['dir_base_idp_shibboleth'])

def indent(elem, level=0):
    '''
    Identa a árvore xml resultante, antes de escrever novamente
    o arquivo.
    Obtido de:
        - https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python e
        - http://effbot.org/zone/element-lib.htm#prettyprint
    '''
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


if __name__ == '__main__':
   main()
