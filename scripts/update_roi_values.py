#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Atualizar valores de ROI para valores conservadores definidos pelo usuário
"""

# Ler arquivo
with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir valores financeiros
old_values = '''                    # Calcular impacto financeiro
                    if categoria == "GLOSA_GUIA":
                        # Valor médio de uma guia: R$ 5000
                        financial_impact = 5000.0
                    elif categoria == "GLOSA_ITEM":
                        # Valor médio de um item/procedimento: R$ 300
                        financial_impact = 300.0
                    else:
                        # Validação: impacto indireto (evita retrabalho)
                        financial_impact = 100.0'''

new_values = '''                    # Calcular impacto financeiro (valores conservadores)
                    if categoria == "GLOSA_GUIA":
                        # Economia por evitar glosa de guia completa
                        financial_impact = 15.0
                    elif categoria == "GLOSA_ITEM":
                        # Economia por evitar glosa de item/procedimento
                        financial_impact = 7.9
                    else:
                        # Validação: evita retrabalho e custos operacionais
                        financial_impact = 5.5'''

content = content.replace(old_values, new_values)

# Salvar
with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Valores de ROI ​​atualizados!")
print("  GLOSA_GUIA: R$ 15,00")
print("  GLOSA_ITEM: R$ 7,90")
print("  VALIDACAO:  R$ 5,50")
print("\n📊 Com 12.784 correções:")
print(f"   ROI estimado: R$ {12784 * 5.5:,.2f} (conservador)")
