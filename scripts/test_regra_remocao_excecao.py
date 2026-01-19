# -*- coding: utf-8 -*-
"""
Script de teste para a regra REGRA_REMOCAO_CD_EXCECAO_ZERO
Verifica se a regra corrige cd_Excecao para '0' em códigos de remoção.
"""

import os
import sys

# Adicionar o diretório raiz ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import lxml.etree as etree
from src.business.rules.rule_engine import RuleEngine

# XML de teste com código de remoção e cd_Excecao = 'L' (deve ser corrigido para '0')
XML_TESTE = """<?xml version="1.0" encoding="UTF-8"?>
<faturaSP_SADT xmlns="http://www.ans.gov.br/ptu/" xmlns:ptu="http://www.ans.gov.br/ptu/">
    <guiasSP_SADT>
        <nr_Guia>12345</nr_Guia>
        <nr_Inscricao>123456789</nr_Inscricao>
        <procedimentosExecutados>
            <dt_Execucao>20251228</dt_Execucao>
            <hr_Inicial>00:00:00</hr_Inicial>
            <hr_Final>00:00:00</hr_Final>
            <id_Avisado>N</id_Avisado>
            <cd_Excecao>L</cd_Excecao>
            <id_GlosaTotal>N</id_GlosaTotal>
            <procedimentos>
                <seq_item>1</seq_item>
                <id_itemUnico>251200510000000000000218000</id_itemUnico>
                <tp_Tabela>18</tp_Tabela>
                <cd_Servico>60018909</cd_Servico>
                <ds_Servico>REMOCAO EM AMBULANCIA SIMPLES ADULTO COM ENFERMAGEM PARA ATENDIMENTO DE URGENC</ds_Servico>
                <qt_Cobrada>1.0000</qt_Cobrada>
            </procedimentos>
        </procedimentosExecutados>
    </guiasSP_SADT>
</faturaSP_SADT>
"""

# XML de teste com código de remoção e cd_Excecao = '0' (NÃO deve ser alterado)
XML_TESTE_JA_CORRETO = """<?xml version="1.0" encoding="UTF-8"?>
<faturaSP_SADT xmlns="http://www.ans.gov.br/ptu/" xmlns:ptu="http://www.ans.gov.br/ptu/">
    <guiasSP_SADT>
        <nr_Guia>12346</nr_Guia>
        <nr_Inscricao>123456789</nr_Inscricao>
        <procedimentosExecutados>
            <dt_Execucao>20251228</dt_Execucao>
            <cd_Excecao>0</cd_Excecao>
            <procedimentos>
                <cd_Servico>60018909</cd_Servico>
                <ds_Servico>REMOCAO EM AMBULANCIA</ds_Servico>
            </procedimentos>
        </procedimentosExecutados>
    </guiasSP_SADT>
</faturaSP_SADT>
"""

# XML de teste com código NÃO é remoção (NÃO deve ser alterado)
XML_TESTE_NAO_REMOCAO = """<?xml version="1.0" encoding="UTF-8"?>
<faturaSP_SADT xmlns="http://www.ans.gov.br/ptu/" xmlns:ptu="http://www.ans.gov.br/ptu/">
    <guiasSP_SADT>
        <nr_Guia>12347</nr_Guia>
        <nr_Inscricao>123456789</nr_Inscricao>
        <procedimentosExecutados>
            <dt_Execucao>20251228</dt_Execucao>
            <cd_Excecao>L</cd_Excecao>
            <procedimentos>
                <cd_Servico>10101012</cd_Servico>
                <ds_Servico>CONSULTA MEDICA</ds_Servico>
            </procedimentos>
        </procedimentosExecutados>
    </guiasSP_SADT>
</faturaSP_SADT>
"""

def get_cd_excecao(xml_tree):
    """Extrai o valor de cd_Excecao do XML."""
    ns = {"ptu": "http://www.ans.gov.br/ptu/"}
    nodes = xml_tree.xpath("//ptu:cd_Excecao", namespaces=ns)
    return nodes[0].text if nodes else None

def run_test(nome, xml_string, esperado_mudanca, valor_esperado=None):
    """Executa um teste e retorna True se passou."""
    print(f"\n{'='*60}")
    print(f"TESTE: {nome}")
    print(f"{'='*60}")
    
    # Parse XML
    xml_tree = etree.fromstring(xml_string.encode('utf-8')).getroottree()
    valor_antes = get_cd_excecao(xml_tree)
    print(f"  cd_Excecao ANTES: {valor_antes}")
    
    # Carregar engine e aplicar regras
    engine = RuleEngine()
    engine.load_all_rules(use_database=False)  # Usar JSON para pegar a nova regra
    
    # Aplicar regras
    modificado = engine.apply_rules_to_xml(xml_tree, execution_id=-1, file_name="teste.xml")
    
    valor_depois = get_cd_excecao(xml_tree)
    print(f"  cd_Excecao DEPOIS: {valor_depois}")
    print(f"  Modificado: {modificado}")
    
    # Verificar resultado
    if esperado_mudanca:
        if modificado and valor_depois == valor_esperado:
            print(f"  ✅ PASSOU - Valor corrigido para '{valor_esperado}'")
            return True
        else:
            print(f"  ❌ FALHOU - Esperava mudar para '{valor_esperado}', obteve '{valor_depois}'")
            return False
    else:
        if not modificado or valor_antes == valor_depois:
            print(f"  ✅ PASSOU - Valor mantido (sem mudança esperada)")
            return True
        else:
            print(f"  ❌ FALHOU - Não deveria ter mudado, mas mudou de '{valor_antes}' para '{valor_depois}'")
            return False

def main():
    print("\n" + "="*60)
    print("TESTE DA REGRA REGRA_REMOCAO_CD_EXCECAO_ZERO")
    print("="*60)
    
    resultados = []
    
    # Teste 1: Remoção com cd_Excecao='L' -> deve mudar para '0'
    resultados.append(run_test(
        "Remoção com cd_Excecao='L' (deve corrigir para '0')",
        XML_TESTE,
        esperado_mudanca=True,
        valor_esperado="0"
    ))
    
    # Teste 2: Remoção com cd_Excecao='0' -> não deve mudar
    resultados.append(run_test(
        "Remoção com cd_Excecao='0' (já correto, não deve mudar)",
        XML_TESTE_JA_CORRETO,
        esperado_mudanca=False
    ))
    
    # Teste 3: Código não é remoção -> não deve mudar
    resultados.append(run_test(
        "Código não é remoção (não deve mudar)",
        XML_TESTE_NAO_REMOCAO,
        esperado_mudanca=False
    ))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    total = len(resultados)
    passou = sum(resultados)
    print(f"  Total: {total}")
    print(f"  Passou: {passou}")
    print(f"  Falhou: {total - passou}")
    
    if all(resultados):
        print("\n✅ TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
