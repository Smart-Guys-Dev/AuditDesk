# -*- coding: utf-8 -*-
"""Script para adicionar a regra de taxa de observacao ao banco de dados"""
import sys
import os
import json
import logging

logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.rule_repository import RuleRepository

# Carregar a regra do JSON
json_path = os.path.join(
    os.path.dirname(__file__), 
    '..', 'src', 'config', 'regras', 'taxas_observacao.json'
)

with open(json_path, 'r', encoding='utf-8') as f:
    rules = json.load(f)

# Verificar se a regra ja existe
repo = RuleRepository()
existing = repo.get_rule_by_id('REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS')

if existing:
    print("Regra ja existe no banco de dados!")
    print(f"  ID: {existing.id}")
    print(f"  Ativo: {existing.ativo}")
else:
    print("Adicionando regra ao banco de dados...")
    
    rule_data = rules[0]
    # Ajustar formato para o esperado pelo create_rule
    rule_data['grupo'] = 'Taxas de Observacao'
    rule_data['categoria'] = 'CORRECAO_AUTOMATICA'
    
    try:
        created = repo.create_rule(rule_data, criado_por='script_setup')
        print(f"Regra criada com sucesso!")
        print(f"  ID: {created.id}")
        print(f"  Versao: {created.versao}")
    except Exception as e:
        print(f"Erro ao criar regra: {e}")
