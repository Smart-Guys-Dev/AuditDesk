import sys
import os
import pytest
from lxml import etree

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import XMLReader

# Namespaces padrão
NAMESPACES = {
    'ans': 'http://www.ans.gov.br/padroes/tiss/schemas',
    'ptu': 'http://unimedbh.com.br/PTU'
}

@pytest.fixture
def rule_engine():
    """Instância configurada do RuleEngine com regras carregadas."""
    engine = RuleEngine()
    engine.load_all_rules()  # Carregar regras
    return engine

@pytest.fixture
def xml_reader():
    """Instância do XMLReader."""
    return XMLReader()

@pytest.fixture
def namespaces():
    """Namespaces XML padrão."""
    return NAMESPACES.copy()

@pytest.fixture
def sample_sadt_xml():
    """XML SADT básico para testes."""
    return """<?xml version="1.0" encoding="UTF-8"?>
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

@pytest.fixture
def sadt_tree(sample_sadt_xml):
    """Árvore lxml do SADT."""
    return etree.fromstring(sample_sadt_xml.encode('utf-8'))

@pytest.fixture
def create_element():
    """Helper para criar elementos XML."""
    def _create_element(tag, text=None, namespace=None):
        if namespace:
            element = etree.Element(f"{{{namespace}}}{tag}")
        else:
            element = etree.Element(tag)
        
        if text:
            element.text = str(text)
        
        return element
    return _create_element


