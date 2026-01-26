"""
Teste forçando carregamento do JSON em vez do banco de dados
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree
from src.business.rules.rule_engine import RuleEngine

# Setup
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)

# Forçar carregamento do JSON em vez do banco
print("Carregando regras do JSON (use_database=False)...")
engine.load_all_rules(use_database=False)

print(f"Total regras: {len(engine.loaded_rules)}")

# Verificar regra de taxa
taxa_rules = [r for r in engine.loaded_rules if "TAXA_OBSERVACAO" in r.get("id", "")]
print(f"Regras taxa: {len(taxa_rules)}")

if taxa_rules:
    rule = taxa_rules[0]
    print(f"\nRegra: {rule.get('id')}")
    print(f"Condições: {rule.get('condicoes')}")

# Aplicar regras
print("\n" + "=" * 40)
print("Aplicando regras...")
engine.apply_rules_to_xml(tree, file_name="test.xml")

# Verificar resultado
ns = {"ptu": "http://www.unimed.com.br/ptu"}
taxa_elements = root.xpath(".//ptu:procedimentosExecutados[./ptu:procedimentos/ptu:cd_Servico='60033681']", namespaces=ns)

if taxa_elements:
    hr_ini = taxa_elements[0].xpath("./ptu:hr_Inicial/text()", namespaces=ns)
    hr_fim = taxa_elements[0].xpath("./ptu:hr_Final/text()", namespaces=ns)
    print(f"\nRESULTADO FINAL:")
    print(f"hr_Inicial: {hr_ini}")
    print(f"hr_Final: {hr_fim}")
    
    if hr_ini and hr_fim and hr_ini[0] != "00:00:01":
        print("\n*** SUCESSO! Horários corrigidos! ***")
    else:
        print("\n*** FALHA! Horários não alterados ***")
