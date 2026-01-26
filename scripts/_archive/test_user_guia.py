
import sys
import os

# Add src to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)
sys.path.append(project_root)

# Agora importar modules com prefixo src se necessario ou direto
try:
    from src.business.rules.rule_engine import RuleEngine
except ImportError:
    from business.rules.rule_engine import RuleEngine
from lxml import etree

def test_user_guide():
    print("=== TESTE DA REGRA EM GUIA ESPECIFICA (USUARIO) ===")
    
    # Setup
    config_dir = os.path.join(project_root, "src", "config")
    engine = RuleEngine(config_dir)
    engine.load_all_rules()  # Usa banco de dados por padrão
    
    # Path to user file
    xml_path = os.path.join(project_root, "tests", "guia_user_request.xml")
    
    if not os.path.exists(xml_path):
        print(f"ERRO: Arquivo nao encontrado {xml_path}")
        return

    print(f"Lendo arquivo: {xml_path}")
    
    # Parse XML
    try:
        xml_tree = etree.parse(xml_path)
    except Exception as e:
        print(f"Erro ao parsear XML: {e}")
        return

    # Check values before
    root = xml_tree.getroot()
    ns = {"ptu": "http://www.unimed.com.br/ptu"}
    
    # Locate the observation tax item (seq_item 12, code 60033681)
    # Using xpath to match the specific item from the user request
    target_items = root.xpath(".//ptu:procedimentosExecutados[./ptu:procedimentos/ptu:cd_Servico='60033681']", namespaces=ns)
    
    if not target_items:
        print("ALERTA: Item de taxa de observacao (60033681) nao encontrado no XML.")
    else:
        item = target_items[0]
        h_ini = item.xpath("./ptu:hr_Inicial/text()", namespaces=ns)
        h_fim = item.xpath("./ptu:hr_Final/text()", namespaces=ns)
        print(f"ANTES: Taxa Observacao - hr_Inicial={h_ini} / hr_Final={h_fim}")
        
    # Apply rules
    print("Aplicando regras...")
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print(f"Regras carregadas: {len(engine.loaded_rules)}")
    for r in engine.loaded_rules:
        if "TAXA_OBSERVACAO" in r.get("id", ""):
            print(f"Regra encontrada: {r.get('id')}")

    engine.apply_rules_to_xml(xml_tree, file_name="guia_user_request.xml")
    
    # Check values after
    if target_items:
        h_ini_new = target_items[0].xpath("./ptu:hr_Inicial/text()", namespaces=ns)
        h_fim_new = target_items[0].xpath("./ptu:hr_Final/text()", namespaces=ns)
        print(f"DEPOIS: Taxa Observacao - hr_Inicial={h_ini_new} / hr_Final={h_fim_new}")
        
        if h_ini_new != h_ini or h_fim_new != h_fim:
            print("\nSUCESSO: Horarios foram modificados!")
            if h_ini_new and h_ini_new[0] != '00:00:01':
                 print(f"Horario valido 'copiado' detectado: {h_ini_new[0]}")
        else:
            print("\nFALHA: Horarios nao foram alterados.")
            
if __name__ == "__main__":
    test_user_guide()
