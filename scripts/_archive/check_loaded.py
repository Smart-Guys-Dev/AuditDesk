# -*- coding: utf-8 -*-
import sys
import os
import logging

# Desabilitar logs
logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar e carregar o engine
from src.business.rules.rule_engine import RuleEngine

print("Carregando rule engine...")
engine = RuleEngine()
engine.load_all_rules()

print(f"Total de regras carregadas: {len(engine.loaded_rules)}")

# Procurar regras com TAXA ou OBSERVACAO no ID
found = False
print("\nProcurando regras relacionadas a taxa/observacao:")
for rule in engine.loaded_rules:
    rule_id = rule.get('id', '')
    if 'TAXA' in rule_id.upper() or 'OBSERVA' in rule_id.upper():
        print(f"  ENCONTRADA: {rule_id}")
        found = True
        
# Se nao achou, listar ultimas 5 regras
if not found:
    print("\nNenhuma regra TAXA encontrada. Ultimas 5 regras:")
    for r in engine.loaded_rules[-5:]:
        print(f"  - {r.get('id')}")
