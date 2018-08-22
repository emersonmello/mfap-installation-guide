# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from shutil import copyfile

idp_root_dir='./'

def main():
    idp_dir = input("Informe o diretorio de instalação do idp. Pressione enter se o endereço " + idp_root_dir + " está correto ")
    if idp_dir is None:
        idp_dir = idp_root_dir
    print("Fazendo backup de "  + idp_root_dir + "/conf/attribute-filter.xml")
    try:
        copyfile(idp_root_dir + "/conf/attribute-filter.xml", idp_root_dir + "/conf/attribute-filter.xml.orig")
    except FileNotFoundError as fnf:
        print("O arquivo attribute-filter.xml não foi encontrado")
    
    print ("Informe o endereço do sp MfaProvider (conforme informado em sp.properties no MfaProvider)")
    mfaprovider_uri = input("Por exemplo dev.chimarrao.rnp.br/conta: ")
    
    continuar = 'sim'
    if mfaprovider_uri is None or mfaprovider_uri == "":
        print("Você náo informou corretamente o endereço do sp. Deseja continuar?")
        continuar = input("Sim/Nao:")

    if continuar.lower() == 'nao':
        print("Saindo da configuração...")
        exit()

    ET.register_namespace('','urn:mace:shibboleth:2.0:afp')
    tree = ET.parse('attribute-filter.xml')
    root = tree.getroot()
    print (root.attrib)
    #mfaProvider = root.find("./AttributeFilterPolicy/[@id='releaseToMfaProvider'")
    #if mfaProvider is not None:
    #    print(mfaProvider)
    print (root.find('AttributeFilterPolicy'))
    filter_policy = ET.SubElement(root,'AttributeFilterPolicy', {'id': 'releaseToMfaProvider'})
    filter_policy.tail = "\n  "
    filter_policy_sub = ET.SubElement(filter_policy, 'PolicyRequirementRule', {'xsi:type':"Requester", "value": "Alterar"})
    filter_policy_sub.tail = "\n    "

    with open('attribute_rules.txt', 'r') as fa:
        for line in fa:
            attribute=line.split(',')
            create_elem_rule(attribute, filter_policy)
    tree.write('attribute-filter.xml')

def create_elem_rule(attribute, root):
    elem = ET.SubElement(root, 'AttributeRule', {'attributeID':attribute[0].strip()})
    elem.tail = "\n  "
    elem_rule = ET.SubElement(elem,'PermitValueRule', {'xsi:type': attribute[1].strip()})
    elem_rule.tail = "\n    "


if __name__ == '__main__':
   main()
