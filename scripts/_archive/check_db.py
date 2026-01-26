#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificação RÁPIDA: Tem dados no banco agora?
"""
import sqlite3

conn = sqlite3.connect('audit_plus.db')
cursor = conn.cursor()

# Total de ROI
cursor.execute("SELECT COUNT(*), SUM(financial_impact) FROM roi_metrics")
total = cursor.fetchone()

# Última execução
cursor.execute("SELECT id, start_time FROM execution_logs ORDER BY id DESC LIMIT 1")
last_exec = cursor.fetchone()

conn.close()

print(f"ROI no banco: {total[0]} registros, R$ {total[1] if total[1] else 0:.2f}")
if last_exec:
    print(f"Última execução: ID {last_exec[0]} em {last_exec[1]}")
else:
    print("Nenhuma execução registrada")

if total[0] == 0:
    print("\n❌ BANCO VAZIO! Precisa processar XMLs novamente.")
else:
    print(f"\n✅ Banco tem dados! Dashboard DEVERIA mostrar.")
