#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testar get_roi_stats() diretamente para ver o erro
"""
import sys
sys.path.insert(0, 'src')

from database import db_manager

print("🔍 Testando get_roi_stats()...\n")

try:
    stats = db_manager.get_roi_stats()
    
    print("✅ Função executou!")
    print(f"\nResultados:")
    print(f"  total_saved: R$ {stats['total_saved']:,.2f}")
    print(f"  total_corrections: {stats['total_corrections']}")
    print(f"  roi_potencial: R$ {stats['roi_potencial']:,.2f}")
    print(f"  roi_total: R$ {stats['roi_total']:,.2f}")
    print(f"  top_rules: {len(stats['top_rules'])} regras")
    
    if stats['total_saved'] == 0:
        print("\n❌ PROBLEMA: total_saved está ZERADO!")
    else:
        print("\n✅ Valores corretos!")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
