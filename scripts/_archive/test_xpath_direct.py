"""
Teste DIRETO do XPath via XMLReader
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES

print(f"NAMESPACES: {NAMESPACES}")

xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

print(f"Root nsmap: {root.nsmap}")

reader = XMLReader()

# Encontrar todos procedimentosExecutados
procs = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"\nTotal procs: {len(procs)}")

# Para o item 12 (taxa de observação)
for i, proc in enumerate(procs):
    # Testar o XPath exato da regra
    xpath = "./ptu:procedimentos/ptu:cd_Servico"
    nodes = reader.find_elements_by_xpath(proc, xpath)
    
    if nodes:
        cd = nodes[0].text
        if cd == "60033681":
            print(f"\n*** ENCONTRADO ***")
            print(f"Indice: {i+1}")
            print(f"XPath: {xpath}")
            print(f"cd_Servico: {cd}")
            print(f"Node encontrado: {nodes}")
            
            # Testar também via lxml direto
            print(f"\nTeste lxml direto:")
            direct = proc.xpath("./ptu:procedimentos/ptu:cd_Servico", namespaces=NAMESPACES)
            print(f"Resultado: {direct}")
            if direct:
                print(f"Texto: {direct[0].text}")
