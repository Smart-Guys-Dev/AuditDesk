# Script FINAL para save_xml_tree - versão 3
# Quebra apenas ANTES de tags de ABERTURA, não de fechamento

codigo_novo = '''    def save_xml_tree(self, xml_tree, output_path):
        """
        Salva uma árvore XML para um arquivo, usando encoding ISO-8859-1.
        Formato TISS: cada elemento em uma linha, SEM indentação.
        """
        try:
            # Garante que o diretório de saída existe
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Serializa o XML SEM pretty_print (tudo em uma linha)
            xml_bytes = etree.tostring(
                xml_tree.getroot(),
                encoding='ISO-8859-1',
                xml_declaration=True,
                pretty_print=False
            )
            
            # Converte para string
            xml_str = xml_bytes.decode('ISO-8859-1')
            
            # Adiciona quebra de linha APENAS antes de tags de ABERTURA
            # Não quebra antes de tags de fechamento </
            import re
            # Adiciona \\n antes de < que NÃO seja seguido por /
            xml_str = re.sub(r'<(?!/)', r'\\n<', xml_str)
            # Remove \\n extras no início
            xml_str = xml_str.lstrip('\\n')
            # Remove \\n antes do XML declaration
            xml_str = xml_str.replace('\\n<?xml', '<?xml')
            
            # Salva o arquivo
            with open(output_path, 'w', encoding='ISO-8859-1') as f:
                f.write(xml_str)
            
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

# Encontrar o próximo método ou fim do arquivo
fim_busca = content.find('\\n    def ', inicio + 10)
if fim_busca == -1:
    fim_busca = len(content)

# Substituir
novo_content = content[:inicio] + codigo_novo + content[fim_busca:]

with open('src/file_handler.py', 'w', encoding='utf-8') as f:
    f.write(novo_content)

print("✓ v3: Agora quebra APENAS antes de tags de abertura!")
