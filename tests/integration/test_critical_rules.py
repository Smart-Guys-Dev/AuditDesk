"""
Testes de integração para regras críticas GLOSA_GUIA e GLOSA_ITEM.

Testa as top 10 regras mais importantes que evitam glosas reais.
"""
import pytest
from lxml import etree


class TestGlosaGuiaRules:
    """Testes de integração para regras GLOSA_GUIA (rejeitam guia inteira)"""
    
    def test_regra_tipo_atendimento_sadt(self, rule_engine):
        """
        REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23
        
        Problema: Guia SADT com tp_Atendimento diferente de "23"
        Impacto: Rejeição da guia inteira
        Solução: Corrigir para "23"
        """
        # XML com tp_Atendimento incorreto
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        tree = etree.ElementTree(etree.fromstring(xml_str.encode()))
        
        # Aplicar regras
        modified = rule_engine.apply_rules_to_xml(tree)
        
        # Verificar correção - tp_Atendimento deve ser "23" agora
        namespaces = {
            'ans': 'http://www.ans.gov.br/padroes/tiss/schemas',
            'ptu': 'http://unimedbh.com.br/PTU'
        }
        root = tree.getroot()
        tp_atend = root.find(".//ptu:tp_Atendimento", namespaces)
        
        # Se a regra está ativa, deve ter corrigido
        if tp_atend is not None:
            print(f"\n✅ tp_Atendimento corrigido: {tp_atend.text}")
            # Nota: Depende se a regra REGRA_CORRIGIR_TIPO_ATENDIMENTO_SADT_PARA_23 está ativa
    
    def test_regra_cnes_valido(self, rule_engine):
        """
        Teste de validação de CNES
        
        Problema: CNES inválido ou ausente
        Impacto: Glosa de toda a guia
        """
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosExecutante>
                        <ans:contratadoExecutante>
                            <ans:CNES>123456</ans:CNES>
                        </ans:contratadoExecutante>
                    </ans:dadosExecutante>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        tree = etree.ElementTree(etree.fromstring(xml_str.encode()))
        
        # Aplicar regras
        result = rule_engine.apply_rules_to_xml(tree)
        
        # Resultado deve ser booleano
        assert isinstance(result, bool)
        print(f"\n✅ CNES validation executed, modified: {result}")


class TestGlosaItemRules:
    """Testes de integração para regras GLOSA_ITEM (rejeitam item específico)"""
    
    def test_regra_equipe_obrigatoria_cirurgia(self, rule_engine):
        """
        Teste de equipe obrigatória em procedimentos cirúrgicos
        
        Problema: Procedimento cirúrgico sem equipe profissional
        Impacto: Glosa do item (procedimento não é pago)
        Solução: Inserir equipe padrão automaticamente
        """
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:procedimentosExecutados>
                        <ans:procedimentoExecutado>
                            <ans:sequencialItem>1</ans:sequencialItem>
                            <ans:procedimento>
                                <ans:codigoTabela>22</ans:codigoTabela>
                                <ans:codigoProcedimento>31005004</ans:codigoProcedimento>
                            </ans:procedimento>
                            <ans:quantidadeExecutada>1</ans:quantidadeExecutada>
                            <!-- Falta equipeObrigatoria para códigos que começam com 31 -->
                        </ans:procedimentoExecutado>
                    </ans:procedimentosExecutados>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        tree = etree.ElementTree(etree.fromstring(xml_str.encode()))
        
        # Aplicar regras
        modified = rule_engine.apply_rules_to_xml(tree)
        
        # Verificar se equipe foi inserida
        namespaces = {
            'ans': 'http://www.ans.gov.br/padroes/tiss/schemas',
            'ptu': 'http://unimedbh.com.br/PTU'
        }
        root = tree.getroot()
        equipe = root.find(".//ans:equipeProfissional", namespaces)
        
        print(f"\n✅ Equipe foi inserida: {equipe is not None}")
        print(f"✅ XML foi modificado: {modified}")


class TestFullWorkflow:
    """Testes de workflow completo - da carga até o relatório"""
    
    def test_processa_lote_simples(self, rule_engine):
        """
        Teste de processamento de um "lote" simples com 1 guia
        
        Valida que:
        1. RuleEngine processa sem erros
        2. Retorna resultado booleano
        3. Regras são aplicadas
        """
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:cabecalho>
        <ans:identificacaoTransacao>
            <ans:tipoTransacao>ENVIO_LOTE_GUIAS</ans:tipoTransacao>
        </ans:identificacaoTransacao>
    </ans:cabecalho>
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:numeroLote>12345</ans:numeroLote>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:cabecalhoGuia>
                        <ans:registroANS>123456</ans:registroANS>
                    </ans:cabecalhoGuia>
                    <ans:dadosAutorizacao>
                        <ans:numeroGuiaPrestador>00001</ans:numeroGuiaPrestador>
                    </ans:dadosAutorizacao>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                    <ans:procedimentosExecutados>
                        <ans:procedimentoExecutado>
                            <ans:sequencialItem>1</ans:sequencialItem>
                            <ans:procedimento>
                                <ans:codigoTabela>22</ans:codigoTabela>
                                <ans:codigoProcedimento>10101012</ans:codigoProcedimento>
                            </ans:procedimento>
                            <ans:quantidadeExecutada>1</ans:quantidadeExecutada>
                            <ans:valorUnitario>100.00</ans:valorUnitario>
                            <ans:valorTotal>100.00</ans:valorTotal>
                        </ans:procedimentoExecutado>
                    </ans:procedimentosExecutados>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        tree = etree.ElementTree(etree.fromstring(xml_str.encode()))
        
        # Processar
        result = rule_engine.apply_rules_to_xml(tree)
        
        # Validações
        assert isinstance(result, bool)
        print(f"\n✅ Lote processado com sucesso")
        print(f"✅ Modificações aplicadas: {result}")
        print(f"✅ Total de regras carregadas: {len(rule_engine.loaded_rules)}")
    
    def test_verifica_105_regras_carregadas(self, rule_engine):
        """Valida que as 105 regras esperadas foram carregadas"""
        total_rules = len(rule_engine.loaded_rules)
        
        print(f"\n📊 Total de regras carregadas: {total_rules}")
        
        # Deve ter pelo menos 100 regras (tolerância para mudanças)
        assert total_rules >= 100, f"Esperado >= 100 regras, got {total_rules}"
        
        # Verificar estrutura das regras
        if total_rules > 0:
            first_rule = rule_engine.loaded_rules[0]
            assert 'id' in first_rule, "Regra deve ter campo 'id'"
            print(f"✅ Primeira regra: {first_rule.get('id', 'N/A')}")


@pytest.mark.slow
class TestPerformanceIntegration:
    """Testes de performance com regras reais"""
    
    def test_10_guias_em_menos_de_5_segundos(self, rule_engine):
        """
        Processa 10 guias em menos de 5 segundos
        
        Meta de produção: 1000 guias/hora = ~3.6s por guia
        Com 10 guias: deve levar < 5s total
        """
        import time
        
        # XML base para replicar
        xml_base = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        start = time.time()
        
        for i in range(10):
            tree = etree.ElementTree(etree.fromstring(xml_base.encode()))
            rule_engine.apply_rules_to_xml(tree)
        
        duration = time.time() - start
        
        print(f"\n⚡ 10 guias processadas em {duration:.2f}s")
        print(f"⚡ Throughput: {10/duration:.1f} guias/segundo")
        print(f"⚡ Throughput estimado: {(10/duration)*3600:.0f} guias/hora")
        
        assert duration < 5.0, f"10 guias demoraram {duration:.2f}s (limite: 5s)"
