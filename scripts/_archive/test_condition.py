"""
Script focado para testar apenas a avaliação de condição
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree
from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES

# Criar engine com caminho absoluto
config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)
engine.load_all_rules()

# Verificar regra
taxa_rules = [r for r in engine.loaded_rules if "TAXA_OBSERVACAO" in r.get("id", "")]
if not taxa_rules:
    print("ERRO: Regra nao encontrada!")
    sys.exit(1)

rule = taxa_rules[0]
print(f"Regra: {rule.get('id')}")

# Carregar XML
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

# Encontrar elemento taxa
reader = XMLReader()
procs = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")

for i, proc in enumerate(procs):
    cd_nodes = reader.find_elements_by_xpath(proc, "./ptu:procedimentos/ptu:cd_Servico")
    if cd_nodes and cd_nodes[0].text == "60033681":
        print(f"\nItem {i+1}: cd_Servico = 60033681")
        
        # Testar cada sub-condição individualmente
        conditions = rule.get("condicoes", {})
        multi = conditions.get("condicao_multipla", {})
        subs = multi.get("sub_condicoes", [])
        
        print(f"Sub-condicoes: {len(subs)}")
        
        for j, sub in enumerate(subs):
            result = engine._evaluate_condition(proc, sub)
            print(f"  Sub {j+1}: {list(sub.keys())} -> {result}")
        
        # Testar condição completa
        full_result = engine._evaluate_condition(proc, conditions)
        print(f"\nResultado completo: {full_result}")
        
        break
