# Script para corrigir workflow_controller.py
with open('src/workflow_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover o parser com remove_blank_text (linhas 284-286)
content = content.replace(
    '''                    # Parse XML
                    parser = etree.XMLParser(remove_blank_text=True)
                    tree = etree.parse(xml_file, parser)''',
    '''                    # Parse XML preservando formato original
                    tree = etree.parse(xml_file)'''
)

with open('src/workflow_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Parser corrigido - formato original será preservado!")
