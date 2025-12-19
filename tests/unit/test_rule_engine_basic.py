"""
Testes simples de validação do RuleEngine - versão inicial.
"""
import pytest
from lxml import etree


class TestRuleEngineBasic:
    """Testes básicos de funcionamento do RuleEngine"""
    
    def test_rule_engine_loads(self, rule_engine):
        """Teste que RuleEngine carrega sem erros"""
        assert rule_engine is not None
        assert hasattr(rule_engine, '_evaluate_condition')
        assert hasattr(rule_engine, '_apply_action')
        assert hasattr(rule_engine, 'apply_rules_to_xml')
    
    def test_evaluate_condition_igual(self, rule_engine):
        """Teste comparação 'igual'"""
        # Criar elemento simples
        element = etree.Element("teste")
        element.text = "valor"
        
        condition = {
            "campo_xml": "teste",
            "tipo_comparacao": "igual",
            "valor_esperado": "valor"
        }
        
        result = rule_engine._evaluate_condition(element, condition)
        assert result == True
    
    def test_evaluate_condition_diferente(self, rule_engine):
        """Teste comparação 'diferente'"""
        element = etree.Element("teste")
        element.text = "valor1"
        
        condition = {
            "campo_xml": "teste",
            "tipo_comparacao": "diferente",
            "valor_esperado": "valor2"
        }
        
        result = rule_engine._evaluate_condition(element, condition)
        assert result == True
    
    def test_apply_rules_to_xml_runs(self, rule_engine, sadt_tree):
        """Teste que apply_rules_to_xml executa sem erro"""
        # sadt_tree já é um Element, preciso criar uma ElementTree
        from lxml import etree
        tree = etree.ElementTree(sadt_tree)
        
        # Apenas verifica que executa sem exception
        result = rule_engine.apply_rules_to_xml(tree)
        
        # Resultado é booleano (modificou ou não)
        assert isinstance(result, bool)

    def test_rules_loaded(self, rule_engine):
        """Verifica que regras foram carregadas"""
        assert hasattr(rule_engine, 'loaded_rules')
        assert isinstance(rule_engine.loaded_rules, list)
        # Deve ter pelo menos algumas regras carregadas
        print(f"\n✅ Total de regras carregadas: {len(rule_engine.loaded_rules)}")
        assert len(rule_engine.loaded_rules) > 0, "Nenhuma regra foi carregada!"


