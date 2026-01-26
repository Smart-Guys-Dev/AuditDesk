# -*- coding: utf-8 -*-
import sys

try:
    with open('output.txt', 'r', encoding='utf-16-le') as f:
        content = f.read()
except UnicodeError:
    try:
        with open('output.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeError:
        with open('output.txt', 'r', encoding='cp1252') as f:
            content = f.read()

# Filtrar linhas contendo DEBUG
print("=== LOGS DE DEBUG ===")
for line in content.splitlines():
    if "DEBUG:" in line or "FALHA" in line or "SUCESSO" in line:
        print(line)
