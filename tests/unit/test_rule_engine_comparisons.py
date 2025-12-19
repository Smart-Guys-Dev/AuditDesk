"""
Testes completos de tipos de comparação do RuleEngine.

Cobre todos os 11 tipos de comparação suportados.
"""
import pytest
from lxml import etree


class TestAllComparisonTypes:
    """Testes para todos os tipos de comparação em _evaluate_condition"""
    
    # 1. IGUAL
    def test_igual_match(self, rule_engine):
        """Comparação 'igual' quando valores são iguais"""
        element = etree.Element("campo")
        element.text = "valor123"
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "igual",
            "valor_esperado": "valor123"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_igual_no_match(self, rule_engine):
        """Comparação 'igual' quando valores são diferentes"""
        element = etree.Element("campo")
        element.text = "valor123"
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "igual",
            "valor_esperado": "outroValor"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 2. DIFERENTE
    def test_diferente_match(self, rule_engine):
        """Comparação 'diferente' quando valores são diferentes"""
        element = etree.Element("campo")
        element.text = "valor1"
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "diferente",
            "valor_esperado": "valor2"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_diferente_no_match(self, rule_engine):
        """Comparação 'diferente' quando valores são iguais"""
        element = etree.Element("campo")
        element.text = "valor1"
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "diferente",
            "valor_esperado": "valor1"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 3. CONTEM
    def test_contem_match(self, rule_engine):
        """Comparação 'contem' quando valor contém substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "contem",
            "valor_esperado": "005"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_contem_no_match(self, rule_engine):
        """Comparação 'contem' quando valor não contém substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "contem",
            "valor_esperado": "999"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 4. NAO_CONTEM
    def test_nao_contem_match(self, rule_engine):
        """Comparação 'nao_contem' quando valor NÃO contém substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "nao_contem",
            "valor_esperado": "999"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_nao_contem_no_match(self, rule_engine):
        """Comparação 'nao_contem' quando valor contém substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "nao_contem",
            "valor_esperado": "005"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 5. CONTEM_INICIO
    def test_contem_inicio_match(self, rule_engine):
        """Comparação 'contem_inicio' quando valor começa com substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "contem_inicio",
            "valor_esperado": "31"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_contem_inicio_no_match(self, rule_engine):
        """Comparação 'contem_inicio' quando valor não começa com substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "contem_inicio",
            "valor_esperado": "40"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 6. NAO_CONTEM_INICIO (implementado recentemente)
    def test_nao_contem_inicio_match(self, rule_engine):
        """Comparação 'nao_contem_inicio' quando valor NÃO começa com substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "nao_contem_inicio",
            "valor_esperado": "40"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_nao_contem_inicio_no_match(self, rule_engine):
        """Comparação 'nao_contem_inicio' quando valor começa com substring"""
        element = etree.Element("codigo")
        element.text = "31005004"
        condition = {
            "campo_xml": "codigo",
            "tipo_comparacao": "nao_contem_inicio",
            "valor_esperado": "31"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 7. EXISTE
    def test_existe_match(self, rule_engine):
        """Comparação 'existe' quando elemento existe"""
        element = etree.Element("campo")
        element.text = "qualquer_valor"
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "existe"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_existe_no_match(self, rule_engine):
        """Comparação 'existe' quando elemento não existe (None)"""
        condition = {
            "campo_xml": "campo_inexistente",
            "tipo_comparacao": "existe"
        }
        assert rule_engine._evaluate_condition(None, condition) == False
    
    # 8. NAO_EXISTE
    def test_nao_existe_match(self, rule_engine):
        """Comparação 'nao_existe' quando elemento não existe"""
        condition = {
            "campo_xml": "campo_inexistente",
            "tipo_comparacao": "nao_existe"
        }
        assert rule_engine._evaluate_condition(None, condition) == True
    
    def test_nao_existe_no_match(self, rule_engine):
        """Comparação 'nao_existe' quando elemento existe"""
        element = etree.Element("campo")
        condition = {
            "campo_xml": "campo",
            "tipo_comparacao": "nao_existe"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 9. MAIOR_QUE
    def test_maior_que_match(self, rule_engine):
        """Comparação 'maior_que' quando valor é maior"""
        element = etree.Element("quantidade")
        element.text = "100"
        condition = {
            "campo_xml": "quantidade",
            "tipo_comparacao": "maior_que",
            "valor_esperado": "50"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_maior_que_no_match(self, rule_engine):
        """Comparação 'maior_que' quando valor é menor ou igual"""
        element = etree.Element("quantidade")
        element.text = "30"
        condition = {
            "campo_xml": "quantidade",
            "tipo_comparacao": "maior_que",
            "valor_esperado": "50"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 10. MENOR_QUE
    def test_menor_que_match(self, rule_engine):
        """Comparação 'menor_que' quando valor é menor"""
        element = etree.Element("quantidade")
        element.text = "30"
        condition = {
            "campo_xml": "quantidade",
            "tipo_comparacao": "menor_que",
            "valor_esperado": "50"
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_menor_que_no_match(self, rule_engine):
        """Comparação 'menor_que' quando valor é maior ou igual"""
        element = etree.Element("quantidade")
        element.text = "100"
        condition = {
            "campo_xml": "quantidade",
            "tipo_comparacao": "menor_que",
            "valor_esperado": "50"
        }
        assert rule_engine._evaluate_condition(element, condition) == False
    
    # 11. LISTA
    def test_lista_match(self, rule_engine):
        """Comparação 'lista' quando valor está na lista"""
        element = etree.Element("carater")
        element.text = "02"
        condition = {
            "campo_xml": "carater",
            "tipo_comparacao": "lista",
            "valor_esperado": ["01", "02", "03", "04"]
        }
        assert rule_engine._evaluate_condition(element, condition) == True
    
    def test_lista_no_match(self, rule_engine):
        """Comparação 'lista' quando valor não está na lista"""
        element = etree.Element("carater")
        element.text = "99"
        condition = {
            "campo_xml": "carater",
            "tipo_comparacao": "lista",
            "valor_esperado": ["01", "02", "03", "04"]
        }
        assert rule_engine._evaluate_condition(element, condition) == False


@pytest.mark.timeout(5)
class TestPerformance:
    """Testes de performance - comparações devem ser rápidas"""
    
    def test_1000_comparacoes_rapidas(self, rule_engine):
        """1000 comparações devem ser executadas em menos de 1 segundo"""
        import time
        
        element = etree.Element("teste")
        element.text = "valor"
        condition = {
            "campo_xml": "teste",
            "tipo_comparacao": "igual",
            "valor_esperado": "valor"
        }
        
        start = time.time()
        for _ in range(1000):
            rule_engine._evaluate_condition(element, condition)
        duration = time.time() - start
        
        assert duration < 1.0, f"1000 comparações demoraram {duration:.2f}s (limite: 1s)"
