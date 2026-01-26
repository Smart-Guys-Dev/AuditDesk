#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Verificar se ROI está sendo salvo no banco
"""
import sqlite3

conn = sqlite3.connect('audit_plus.db')
cursor = conn.cursor()

print("🔍 Investigando dados de ROI...\n")

# 1. Última execução
cursor.execute("SELECT id, operation_type, status, start_time FROM execution_logs ORDER BY id DESC LIMIT 1")
last_exec = cursor.fetchone()

if last_exec:
    print(f"📋 Última execução:")
    print(f"   ID: {last_exec[0]}")
    print(f"   Tipo: {last_exec[1]}")
    print(f"   Status: {last_exec[2]}")
    print(f"   Início: {last_exec[3]}")
    
    # 2. ROI dessa execução
    cursor.execute("SELECT COUNT(*), SUM(financial_impact) FROM roi_metrics WHERE execution_id = ?", (last_exec[0],))
    roi_data = cursor.fetchone()
    
    print(f"\n💰 ROI registrado nessa execução:")
    print(f"   Correções: {roi_data[0]}")
    print(f"   Total: R$ {roi_data[1] if roi_data[1] else 0:,.2f}")
    
    if roi_data[0] > 0:
        # Mostrar alguns exemplos
        cursor.execute("""
            SELECT rule_id, correction_type, financial_impact 
            FROM roi_metrics 
            WHERE execution_id = ? 
            LIMIT 5
        """, (last_exec[0],))
        
        print(f"\n📝 Exemplos de ROI:")
        for row in cursor.fetchall():
            print(f"   {row[0][:50]}: {row[1]} = R$ {row[2]:.2f}")
else:
    print("❌ Nenhuma execução encontrada!")

# 3. Total geral no banco
cursor.execute("SELECT COUNT(*), SUM(financial_impact) FROM roi_metrics")
total = cursor.fetchone()
print(f"\n📊 Total geral no banco:")
print(f"   Correções: {total[0]}")
print(f"   Total: R$ {total[1] if total[1] else 0:,.2f}")

conn.close()

print("\n" + "="*50)
if total[0] == 0:
    print("⚠️  PROBLEMA: Nenhum ROI foi salvo!")
    print("\nPossíveis causas:")
    print("1. execution_id está -1")
    print("2. Código não chegou no log_roi_metric")
    print("3. Erro silencioso no try/except")
else:
    print("✅ ROI está no banco!")
    print("⚠️  Mas dashboard não mostra...")
    print("   → Problema está no get_roi_stats() ou no load_data()")
