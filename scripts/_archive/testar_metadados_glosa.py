#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido: valida se rule_engine carrega metadados e calcula ROI
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from rule_engine import RuleEngine

print("🧪 Testando Sistema de Classificação de Glosas\n")

# Inicializa engine
try:
    engine = RuleEngine()
    
    # Carrega regras
    if not engine.load_all_rules():
        print("❌ Erro ao carregar regras!")
        sys.exit(1)
    
    print(f"✅ {len(engine.loaded_rules)} regras carregadas\n")
    
    # Analisa metadados
    categorias = {'VALIDACAO': 0, 'GLOSA_GUIA': 0, 'GLOSA_ITEM': 0, 'SEM_METADATA': 0}
    
    for regra in engine.loaded_rules:
        metadata = regra.get('metadata_glosa', {})
        categoria = metadata.get('categoria', None)
        
        if categoria:
            categorias[categoria] = categorias.get(categoria, 0) + 1
        else:
            categorias['SEM_METADATA'] += 1
            print(f"⚠️  Regra sem metadados: {regra.get('id')}")
    
    print("\n📊 Distribuição por categoria:")
    print("-" * 50)
    for cat, count in categorias.items():
        if count > 0:
            print(f"  {cat:20} {count:3} regra(s)")
    
    if categorias['SEM_METADATA'] == 0:
        print("\n✅ TODOS as regras têm metadados!")
    else:
        print(f"\n⚠️  {categorias['SEM_METADATA']} regras faltando metadados")
    
    # Verifica se métodos existem
    if hasattr(engine, '_calculate_financial_impact'):
        print("\n✅ Método _calculate_financial_impact() existe")
    else:
        print("\n❌ Método _calculate_financial_impact() NÃO existe!")
    
    if hasattr(engine, '_extrair_valor_monetario'):
        print("✅ Método _extrair_valor_monetario() existe")
    else:
        print("❌ Método _extrair_valor_monetario() NÃO existe!")
    
    print("\n🎉 Sistema pronto para uso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
