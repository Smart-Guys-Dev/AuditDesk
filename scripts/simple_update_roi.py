#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script SIMPLES para atualizar valores de ROI
"""

print("🔄 Atualizando valores de ROI...")

# Ler arquivo
with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituição 1: GLOSA_GUIA
content = content.replace(
    'financial_impact = 5000.0',
    'financial_impact = 15.0'
)

# Substituição 2: GLOSA_ITEM  
content = content.replace(
    'financial_impact = 300.0',
    'financial_impact = 7.9'
)

# Substituição 3: VALIDACAO
content = content.replace(
    'financial_impact = 100.0',
    'financial_impact = 5.5'
)

# Salvar
with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Valores atualizados!")
print("   GLOSA_GUIA: R$ 5000 → R$ 15")
print("   GLOSA_ITEM: R$ 300 → R$ 7.90")
print("   VALIDACAO: R$ 100 → R$ 5.50")
