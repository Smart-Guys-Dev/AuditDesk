# -*- coding: utf-8 -*-
"""Debug da regra REGRA_REMOCAO_CD_EXCECAO_ZERO"""
import sys
import os
import logging

# Suprimir logs
logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lxml.etree as etree
from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

print(f"Namespace do projeto: {NAMESPACES}")

# XML de teste com namespace CORRETO do projeto
XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<ptu:faturaSP_SADT xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
    <ptu:guiasSP_SADT>
        <ptu:procedimentosExecutados>
            <ptu:cd_Excecao>L</ptu:cd_Excecao>
            <ptu:procedimentos>
                <ptu:cd_Servico>60018909</ptu:cd_Servico>
            </ptu:procedimentos>
        </ptu:procedimentosExecutados>
    </ptu:guiasSP_SADT>
</ptu:faturaSP_SADT>'''

tree = etree.fromstring(XML).getroottree()
root = tree.getroot()

engine = RuleEngine()
engine.load_all_rules(use_database=False)

# Encontrar a regra
regra = [r for r in engine.loaded_rules if 'EXCECAO_ZERO' in r.get('id', '')][0]
print("Regra:", regra.get('id'))
print()

# Encontrar elementos usando o mesmo método que o engine usa
procs = engine.xml_reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print(f"ProcedimentosExecutados encontrados: {len(procs)}")

if procs:
    elem = procs[0]

    # Verificar cd_Servico
    cd_servico = engine.xml_reader.find_elements_by_xpath(elem, "./ptu:procedimentos/ptu:cd_Servico")
    print(f"cd_Servico: {cd_servico[0].text if cd_servico else 'NAO ENCONTRADO'}")
    
    # Verificar cd_Excecao
    cd_excecao = engine.xml_reader.find_elements_by_xpath(elem, "./ptu:cd_Excecao")
    print(f"cd_Excecao (antes): {cd_excecao[0].text if cd_excecao else 'NAO ENCONTRADO'}")
    
    # Avaliar a condição
    condicoes = regra.get('condicoes', {})
    resultado = engine._evaluate_condition(elem, condicoes)
    print(f"\nResultado da avaliacao da condicao: {resultado}")
    
    if not resultado:
        # Testar cada sub-condição individualmente
        print("\n--- Testando sub-condicoes individualmente ---")
        sub_condicoes = condicoes.get('condicao_multipla', {}).get('sub_condicoes', [])
        for i, sc in enumerate(sub_condicoes):
            resultado_sc = engine._evaluate_condition(elem, sc)
            print(f"Sub-condicao {i+1}: {resultado_sc}")
            if 'condicao_tag_valor' in sc:
                ctv = sc['condicao_tag_valor']
                print(f"  xpath: {ctv.get('xpath')}")
                print(f"  tipo_comparacao: {ctv.get('tipo_comparacao')}")
                if 'valor_permitido' in ctv:
                    print(f"  valor_permitido: ...{len(ctv['valor_permitido'])} codigos...")
                if 'valor' in ctv:
                    print(f"  valor: {ctv.get('valor')}")
else:
    print("ERRO: Nenhum procedimentosExecutados encontrado!")

# Agora aplicar as regras
print("\n--- Aplicando regras ---")
modificado = engine.apply_rules_to_xml(tree, -1, 'teste.xml')
print(f"Modificado: {modificado}")

cd_excecao_depois = engine.xml_reader.find_elements_by_xpath(root, ".//ptu:cd_Excecao")
print(f"cd_Excecao (depois): {cd_excecao_depois[0].text if cd_excecao_depois else 'NAO ENCONTRADO'}")

if cd_excecao_depois and cd_excecao_depois[0].text == '0':
    print("\n[OK] TESTE PASSOU - cd_Excecao foi corrigido para 0!")
else:
    print("\n[FALHOU] TESTE FALHOU - cd_Excecao deveria ser 0")
