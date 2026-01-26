# -*- coding: utf-8 -*-
import sys
import os
import json

# Caminho do arquivo de regras
file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'config', 'regras', 'taxas_observacao.json')
file_path = os.path.abspath(file_path)

print(f"Verificando: {file_path}")
print(f"Existe: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    print(f"Regras no arquivo: {len(rules)}")
    for r in rules:
        print(f"  - ID: {r.get('id')}")
        print(f"    Ativo: {r.get('ativo')}")
