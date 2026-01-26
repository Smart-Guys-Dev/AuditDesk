"""
Teste da regra REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from lxml import etree
from src.business.rules.rule_engine import RuleEngine

print("=" * 60)
print("TESTE: REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS (00:00:00)")
print("=" * 60)

config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)
engine.load_all_rules()

# Verificar regra
regra = [r for r in engine.loaded_rules if "TAXA_OBSERVACAO" in r.get("id", "")]
print(f"\nRegra encontrada: {len(regra) > 0}")
if regra:
    print(f"ID: {regra[0].get('id')}")
    print(f"Ativo: {regra[0].get('ativo')}")
    import json
    print(f"Condicoes completas:\n{json.dumps(regra[0].get('condicoes'), indent=2)}")

# Carregar XML de teste
xml_path = os.path.join(project_root, "tests", "test_taxa_obs_00.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

ns = {"ptu": "http://ptu.unimed.coop.br/schemas/V3_0"}

# Buscar o procedimento da taxa
taxa_proc = root.xpath(".//ptu:procedimentosExecutados[ptu:procedimentos/ptu:cd_Servico='60033681']", namespaces=ns)
if taxa_proc:
    print("\n--- Testando condições manualmente ---")
    elem = taxa_proc[0]
    
    # Condição 1: cd_Servico = 60033681
    cd = elem.xpath("./ptu:procedimentos/ptu:cd_Servico/text()", namespaces=ns)
    print(f"1. cd_Servico: {cd[0] if cd else 'N/A'} == 60033681? {cd[0] == '60033681' if cd else False}")
    
    # Condição 2a: hr_Inicial = hr_Final
    hr_ini = elem.xpath("./ptu:hr_Inicial/text()", namespaces=ns)
    hr_fim = elem.xpath("./ptu:hr_Final/text()", namespaces=ns)
    print(f"2a. hr_Inicial ({hr_ini[0] if hr_ini else 'N/A'}) == hr_Final ({hr_fim[0] if hr_fim else 'N/A'})? {hr_ini[0] == hr_fim[0] if hr_ini and hr_fim else False}")
    
    # Condição 2b: hr_Inicial começa com 00:00
    print(f"2b. hr_Inicial começa com '00:00'? {hr_ini[0].startswith('00:00') if hr_ini else False}")
    
    # Testar avaliação da regra
    print("\n--- Testando _evaluate_condition ---")
    if regra:
        conds = regra[0].get("condicoes", {})
        result = engine._evaluate_condition(elem, conds)
        print(f"Resultado: {result}")

# Aplicar regras
print("\n--- Aplicando regras ---")
result = engine.apply_rules_to_xml(tree, file_name="test_taxa_obs_00.xml")
print(f"Resultado apply_rules_to_xml: {'Modificado' if result else 'Sem modificação'}")

# Verificar resultado
taxa_proc = root.xpath(".//ptu:procedimentosExecutados[ptu:procedimentos/ptu:cd_Servico='60033681']", namespaces=ns)
if taxa_proc:
    hr_ini = taxa_proc[0].xpath("./ptu:hr_Inicial/text()", namespaces=ns)
    print(f"\nhr_Inicial FINAL: {hr_ini[0] if hr_ini else 'N/A'}")
    if hr_ini and hr_ini[0] != "00:00:00":
        print("✅ SUCESSO!")
    else:
        print("❌ FALHA!")

