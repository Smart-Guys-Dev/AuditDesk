# test_regra_tipo_atendimento.py
"""
Teste específico para a regra REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23
Verifica se a regra está funcionando corretamente.
"""

import os
import sys
from lxml import etree

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

def test_regra_tipo_atendimento():
    """Testa a regra de correção de tipo de atendimento SADT"""
    
    print("="*80)
    print("🧪 TESTE: REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23")
    print("="*80)
    print()
    
    # Criar XML de teste com tp_Atendimento = 04 e sem código de consulta
    xml_teste = """<?xml version="1.0" encoding="UTF-8"?>
<ptu:mensagemTISS xmlns:ptu="http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico">
    <ptu:guiaSADT-SP>
        <ptu:tp_Atendimento>04</ptu:tp_Atendimento>
        <ptu:procedimentosExecutados>
            <ptu:procedimentos>
                <ptu:cd_Servico>20104162</ptu:cd_Servico>
            </ptu:procedimentos>
        </ptu:procedimentosExecutados>
    </ptu:guiaSADT-SP>
</ptu:mensagemTISS>
"""
    
    print("📋 **XML de Teste:**")
    print("   - tp_Atendimento: 04")
    print("   - cd_Servico: 20104162 (não começa com '10', não é consulta)")
    print()
    
    # Parsear XML
    root = etree.fromstring(xml_teste.encode())
    # Buscar qualquer tipo de guia SADT
    guia = root.find(".//ptu:guiaSADT-SP", namespaces=NAMESPACES)
    if guia is None:
        guia = root.find(".//ptu:guiaSP-SADT", namespaces=NAMESPACES)  
    if guia is None:
        guia = root.find(".//ptu:guiaSadt", namespaces=NAMESPACES)
    
    if guia is None:
        print("❌ ERRO: Guia SADT não encontrada no XML de teste")
        return False
    
    # Carregar engine e regras
    print("🔧 Carregando RuleEngine e regras...")
    engine = RuleEngine()
    success = engine.load_all_rules()
    
    if not success:
        print("❌ ERRO: Falha ao carregar regras")
        return False
    
    print(f"✅ {len(engine.loaded_rules)} regras carregadas")
    print()
    
    # Buscar a regra específica
    regra_encontrada = None
    for regra in engine.loaded_rules:
        if regra.get("id") == "REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23":
            regra_encontrada = regra
            break
    
    if not regra_encontrada:
        print("❌ REGRA NÃO ENCONTRADA!")
        print("   A regra 'REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23' não está nas regras carregadas")
        return False
    
    print("✅ REGRA ENCONTRADA!")
    print(f"   ID: {regra_encontrada.get('id')}")
    print(f"   Descrição: {regra_encontrada.get('descricao')}")
    print(f"   Ativa: {regra_encontrada.get('ativo')}")
    print()
    
    # Verificar valor ANTES
    tp_atendimento_antes = guia.find("./ptu:tp_Atendimento", namespaces=NAMESPACES)
    valor_antes = tp_atendimento_antes.text if tp_atendimento_antes is not None else "N/A"
    
    print("🔍 **ANTES da aplicação:**")
    print(f"   tp_Atendimento = '{valor_antes}'")
    print()
    
    # Aplicar regra
    print("⚙️  Aplicando regra...")
    modificado = engine.apply_single_rule_to_element(guia, regra_encontrada)
    
    # Verificar valor DEPOIS
    tp_atendimento_depois = guia.find("./ptu:tp_Atendimento", namespaces=NAMESPACES)
    valor_depois = tp_atendimento_depois.text if tp_atendimento_depois is not None else "N/A"
    
    print()
    print("🔍 **DEPOIS da aplicação:**")
    print(f"   tp_Atendimento = '{valor_depois}'")
    print(f"   Modificado: {modificado}")
    print()
    
    # Verificar resultado
    print("="*80)
    if modificado and valor_depois == "23":
        print("🎉 TESTE PASSOU!")
        print("✅ Regra funcionou corretamente:")
        print(f"   - Alterou tp_Atendimento de '{valor_antes}' para '{valor_depois}'")
        print()
        return True
    elif not modificado and valor_antes == "23":
        print("✅ TESTE PASSOU!")
        print("   Regra detectou que já estava correto (idempotência)")
        print()
        return True
    else:
        print("❌ TESTE FALHOU!")
        print(f"   Esperado: tp_Atendimento = '23'")
        print(f"   Obtido: tp_Atendimento = '{valor_depois}'")
        print(f"   Modificado: {modificado}")
        print()
        return False


if __name__ == "__main__":
    success = test_regra_tipo_atendimento()
    sys.exit(0 if success else 1)
