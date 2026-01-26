"""
Diagnóstico: Por que nenhuma regra está sendo aplicada?
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # _archive -> scripts -> project
sys.path.insert(0, project_root)

from src.business.rules.rule_engine import RuleEngine

print("=" * 60)
print("DIAGNÓSTICO: REGRAS CARREGADAS")
print("=" * 60)

config_dir = os.path.join(project_root, "src", "config")
engine = RuleEngine(config_dir)

# Testar carregamento do banco
print("\n1. Tentando carregar do BANCO DE DADOS...")
engine.load_all_rules(use_database=True)
db_count = len(engine.loaded_rules)
print(f"   Regras do banco: {db_count}")

if db_count > 0:
    print(f"   Primeiras 5 regras:")
    for r in engine.loaded_rules[:5]:
        print(f"     - {r.get('id')}: {r.get('ativo')}")
else:
    print("   PROBLEMA: Nenhuma regra carregada do banco!")

# Testar carregamento do JSON
print("\n2. Tentando carregar do JSON...")
engine2 = RuleEngine(config_dir)
engine2.load_all_rules(use_database=False)
json_count = len(engine2.loaded_rules)
print(f"   Regras do JSON: {json_count}")

if json_count > 0:
    print(f"   Primeiras 5 regras:")
    for r in engine2.loaded_rules[:5]:
        print(f"     - {r.get('id')}: ativo={r.get('ativo')}")

# Verificar listas externas
print("\n3. Listas externas carregadas:")
for list_id in engine.external_lists:
    count = len(engine.external_lists[list_id])
    print(f"   - {list_id}: {count} itens")

print("\n" + "=" * 60)
if db_count == 0 and json_count > 0:
    print("DIAGNÓSTICO: Banco de dados vazio, mas JSONs têm regras!")
    print("SOLUÇÃO: Execute 'python scripts/sync_rules_to_db.py'")
elif db_count > 0:
    print(f"OK: {db_count} regras disponíveis no banco.")
print("=" * 60)
