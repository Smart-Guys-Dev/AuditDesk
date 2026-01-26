"""
Script de debug detalhado para a regra REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS
"""
import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from lxml import etree

print("=" * 60)
print("DEBUG: Verificação da Regra de Taxa de Observação")
print("=" * 60)

# 1. Verificar XML
xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
print(f"\n1. XML Path: {xml_path}")
print(f"   Existe: {os.path.exists(xml_path)}")

tree = etree.parse(xml_path)
root = tree.getroot()
print(f"   Root namespace: {root.nsmap}")

# 2. Verificar namespace no XMLReader
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES
print(f"\n2. NAMESPACES no XMLReader: {NAMESPACES}")

# 3. Buscar todos procedimentosExecutados
reader = XMLReader()
procs = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"\n3. Total procedimentosExecutados encontrados: {len(procs)}")

# 4. Para cada procedimento, mostrar cd_Servico e horários
print("\n4. Detalhes de cada procedimentosExecutados:")
for i, proc in enumerate(procs):
    cd_servico_nodes = reader.find_elements_by_xpath(proc, "./ptu:procedimentos/ptu:cd_Servico")
    hr_ini_nodes = reader.find_elements_by_xpath(proc, "./ptu:hr_Inicial")
    hr_fim_nodes = reader.find_elements_by_xpath(proc, "./ptu:hr_Final")
    
    cd_servico = cd_servico_nodes[0].text if cd_servico_nodes else "N/A"
    hr_ini = hr_ini_nodes[0].text if hr_ini_nodes else "N/A"
    hr_fim = hr_fim_nodes[0].text if hr_fim_nodes else "N/A"
    
    # Marcar taxa de observação
    marker = " <-- TAXA OBSERVACAO" if cd_servico in ["60033681", "60033665"] else ""
    print(f"   [{i+1:2d}] cd_Servico={cd_servico}, hr_Inicial={hr_ini}, hr_Final={hr_fim}{marker}")

# 5. Verificar RuleEngine
print("\n5. Verificando RuleEngine:")
from src.business.rules.rule_engine import RuleEngine

# Usar caminho absoluto correto
config_dir = os.path.join(project_root, "src", "config")
print(f"   Config dir passado: {config_dir}")

engine = RuleEngine(config_dir)
print(f"   Engine config_dir: {engine.config_dir}")
print(f"   Rules config path: {os.path.join(engine.config_dir, 'rules_config.json')}")
print(f"   Existe rules_config.json: {os.path.exists(os.path.join(engine.config_dir, 'rules_config.json'))}")

# 6. Carregar regras
print("\n6. Carregando regras...")
engine.load_all_rules()
print(f"   Total regras carregadas: {len(engine.loaded_rules)}")

# 7. Verificar se regra taxa observação está carregada
taxa_rules = [r for r in engine.loaded_rules if "TAXA_OBSERVACAO" in r.get("id", "")]
print(f"   Regras de taxa observação: {len(taxa_rules)}")

if taxa_rules:
    rule = taxa_rules[0]
    print(f"\n7. Detalhes da regra:")
    print(f"   ID: {rule.get('id')}")
    print(f"   Ativo: {rule.get('ativo')}")
    print(f"   Condições: {rule.get('condicoes')}")
    
    # 8. Testar manualmente a condição
    print("\n8. Teste manual da condição para cada procedimento:")
    for i, proc in enumerate(procs):
        # Condição 1: cd_Servico in [60033681, 60033665]
        cd_servico_nodes = reader.find_elements_by_xpath(proc, "./ptu:procedimentos/ptu:cd_Servico")
        cd_servico = cd_servico_nodes[0].text if cd_servico_nodes else None
        cond1 = cd_servico in ["60033681", "60033665"]
        
        # Condição 2: hr_Inicial == hr_Final
        hr_ini_nodes = reader.find_elements_by_xpath(proc, "./ptu:hr_Inicial")
        hr_fim_nodes = reader.find_elements_by_xpath(proc, "./ptu:hr_Final")
        hr_ini = hr_ini_nodes[0].text if hr_ini_nodes else None
        hr_fim = hr_fim_nodes[0].text if hr_fim_nodes else None
        cond2 = hr_ini == hr_fim if (hr_ini and hr_fim) else False
        
        if cond1 or cond2:
            print(f"   [{i+1:2d}] cd={cd_servico}, cond1(taxa)={cond1}, cond2(hr==)={cond2}, AND={cond1 and cond2}")

print("\n" + "=" * 60)
print("DEBUG COMPLETO")
print("=" * 60)
