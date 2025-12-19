"""
Testes unitários para RuleEngine.

Testa todas as funcionalidades core do motor de regras:
- _evaluate_condition: todos os tipos de comparação
- _execute_action: todas as ações
- Idempotência das regras
"""
import pytest
from lxml import etree


class TestEvaluateCondition:
    """Testes para _evaluate_condition"""
    
    def test_igual_true(self, rule_engine, create_element):
        """Testa comparação 'igual' quando valores são iguais"""
        condition = {
            "campo_xml": "tp_Atendimento",
            "tipo_comparacao": "igual",
            "valor_esperado": "23"
        }
        element = create_element("tp_Atendimento", "23")
        
        # NAMESPACES definido em conftest
        from conftest import NAMESPACES
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_igual_false(self, rule_engine):
        """Testa comparação 'igual' quando valores são diferentes"""
        condition = {
            "campo_xml": "tp_Atendimento",
            "tipo_comparacao": "igual",
            "valor_esperado": "23"
        }
        element = create_element("tp_Atendimento", "05")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == False
    
    def test_diferente_true(self, rule_engine):
        """Testa comparação 'diferente' quando valores são diferentes"""
        condition = {
            "campo_xml": "tp_Atendimento",
            "tipo_comparacao": "diferente",
            "valor_esperado": "23"
        }
        element = create_element("tp_Atendimento", "05")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_contém_true(self, rule_engine):
        """Testa comparação 'contem' quando valor contém substring"""
        condition = {
            "campo_xml": "cd_Procedimento",
            "tipo_comparacao": "contem",
            "valor_esperado": "31"
        }
        element = create_element("cd_Procedimento", "31005004")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_nao_contem_false(self, rule_engine):
        """Testa comparação 'nao_contem' quando valor contém substring"""
        condition = {
            "campo_xml": "cd_Procedimento",
            "tipo_comparacao": "nao_contem",
            "valor_esperado": "31"
        }
        element = create_element("cd_Procedimento", "31005004")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == False
    
    def test_contem_inicio_true(self, rule_engine):
        """Testa 'contem_inicio' quando valor começa com substring"""
        condition = {
            "campo_xml": "cd_Procedimento",
            "tipo_comparacao": "contem_inicio",
            "valor_esperado": "31"
        }
        element = create_element("cd_Procedimento", "31005004")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_contem_inicio_false(self, rule_engine):
        """Testa 'contem_inicio' quando valor não começa com substring"""
        condition = {
            "campo_xml": "cd_Procedimento",
            "tipo_comparacao": "contem_inicio",
            "valor_esperado": "40"
        }
        element = create_element("cd_Procedimento", "31005004")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == False
    
    def test_nao_contem_inicio_true(self, rule_engine):
        """Testa 'nao_contem_inicio' implementado recentemente"""
        condition = {
            "campo_xml": "cd_Procedimento",
            "tipo_comparacao": "nao_contem_inicio",
            "valor_esperado": "40"
        }
        element = create_element("cd_Procedimento", "31005004")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_existe_true(self, rule_engine):
        """Testa 'existe' quando elemento existe"""
        condition = {
            "campo_xml": "tp_Atendimento",
            "tipo_comparacao": "existe"
        }
        element = create_element("tp_Atendimento", "23")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_nao_existe_true(self, rule_engine):
        """Testa 'nao_existe' quando elemento não existe"""
        condition = {
            "campo_xml": "equipeObrigatoria",
            "tipo_comparacao": "nao_existe"
        }
        # Element é None quando não encontrado
        result = rule_engine._evaluate_condition(None, condition, NAMESPACES)
        assert result == True
    
    def test_lista_true(self, rule_engine):
        """Testa 'lista' quando valor está na lista"""
        condition = {
            "campo_xml": "tpCaraterAtend",
            "tipo_comparacao": "lista",
            "valor_esperado": ["01", "02", "03"]
        }
        element = create_element("tpCaraterAtend", "02")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_maior_que_true(self, rule_engine):
        """Testa 'maior_que' com números"""
        condition = {
            "campo_xml": "qtdExecutada",
            "tipo_comparacao": "maior_que",
            "valor_esperado": "5"
        }
        element = create_element("qtdExecutada", "10")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True
    
    def test_menor_que_true(self, rule_engine):
        """Testa 'menor_que' com números"""
        condition = {
            "campo_xml": "qtdExecutada",
            "tipo_comparacao": "menor_que",
            "valor_esperado": "10"
        }
        element = create_element("qtdExecutada", "5")
        
        result = rule_engine._evaluate_condition(element, condition, NAMESPACES)
        assert result == True


class TestExecuteAction:
    """Testes para _execute_action"""
    
    def test_alterar_campo_modifica(self, rule_engine, sadt_tree, namespaces):
        """Testa que 'alterar_campo' modifica o valor corretamente"""
        action = {
            "tipo": "alterar_campo",
            "tag_alvo": ".//ptu:tp_Atendimento",
            "novo_valor": "23"
        }
        
        # Valor inicial é "05"
        element = sadt_tree.find(".//ptu:tp_Atendimento", namespaces)
        assert element.text == "05"
        
        # Executar ação
        modified = rule_engine._execute_action(sadt_tree, action, namespaces)
        
        # Verificar que foi modificado
        assert modified == True
        element = sadt_tree.find(".//ptu:tp_Atendimento", namespaces)
        assert element.text == "23"
    
    def test_alterar_campo_idempotente(self, rule_engine, sadt_tree, namespaces):
        """Testa que alterar_campo é idempotente"""
        action = {
            "tipo": "alterar_campo",
            "tag_alvo": ".//ptu:tp_Atendimento",
            "novo_valor": "05"  # Mesmo valor que já está
        }
        
        # Executar ação com valor já correto
        modified = rule_engine._execute_action(sadt_tree, action, namespaces)
        
        # Não deve reportar modificação
        assert modified == False
    
    def test_inserir_elemento(self, rule_engine, sadt_tree, namespaces):
        """Testa inserção de novo elemento"""
        action = {
            "tipo": "inserir_elemento",
            "tag_pai": ".//ans:dadosAtendimento",
            "novo_elemento": {
                "tag": "ptu:novoElemento",
                "texto": "valor_teste"
            }
        }
        
        # Executar
        modified = rule_engine._execute_action(sadt_tree, action, namespaces)
        
        # Verificar inserção
        assert modified == True
        elemento = sadt_tree.find(".//ptu:novoElemento", namespaces)
        assert elemento is not None
        assert elemento.text == "valor_teste"
    
    def test_remover_elemento(self, rule_engine, sadt_tree, namespaces):
        """Testa remoção de elemento"""
        action = {
            "tipo": "remover_elemento",
            "tag_alvo": ".//ptu:tp_Atendimento"
        }
        
        # Verificar que existe
        assert sadt_tree.find(".//ptu:tp_Atendimento", namespaces) is not None
        
        # Executar
        modified = rule_engine._execute_action(sadt_tree, action, namespaces)
        
        # Verificar remoção
        assert modified == True
        assert sadt_tree.find(".//ptu:tp_Atendimento", namespaces) is None


class TestRuleIdempotence:
    """Testes de idempotência - regras não devem modificar XMLs já corretos"""
    
    def test_reordenar_elementos_ja_ordenados(self, rule_engine):
        """Testa que reordenar elementos já ordenados não modifica"""
        # Criar XML com elementos já na ordem correta
        pai = etree.Element("pai")
        etree.SubElement(pai, "grauPart").text = "1"
        etree.SubElement(pai, "codProfissional").text = "123"
        
        action = {
            "tipo": "reordenar_elementos_filhos",
            "tag_alvo": ".",
            "ordem_esperada": ["grauPart", "codProfissional"]
        }
        
        # Executar
        modified = rule_engine._execute_action(pai, action, {})
        
        # Não deve modificar (já está correto)
        assert modified == False
    
    def test_reordenar_elementos_fora_de_ordem(self, rule_engine):
        """Testa que reordenar elementos realmente reordena"""
        # Criar XML com elementos fora de ordem
        pai = etree.Element("pai")
        etree.SubElement(pai, "codProfissional").text = "123"
        etree.SubElement(pai, "grauPart").text = "1"
        
        action = {
            "tipo": "reordenar_elementos_filhos",
            "tag_alvo": ".",
            "ordem_esperada": ["grauPart", "codProfissional"]
        }
        
        # Executar
        modified = rule_engine._execute_action(pai, action, {})
        
        # Deve modificar
        assert modified == True
        
        # Verificar ordem
        filhos = list(pai)
        assert filhos[0].tag == "grauPart"
        assert filhos[1].tag == "codProfissional"


@pytest.mark.timeout(5)
class TestPerformance:
    """Testes de performance - cada teste deve ser rápido"""
    
    def test_evaluate_condition_rapido(self, rule_engine):
        """Testa que evaluate_condition é rápida (< 0.01s)"""
        import time
        
        condition = {
            "campo_xml": "teste",
            "tipo_comparacao": "igual",
            "valor_esperado": "valor"
        }
        element = create_element("teste", "valor")
        
        start = time.time()
        for _ in range(1000):
            rule_engine._evaluate_condition(element, condition, {})
        duration = time.time() - start
        
        # 1000 avaliações em < 1s
        assert duration < 1.0
