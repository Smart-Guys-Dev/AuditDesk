# core/hash_calculator.py

import hashlib
import logging
import re
import lxml.etree as etree

# ✅ FIX: Usar logger adequado ao invés de basicConfig hardcoded
logger = logging.getLogger(__name__)

def _extrair_conteudo_puro_de_bloco(bloco_xml_str: str) -> str:
    """
    Função auxiliar que replica a lógica de limpeza do script validado.
    Remove quebras de linha, espaços entre tags e todas as tags XML,
    deixando apenas o conteúdo textual puro e concatenado.
    """
    texto_sem_quebras = bloco_xml_str.replace('\n', '').replace('\r', '')
    texto_sem_espacos = re.sub(r'>\s+<', '><', texto_sem_quebras)
    conteudo_puro = re.sub(r'<[^>]+>', '', texto_sem_espacos)
    return conteudo_puro.strip()

def calcular_hash_bloco_guia_cobranca(raiz_xml_completo):
    """
    Calcula o hash MD5 focando APENAS no conteúdo do bloco <GuiaCobrancaUtilizacao>,
    seguindo a lógica que foi validada e aceita pela CMB.

    Args:
        raiz_xml_completo: O elemento raiz da árvore XML (objeto lxml.etree._Element)
                           APÓS todas as correções de negócio do WorkflowController.

    Returns:
        str: O hash MD5 hexadecimal, ou None se o bloco não for encontrado ou ocorrer erro.
    """
    if raiz_xml_completo is None:
        logger.error("A raiz do XML fornecida é nula. Não é possível calcular o hash.")
        return None

    try:
        guia_node_list = raiz_xml_completo.xpath("//*[local-name()='GuiaCobrancaUtilizacao']")
        if not guia_node_list:
            logger.error("Bloco <GuiaCobrancaUtilizacao> não encontrado no XML para cálculo do hash.")
            return None
        
        guia_node = guia_node_list[0]

        bloco_guia_bytes = etree.tostring(guia_node) 
        bloco_guia_str = bloco_guia_bytes.decode("ISO-8859-1") 

        bloco_guia_sem_hash_interno = re.sub(r"<(\w+:)?hash>.*?</(\w+:)?hash>", "", bloco_guia_str, flags=re.IGNORECASE | re.DOTALL)
        
        conteudo_puro_do_bloco = _extrair_conteudo_puro_de_bloco(bloco_guia_sem_hash_interno)
        
        novo_hash = hashlib.md5(conteudo_puro_do_bloco.encode("ISO-8859-1")).hexdigest()
        
        logger.info(f"Hash do bloco GuiaCobrancaUtilizacao calculado com sucesso: {novo_hash}")
        return novo_hash

    except Exception as e:
        logger.exception(f"Erro inesperado durante o cálculo do hash do bloco GuiaCobrancaUtilizacao: {e}")
        return None