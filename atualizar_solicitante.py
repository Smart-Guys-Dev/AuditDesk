#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Atualiza classificação da regra de solicitante para GLOSA_GUIA
"""
import json

arquivo = 'src/config/regras/outros.json'

with open(arquivo, 'r', encoding='utf-8') as f:
    regras = json.load(f)

for regra in regras:
    if regra['id'] == 'REGRA_CORRIGIR_SOLICITANTE_GENERICO_UNIMED':
        regra['metadata_glosa'] = {
            'categoria': 'GLOSA_GUIA',
            'impacto': 'ALTO',
            'razao': 'Dados do solicitante incorretos resultam em glosa total da guia pela operadora'
        }
        print(f"✓ Regra atualizada: {regra['id']}")
        print(f"  Categoria: GLOSA_GUIA")
        print(f"  Impacto: ALTO")

with open(arquivo, 'w', encoding='utf-8') as f:
    json.dump(regras, f, ensure_ascii=False, indent=2)

print("\n✅ Arquivo salvo!")
