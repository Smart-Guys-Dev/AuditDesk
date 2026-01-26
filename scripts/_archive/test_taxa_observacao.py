# -*- coding: utf-8 -*-
"""
Teste para verificar a regra de correção de horários em taxas de observação.
"""
import lxml.etree as etree
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.business.rules.rule_engine import RuleEngine

# XML de teste baseado no exemplo real
XML_TESTE = """<?xml version="1.0" encoding="UTF-8"?>
<ptu:FaturaCobrancaA500 xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
<ptu:guiaSADT>
    <ptu:dadosGuia>
        <ptu:procedimentosExecutados>
            <ptu:hr_Inicial>10:53:31</ptu:hr_Inicial>
            <ptu:hr_Final>14:28:00</ptu:hr_Final>
            <ptu:procedimentos>
                <ptu:cd_Servico>1900227633</ptu:cd_Servico>
                <ptu:ds_Servico>AGULHA HIPODERMICA</ptu:ds_Servico>
            </ptu:procedimentos>
        </ptu:procedimentosExecutados>
        <ptu:procedimentosExecutados>
            <ptu:hr_Inicial>00:00:01</ptu:hr_Inicial>
            <ptu:hr_Final>00:00:01</ptu:hr_Final>
            <ptu:procedimentos>
                <ptu:cd_Servico>60033681</ptu:cd_Servico>
                <ptu:ds_Servico>TAXA DE SALA DE OBSERVACAO ATE 6 HORAS</ptu:ds_Servico>
            </ptu:procedimentos>
        </ptu:procedimentosExecutados>
    </ptu:dadosGuia>
</ptu:guiaSADT>
</ptu:FaturaCobrancaA500>
"""

def test_regra_taxa_observacao():
    """Testa se a regra corrige os horários da taxa de observação."""
    print("=" * 60)
    print("TESTE: Regra de Taxa de Observação")
    print("=" * 60)
    
    # Carregar motor de regras
    engine = RuleEngine()
    engine.load_all_rules(use_database=False)
    
    # Verificar se a regra foi carregada
    regra_encontrada = any(r.get("id") == "REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS" for r in engine.loaded_rules)
    print(f"\n[OK] Regra carregada: {regra_encontrada}")
    
    if not regra_encontrada:
        print("[ERRO] Regra nao encontrada!")
        return False
    
    # Parsear XML de teste
    tree = etree.fromstring(XML_TESTE.encode()).getroottree()
    
    # Mostrar valores ANTES
    ns = {"ptu": "http://ptu.unimed.coop.br/schemas/V3_0"}
    procs = tree.xpath("//ptu:procedimentosExecutados", namespaces=ns)
    
    print("\n--- ANTES ---")
    for i, proc in enumerate(procs):
        hr_ini = proc.find("ptu:hr_Inicial", ns).text
        hr_fim = proc.find("ptu:hr_Final", ns).text
        cd_serv = proc.find("ptu:procedimentos/ptu:cd_Servico", ns).text
        print(f"Item {i+1}: cd_Servico={cd_serv}, hr_Inicial={hr_ini}, hr_Final={hr_fim}")
    
    # Aplicar regras
    modified = engine.apply_rules_to_xml(tree, -1, "teste_taxa_obs.xml")
    
    print(f"\n[OK] Regras aplicadas. Modificado: {modified}")
    
    # Mostrar valores DEPOIS
    print("\n--- DEPOIS ---")
    procs = tree.xpath("//ptu:procedimentosExecutados", namespaces=ns)
    for i, proc in enumerate(procs):
        hr_ini = proc.find("ptu:hr_Inicial", ns).text
        hr_fim = proc.find("ptu:hr_Final", ns).text
        cd_serv = proc.find("ptu:procedimentos/ptu:cd_Servico", ns).text
        print(f"Item {i+1}: cd_Servico={cd_serv}, hr_Inicial={hr_ini}, hr_Final={hr_fim}")
    
    # Verificar se a correção foi aplicada
    taxa_obs = procs[1]  # Segundo item é a taxa de observação
    hr_ini_corrigido = taxa_obs.find("ptu:hr_Inicial", ns).text
    hr_fim_corrigido = taxa_obs.find("ptu:hr_Final", ns).text
    
    sucesso = (hr_ini_corrigido == "10:53:31" and hr_fim_corrigido == "14:28:00")
    
    print("\n" + "=" * 60)
    if sucesso:
        print("[PASSOU] TESTE PASSOU: Horarios corrigidos corretamente!")
    else:
        print("[FALHOU] TESTE FALHOU: Horarios nao foram corrigidos!")
    print("=" * 60)
    
    return sucesso


if __name__ == "__main__":
    success = test_regra_taxa_observacao()
    sys.exit(0 if success else 1)
