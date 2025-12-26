# Script para corrigir rule_engine.py - usar namedtuple em vez de dict

with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar import no topo
if 'from collections import namedtuple' not in content:
    content = content.replace(
        'import lxml.etree as etree',
        'import lxml.etree as etree\nfrom collections import namedtuple'
    )

# Adicionar definição de CorrectionResult após os imports
if 'CorrectionResult = namedtuple' not in content:
    # Encontrar a linha após logger = logging.getLogger(__name__)
    content = content.replace(
        'logger = logging.getLogger(__name__)',
        '''logger = logging.getLogger(__name__)

# Estrutura temporária para compatibilidade com ROI
CorrectionResult = namedtuple('CorrectionResult', ['rule_id', 'rule_description', 'correction_type', 'financial_impact'])'''
    )

# Substituir o retorno de dict para namedtuple
old_return = 'return [{"rule_id": "APLICADAS", "rule_description": "Regras aplicadas", "correction_type": "AUTO", "financial_impact": 0.0}] if alterations_made else []'
new_return = 'return [CorrectionResult("APLICADAS", "Regras aplicadas", "AUTO", 0.0)] if alterations_made else []'

content = content.replace(old_return, new_return)

with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Arquivo corrigido com namedtuple!")
