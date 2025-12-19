#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Descobrir quais regras foram mais aplicadas
"""
import sqlite3

conn = sqlite3.connect('audit_plus.db')
cursor = conn.cursor()

print("📊 TOP 20 REGRAS MAIS APLICADAS (Execução #32)\n")
print("="*70)

# Buscar da tabela roi_metrics (se existir)
try:
    cursor.execute("""
        SELECT rule_id, COUNT(*) as qtd, correction_type
        FROM roi_metrics
        WHERE execution_id = 32
        GROUP BY rule_id
        ORDER BY qtd DESC
        LIMIT 20
    """)
    
    resultados = cursor.fetchall()
    
    if resultados:
        print(f"\n{'#':<4} {'Regra':<50} {'Qtd':<8} {'Tipo':<15}")
        print("-"*70)
        
        for i, (regra, qtd, tipo) in enumerate(resultados, 1):
            print(f"{i:<4} {regra[:48]:<50} {qtd:<8} {tipo:<15}")
    else:
        print("❌ Nenhum dado encontrado na tabela roi_metrics")
        
except Exception as e:
    print(f"❌ Erro ao consultar roi_metrics: {e}")

# Tentar outra abordagem - execution_details
try:
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%execution%'
    """)
    tabelas = cursor.fetchall()
    print(f"\n\nTabelas de execução disponíveis: {tabelas}")
    
except Exception as e:
    print(f"Erro: {e}")

conn.close()

print("\n" + "="*70)
print("💡 Com base nessas regras, vou adicionar metadata_glosa!")
