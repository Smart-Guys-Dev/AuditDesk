# Script para reescrever save_xml_tree no file_handler.py

codigo_novo = '''    def save_xml_tree(self, xml_tree, output_path):
        """
        Salva uma árvore XML para um arquivo, usando encoding ISO-8859-1.
        Mantém quebras de linha mas SEM indentação (formato TISS padrão).
        """
        try:
            # Garante que o diretório de saída existe
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Serializa o XML com pretty_print para ter quebras de linha
            xml_bytes = etree.tostring(
                xml_tree.getroot(),
                encoding='ISO-8859-1',
                xml_declaration=True,
                pretty_print=True
            )
            
            # Remove TODA a indentação (espaços/tabs antes de tags)
            # Mantém apenas quebras de linha
            xml_str = xml_bytes.decode('ISO-8859-1')
            lines = xml_str.split('\\n')
            lines_sem_indent = [line.lstrip() for line in lines]
            xml_final = '\\n'.join(lines_sem_indent)
            
            # Salva o arquivo
            with open(output_path, 'w', encoding='ISO-8859-1') as f:
                f.write(xml_final)
            
            logging.info(f"XML salvo em: {output_path}")
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar XML em {output_path}: {e}")
            return False'''

with open('src/file_handler.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar início e fim do método
inicio = content.find('    def save_xml_tree(self, xml_tree, output_path):')
if inicio == -1:
    print("❌ Método não encontrado!")
    exit(1)

# Encontrar o próximo método ou fim da classe
fim_busca = content.find('\n    def ', inicio + 10)
if fim_busca == -1:
    fim_busca = content.find('\nclass ', inicio + 10)
if fim_busca == -1:
    fim_busca = len(content)

# Substituir
novo_content = content[:inicio] + codigo_novo + content[fim_busca:]

with open('src/file_handler.py', 'w', encoding='utf-8') as f:
    f.write(novo_content)

print("✓ Método save_xml_tree reescrito com sucesso!")
