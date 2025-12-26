#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico COMPLETO - ROI não aparece no dashboard
"""
import sqlite3

conn = sqlite3.connect('audit_plus.db')
cursor = conn.cursor()

print("="*60)
print("DIAGNÓSTICO COMPLETO DO PROBLEMA")
print("="*60)

# 1. Última execução
print("\n1️⃣ ÚLTIMA EXECUÇÃO:")
cursor.execute("""
    SELECT id, operation_type, status, start_time, total_files, success_count 
    FROM execution_logs 
    ORDER BY id DESC LIMIT 1
""")
last_exec = cursor.fetchone()
if last_exec:
    print(f"   ID: {last_exec[0]}")
    print(f"   Tipo: {last_exec[1]}")
    print(f"   Status: {last_exec[2]}")
    print(f"   Arquivos: {last_exec[4]} (sucesso: {last_exec[5]})")
else:
    print("   ❌ NENHUMA EXECUÇÃO!")

# 2. ROI dessa execução
print("\n2️⃣ ROI DA ÚLTIMA EXECUÇÃO:")
if last_exec:
    cursor.execute("""
        SELECT COUNT(*), SUM(financial_impact), 
               MIN(financial_impact), MAX(financial_impact)
        FROM roi_metrics 
        WHERE execution_id = ?
    """, (last_exec[0],))
    roi = cursor.fetchone()
    print(f"   Registros: {roi[0]}")
    print(f"   Total: R$ {roi[1] if roi[1] else 0:.2f}")
    print(f"   Mín: R$ {roi[2] if roi[2] else 0:.2f}")
    print(f"   Máx: R$ {roi[3] if roi[3] else 0:.2f}")
    
    if roi[0] > 0:
        cursor.execute("""
            SELECT correction_type, financial_impact 
            FROM roi_metrics 
            WHERE execution_id = ? 
            LIMIT 3
        """, (last_exec[0],))
        print("\n   Exemplos:")
        for r in cursor.fetchall():
            print(f"      {r[0]}: R$ {r[1]:.2f}")

# 3. Total no banco
print("\n3️⃣ TOTAL NO BANCO (TODAS EXECUÇÕES):")
cursor.execute("SELECT COUNT(*), SUM(financial_impact) FROM roi_metrics")
total = cursor.fetchone()
print(f"   Registros: {total[0]}")
print(f"   Total: R$ {total[1] if total[1] else 0:.2f}")

# 4. get_roi_stats simulado
print("\n4️⃣ SIMULANDO get_roi_stats():")
cursor.execute("""
    SELECT 
        SUM(financial_impact) as total_saved,
        COUNT(*) as total_corrections
    FROM roi_metrics
""")
stats = cursor.fetchone()
print(f"   total_saved: R$ {stats[0] if stats[0] else 0:.2f}")
print(f"   total_corrections: {stats[1]}")

conn.close()

print("\n" + "="*60)
print("PROBLEMA IDENTIFICADO:")
if total[0] == 0:
    print("❌ ROI NÃO ESTÁ SENDO SALVO NO BANCO!")
    print("   Motivo provável: execution_id = -1")
elif stats[0] == 0:
    print("❌ ROI tem 0 valor no banco!")
else:
    print("⚠️  ROI está no banco MAS dashboard não mostra!")
    print("   Problema no load_data() do dashboard")
print("="*60)
