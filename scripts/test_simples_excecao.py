# -*- coding: utf-8 -*-
"""Teste simples e direto da regra REGRA_REMOCAO_CD_EXCECAO_ZERO"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lxml.etree as etree
from src.business.rules.rule_engine import RuleEngine

XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<faturaSP_SADT xmlns="http://www.ans.gov.br/ptu/" xmlns:ptu="http://www.ans.gov.br/ptu/">
    <guiasSP_SADT><procedimentosExecutados>
        <cd_Excecao>L</cd_Excecao>
        <procedimentos><cd_Servico>60018909</cd_Servico></procedimentos>
    </procedimentosExecutados></guiasSP_SADT>
</faturaSP_SADT>'''

tree = etree.fromstring(XML).getroottree()
ns = {'ptu': 'http://www.ans.gov.br/ptu/'}

print('ANTES:', tree.xpath('//ptu:cd_Excecao/text()', namespaces=ns))

engine = RuleEngine()
engine.load_all_rules(use_database=False)

# Verificar regra
regras = [r for r in engine.loaded_rules if 'EXCECAO_ZERO' in r.get('id', '')]
print(f'Regra EXCECAO_ZERO carregada: {len(regras) > 0}')
if regras:
    print(f"  ID: {regras[0].get('id')}")
    print(f"  Ativo: {regras[0].get('ativo')}")

modificado = engine.apply_rules_to_xml(tree, -1, 'teste.xml')
print('Modificado:', modificado)
print('DEPOIS:', tree.xpath('//ptu:cd_Excecao/text()', namespaces=ns))

if tree.xpath('//ptu:cd_Excecao/text()', namespaces=ns) == ['0']:
    print('\n✅ TESTE PASSOU - cd_Excecao foi corrigido para 0!')
else:
    print('\n❌ TESTE FALHOU - cd_Excecao deveria ser 0')
