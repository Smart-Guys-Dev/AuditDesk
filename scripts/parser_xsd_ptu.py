# -*- coding: utf-8 -*-
"""
Parser de Schemas XSD PTU
Extrai automaticamente a estrutura hierárquica dos schemas XSD
e gera documentação atualizada das estruturas de guias.
"""
import os
import lxml.etree as etree
from collections import defaultdict

# Namespace do XSD
XSD_NS = {"xs": "http://www.w3.org/2001/XMLSchema"}

class XSDParser:
    def __init__(self, schemas_dir):
        self.schemas_dir = schemas_dir
        self.types = {}  # nome_tipo -> estrutura
        self.elements = {}  # nome_elemento -> tipo
        
    def load_schema(self, filename):
        """Carrega e parseia um arquivo XSD."""
        path = os.path.join(self.schemas_dir, filename)
        if not os.path.exists(path):
            print(f"Arquivo não encontrado: {path}")
            return None
        
        try:
            tree = etree.parse(path)
            return tree.getroot()
        except Exception as e:
            print(f"Erro ao parsear {filename}: {e}")
            return None
    
    def extract_complex_types(self, root):
        """Extrai todos os complexTypes do schema."""
        for ct in root.xpath("//xs:complexType[@name]", namespaces=XSD_NS):
            type_name = ct.get("name")
            elements = self._extract_elements_from_type(ct)
            self.types[type_name] = elements
    
    def _extract_elements_from_type(self, complex_type):
        """Extrai os elementos de um complexType."""
        elements = []
        
        # Buscar em sequence, choice, all
        for container in ["xs:sequence", "xs:choice", "xs:all"]:
            for seq in complex_type.xpath(f".//{container}", namespaces=XSD_NS):
                for elem in seq.xpath("./xs:element", namespaces=XSD_NS):
                    elem_info = {
                        "name": elem.get("name"),
                        "type": elem.get("type", "inline"),
                        "min": elem.get("minOccurs", "1"),
                        "max": elem.get("maxOccurs", "1")
                    }
                    
                    # Se tem complexType inline, extrair recursivamente
                    inline_ct = elem.xpath("./xs:complexType", namespaces=XSD_NS)
                    if inline_ct:
                        elem_info["children"] = self._extract_elements_from_type(inline_ct[0])
                    
                    elements.append(elem_info)
        
        return elements
    
    def get_type_hierarchy(self, type_name, depth=0, max_depth=5):
        """Gera a hierarquia de um tipo recursivamente."""
        if depth > max_depth or type_name not in self.types:
            return []
        
        result = []
        for elem in self.types[type_name]:
            elem_type = elem.get("type", "")
            children = elem.get("children", [])
            
            # Limpar prefixo ptu:
            if elem_type.startswith("ptu:"):
                elem_type = elem_type[4:]
            
            result.append({
                "name": elem["name"],
                "type": elem_type,
                "min": elem["min"],
                "max": elem["max"],
                "children": children if children else self.get_type_hierarchy(elem_type, depth + 1, max_depth)
            })
        
        return result
    
    def print_hierarchy(self, type_name, indent=0):
        """Imprime a hierarquia de forma legível."""
        hierarchy = self.get_type_hierarchy(type_name)
        self._print_tree(hierarchy, indent)
    
    def _print_tree(self, elements, indent=0):
        """Imprime árvore de elementos."""
        for elem in elements:
            prefix = "│   " * (indent - 1) + "├── " if indent > 0 else ""
            multiplicity = ""
            if elem["max"] == "unbounded" or int(elem.get("max", "1")) > 1:
                multiplicity = " *"
            elif elem["min"] == "0":
                multiplicity = " ?"
            
            print(f"{prefix}{elem['name']}{multiplicity}")
            
            if elem.get("children"):
                self._print_tree(elem["children"], indent + 1)
    
    def find_element_location(self, element_name):
        """Encontra em quais tipos um elemento aparece."""
        locations = []
        for type_name, elements in self.types.items():
            for elem in elements:
                if elem["name"] == element_name:
                    locations.append(type_name)
                # Verificar em filhos inline
                for child in elem.get("children", []):
                    if child.get("name") == element_name:
                        locations.append(f"{type_name} > {elem['name']}")
        return locations
    
    def generate_markdown_doc(self, guia_types):
        """Gera documentação Markdown das estruturas."""
        output = ["# Estruturas PTU Extraídas do XSD\n"]
        output.append("*Gerado automaticamente a partir dos schemas XSD*\n\n")
        
        for guia_name, type_name in guia_types.items():
            output.append(f"## {guia_name}\n")
            output.append(f"Tipo: `{type_name}`\n\n")
            output.append("```\n")
            
            # Capturar saída da hierarquia
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            self.print_hierarchy(type_name)
            hierarchy_str = buffer.getvalue()
            sys.stdout = old_stdout
            
            output.append(hierarchy_str)
            output.append("```\n\n")
        
        return "".join(output)


def main():
    schemas_dir = os.path.join("src", "schemas")
    parser = XSDParser(schemas_dir)
    
    print("=" * 60)
    print("PARSER DE SCHEMAS XSD PTU")
    print("=" * 60)
    
    # Carregar schema de tipos complexos
    root = parser.load_schema("ptu_ComplexTypes-V3_0.xsd")
    if not root:
        return
    
    print(f"\nSchema carregado com sucesso!")
    
    # Extrair tipos
    parser.extract_complex_types(root)
    print(f"Tipos complexos encontrados: {len(parser.types)}")
    
    # Listar alguns tipos importantes
    important_types = [t for t in parser.types.keys() if any(x in t.lower() for x in ["sadt", "consulta", "internacao", "honorario", "guia"])]
    print(f"\nTipos relacionados a guias: {len(important_types)}")
    for t in sorted(important_types)[:20]:
        print(f"  - {t}")
    
    # Buscar onde cd_Excecao está localizado
    print("\n" + "=" * 60)
    print("LOCALIZAÇÃO DE cd_Excecao:")
    print("=" * 60)
    locations = parser.find_element_location("cd_Excecao")
    for loc in locations:
        print(f"  → {loc}")
    
    # Buscar onde procedimentosExecutados está localizado
    print("\n" + "=" * 60)
    print("LOCALIZAÇÃO DE procedimentosExecutados:")
    print("=" * 60)
    locations = parser.find_element_location("procedimentosExecutados")
    for loc in locations:
        print(f"  → {loc}")
    
    # Mostrar hierarquia de ct_SADT
    print("\n" + "=" * 60)
    print("ESTRUTURA ct_SADT:")
    print("=" * 60)
    parser.print_hierarchy("ct_SADT")
    
    print("\n" + "=" * 60)
    print("ESTRUTURA ct_dadosGuiaConsulta:")
    print("=" * 60)
    parser.print_hierarchy("ct_dadosGuiaConsulta")


if __name__ == "__main__":
    main()
