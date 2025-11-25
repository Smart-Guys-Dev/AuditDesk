# Validador XML/core/xml_reader.py
import lxml.etree as etree
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - (xml_reader) - %(message)s')

# NAMESPACES globais para uso consistente
NAMESPACES = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'} 

class XMLReader:
    def __init__(self):
        # recover=True tenta corrigir XMLs malformados, strip_cdata=False mantém CDATA, resolve_entities=False não expande entidades
        self.parser = etree.XMLParser(recover=True, strip_cdata=False, resolve_entities=False)

    def load_xml_tree(self, xml_path):
        """
        Carrega um arquivo XML e retorna sua árvore etree.
        """
        try:
            tree = etree.parse(xml_path, self.parser)
            return tree
        except etree.XMLSyntaxError as e:
            logging.error(f"Erro de sintaxe XML ao carregar {xml_path}: {e}")
            return None
        except Exception as e:
            logging.error(f"Erro ao carregar XML {xml_path}: {e}")
            return None
    
    def find_elements_by_xpath(self, element, xpath_expr):
        """
        Encontra elementos dentro de outro elemento usando uma expressão XPath.
        """
        # logging.debug(f"DEBUG: Buscando XPath '{xpath_expr}' a partir de '{etree.QName(element).localname}'")
        return element.xpath(xpath_expr, namespaces=NAMESPACES)

    def get_element_text(self, element):
        """
        Retorna o texto de um elemento, tratando None e espaços em branco.
        """
        if element is None:
            logging.debug(f"DEBUG: get_element_text recebendo elemento None. Retornando None.")
            return None
        
        # Garante que o texto seja tratado como string e strip() remove espaços/quebras de linha
        # Se element.text for None, str(None) vira "None", então verificamos explicitamente
        text_content = element.text
        if text_content is not None:
            text_content = text_content.strip()
        
        # logging.debug(f"DEBUG: get_element_text para <{etree.QName(element).localname}>. Texto bruto: '{text_content}'")
        return text_content
    
    def ensure_child(self, parent, qname: str):
        import lxml.etree as etree
        from .xml_reader import NAMESPACES
        tag = qname[2:] if qname.startswith("./") else qname
        if ":" in tag:
            prefix, local = tag.split(":", 1)
            full = f"{{{NAMESPACES[prefix]}}}{local}"
        else:
            full = tag
        child = parent.find(full)
        if child is None:
            child = etree.SubElement(parent, full)
        return child
