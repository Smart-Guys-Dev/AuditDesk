#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para resetar dados de ROI no banco
"""
import sqlite3
import os

# Conectar ao banco
db_path = 'audit_plus.db'

if not os.path.exists(db_path):
    print("❌ Banco de dados não encontrado!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🗑️  Limpando dados de ROI...")

try:
    # Limpar ROI Metrics (correções)
    cursor.execute("DELETE FROM roi_metrics")
    roi_deleted = cursor.rowcount
    
    # Limpar Alert Metrics (alertas)
    cursor.execute("DELETE FROM alert_metrics")
    alert_deleted = cursor.rowcount
    
    conn.commit()
    
    print(f"✅ ROI Metrics: {roi_deleted} registros removidos")
    print(f"✅ Alert Metrics: {alert_deleted} registros removidos")
    print("\n🎉 Banco resetado! Próximas validações vão popular os dados novamente.")
    
except sqlite3.Error as e:
    print(f"❌ Erro ao limpar banco: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n📌 Próximo passo:")
print("   1. Execute 'Validar Regras' em alguns XMLs")
print("   2. Execute 'Verificar Internações Curtas'")
print("   3. Veja o Dashboard com valores atualizados!")
