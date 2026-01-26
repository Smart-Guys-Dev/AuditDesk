"""
Teste da regra REGRA_CORRIGIR_TP_PARTICIPACAO_CAUTERIZACAO_QUIMICA
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Subir dois níveis (_archive -> scripts -> project_root)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from lxml import etree
from src.business.rules.rule_engine import RuleEngine

print("=" * 60)
print("TESTE: REGRA_CORRIGIR_TP_PARTICIPACAO_CAUTERIZACAO_QUIMICA")
print("=" * 60)

# Setup
config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)
engine.load_all_rules()

# Verificar se regra foi carregada
regra = [r for r in engine.loaded_rules if "TP_PARTICIPACAO_CAUTERIZACAO" in r.get("id", "")]
print(f"\nRegra carregada: {len(regra) > 0}")
if regra:
    print(f"ID: {regra[0].get('id')}")

# Carregar XML de teste
xml_path = os.path.join(project_root, "tests", "test_tp_participacao.xml")
tree = etree.parse(xml_path)
root = tree.getroot()

ns = {"ptu": "http://www.unimed.com.br/ptu"}

# Valor ANTES
tp_antes = root.xpath(".//ptu:tp_Participacao/text()", namespaces=ns)
print(f"\nANTES: tp_Participacao = {tp_antes}")

# Aplicar regras
print("\nAplicando regras...")
engine.apply_rules_to_xml(tree, file_name="test_tp_participacao.xml")

# Valor DEPOIS
tp_depois = root.xpath(".//ptu:tp_Participacao/text()", namespaces=ns)
print(f"DEPOIS: tp_Participacao = {tp_depois}")

# Verificar resultado
if tp_antes and tp_depois:
    if tp_antes[0] == "11" and tp_depois[0] == "12":
        print("\n" + "=" * 60)
        print("✅ SUCESSO! tp_Participacao corrigido de 11 para 12")
        print("=" * 60)
    elif tp_antes[0] == tp_depois[0]:
        print("\n" + "=" * 60)
        print("❌ FALHA! tp_Participacao não foi alterado")
        print("=" * 60)
    else:
        print(f"\n⚠️ Valor alterado de {tp_antes[0]} para {tp_depois[0]}")
