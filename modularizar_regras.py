#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para modularizar regras em grupos temáticos
"""
import json
import os
from collections import defaultdict

# Carrega o arquivo original
with open('src/config/regras_grupo_1200.json', 'r', encoding='utf-8') as f:
    todas_regras = json.load(f)

print(f"📋 Total de regras carregadas: {len(todas_regras)}\n")

# Define os grupos baseados em palavras-chave no ID ou descrição
grupos = {
    'equipe_profissional': {
        'keywords': ['EQUIPE', 'PLANTONISTA', 'PARTICIPACAO', 'ORDEM_EQUIPE'],
        'descricao': 'Regras de equipe profissional e reordenação'
    },
    'cnes': {
        'keywords': ['CNES'],
        'descricao': 'Regras de CNES por prestador'
    },
    'cpf_prestadores': {
        'keywords': ['GARANTIR_CPF', 'CPF_PRESTADOR'],
        'descricao': 'Regras de CPF/CNPJ de prestadores'
    },
    'auditoria': {
        'keywords': ['AUDITOR', 'AUDITORIA'],
        'descricao': 'Regras de dados de auditoria'
    },
    'conselho': {
        'keywords': ['CONSELHO', 'CBO'],
        'descricao': 'Regras de conselho profissional'
    },
    'procedimentos': {
        'keywords': ['ACRESCIMO', 'ANVISA', 'INDICACAO'],
        'descricao': 'Regras de procedimentos e serviços'
    },
    'internacao': {
        'keywords': ['MULTIPLICADOR', 'ACOMODACAO'],
        'descricao': 'Regras de internação'
    },
    'pj_para_pf': {
        'keywords': ['PJ_PARA_PF', 'NORMALIZAR', 'RODRIGO'],
        'descricao': 'Regras de conversão PJ para PF'
    },
    'outros': {
        'keywords': [],
        'descricao': 'Outras regras não categorizadas'
    }
}

# Separa as regras por grupo
regras_por_grupo = defaultdict(list)

for regra in todas_regras:
    regra_id = regra.get('id', '')
    regra_desc = regra.get('descricao', '')
    texto_busca = (regra_id + ' ' + regra_desc).upper()
    
    categorizada = False
    for grupo_nome, grupo_info in grupos.items():
        if grupo_nome == 'outros':
            continue
        
        for keyword in grupo_info['keywords']:
            if keyword in texto_busca:
                regras_por_grupo[grupo_nome].append(regra)
                categorizada = True
                break
        
        if categorizada:
            break
    
    if not categorizada:
        regras_por_grupo['outros'].append(regra)

# Cria a pasta de regras se não existir
pasta_regras = 'src/config/regras'
os.makedirs(pasta_regras, exist_ok=True)

# Salva cada grupo em seu arquivo
print("📁 Criando arquivos de regras...\n")
for grupo_nome, regras in regras_por_grupo.items():
    if not regras:
        continue
    
    arquivo = os.path.join(pasta_regras, f'{grupo_nome}.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(regras, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {arquivo}")
    print(f"  {len(regras)} regra(s) - {grupos[grupo_nome]['descricao']}")

print(f"\n✅ Modularização concluída!")
print(f"📂 Arquivos salvos em: {pasta_regras}/")
print(f"\n💡 O arquivo original 'regras_grupo_1200.json' foi mantido como backup.")
