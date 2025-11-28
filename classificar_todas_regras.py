#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script MASTER para classificar TODAS as regras automaticamente
"""
import json
import os

# Mapeamento: ID da regra → Categoria de glosa
CLASSIFICACAO = {
    # === VALIDACAO (Bloqueante) ===
    'REGRA_ORDEM_': 'VALIDACAO',  # Todas as regras de ordenação
    'REGRA_GARANTIR_CNES_': 'VALIDACAO',
    'REGRA_GARANTIR_CPF_PRESTADOR_': 'VALIDACAO',
    
    # === GLOSA_GUIA (Alto impacto) ===
    'REGRA_GARANTIR_NOME_MEDICO_AUDITOR': 'GLOSA_GUIA',
    'REGRA_GARANTIR_CRM_MEDICO_AUDITOR': 'GLOSA_GUIA',
    'REGRA_GARANTIR_UF_MEDICO_AUDITOR': 'GLOSA_GUIA',
    'REGRA_CORRIGIR_MULTIPLICADOR_ACOMODACAO': 'GLOSA_GUIA',
    
    # === GLOSA_ITEM (Médio/Baixo impacto) ===
    'REGRA_CORRIGIR_PJ_PARA_PF': 'GLOSA_ITEM',
    'REGRA_10104020_NORMALIZAR': 'GLOSA_ITEM',
    'REGRA_PROFISSIONAL_PADRAO': 'GLOSA_ITEM',
    'REGRA_NORMALIZAR_EQUIPE': 'GLOSA_ITEM',
    'REGRA_CORRIGIR_CONSELHO': 'GLOSA_ITEM',
    'REGRA_GARANTIR_INDICACAO': 'GLOSA_ITEM',
}

# Metadados por categoria
METADATA_TEMPLATES = {
    'VALIDACAO': {
        'categoria': 'VALIDACAO',
        'impacto': 'ALTO',
        'razao': 'Erro de validação impede postagem da fatura'
    },
    'GLOSA_GUIA': {
        'categoria': 'GLOSA_GUIA',
        'impacto': 'ALTO',
        'razao': 'Operadora glosa a guia inteira se informação estiver incorreta'
    },
    'GLOSA_ITEM': {
        'categoria': 'GLOSA_ITEM',
        'impacto': 'MEDIO',
        'razao': 'Operadora glosa apenas o procedimento específico'
    }
}

def classificar_regra(regra_id):
    """Classifica uma regra baseada no ID."""
    for prefixo, categoria in CLASSIFICACAO.items():
        if regra_id.startswith(prefixo):
            return categoria
    return 'GLOSA_ITEM'  # Default

pasta = 'src/config/regras'
total_atualizadas = 0

for arquivo in os.listdir(pasta):
    if not arquivo.endswith('.json'):
        continue
    
    caminho = os.path.join(pasta, arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    for regra in regras:
        # Pula se já tem metadados
        if 'metadata_glosa' in regra:
            continue
        
        categoria = classificar_regra(regra['id'])
        regra['metadata_glosa'] = METADATA_TEMPLATES[categoria].copy()
        total_atualizadas += 1
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(regras, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {arquivo}: {len(regras)} regras")

print(f"\n✅ {total_atualizadas} regras atualizadas no total!")
