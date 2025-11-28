# Script para remover etree.indent do file_handler.py
with open('src/file_handler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e remover as linhas do etree.indent (linhas 34-36)
new_lines = []
skip_next = 0
for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue
    
    if 'etree.indent(xml_tree.getroot(), space="")' in line:
        # Pular esta linha e as 2 anteriores de comentário
        new_lines.pop()  # Remove "# Re-indenta toda a árvore..."
        new_lines.pop()  # Remove "# --- LINHA ADICIONADA..."
        continue
    
    new_lines.append(line)

with open('src/file_handler.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ etree.indent removido do file_handler.py!")
