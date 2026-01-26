#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adiciona metadata em TODAS as categorias principais de regras
"""
import json
import os

print("🔧 ADICIONANDO METADATA EM MASSA\n")
print("="*70)

# Mapeamento: arquivo → categoria
REGRAS_CONFIG = {
    'src/config/regras/auditoria.json': {
        'categoria': 'GLOSA_GUIA',
        'impacto': 'ALTO',
        'razao': 'Dados de auditoria obrigatórios - ausência causa glosa total',
        'contabilizar': True
    },
    'src/config/regras/conselho.json': {
        'categoria': 'GLOSA_ITEM',
        'impacto': 'MEDIO',
        'razao': 'Conselho/CBO incorreto causa glosa do item',
        'contabilizar': True
    },
    'src/config/regras/equipe_profissional.json': {
        'categoria': 'OTIMIZACAO',  # Maioria é otimização (ordem)
        'impacto': 'BAIXO',
        'razao': 'Correção de ordem de tags (XSD)',
        'contabilizar': False
    }
}

# Regras especiais que devem ser GLOSA_ITEM mesmo em equipe_profissional
REGRAS_GLOSA_ITEM_EQUIPE = [
    'REGRA_GARANTIR_NOME_PROFISSIONAL',
    'REGRA_GARANTIR_CONSELHO_PROFISSIONAL',
    'REGRA_GARANTIR_NUMERO_CONSELHO_PROFISSIONAL',
    'REGRA_GARANTIR_UF_PROFISSIONAL',
    'REGRA_GARANTIR_CBO_PROFISSIONAL'
]

total_atualizado = 0

for arquivo, metadata_base in REGRAS_CONFIG.items():
    if not os.path.exists(arquivo):
        print(f"⚠️  Arquivo não encontrado: {arquivo}")
        continue
    
    print(f"\n📝 Processando: {arquivo}")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    atualizado = 0
    ja_tinha = 0
    
    for regra in regras:
        rule_id = regra.get('id', 'UNKNOWN')
        
        # Já tem metadata?
        if 'metadata_glosa' in regra:
            ja_tinha += 1
            continue
        
        # Regra especial?
        metadata = metadata_base.copy()
        
        if arquivo.endswith('equipe_profissional.json'):
            # Verificar se é regra que deve ser GLOSA_ITEM
            if any(especial in rule_id for especial in REGRAS_GLOSA_ITEM_EQUIPE):
                metadata = {
                    'categoria': 'GLOSA_ITEM',
                    'impacto': 'MEDIO',
                    'razao': 'Dados profissionais obrigatórios - ausência causa glosa do item',
                    'contabilizar': True
                }
        
        # Adicionar metadata
        regra['metadata_glosa'] = metadata
        atualizado += 1
    
    # Salvar
    if atualizado > 0:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(regras, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Atualizado: {atualizado} regras")
        print(f"   ℹ️  Já tinham: {ja_tinha} regras")
        total_atualizado += atualizado
    else:
        print(f"   ℹ️  Todas {ja_tinha} regras já tinham metadata")

print(f"\n{'='*70}")
print(f"✅ TOTAL ATUALIZADO: {total_atualizado} regras")
print(f"{'='*70}\n")

# Resumo final
print("📊 RESUMO POR CATEGORIA:\n")

categorias = {
    'src/config/regras/cnes.json': 'GLOSA_GUIA (CNES)',
    'src/config/regras_tp_participacao.json': 'GLOSA_ITEM (Participação)',
    'src/config/regras/auditoria.json': 'GLOSA_GUIA (Auditoria)',
    'src/config/regras/conselho.json': 'GLOSA_ITEM (Conselho/CBO)',
    'src/config/regras/equipe_profissional.json': 'OTIMIZAÇÃO + GLOSA_ITEM (Equipe)'
}

for arquivo, desc in categorias.items():
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            regras = json.load(f)
        com_metadata = sum(1 for r in regras if 'metadata_glosa' in r)
        print(f"   {desc}: {com_metadata}/{len(regras)} com metadata")

print(f"\n{'='*70}")
print("🎯 Agora processe novamente para ver os valores REAIS!")
print(f"{'='*70}")
