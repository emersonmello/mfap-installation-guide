# -*- coding: utf-8 -*-
'''
Configura arquivos xml necessários para a implantação
e estabelecimento de confiança entre o SP MfaProvider
e o IdP customizado para multifator.
Autora: shirlei@gmail.com - 2018
Versão: 1.0

'''
import xml.etree.ElementTree as ET

import utils
from utils import CommentedTreeBuilder

import ConfigParser
config = ConfigParser.ConfigParser()

config.read('config.ini')

ATTRIBUTE_FILTER_FILE = '/conf/attribute-filter.xml'
MFA_FILTER_POLICY_ID = 'releaseToMfaProvider'
METADATA_PROVIDER_FILE = '/conf/metadata-providers.xml'
SP_METADATA_FILE = '/metadata/mfaprovider-metadata.xml'
RELYING_PARTY_FILE = '/conf/relying-party.xml'


def config_attribute_filters(idp_base_dir):
    filter_file = idp_base_dir + 'conf/attribute-filter.xml'
    utils.backup_original_file(filter_file)
    ET.register_namespace('','urn:mace:shibboleth:2.0:afp')
    # namespace for attribute filter policy.
    # See https://wiki.shibboleth.net/confluence/display/IDP30/AttributeFilterPolicyConfiguration
    ns = {"afp": "urn:mace:shibboleth:2.0:afp"} 
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(filter_file, parser)
    root = tree.getroot()
    for child in root.findall('afp:AttributeFilterPolicy', ns):
        if child.attrib['id'] == 'config_metadata_provider':
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
    utils.indent(root)
    tree.write(filter_file)

    return True

def create_elem_rule(attribute, root):
    elem = ET.SubElement(root, 'AttributeRule', {'attributeID':attribute[0].strip()})
    elem.tail = "\n  "
    elem_rule = ET.SubElement(elem,'PermitValueRule', {'xsi:type': attribute[1].strip()})
    elem_rule.tail = "\n    "

def config_metadata_provider(idp_base_dir):
    metadata_file  = idp_base_dir + '/conf/metadata-providers.xml'
    sp_file = idp_base_dir + '/metadata/mfaprovider-metadata.xml'
    print ("sp file: "+ sp_file)
    print("Metadata_file : " + metadata_file)
    utils.backup_original_file(metadata_file)
    
    # namespace for Metadata Provider.
    # https://wiki.shibboleth.net/confluence/display/IDP30/MetadataConfiguration
    ET.register_namespace('','urn:mace:shibboleth:2.0:metadata')
    ns = {"mdp": "urn:mace:shibboleth:2.0:metadata", "xsitype": "http://www.w3.org/2001/XMLSchema-instance"} 
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(metadata_file, parser)
    root = tree.getroot()
    for child in root.findall('./mdp:MetadataProvider', ns):
        if child.attrib['id'] == 'MfaProviderMetadata':
            # caso já exista um AttributeFilterPolicy para o MfaProvider 
            # (este script já foi executado, por exemplo), remove.
            root.remove(child)
    metadata_details = {'id': 'MfaProviderMetadata', 'xsi:type': 'FilesystemMetadataProvider',
            'metadataFile': sp_file}
    ET.SubElement(root,'MetadataProvider', metadata_details)
    utils.indent(root)
    tree.write(metadata_file)

    return True

def config_relying_party(idp_base_dir):
    relying_file = idp_base_dir + RELYING_PARTY_FILE
    utils.backup_original_file(relying_file)
    namespaces = {'': 'http://www.springframework.org/schema/beans',
            'context': 'http://www.springframework.org/schema/context',
            'util': 'http://www.springframework.org/schema/util',
            'p': 'http://www.springframework.org/schema/p',
            'c': 'http://www.springframework.org/schema/c',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix,uri)
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(relying_file, parser)
    root = tree.getroot()
    elem = root.find('.//{http://id.incommon.org/assurance/mfa}bean')
    print(elem)
    for child in root.findall('{http://www.springframework.org/schema/beans}bean'):
        if child.attrib['id'] == 'MfaPrincipal' or child.attrib['id'] == 'PasswordPrincipal':
            root.remove(child)
    
    for child in root.findall('./{http://www.springframework.org/schema/beans}bean/[@parent="SAML2.SSO"]'):
        print(child.attrib)
        print(child.tag)
        if 'parent' in child.attrib:
            if child.attrib['parent'] == "SAML2.SSO":
                print("SAML2.SSO")
                print (child.attrib)

    ET.SubElement(root, 'bean',  {'id': 'MfaPrincipal', 'parent': 'shibboleth.SAML2AuthnContextClassRef',
            'c:classRef': 'http://id.incommon.org/assurance/mfa'})
    ET.Element('bean',  {'id': 'MfaPrincipal', 'parent': 'shibboleth.SAML2AuthnContextClassRef',
            'c:classRef': 'http://id.incommon.org/assurance/mfa'})
  
    bean_password_details = {'id': 'PasswordPrincipal', 'parent': 'shibboleth.SAML2AuthnContextClassRef', 
            'c:classRef':'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'} 
    ET.SubElement(root,'bean', bean_password_details)
    utils.indent(root)
    tree.write(relying_file)

    return True

def main():
    #config_attribute_filters(config.get('idp','dir_base_idp_shibboleth'))
    #config_metadata_provider(config.get('idp','dir_base_idp_shibboleth'))
    config_relying_party(config.get('idp','dir_base_idp_shibboleth'))


if __name__ == '__main__':
    main()
