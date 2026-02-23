# src/validator/core/file_handler.py
import os
import glob
import logging
import lxml.etree as etree # Garanta que esta importação existe


# Configuração de logger específico para o módulo
logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self):
        pass

    def list_xml_files(self, folder_path):
        """
        Lista todos os arquivos .051 em uma pasta especificada.
        Retorna uma lista de caminhos completos para os arquivos .051.
        """
        if not os.path.isdir(folder_path):
            logging.error(f"Caminho não é uma pasta válida: {folder_path}")
            return []
        return glob.glob(os.path.join(folder_path, "*.051"))

    def save_xml_tree(self, xml_tree, output_path):
        """
        Salva uma árvore XML para um arquivo, usando encoding ISO-8859-1 e pretty_print.
        """
        try:
            # Garante que o diretório de saída existe
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # --- LINHA ADICIONADA PARA CORRIGIR A FORMATAÇÃO ---
            # Re-indenta toda a árvore do XML para garantir a formatação correta
            etree.indent(xml_tree.getroot(), space="")

            xml_tree.write(output_path, encoding='ISO-8859-1', xml_declaration=True, pretty_print=True)
            logger.info(f"XML salvo em: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar XML em {output_path}: {e}")
            return False