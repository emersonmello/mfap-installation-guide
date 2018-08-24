# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from shutil import copyfile
from lxml import etree

idp_root_dir='./'
URI = 'idp2ampto.cafeexpresso.rnp.br'
ATTRIBUTE_FILTER_FILE = './attribute-filter.xml'
MFA_FILTER_POLICY_ID = 'releaseToMfaProvider'

def main():
    print("Fazendo backup de "  + ATTRIBUTE_FILTER_FILE)
    try:
        copyfile(ATTRIBUTE_FILTER_FILE, ATTRIBUTE_FILTER_FILE + ".orig")
    except FileNotFoundError as fnf:
        print("O arquivo attribute-filter.xml não foi encontrado")
    
    ET.register_namespace('','urn:mace:shibboleth:2.0:afp')
    # namespace for attribute filter policy.
    # See https://wiki.shibboleth.net/confluence/display/IDP30/AttributeFilterPolicyConfiguration
    ns = {"afp": "urn:mace:shibboleth:2.0:afp"} 
    tree = ET.parse('attribute-filter.xml')
    root = tree.getroot()
    for child in root.findall('afp:AttributeFilterPolicy', ns):
        if child.attrib['id'] == MFA_FILTER_POLICY_ID:
            root.remove(child)

    root.tail = "\n    "
    filter_policy = ET.SubElement(root,'AttributeFilterPolicy', {'id': 'releaseToMfaProvider'})
    filter_policy.tail = "\n  "
    filter_policy_sub = ET.SubElement(filter_policy, 'PolicyRequirementRule', {'xsi:type':"Requester", "value": "Alterar"})

    with open('attribute_rules.txt', 'r') as fa:
        for line in fa:
            attribute=line.split(',')
            create_elem_rule(attribute, filter_policy)
    indent(root)
    tree.write('attribute-filter.xml')


def indent(elem, level=0):
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

def create_elem_rule(attribute, root):
    elem = ET.SubElement(root, 'AttributeRule', {'attributeID':attribute[0].strip()})
    elem.tail = "\n  "
    elem_rule = ET.SubElement(elem,'PermitValueRule', {'xsi:type': attribute[1].strip()})
    elem_rule.tail = "\n    "


if __name__ == '__main__':
   main()
