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

# Salvar output limpo
with open('debug_filtered.log', 'w', encoding='utf-8') as f:
    for line in content.splitlines():
        f.write(line + "\n")
