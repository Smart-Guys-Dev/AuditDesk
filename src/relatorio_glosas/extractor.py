"""
Extrator de Valores Reais do XML

Extrai valores financeiros dos XMLs TISS para cálculo preciso de glosas evitadas.
"""
from lxml import etree

# Namespaces XML TISS
NAMESPACES = {
    'ptu': 'http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico'
}


def extrair_nr_guia_prestador(elemento):
    """
    Extrai o número da guia do prestador
    
    Args:
        elemento: Elemento XML (pode ser qualquer elemento dentro da guia)
        
    Returns:
       str: Número da guia
    """
    # Encontrar o elemento guia pai
    guia = elemento.xpath(
        'ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | '
        'ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta',
        namespaces=NAMESPACES
    )
    
    if not guia:
        return None
    
    nr_guia = guia[0].find('.//ptu:nr_GuiaPrestador', namespaces=NAMESPACES)
    return nr_guia.text if nr_guia is not None else None


def extrair_valor_total_guia(elemento):
    """
    Extrai o valor TOTAL da guia
    
    Tenta primeiro o campo nr_GuiaIsPrestador (se existir).
    Se não existir, soma TODOS os procedimentos da guia.
    
    Args:
        elemento: Elemento XML dentro da guia
        
    Returns:
        float: Valor total da guia em R$
    """
    # Encontrar guia pai
    guia = elemento.xpath(
        'ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | '
        'ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta',
        namespaces=NAMESPACES
    )
    
    if not guia:
        return 0.0
    
    guia_element = guia[0]
    
    # Tentar nr_GuiaPrestador (valor total informado)
    valor_total_tag = guia_element.find('.//ptu:nr_GuiaPrestador', namespaces=NAMESPACES)
    if valor_total_tag is not None and valor_total_tag.text:
        try:
            return float(valor_total_tag.text)
        except:
            pass
    
    # Se não tem, somar todos procedimentos
    total = 0.0
    procedimentos = guia_element.findall('.//ptu:procedimentosExecutados', namespaces=NAMESPACES)
    
    for proc in procedimentos:
        valor_proc = extrair_valor_procedimento(proc)
        total += valor_proc
    
    return total


def extrair_valor_procedimento(procedimento_element):
    """
    Extrai valor de um procedimento individual
    
    Soma: vl_ServCobrado + tx_AdmServico
    
    Args:
        procedimento_element: Elemento <procedimentosExecutados>
        
    Returns:
        float: Valor total do procedimento
    """
    valores = procedimento_element.find('.//ptu:valores', namespaces=NAMESPACES)
    if valores is None:
        return 0.0
    
    vl_serv = 0.0
    tx_adm = 0.0
    
    # vl_ServCobrado
    vl_serv_tag = valores.find('.//ptu:vl_ServCobrado', namespaces=NAMESPACES)
    if vl_serv_tag is not None and vl_serv_tag.text:
        try:
            vl_serv = float(vl_serv_tag.text)
        except:
            pass
    
    # tx_AdmServico
    tx_adm_tag = valores.find('.//ptu:tx_AdmServico', namespaces=NAMESPACES)
    if tx_adm_tag is not None and tx_adm_tag.text:
        try:
            tx_adm = float(tx_adm_tag.text)
        except:
            pass
    
    return vl_serv + tx_adm


def extrair_seq_item(procedimento_element):
    """
    Extrai o seq_item do procedimento
    
    Args:
        procedimento_element: Elemento <procedimentosExecutados>
        
    Returns:
        int: Número sequencial do item
    """
    seq_tag = procedimento_element.find('.//ptu:seq_item', namespaces=NAMESPACES)
    if seq_tag is not None and seq_tag.text:
        try:
            return int(seq_tag.text)
        except:
            return 0
    return 0


def extrair_cd_servico(procedimento_element):
    """
    Extrai o código do serviço/procedimento
    
    Args:
        procedimento_element: Elemento <procedimentosExecutados>
        
    Returns:
        str: Código do serviço
    """
    cd_tag = procedimento_element.find('.//ptu:procedimentos/ptu:cd_Servico', namespaces=NAMESPACES)
    return cd_tag.text if cd_tag is not None and cd_tag.text else None


def contar_procedimentos_guia(elemento):
    """
    Conta quantos procedimentos existem na guia
    
    Args:
        elemento: Elemento XML dentro da guia
        
    Returns:
        int: Quantidade de procedimentos
    """
    guia = elemento.xpath(
        'ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | '
        'ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta',
        namespaces=NAMESPACES
    )
    
    if not guia:
        return 0
    
    procedimentos = guia[0].findall('.//ptu:procedimentosExecutados', namespaces=NAMESPACES)
    return len(procedimentos)


def localizar_procedimento(elemento, seq_item):
    """
    Localiza um procedimento específico pelo seq_item
    
    Args:
        elemento: Elemento XML dentro da guia
        seq_item: Número sequencial do item
        
    Returns:
        Element: Elemento <procedimentosExecutados> ou None
    """
    guia = elemento.xpath(
        'ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | '
        'ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta',
        namespaces=NAMESPACES
    )
    
    if not guia:
        return None
    
    procedimentos = guia[0].findall('.//ptu:procedimentosExecutados', namespaces=NAMESPACES)
    
    for proc in procedimentos:
        seq = extrair_seq_item(proc)
        if seq == seq_item:
            return proc
    
    return None
