"""
Script minimalista para testar a regra de taxa de observação
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES

print("=" * 60)
print("TESTE MINIMALISTA")
print("=" * 60)

# Carregar XML
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

# Namespace do XML
print(f"Namespace do XML: {root.nsmap}")
print(f"NAMESPACES do XMLReader: {NAMESPACES}")

# XMLReader
reader = XMLReader()

# Buscar procedimentosExecutados
procs = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"\nTotal procedimentosExecutados: {len(procs)}")

# Para cada um, testar o XPath da regra
for i, proc in enumerate(procs):
    # XPath da regra: ./ptu:procedimentos/ptu:cd_Servico
    cd_nodes = reader.find_elements_by_xpath(proc, "./ptu:procedimentos/ptu:cd_Servico")
    if cd_nodes:
        cd = cd_nodes[0].text
        if cd in ["60033681", "60033665"]:
            print(f"\n*** ENCONTRADO TAXA OBSERVAÇÃO ***")
            print(f"    Índice: {i+1}")
            print(f"    cd_Servico: {cd}")
            
            # Verificar horários
            hr_ini = reader.find_elements_by_xpath(proc, "./ptu:hr_Inicial")
            hr_fim = reader.find_elements_by_xpath(proc, "./ptu:hr_Final")
            if hr_ini and hr_fim:
                print(f"    hr_Inicial: {hr_ini[0].text}")
                print(f"    hr_Final: {hr_fim[0].text}")
                print(f"    Iguais: {hr_ini[0].text == hr_fim[0].text}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
