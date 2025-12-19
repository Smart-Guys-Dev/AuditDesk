#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico: Por que tracking está zerado?
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("🔍 DIAGNÓSTICO DO TRACKING\n")
print("="*70)

# 1. Verificar tabelas
print("\n1️⃣ Verificando se tabelas existem...")
try:
    conn = sqlite3.connect('audit_plus.db')
    cursor = conn.cursor()
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row[0] for row in cursor.fetchall()]
    
    tab_glosas = ['glosas_evitadas_guias', 'glosas_evitadas_items', 'otimizacoes']
    for tab in tab_glosas:
        if tab in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tab}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {tab}: {count} registros")
        else:
            print(f"   ❌ {tab}: NÃO EXISTE!")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Verificar import do tracker
print("\n2️⃣ Verificando integração no rule_engine...")
try:
    with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    if 'from .relatorio_glosas import tracker' in conteudo:
        print("   ✅ Import do tracker encontrado")
    else:
        print("   ❌ Import do tracker NÃO encontrado")
    
    if 'tracker.processar_correcao' in conteudo:
        print("   ✅ Chamada ao tracker encontrada")
    else:
        print("   ❌ Chamada ao tracker NÃO encontrada")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. Verificar metadata nas regras
print("\n3️⃣ Verificando regras com metadata_glosa...")
try:
    import json
    
    # CNES
    with open('src/config/regras/cnes.json', 'r', encoding='utf-8') as f:
        cnes = json.load(f)
    
    cnes_metadata = [r for r in cnes if 'metadata_glosa' in r and r['metadata_glosa'].get('contabilizar')]
    print(f"   CNES com metadata contabilizar=True: {len(cnes_metadata)}/{len(cnes)}")
    
    # Participação
    with open('src/config/regras_tp_participacao.json', 'r', encoding='utf-8') as f:
        part = json.load(f)
    
    part_metadata = [r for r in part if 'metadata_glosa' in r and r['metadata_glosa'].get('contabilizar')]
    print(f"   Participação com metadata contabilizar=True: {len(part_metadata)}/{len(part)}")
    
    # Mostrar exemplo
    if cnes_metadata:
        exemplo = cnes_metadata[0]
        print(f"\n   Exemplo de metadata:")
        print(f"   Regra: {exemplo['id']}")
        print(f"   Categoria: {exemplo['metadata_glosa'].get('categoria')}")
        print(f"   Contabilizar: {exemplo['metadata_glosa'].get('contabilizar')}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 4. Verificar última execução
print("\n4️⃣ Verificando última execução...")
try:
    cursor.execute("SELECT id, file_count FROM execution_logs ORDER BY id DESC LIMIT 1")
    ultima = cursor.fetchone()
    if ultima:
        print(f"   Última execução: ID #{ultima[0]}, {ultima[1]} arquivos")
    else:
        print(f"   ❌ Nenhuma execução encontrada")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Diagnóstico final
print("\n" + "="*70)
print("📊 DIAGNÓSTICO:")
print()

cursor.execute("SELECT COUNT(*) FROM glosas_evitadas_guias")
guias = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM glosas_evitadas_items")
itens = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM otimizacoes")
otims = cursor.fetchone()[0]

if guias == 0 and itens == 0:
    print("❌ PROBLEMA: Nenhum dado capturado!")
    print()
    print("POSSÍVEIS CAUSAS:")
    print("1. Tracker teve erro silencioso")
    print("2. Regras aplicadas não têm metadata_glosa")
    print("3. Processamento foi antes da integração")
    print()
    print("SOLUÇÃO:")
    print("→ Processar novamente para testar o tracking")
else:
    print(f"✅ Sistema funcionando!")
    print(f"   Guias: {guias}")
    print(f"   Itens: {itens}")

print(f"\n✅ Otimizações capturadas: {otims}")
print("="*70)

conn.close()
