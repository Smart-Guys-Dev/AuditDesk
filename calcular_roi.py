#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para calcular ROI manualmente e verificar get_roi_stats
"""
import sqlite3

conn = sqlite3.connect('audit_plus.db')
cursor = conn.cursor()

print("💰 Calculando ROI manualmente...\n")

# ROI Realizado
cursor.execute("SELECT SUM(financial_impact), COUNT(*) FROM roi_metrics")
roi_realizado, total_corrections = cursor.fetchone()

print(f"✅ ROI Realizado: R$ {roi_realizado:,.2f}")
print(f"   Total de correções: {total_corrections}")

# ROI Potencial
cursor.execute("SELECT SUM(financial_impact), COUNT(*) FROM alert_metrics WHERE status='POTENCIAL'")
roi_potencial, total_alertas = cursor.fetchone()

if roi_potencial is None:
    roi_potencial = 0.0
if total_alertas is None:
    total_alertas = 0

print(f"\n⚠️  ROI Potencial: R$ {roi_potencial:,.2f}")
print(f"   Total de alertas: {total_alertas}")

# ROI Total
roi_total = roi_realizado + roi_potencial
print(f"\n💰 ROI Total: R$ {roi_total:,.2f}")

# Top 5 regras
print("\n🏆 Top 5 Regras:")
cursor.execute("""
    SELECT rule_id, SUM(financial_impact) as total, COUNT(*) as qtd
    FROM roi_metrics
    GROUP BY rule_id
    ORDER BY total DESC
    LIMIT 5
""")

for i, (rule_id, total, qtd) in enumerate(cursor.fetchall(), 1):
    print(f"   {i}. {rule_id}: R$ {total:,.2f} ({qtd}x)")

conn.close()

print("\n" + "="*50)
print("🔍 DIAGNÓSTICO:")
if roi_realizado > 0:
    print("✅ Dados estão no banco")
    print("❌ Problema está no get_roi_stats() do dashboard")
    print("   → Dashboard não está buscando os dados corretamente")
