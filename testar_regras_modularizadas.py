#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar o carregamento das regras modularizadas
"""
import sys
sys.path.insert(0, 'src')

from rule_engine import RuleEngine

print("🧪 Testando carregamento de regras modularizadas...\n")

# Inicializa o engine
engine = RuleEngine()

# Carrega as regras
if engine.load_all_rules():
    print(f"\n✅ Sucesso! {len(engine.loaded_rules)} regras ativas carregadas.")
    
    # Mostra resumo por grupo
    print("\n📊 Resumo por arquivo:")
    print("-" * 60)
    
    # Conta regras por ID prefix (identificar grupo)
    grupos_count = {}
    for regra in engine.loaded_rules:
        regra_id = regra.get('id', '')
        # Pega a primeira parte do ID antes do primeiro underscore
        if '_' in regra_id:
            prefixo = regra_id.split('_')[1] if regra_id.startswith('REGRA_') else regra_id.split('_')[0]
        else:
            prefixo = 'OUTROS'
        
        grupos_count[prefixo] = grupos_count.get(prefixo, 0) + 1
    
    for grupo, count in sorted(grupos_count.items()):
        print(f"  {grupo:30} {count:3} regra(s)")
    
    print("\n✅ Sistema pronto para uso!")
else:
    print("\n❌ Erro ao carregar regras!")
    sys.exit(1)
