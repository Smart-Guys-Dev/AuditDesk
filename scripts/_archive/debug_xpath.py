import os
import sys

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)
sys.path.append(project_root)

from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES

def test_xpath():
    print(f"Project Root: {project_root}")
    print(f"NAMESPACES in XMLReader: {NAMESPACES}")
    
    xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        return

    reader = XMLReader()
    print(f"Loading XML: {xml_path}")
    tree = reader.load_xml_tree(xml_path)
    root = tree.getroot()
    print(f"Root tag: {root.tag}")
    
    # Test finding procedimentosExecutados
    xpath = ".//ptu:procedimentosExecutados"
    elements = reader.find_elements_by_xpath(root, xpath)
    print(f"Found {len(elements)} elements with xpath '{xpath}'")
    
    if elements:
        print("First element found.")
        # Test finding cd_Servico inside first element
        first = elements[0]
        # In rule config we have: ./ptu:procedimentos/ptu:cd_Servico
        child_xpath = "./ptu:procedimentos/ptu:cd_Servico"
        children = reader.find_elements_by_xpath(first, child_xpath)
        print(f"Found {len(children)} children with xpath '{child_xpath}' in first element")
        if children:
            print(f"Value: {children[0].text}")

if __name__ == "__main__":
    test_xpath()
