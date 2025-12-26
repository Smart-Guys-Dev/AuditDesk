# Script temporário para corrigir rule_engine.py
import re

with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir o retorno
old_return = 'return alterations_made'
new_return = '''# Retorna lista com item dummy se houver modificações
        return [{"rule_id": "APLICADAS", "rule_description": "Regras aplicadas", "correction_type": "AUTO", "financial_impact": 0.0}] if alterations_made else []'''

content = content.replace(old_return, new_return)

with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Arquivo corrigido!")
