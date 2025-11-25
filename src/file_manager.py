# src/file_manager.py

import os
import glob
import shutil
import zipfile
import lxml.etree as etree

def listar_arquivos_zip(caminho_pasta):
    if not os.path.isdir(caminho_pasta):
        return []
    return glob.glob(os.path.join(caminho_pasta, "*.zip"))

def listar_arquivos_051(caminho_pasta):
    if not os.path.isdir(caminho_pasta):
        return []
    return glob.glob(os.path.join(caminho_pasta, "*.051"))

def fazer_backup_fatura(caminho_fatura_original, caminho_pasta_backup):
    if not os.path.isfile(caminho_fatura_original): return False
    nome_arquivo = os.path.basename(caminho_fatura_original)
    caminho_destino_backup = os.path.join(caminho_pasta_backup, nome_arquivo)
    try:
        if not os.path.exists(caminho_destino_backup):
            shutil.copy2(caminho_fatura_original, caminho_destino_backup)
        return True
    except Exception:
        return False

def extrair_xml_fatura_do_zip(caminho_zip, pasta_destino):
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as arquivo_zip_aberto:
            for nome_arquivo_interno in arquivo_zip_aberto.namelist():
                if nome_arquivo_interno.lower().endswith(".051"):
                    arquivo_zip_aberto.extract(nome_arquivo_interno, path=pasta_destino)
                    return os.path.join(pasta_destino, nome_arquivo_interno)
            return None
    except (zipfile.BadZipFile, FileNotFoundError):
        return None

def extrair_xmls_de_lista_zips(lista_caminhos_zips, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)
    for caminho_zip in lista_caminhos_zips:
        if os.path.exists(caminho_zip):
            extrair_xml_fatura_do_zip(caminho_zip, pasta_destino)

def organizar_faturas_por_auditor(plano_distribuicao, pasta_faturas_origem, pasta_distribuicao_raiz):
    for nome_auditor, dados in plano_distribuicao.items():
        nome_pasta_auditor = nome_auditor.replace(' ', '_').replace('.', '')
        caminho_pasta_auditor = os.path.join(pasta_distribuicao_raiz, nome_pasta_auditor)
        os.makedirs(caminho_pasta_auditor, exist_ok=True)
        for fatura in dados['faturas']:
            caminho_original = fatura.get('caminho_zip_original')
            if caminho_original and os.path.exists(caminho_original):
                shutil.move(caminho_original, caminho_pasta_auditor)

def recriar_zip_com_hash_atualizado(caminho_zip_original, caminho_xml_corrigido, novo_hash):
    try:
        pasta_backup = os.path.dirname(caminho_zip_original)
        pasta_raiz = os.path.dirname(pasta_backup)
        pasta_validacao = os.path.join(pasta_raiz, "Validacao_CMB")
        os.makedirs(pasta_validacao, exist_ok=True)
        novo_caminho_zip = os.path.join(pasta_validacao, os.path.basename(caminho_zip_original))

        parser = etree.XMLParser(recover=True, strip_cdata=False, resolve_entities=False)
        arvore_xml = etree.parse(caminho_xml_corrigido, parser)
        raiz = arvore_xml.getroot()
        
        ns = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'}
        hash_node = raiz.find('ptu:hash', ns)
        if hash_node is not None:
            hash_node.text = novo_hash
        else:
            nova_tag_hash = etree.Element(f"{{{ns['ptu']}}}hash")
            nova_tag_hash.text = novo_hash
            raiz.append(nova_tag_hash)

        xml_bytes_finais = etree.tostring(raiz, encoding='ISO-8859-1', xml_declaration=True, pretty_print=True)
        nome_xml_interno = os.path.basename(caminho_xml_corrigido)

        with zipfile.ZipFile(novo_caminho_zip, 'w', zipfile.ZIP_DEFLATED) as novo_zip:
            if os.path.exists(caminho_zip_original):
                with zipfile.ZipFile(caminho_zip_original, 'r') as zip_original:
                    for item in zip_original.infolist():
                        if not item.filename.lower().endswith('.051'):
                            novo_zip.writestr(item, zip_original.read(item.filename))
            novo_zip.writestr(nome_xml_interno, xml_bytes_finais)
        return novo_caminho_zip
    except Exception:
        return None

def validar_xml_com_xsd(caminho_xsd, caminho_xml):
    """
    Valida um arquivo XML contra um arquivo XSD.
    Retorna (True, "Mensagem de Sucesso") se for válido,
    ou (False, "Log de Erros") se for inválido.
    """
    try:
        # Carrega o arquivo de schema (XSD)
        schema_doc = etree.parse(caminho_xsd)
        schema = etree.XMLSchema(schema_doc)

        # Carrega o arquivo XML para validar
        parser_xml = etree.XMLParser(recover=True)
        xml_doc = etree.parse(caminho_xml, parser=parser_xml)

        # Valida o XML. Se for inválido, uma exceção é levantada.
        schema.assertValid(xml_doc)
        return True, "Arquivo XML está válido conforme o schema XSD."

    except etree.DocumentInvalid as err:
        # Retorna o log de erros para ser exibido na interface
        return False, f"Erro de validação XSD:\n{err.error_log}"
        
    except Exception as e:
        return False, f"Ocorreu um erro inesperado durante a validação XSD: {e}"