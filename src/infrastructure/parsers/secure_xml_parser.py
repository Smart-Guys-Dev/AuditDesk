# src/infrastructure/parsers/secure_xml_parser.py
"""
Secure XML Parser
Parser XML seguro usando defusedxml para prevenir XXE e outras vulnerabilidades.

✅ SEGURANÇA: Proteção contra:
- XXE (XML External Entity) Injection
- Billion Laughs Attack (DoS)
- Entity Expansion Attacks
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

# ✅ SEGURANÇA: Usar defusedxml ao invés de xml.etree.ElementTree
try:
    import defusedxml.ElementTree as ET
    DEFUSEDXML_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ defusedxml disponível - XML parsing seguro ativado")
except ImportError:
    # Fallback para ET padrão (com aviso)
    import xml.etree.ElementTree as ET
    DEFUSEDXML_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ defusedxml não instalado - usando xml.etree padrão (INSEGURO)")


class SecureXMLParser:
    """
    Parser XML seguro com proteções contra ataques comuns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not DEFUSEDXML_AVAILABLE:
            self.logger.warning(
                "🚨 AVISO DE SEGURANÇA: defusedxml não está instalado. "
                "Instale com: pip install defusedxml"
            )
    
    def parse_file(self, file_path: str) -> Optional[ET.Element]:
        """
        Faz parsing seguro de arquivo XML.
        
        Args:
            file_path: Caminho do arquivo XML
            
        Returns:
            Element root do XML ou None se erro
        """
        try:
            # Validar caminho
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            if not path.is_file():
                self.logger.error(f"Caminho não é um arquivo: {file_path}")
                return None
            
            # ✅ SEGURANÇA: Parser com proteções
            if DEFUSEDXML_AVAILABLE:
                # defusedxml já tem proteções built-in
                tree = ET.parse(file_path)
            else:
                # Tentar adicionar proteções manualmente
                parser = ET.XMLParser()
                
                # Disable DTD processing
                parser.entity = {}  
                
                tree = ET.parse(file_path, parser=parser)
            
            root = tree.getroot()
            self.logger.debug(f"✅ XML parsed com sucesso: {file_path}")
            
            return root
            
        except ET.ParseError as e:
            self.logger.error(f"❌ Erro de parsing XML em {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro ao ler arquivo XML {file_path}: {e}")
            return None
    
    def parse_string(self, xml_string: str) -> Optional[ET.Element]:
        """
        Faz parsing seguro de string XML.
        
        Args:
            xml_string: String contendo XML
            
        Returns:
            Element root do XML ou None se erro
        """
        try:
            if DEFUSEDXML_AVAILABLE:
                root = ET.fromstring(xml_string)
            else:
                parser = ET.XMLParser()
                parser.entity = {}
                root = ET.fromstring(xml_string, parser=parser)
            
            return root
            
        except ET.ParseError as e:
            self.logger.error(f"❌ Erro de parsing XML string: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar XML string: {e}")
            return None
    
    def find_element(self, root: ET.Element, path: str, namespaces: Optional[Dict[str, str]] = None) -> Optional[ET.Element]:
        """
        Busca elemento no XML de forma segura.
        
        Args:
            root: Element root
            path: XPath do elemento
            namespaces: Dicionário de namespaces
            
        Returns:
            Element encontrado ou None
        """
        try:
            if namespaces:
                element = root.find(path, namespaces=namespaces)
            else:
                element = root.find(path)
            
            return element
        except Exception as e:
            self.logger.error(f"Erro ao buscar elemento {path}: {e}")
            return None
    
    def find_all_elements(self, root: ET.Element, path: str, namespaces: Optional[Dict[str, str]] = None) -> list:
        """
        Busca todos os elementos matching no XML.
        
        Args:
            root: Element root
            path: XPath dos elementos
            namespaces: Dicionário de namespaces
            
        Returns:
            Lista de elementos encontrados
        """
        try:
            if namespaces:
                elements = root.findall(path, namespaces=namespaces)
            else:
                elements = root.findall(path)
            
            return elements
        except Exception as e:
            self.logger.error(f"Erro ao buscar elementos {path}: {e}")
            return []
    
    def get_text(self, element: Optional[ET.Element], default: str = "") -> str:
        """
        Extrai texto de elemento de forma segura.
        
        Args:
            element: Element XML
            default: Valor padrão se elemento for None
            
        Returns:
            Texto do elemento ou default
        """
        if element is None:
            return default
        
        text = element.text
        return text if text is not None else default
    
    def get_attribute(self, element: Optional[ET.Element], attr_name: str, default: str = "") -> str:
        """
        Extrai atributo de elemento de forma segura.
        
        Args:
            element: Element XML
            attr_name: Nome do atributo
            default: Valor padrão se atributo não existir
            
        Returns:
            Valor do atributo ou default
        """
        if element is None:
            return default
        
        return element.get(attr_name, default)


# Singleton global
_secure_parser = None

def get_secure_parser() -> SecureXMLParser:
    """
    Retorna instância singleton do parser seguro.
    
    Returns:
        SecureXMLParser instance
    """
    global _secure_parser
    if _secure_parser is None:
        _secure_parser = SecureXMLParser()
    return _secure_parser
