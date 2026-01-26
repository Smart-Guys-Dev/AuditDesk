"""
Comparação direta: mesmo elemento, mesmo XPath, resultado diferente?
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree
from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES

# Setup
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)
engine.load_all_rules()

reader = XMLReader()

# Encontrar item taxa via RuleEngine (como ele faz)
procs_via_engine = engine.xml_reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"procs via engine.xml_reader: {len(procs_via_engine)}")

# Encontrar item taxa via XMLReader direto
procs_via_reader = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"procs via reader: {len(procs_via_reader)}")

# Pegar o item 12 (taxa)
for i, proc in enumerate(procs_via_engine):
    cd_check = engine.xml_reader.find_elements_by_xpath(proc, ".//ptu:cd_Servico")
    if cd_check and cd_check[0].text == "60033681":
        print(f"\n=== ITEM TAXA (índice {i}) ===")
        print(f"Elemento ID: {id(proc)}")
        print(f"Tag: {proc.tag}")
        
        # Testar XPath exato
        xpath = "./ptu:procedimentos/ptu:cd_Servico"
        result1 = engine.xml_reader.find_elements_by_xpath(proc, xpath)
        print(f"\nvia engine.xml_reader.find_elements_by_xpath:")
        print(f"  XPath: {xpath}")
        print(f"  Result: {result1}")
        
        # Testar via etree direto
        result2 = proc.xpath(xpath, namespaces=NAMESPACES)
        print(f"\nvia proc.xpath direto:")
        print(f"  XPath: {xpath}")
        print(f"  Result: {result2}")
        
        # Verificar se NAMESPACES são os mesmos
        from src.infrastructure.parsers.xml_reader import NAMESPACES as NS_FROM_READER
        print(f"\nNAMESPACES from reader: {NS_FROM_READER}")
        
        break
