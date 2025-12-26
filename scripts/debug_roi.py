#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar se há dados de ROI no banco
"""
import sqlite3
import os

db_path = 'audit_plus.db'

if not os.path.exists(db_path):
    print("❌ Banco de dados não encontrado!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔍 Investigando dados no banco...\n")

# 1. Verificar ExecutionLog
cursor.execute("SELECT id, operation_type, status, start_time FROM execution_logs ORDER BY id DESC LIMIT 5")
executions = cursor.fetchall()
print("📋 Últimas 5 execuções:")
for ex in executions:
    print(f"   ID: {ex[0]} | Tipo: {ex[1]} | Status: {ex[2]} | Início: {ex[3]}")

print()

# 2. Verificar ROIMetrics
cursor.execute("SELECT COUNT(*) FROM roi_metrics")
roi_count = cursor.fetchone()[0]
print(f"💰 Total de registros em roi_metrics: {roi_count}")

if roi_count > 0:
    cursor.execute("""
        SELECT execution_id, rule_id, correction_type, financial_impact 
        FROM roi_metrics 
        ORDER BY id DESC LIMIT 5
    """)
    rois = cursor.fetchall()
    print("\n   Últimos 5 registros de ROI:")
    for roi in rois:
        print(f"   Exec: {roi[0]} | Regra: {roi[1]} | Tipo: {roi[2]} | R$ {roi[3]:.2f}")

print()

# 3. Verificar última execução
cursor.execute("SELECT MAX(id) FROM execution_logs WHERE operation_type='VALIDATION'")
last_exec_id = cursor.fetchone()[0]

if last_exec_id:
    print(f"🎯 Última validação: Execution ID {last_exec_id}")
    
    cursor.execute("SELECT COUNT(*) FROM roi_metrics WHERE execution_id = ?", (last_exec_id,))
    rois_last = cursor.fetchone()[0]
    print(f"   ROI registrado nessa execução: {rois_last} registros")
    
    if rois_last > 0:
        cursor.execute("""
            SELECT SUM(financial_impact) 
            FROM roi_metrics 
            WHERE execution_id = ?
        """, (last_exec_id,))
        total_roi = cursor.fetchone()[0]
        print(f"   💵 Total ROI: R$ {total_roi:,.2f}")

conn.close()

print("\n" + "="*50)
if roi_count == 0:
    print("⚠️  PROBLEMA: Nenhum ROI foi salvo!")
    print("   Possíveis causas:")
    print("   1. Regras aplicadas não têm metadados_glosa")
    print("   2. Erro silencioso no log_roi_metric")
    print("   3. execution_id ainda está -1")
else:
    print("✅ Dados de ROI encontrados no banco!")
