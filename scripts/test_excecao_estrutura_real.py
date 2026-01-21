# -*- coding: utf-8 -*-
"""Teste da regra REGRA_REMOCAO_CD_EXCECAO_ZERO com estrutura correta"""
import sys
import os
import logging

logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lxml.etree as etree
from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

# XML de teste com estrutura REAL: cd_Excecao está FORA de procedimentosExecutados
XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<ptu:faturaSP_SADT xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
    <ptu:guiasSP_SADT>
        <ptu:dadosGuia>
            <ptu:nr_Ver_TISS>4.02.00</ptu:nr_Ver_TISS>
            <ptu:nr_LotePrestador>38976</ptu:nr_LotePrestador>
            <ptu:nr_Guias>
                <ptu:nr_GuiaTissPrestador>258490485</ptu:nr_GuiaTissPrestador>
            </ptu:nr_Guias>
            <ptu:id_Liminar>N</ptu:id_Liminar>
            <ptu:id_Continuado>S</ptu:id_Continuado>
            <ptu:id_Avisado>N</ptu:id_Avisado>
            <ptu:cd_Excecao>L</ptu:cd_Excecao>
            <ptu:id_GlosaTotal>N</ptu:id_GlosaTotal>
            <ptu:procedimentosExecutados>
                <ptu:dt_Execucao>20251226</ptu:dt_Execucao>
                <ptu:hr_Inicial>10:32:00</ptu:hr_Inicial>
                <ptu:hr_Final>10:32:00</ptu:hr_Final>
                <ptu:procedimentos>
                    <ptu:seq_item>1</ptu:seq_item>
                    <ptu:tp_Tabela>18</ptu:tp_Tabela>
                    <ptu:cd_Servico>60018909</ptu:cd_Servico>
                    <ptu:ds_Servico>REMOCAO EM AMBULANCIA SIMPLES ADULTO COM ENFERMAGEM</ptu:ds_Servico>
                    <ptu:qt_Cobrada>400.0000</ptu:qt_Cobrada>
                </ptu:procedimentos>
            </ptu:procedimentosExecutados>
        </ptu:dadosGuia>
    </ptu:guiasSP_SADT>
</ptu:faturaSP_SADT>'''

tree = etree.fromstring(XML).getroottree()
root = tree.getroot()

engine = RuleEngine()
engine.load_all_rules(use_database=False)

# Valor antes
cd_excecao_antes = root.xpath("//ptu:cd_Excecao/text()", namespaces=NAMESPACES)
print(f"cd_Excecao ANTES: {cd_excecao_antes}")

# Aplicar regras
modificado = engine.apply_rules_to_xml(tree, -1, 'teste_fatura.xml')
print(f"Modificado: {modificado}")

# Valor depois
cd_excecao_depois = root.xpath("//ptu:cd_Excecao/text()", namespaces=NAMESPACES)
print(f"cd_Excecao DEPOIS: {cd_excecao_depois}")

if cd_excecao_depois == ['0']:
    print("\n[OK] TESTE PASSOU - cd_Excecao foi corrigido para 0!")
else:
    print("\n[FALHOU] TESTE FALHOU - cd_Excecao deveria ser 0")
