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

def config_attribute_filters(idp_base_dir,idphost):
    filter_file = idp_base_dir + '/conf/attribute-filter.xml'
    utils.backup_original_file(filter_file)
    try:
        # namespace for attribute filter policy.
        # See https://wiki.shibboleth.net/confluence/display/IDP30/AttributeFilterPolicyConfiguration
        ns= dict([node for _, node in ET.iterparse(filter_file, events=['start-ns'])])
        for prefix, uri in ns.items():
            ET.register_namespace(prefix,uri)
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        tree = ET.parse(filter_file, parser)
        root = tree.getroot()
        for child in root.findall('{urn:mace:shibboleth:2.0:afp}AttributeFilterPolicy'):
            if child.attrib['id'] == 'config_metadata_provider':
                # caso já exista um AttributeFilterPolicy para o MfaProvider
                # (este script já foi executado, por exemplo), remove.
                root.remove(child)

        filter_policy = ET.SubElement(root,'AttributeFilterPolicy',
                {'id': 'releaseToMfaProvider'})
        filter_policy_sub = ET.SubElement(filter_policy, 'PolicyRequirementRule',
                {'xsi:type':"Requester", "value": idphost})

        # cria uma regra de liberação de atributo para cada atributo definido em
        # attribute_rules.txt. Cada atributo deve estar em uma linha, na forma atributo,regra: 
        # eduPersonPrincipalName,ANY
        with open('attribute_rules.txt', 'r') as fa:
            for line in fa:
                attribute=line.split(',')
                create_elem_rule(attribute, filter_policy)
        utils.indent(root)
        tree.write(filter_file)
    except IOError as e:
        #TODO: Reverter para arquivo original
        print("Houve um erro ao escrever o arquivo conf/attribute-filter.xml")
        print("Erro: ", e)
        return False

    return True

def create_elem_rule(attribute, root):
    elem = ET.SubElement(root, 'AttributeRule', {'attributeID':attribute[0].strip()})
    elem.tail = "\n  "
    elem_rule = ET.SubElement(elem,'PermitValueRule', {'xsi:type': attribute[1].strip()})
    elem_rule.tail = "\n    "

def config_metadata_provider(idp_base_dir):
    metadata_file  = idp_base_dir + '/conf/metadata-providers.xml'
    sp_file = idp_base_dir + '/metadata/mfaprovider-metadata.xml'
    utils.backup_original_file(metadata_file)
    try:
        # namespace for Metadata Provider.
        # https://wiki.shibboleth.net/confluence/display/IDP30/MetadataConfiguration
        ns= dict([node for _, node in ET.iterparse(metadata_file, events=['start-ns'])])
        for prefix, uri in ns.items():
            ET.register_namespace(prefix,uri)
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        tree = ET.parse(metadata_file, parser)
        root = tree.getroot()
        for child in root.findall('{urn:mace:shibboleth:2.0:metadata}MetadataProvider'):
            if child.attrib['id'] == 'MfaProviderMetadata':
                # caso já exista um AttributeFilterPolicy para o MfaProvider 
                # (este script já foi executado, por exemplo), remove.
                root.remove(child)
        metadata_details = {'id': 'MfaProviderMetadata', 'xsi:type': 'FilesystemMetadataProvider',
                'metadataFile': sp_file}
        ET.SubElement(root,'MetadataProvider', metadata_details)
        utils.indent(root)
        tree.write(metadata_file)
    except IOError as e:
        #TODO: Reverter para arquivo original
        print("Houve um erro ao escrever o arquivo conf/metadata-providers.xml")
        print("Erro: ", e)
        return False
    return True

def config_relying_party(idp_base_dir):
    relying_file = idp_base_dir + '/conf/relying-party.xml'
    utils.backup_original_file(relying_file)
    try:
        ns= dict([node for _, node in ET.iterparse(relying_file, events=['start-ns'])])
        for prefix, uri in ns.items():
            ET.register_namespace(prefix,uri)
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        tree = ET.parse(relying_file, parser)
        root = tree.getroot()

        for child in root.findall('{http://www.springframework.org/schema/beans}bean'):
            if child.attrib['id'] == 'MfaPrincipal' or child.attrib['id'] == 'PasswordPrincipal':
                root.remove(child)

        for child in tree.iterfind('{http://www.springframework.org/schema/beans}bean[@id="shibboleth.DefaultRelyingParty"]/{http://www.springframework.org/schema/beans}property/{http://www.springframework.org/schema/beans}list'):
            for elem in child:
                if elem.tag == '{http://www.springframework.org/schema/beans}bean':
                    if 'parent' in elem.attrib:
                        if (elem.attrib['parent'] == "SAML2.SSO"  
                            and elem.attrib['{http://www.springframework.org/schema/p}postAuthenticationFlows'] == 'attribute-release'):
                            child.remove(elem)

            bean_parent = ET.SubElement(child,
                    '{http://www.springframework.org/schema/beans}bean',
                    {'parent': 'SAML2.SSO',
                        'p:postAuthenticationFlows': 'attribute-release'})
            property_bean = ET.SubElement(bean_parent,
                    '{http://www.springframework.org/schema/beans}property',
                    {'name': 'defaultAuthenticationMethods'})
            list_bean = ET.SubElement(property_bean,
                    '{http://www.springframework.org/schema/beans}list')
            ref1 = ET.SubElement(list_bean, 'ref', {'bean': 'MfaPrincipal'})
            ref2 = ET.SubElement(list_bean, 'ref', {'bean': 'PasswordPrincipal'})
        
        bean_elem = ET.Element('{http://www.springframework.org/schema/beans}bean',
                {'id': 'MfaPrincipal',
                    'parent': 'shibboleth.SAML2AuthnContextClassRef',
                    '{http://www.springframework.org/schema/c}classRef':
                    'http://id.incommon.org/assurance/mfa'})

        bean_password = ET.Element('{http://www.springframework.org/schema/beans}bean',
            {'id': 'PasswordPrincipal',
            'parent': 'shibboleth.SAML2AuthnContextClassRef',
            '{http://www.springframework.org/schema/c}classRef':
            'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'})

        # insere logo depois do elemento root,no início do arquivo
        root.insert(1, bean_elem)
        root.insert(2, bean_password)

        utils.indent(root)
        tree.write(relying_file)
    except Exception as e:
        #TODO: Reverter para arquivo original
        print("Houve algum erro ao escrever no arquivo: " , relying_file)
        print("Erro: ", e)
        return False
    return True

def config_general_authn(idp_base_dir):
    authn_file = idp_base_dir + '/conf/authn/general-authn.xml'
    utils.backup_original_file(authn_file)
    try:
        ns= dict([node for _, node in ET.iterparse(authn_file, events=['start-ns'])])
        for prefix, uri in ns.items():
            ET.register_namespace(prefix,uri)
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        tree = ET.parse(authn_file, parser)
        root = tree.getroot()

        # configura fluxo da autenticação com multifator

        elem_list = root.find('util:list[@id="shibboleth.AvailableAuthenticationFlows"]', ns)
        ## remove  se já existe
        if elem_list is not None:
            elem_bean_flow = root.find('util:list/{http://www.springframework.org/schema/beans}bean[@id="authn/mfa-provider-flow"]', ns)
            if elem_bean_flow is not None:
                elem_list.remove(elem_bean_flow)

            ## cria bean
            bean_authn_mfa = ET.SubElement(elem_list,
                '{http://www.springframework.org/schema/beans}bean',
                {'id':'authn/mfa-provider-flow',
                'parent':'shibboleth.AuthenticationFlow',
                '{http://www.springframework.org/schema/p}passiveAuthenticationSupported' : 'true',
                '{http://www.springframework.org/schema/p}forcedAuthenticationSupported' : 'true',
                '{http://www.springframework.org/schema/p}nonBrowserSupported' :  'true'
                })
            bean_authn_mfa_property = ET.SubElement( bean_authn_mfa,
            '{http://www.springframework.org/schema/beans}property',
            {'name' : 'supportedPrincipals'})

            bean_authn_mfa_property_list = ET.SubElement( bean_authn_mfa_property,
            '{http://www.springframework.org/schema/beans}list')

            bean_mfa1 = ET.SubElement(  bean_authn_mfa_property_list,
            '{http://www.springframework.org/schema/beans}bean',
            {'parent' : 'shibboleth.SAML2AuthnContextClassRef',
            '{http://www.springframework.org/schema/c}classRef':
                'http://id.incommon.org/assurance/mfa'})

            bean_mfa2= ET.SubElement(bean_authn_mfa_property_list,
            '{http://www.springframework.org/schema/beans}bean',
            {'parent' : 'shibboleth.SAML1AuthenticationMethod',
            '{http://www.springframework.org/schema/c}method':
                'http://id.incommon.org/assurance/mfa'})

            elem_bean_flow_failure = root.find('util:list/{http://www.springframework.org/schema/beans}bean[@id="authn/mfa-failure-request-flow"]', ns)
            if elem_bean_flow_failure is not None:
                elem_list.remove(elem_bean_flow_failure)

            elem_bean_flow_failure = ET.SubElement(elem_list,
            '{http://www.springframework.org/schema/beans}bean',
            {'id':'authn/mfa-failure-request-flow',
            'parent':'shibboleth.AuthenticationFlow',
            '{http://www.springframework.org/schema/p}passiveAuthenticationSupported':'true',
            '{http://www.springframework.org/schema/p}forcedAuthenticationSupported':'true',
            })

            elem_bean_fido = root.find('util:list/{http://www.springframework.org/schema/beans}bean[@id="authn/fido-ecp-flow"]', ns)
            if elem_bean_fido is not None:
                elem_list.remove(elem_bean_fido)

            elem_bean_fido = ET.SubElement(elem_list,'bean', {
                'id' : 'authn/fido-ecp-flow',
                'parent' : 'shibboleth.AuthenticationFlow',
                '{http://www.springframework.org/schema/p}passiveAuthenticationSupported':'true',
                '{http://www.springframework.org/schema/p}forcedAuthenticationSupported':'true',
                '{http://www.springframework.org/schema/p}nonBrowserSupported':'true'
            })

        # cria <bean parent="shibboleth.SAML2AuthnContextClassRef"
        #                        c:classRef="http://id.incommon.org/assurance/mfa" />
        # no bean id="authn/MFA", dentro de property->list
        # Remove se já existir, antes de criar

        elem_list = root.find('util:list[@id="shibboleth.AvailableAuthenticationFlows"]/{http://www.springframework.org/schema/beans}bean[@id="authn/MFA"]/{http://www.springframework.org/schema/beans}property[@name="supportedPrincipals"]/{http://www.springframework.org/schema/beans}list', ns)

        elem_mfa = root.find('util:list[@id="shibboleth.AvailableAuthenticationFlows"]/{http://www.springframework.org/schema/beans}bean[@id="authn/MFA"]/{http://www.springframework.org/schema/beans}property[@name="supportedPrincipals"]/{http://www.springframework.org/schema/beans}list/{http://www.springframework.org/schema/beans}bean[@c:classRef="http://id.incommon.org/assurance/mfa"]', ns)

        if elem_mfa is not None:
            elem_list.remove(elem_mfa)

        bean_elem =  ET.SubElement(elem_list, '{http://www.springframework.org/schema/beans}bean',
            {'parent': 'shibboleth.SAML2AuthnContextClassRef',
            '{http://www.springframework.org/schema/c}classRef':
            'http://id.incommon.org/assurance/mfa'})

        # configura ordem dos fatores
        elem =  root.find('util:map/[@id="shibboleth.AuthenticationPrincipalWeightMap"]', ns)
        if elem is not None:
            root.remove(elem)

        authn_principal = ET.SubElement(root,'util:map',
                {'id': 'shibboleth.AuthenticationPrincipalWeightMap'})

        entry1 = ET.SubElement(authn_principal, 'entry')
        key1 = ET.SubElement(entry1, 'key')
        value1 = ET.SubElement(entry1, 'value')
        value1.text = "1"
        bean1 = ET.SubElement(key1,'{http://www.springframework.org/schema/beans}bean',
            {'parent': 'shibboleth.SAML2AuthnContextClassRef',
            '{http://www.springframework.org/schema/c}classRef':
            'http://id.incommon.org/assurance/mfa'})

        entry2 = ET.SubElement(authn_principal, 'entry')
        key2 = ET.SubElement(entry2, 'key')
        bean2 = ET.SubElement(key2,'{http://www.springframework.org/schema/beans}bean',
            {'parent': 'shibboleth.SAML2AuthnContextClassRef',
            '{http://www.springframework.org/schema/c}classRef':
            'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'})
        value2 = ET.SubElement(entry2, 'value')
        value2.text = "2"
        utils.indent(root)
        tree.write(authn_file)
    except Exception as e:
        #TODO: Reverter para arquivo original
        print("Houve algum erro ao escrever no arquivo: " , authn_file)
        print("Erro: ", e)
        return False

    return True

def main():
    '''
        O objetivo desde método é facilitar o debug deste script. Na instalação
        do MfaProvider ele não deve ser executado separadamente, pois ele é utilizado
        via importação em install.py
    '''
    config_attribute_filters(config.get('idp','dir_base_idp_shibboleth'))
    config_metadata_provider(config.get('idp','dir_base_idp_shibboleth'))
    config_relying_party(config.get('idp','dir_base_idp_shibboleth'))
    config_general_authn(config.get('idp', 'dir_base_idp_shibboleth'))


if __name__ == '__main__':
    main()
