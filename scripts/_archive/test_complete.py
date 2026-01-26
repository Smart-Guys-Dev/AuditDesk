"""
Script completo para testar a regra via RuleEngine
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import logging
logging.basicConfig(level=logging.DEBUG)

from lxml import etree
from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

print("=" * 60)
print("TESTE COMPLETO VIA RULEENGINE")
print("=" * 60)

# Criar engine com caminho absoluto
config_dir = os.path.join(project_root, "src", "config")
print(f"Config dir: {config_dir}")

engine = RuleEngine(config_dir)
print(f"Engine config_dir: {engine.config_dir}")
print(f"Existe: {os.path.exists(engine.config_dir)}")

# Carregar regras
print("\nCarregando regras...")
engine.load_all_rules()
print(f"Total regras: {len(engine.loaded_rules)}")

# Verificar regra de taxa
taxa_rules = [r for r in engine.loaded_rules if "TAXA_OBSERVACAO" in r.get("id", "")]
print(f"Regras taxa observação: {len(taxa_rules)}")

if not taxa_rules:
    print("ERRO: Regra TAXA_OBSERVACAO não foi carregada!")
    print("\nRegras disponíveis:")
    for r in engine.loaded_rules[:10]:
        print(f"  - {r.get('id')}")
else:
    rule = taxa_rules[0]
    print(f"\nRegra encontrada: {rule.get('id')}")
    print(f"Ativo: {rule.get('ativo')}")

# Carregar XML
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
print(f"\nCarregando XML: {xml_path}")
tree = etree.parse(xml_path)
root = tree.getroot()

# Encontrar elemento alvo manualmente
ns = {"ptu": "http://www.unimed.com.br/ptu"}
taxa_elements = root.xpath(".//ptu:procedimentosExecutados[./ptu:procedimentos/ptu:cd_Servico='60033681']", namespaces=ns)
print(f"\nElementos taxa 60033681 encontrados via xpath direto: {len(taxa_elements)}")

if taxa_elements:
    elem = taxa_elements[0]
    hr_ini = elem.xpath("./ptu:hr_Inicial/text()", namespaces=ns)
    hr_fim = elem.xpath("./ptu:hr_Final/text()", namespaces=ns)
    print(f"hr_Inicial: {hr_ini}")
    print(f"hr_Final: {hr_fim}")
    
    # Testar _evaluate_condition manualmente
    if taxa_rules:
        rule = taxa_rules[0]
        conditions = rule.get("condicoes", {})
        print(f"\nTestando _evaluate_condition...")
        print(f"Condições: {conditions}")
        result = engine._evaluate_condition(elem, conditions)
        print(f"Resultado: {result}")

# Aplicar regras
print("\n" + "=" * 40)
print("Aplicando regras via apply_rules_to_xml...")
print("=" * 40)

engine.apply_rules_to_xml(tree, file_name="test.xml")

# Verificar resultado
if taxa_elements:
    hr_ini_new = taxa_elements[0].xpath("./ptu:hr_Inicial/text()", namespaces=ns)
    hr_fim_new = taxa_elements[0].xpath("./ptu:hr_Final/text()", namespaces=ns)
    print(f"\nAPÓS APLICAÇÃO:")
    print(f"hr_Inicial: {hr_ini_new}")
    print(f"hr_Final: {hr_fim_new}")
    
    if hr_ini_new != hr_ini or hr_fim_new != hr_fim:
        print("\n*** SUCESSO! Horários foram modificados! ***")
    else:
        print("\n*** FALHA! Horários NÃO foram modificados! ***")

print("\n" + "=" * 60)
