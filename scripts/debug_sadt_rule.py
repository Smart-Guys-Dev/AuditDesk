# debug_sadt_rule.py
"""
Script de debug para a regra de tipo de atendimento SADT
"""

import os
import sys
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

# XML REAL do usuário
xml_teste = """<?xml version='1.0' encoding='ISO-8859-1'?>
<ptu:GuiaCobrancaUtilizacao xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<ptu:arquivoCobrancaUtilizacao>
<ptu:Tipoguia>
<ptu:guiaSADT>
<ptu:dadosAtendimento>
<ptu:tp_Atendimento>04</ptu:tp_Atendimento>
<ptu:tp_IndAcidente>9</ptu:tp_IndAcidente>
<ptu:tp_Consulta>1</ptu:tp_Consulta>
</ptu:dadosAtendimento>
<ptu:dadosGuia>
<ptu:procedimentosExecutados>
<ptu:dt_Execucao>20251209</ptu:dt_Execucao>
<ptu:procedimentos>
<ptu:seq_item>1</ptu:seq_item>
<ptu:cd_Servico>40901300</ptu:cd_Servico>
<ptu:ds_Servico>US TRANSVAGINAL</ptu:ds_Servico>
</ptu:procedimentos>
</ptu:procedimentosExecutados>
<ptu:procedimentosExecutados>
<ptu:dt_Execucao>20251209</ptu:dt_Execucao>
<ptu:procedimentos>
<ptu:seq_item>2</ptu:seq_item>
<ptu:cd_Servico>40901122</ptu:cd_Servico>
<ptu:ds_Servico>US ABDOME TOTAL</ptu:ds_Servico>
</ptu:procedimentos>
</ptu:procedimentosExecutados>
</ptu:dadosGuia>
</ptu:guiaSADT>
</ptu:Tipoguia>
</ptu:arquivoCobrancaUtilizacao>
</ptu:GuiaCobrancaUtilizacao>
"""

print("="*80)
print("🔍 DEBUG: Regra de Tipo de Atendimento SADT")
print("="*80)
print()

# Carregar engine
engine = RuleEngine()
engine.load_all_rules()

# Buscar a regra
regra = None
for r in engine.loaded_rules:
    if r.get("id") == "REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23":
        regra = r
        break

if not regra:
    print("❌ REGRA NÃO ENCONTRADA NAS REGRAS CARREGADAS!")
    sys.exit(1)

print("✅ Regra encontrada:")
print(f"   ID: {regra['id']}")
print(f"   Ativa: {regra['ativo']}")
print()

# Parsear XML
root = etree.fromstring(xml_teste.encode('ISO-8859-1'))

# Detectar namespace dinamicamente
ns = None
if root.nsmap:
    # Pegar o namespace padrão ou 'ptu'
    ns = root.nsmap.get('ptu') or root.nsmap.get(None)

# Criar NAMESPACES dinâmico
if ns:
    NS = {'ptu': ns}
    print(f"✓ Namespace detectado: {ns}")
else:
    NS = NAMESPACES
    print(f"✓ Usando namespace padrão")

print()

# Buscar guia SADT
guia = root.find(".//ptu:guiaSADT", namespaces=NS)

if not guia:
    print("❌ Guia SADT não encontrada!")
    sys.exit(1)

print("✅ Guia SADT encontrada")
print()

# Verificar condições manualmente
condicoes = regra.get("condicoes", {})
tipo_elemento = condicoes.get("tipo_elemento")
print(f"📋 Tipo de elemento esperado: {tipo_elemento}")
print()

# Testar condições
print("🔍 Testando condições:")
print("-" * 80)

# Condição 1: tp_Atendimento = 04
tp_atend_node = guia.find(".//ptu:tp_Atendimento", namespaces=NS)
if tp_atend_node is not None:
    valor = tp_atend_node.text
    print(f"✓ tp_Atendimento encontrado: '{valor}'")
    print(f"  → É '04'? {valor == '04'}")
else:
    print("✗ tp_Atendimento NÃO encontrado!")

print()

# Condição 2: cd_Servico não começa com 10
cd_servico_nodes = guia.findall(".//ptu:cd_Servico", namespaces=NS)
print(f"✓ Encontrados {len(cd_servico_nodes)} cd_Servico")
for i, node in enumerate(cd_servico_nodes):
    valor = node.text if node.text else ""
    comeca_com_10 = valor.startswith("10")
    nao_comeca_com_10 = not comeca_com_10
    print(f"  [{i+1}] cd_Servico = '{valor}'")
    print(f"      → Começa com '10'? {comeca_com_10}")
    print(f"      → NÃO começa com '10'? {nao_comeca_com_10} ✓" if nao_comeca_com_10 else f"      → NÃO começa com '10'? {nao_comeca_com_10}")

print()
print("-" * 80)

# Avaliar condição usando engine
print("🔧 Avaliando condição usando RuleEngine:")
resultado = engine._evaluate_condition(guia, condicoes)
print(f"   Resultado: {resultado}")
print()

if resultado:
    print("✅ CONDIÇÃO PASSOU! Regra deveria ser aplicada.")
    print()
    print("⚙️  Aplicando ação...")
    modificado = engine._apply_action(guia, regra.get("acao", {}))
    print(f"   Modificado: {modificado}")
    
    # Verificar resultado
    tp_atend_depois = guia.find(".//ptu:tp_Atendimento", namespaces=NS)
    if tp_atend_depois is not None:
        print(f"   tp_Atendimento DEPOIS: '{tp_atend_depois.text}'")
        if tp_atend_depois.text == "23":
            print("   🎉 SUCESSO! Alterado para '23'")
        else:
            print(f"   ❌ FALHOU! Ainda é '{tp_atend_depois.text}'")
else:
    print("❌ CONDIÇÃO FALHOU! Regra NÃO seria aplicada.")
    print()
    print("🐛 Debug das sub-condições:")
    sub_conds = condicoes.get("condicao_multipla", {}).get("sub_condicoes", [])
    for i, sc in enumerate(sub_conds):
        res = engine._evaluate_condition(guia, sc)
        print(f"   [{i+1}] {sc.get('condicao_tag_valor', {}).get('xpath', 'N/A')}: {res}")

print()
print("="*80)
