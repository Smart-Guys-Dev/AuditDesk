# Script COMPLETO para corrigir workflow_controller.py
with open('src/workflow_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituição 1: Remover parser com remove_blank_text
old_parser = '''                    # Parse XML
                    parser = etree.XMLParser(remove_blank_text=True)
                    tree = etree.parse(xml_file, parser)'''

new_parser = '''                    # Parse XML preservando formato original
                    tree = etree.parse(xml_file)'''

content = content.replace(old_parser, new_parser)

# Verificar se mudou
if old_parser not in content and new_parser in content:
    print("✓ Parser removido!")
else:
    print("⚠ Parser NÃO foi alterado")

with open('src/workflow_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Arquivo salvo!")
