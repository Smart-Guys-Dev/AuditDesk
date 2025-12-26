#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar metadados de glosa em todas as regras de CNES
"""
import json

# Carrega o arquivo
with open('src/config/regras/cnes.json', 'r', encoding='utf-8') as f:
    regras = json.load(f)

# Metadados padrão para todas as regras de CNES
metadata_cnes = {
    "categoria": "VALIDACAO",
    "impacto": "ALTO",
    "razao": "CNES incorreto ou ausente impede postagem da fatura (validação obrigatória)"
}

# Adiciona metadados em cada regra
for regra in regras:
    regra['metadata_glosa'] = metadata_cnes
    print(f"✓ {regra['id']}")

# Salva de volta
with open('src/config/regras/cnes.json', 'w', encoding='utf-8') as f:
    json.dump(regras, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(regras)} regras de CNES atualizadas com metadados!")
