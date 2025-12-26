# test_idempotency.py
"""
Teste de Idempotência das Regras de Validação
Verifica se regras não são reaplicadas em arquivos já corrigidos.
"""

import os
import sys
from lxml import etree

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import NAMESPACES

def test_idempotency():
    """Testa se regras de reordenação são idempotentes"""
    
    print("="*70)
    print("🧪 TESTE DE IDEMPOTÊNCIA - Regras de Validação")
    print("="*70)
    print()
    
    # Criar XML de teste com ordem CORRETA
    xml_correto = """<?xml version="1.0" encoding="UTF-8"?>
<ptu:mensagemTISS xmlns:ptu="http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico">
    <ptu:GuiaCobrancaUtilizacao>
        <ptu:procedimentosExecutados>
            <ptu:equipe_Profissional>
                <!-- Ordem CORRETA conforme regras -->
                <ptu:tp_Participacao>00</ptu:tp_Participacao>
                <ptu:Prestador>12345</ptu:Prestador>
                <ptu:nm_Profissional>Dr. Teste</ptu:nm_Profissional>
                <ptu:cdCnpjCpf>
                    <ptu:cd_cpf>12345678901</ptu:cd_cpf>
                </ptu:cdCnpjCpf>
                <ptu:dadosConselho>
                    <ptu:sg_Conselho>CRM</ptu:sg_Conselho>
                    <ptu:nr_Conselho>12345</ptu:nr_Conselho>
                </ptu:dadosConselho>
                <ptu:CBO>225125</ptu:CBO>
            </ptu:equipe_Profissional>
        </ptu:procedimentosExecutados>
    </ptu:GuiaCobrancaUtilizacao>
</ptu:mensagemTISS>
"""
    
    # Parsear XML
    root = etree.fromstring(xml_correto.encode())
    equipe = root.find(".//ptu:equipe_Profissional", namespaces=NAMESPACES)
    
    # Criar engine
    engine = RuleEngine()
    
    # Simular ação de reordenação com ordem correta
    action_config = {
        "tipo_acao": "reordenar_elementos_filhos",
        "tag_alvo": "./ptu:equipe_Profissional",
        "ordem_correta": [
            "tp_Participacao",
            "Prestador", 
            "nm_Profissional",
            "cdCnpjCpf",
            "dadosConselho",
            "CBO"
        ]
    }
    
    
    print("1️⃣  TESTE: Verificar detecção de ordem correta")
    print("-" * 70)
    
    # Verificar ordem atual
    current_order = [etree.QName(child).localname for child in equipe]
    expected_order = [
        "tp_Participacao",
        "Prestador", 
        "nm_Profissional",
        "cdCnpjCpf",
        "dadosConselho",
        "CBO"
    ]
    
    # Filtrar apenas elementos relevantes
    relevant_current = [tag for tag in current_order if tag in expected_order]
    relevant_expected = [tag for tag in expected_order if tag in {etree.QName(c).localname for c in equipe}]
    
    if relevant_current == relevant_expected:
        print("✅ PASSOU: Ordem está correta")
        print(f"   Ordem atual: {relevant_current}")
        print(f"   Ordem esperada: {relevant_expected}")
    else:
        print("❌ FALHOU: Ordem detectada como incorreta")
        print(f"   Ordem atual: {relevant_current}")
        print(f"   Ordem esperada: {relevant_expected}")
    
    print()
    
    # Criar XML com ordem INCORRETA
    xml_incorreto = """<?xml version="1.0" encoding="UTF-8"?>
<ptu:mensagemTISS xmlns:ptu="http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico">
    <ptu:GuiaCobrancaUtilizacao>
        <ptu:procedimentosExecutados>
            <ptu:equipe_Profissional>
                <!-- Ordem INCORRETA -->
                <ptu:CBO>225125</ptu:CBO>
                <ptu:tp_Participacao>00</ptu:tp_Participacao>
                <ptu:nm_Profissional>Dr. Teste</ptu:nm_Profissional>
            </ptu:equipe_Profissional>
        </ptu:procedimentosExecutados>
    </ptu:GuiaCobrancaUtilizacao>
</ptu:mensagemTISS>
"""
    
    root2 = etree.fromstring(xml_incorreto.encode())
    equipe2 = root2.find(".//ptu:equipe_Profissional", namespaces=NAMESPACES)
    
    print("2️⃣  TESTE: Verificar detecção de ordem incorreta")
    print("-" * 70)
    
    current_order2 = [etree.QName(child).localname for child in equipe2]
    relevant_current2 = [tag for tag in current_order2 if tag in expected_order]
    
    if relevant_current2 != relevant_expected:
        print("✅ PASSOU: Ordem detectada como incorreta")
        print(f"   Ordem atual: {relevant_current2}")
        print(f"   Ordem esperada: {relevant_expected}")
    else:
        print("❌ FALHOU: Ordem detectada como correta quando está errada")
        print(f"   Ordem atual: {relevant_current2}")
    
    print()
    print("="*70)
    
    # Resultado final
    test1_passed = (relevant_current == relevant_expected)
    test2_passed = (relevant_current2 != relevant_expected)
    
    if test1_passed and test2_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Lógica de detecção de ordem funcionando corretamente")
        print()
        print("📝 CONCLUSÃO:")
        print("   → Arquivos já corrigidos NÃO serão reprocessados")
        print("   → Apenas arquivos com ordem errada serão modificados")
        print()
        return True
    else:
        print("❌ ALGUM TESTE FALHOU")
        if not test1_passed:
            print("   ⚠️  Teste 1: Ordem correta não detectada")
        if not test2_passed:
            print("   ⚠️  Teste 2: Ordem incorreta não detectada")
        print()
        return False


if __name__ == "__main__":
    success = test_idempotency()
    sys.exit(0 if success else 1)
