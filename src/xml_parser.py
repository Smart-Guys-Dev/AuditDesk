# src/xml_parser.py

import logging
import lxml.etree as etree
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

NAMESPACES = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'}

def _parse_xml_file(caminho_arquivo_xml: str) -> Optional[etree._ElementTree]:
    """Parser XML comum para todas as funções."""
    try:
        parser_xml = etree.XMLParser(recover=True)
        return etree.parse(caminho_arquivo_xml, parser=parser_xml)
    except Exception as e:
        logging.error(f"Erro ao fazer parse do XML '{os.path.basename(caminho_arquivo_xml)}': {e}")
        return None

def _obter_texto_elemento(elemento: etree._Element, xpath_expr: str) -> Optional[str]:
    """Função auxiliar para extrair texto de elemento com tratamento de erro."""
    try:
        nodes = elemento.xpath(xpath_expr, namespaces=NAMESPACES)
        if nodes and nodes[0].text is not None:
            return nodes[0].text.strip()
        return None
    except Exception:
        return None

def _calcular_valor_total_guia(guia: etree._Element) -> float:
    """Calcula o valor total de uma guia de internação."""
    valor_total_guia = 0.0
    for proc in guia.xpath('.//ptu:procedimentosExecutados', namespaces=NAMESPACES):
        valor_str = _obter_texto_elemento(proc, './/ptu:valores/ptu:vl_ServCobrado')
        if valor_str:
            try:
                valor_str_corrigido = valor_str.replace(',', '.')
                valor_total_guia += float(valor_str_corrigido)
            except (ValueError, TypeError):
                continue
    return valor_total_guia

def _extrair_dados_guia(guia: etree._Element) -> Dict[str, str]:
    """Extrai dados básicos de uma guia de internação."""
    return {
        "numero_guia": _obter_texto_elemento(guia, './/ptu:nr_Guias/ptu:nr_GuiaTissPrestador') or '',
        "codigo_beneficiario": _obter_texto_elemento(guia, './/ptu:dadosBeneficiario/ptu:id_Benef') or '',
        "nome_beneficiario": _obter_texto_elemento(guia, './/ptu:dadosBeneficiario/ptu:nm_Benef') or '',
        "regime_internacao": _obter_texto_elemento(guia, './/ptu:dadosInternacao/ptu:rg_Internacao') or '',
    }

def _parse_data_flexivel(date_string: str) -> Optional[datetime]:
    """Tenta analisar uma string de data/hora com múltiplos formatos - CORRIGIDA."""
    if not date_string:
        return None
        
    clean_string = date_string.strip()
    
    # ✅ CORREÇÃO: Adicionar suporte para formato SEM ESPAÇO
    formatos = [
        '%Y/%m/%d %H:%M:%S',      # Formato correto: 2025/09/01 12:26:00
        '%Y/%m/%d%H:%M:%S',       # Formato problemático: 2025/09/0112:26:00
        '%Y/%m/%d %H:%M:%S-%f',   # Com timezone: 2025/09/01 12:26:00-04  
        '%Y/%m/%d%H:%M:%S-%f',    # Com timezone sem espaço: 2025/09/0112:26:00-04
        '%Y-%m-%d %H:%M:%S',      # Formato alternativo
        '%Y-%m-%d%H:%M:%S',       # Formato alternativo sem espaço
    ]
    
    for fmt in formatos:
        try:
            if '-%f' in fmt and '-' in clean_string:
                if len(clean_string) >= 21:
                    if ' ' in clean_string[:10]:
                        string_to_parse = clean_string[:19]
                        return datetime.strptime(string_to_parse, fmt.replace('-%f', ''))
                    else:
                        if len(clean_string) >= 16:
                            string_to_parse = clean_string[:16]
                            return datetime.strptime(string_to_parse, '%Y/%m/%d%H:%M:%S')
                string_sem_timezone = re.sub(r'-\d+$', '', clean_string)
                return datetime.strptime(string_sem_timezone, fmt.replace('-%f', ''))
            else:
                return datetime.strptime(clean_string, fmt)
        except ValueError:
            continue
    
    # ✅ Parser manual para o formato problemático
    try:
        match = re.match(r'(\d{4})/(\d{2})/(\d{2})(\d{2}):(\d{2}):(\d{2})', clean_string)
        if match:
            year, month, day, hour, minute, second = map(int, match.groups())
            return datetime(year, month, day, hour, minute, second)
    except:
        pass
    
    logging.warning(f"Formato de data não reconhecido: '{clean_string}'")
    return None

def _validar_e_calcular_duracao(dt_ini_str: Optional[str], dt_fim_str: Optional[str], numero_guia: str) -> Optional[timedelta]:
    """Valida e calcula a duração entre duas datas - CORRIGIDA."""
    if dt_ini_str is None or dt_fim_str is None:
        return None
        
    dt_ini_clean = str(dt_ini_str).strip()
    dt_fim_clean = str(dt_fim_str).strip()
    
    if len(dt_ini_clean) < 10 or len(dt_fim_clean) < 10:
        return None

    dt_ini = _parse_data_flexivel(dt_ini_clean)
    dt_fim = _parse_data_flexivel(dt_fim_clean)

    if dt_ini and dt_fim:
        if dt_fim >= dt_ini:
            return dt_fim - dt_ini
        else:
            logging.warning(f"Data final anterior à data inicial na guia {numero_guia}.")
            return None
    else:
        logging.warning(f"Não foi possível processar datas para guia {numero_guia}.")
        return None

def extrair_dados_fatura_xml(caminho_arquivo_xml: str) -> Optional[Dict[str, Optional[str]]]:
    """Extrai dados básicos da fatura do XML."""
    arvore_xml = _parse_xml_file(caminho_arquivo_xml)
    if not arvore_xml: 
        return None
        
    raiz = arvore_xml.getroot()
    cod_unimed_str = _obter_texto_elemento(raiz, './/ptu:cd_Uni_Destino')
    if cod_unimed_str: 
        cod_unimed_str = cod_unimed_str.zfill(3)
        
    return {
        'numero_fatura': _obter_texto_elemento(raiz, './/ptu:nr_Documento'),
        'competencia': _obter_texto_elemento(raiz, './/ptu:nr_Competencia'),
        'codigo_unimed_destino': cod_unimed_str,
        'data_emissao': _obter_texto_elemento(raiz, './/ptu:dt_EmissaoDoc'),
        'data_vencimento': _obter_texto_elemento(raiz, './/ptu:dt_VencimentoDoc'),
        'valor_total_documento': _obter_texto_elemento(raiz, './/ptu:vl_TotalDoc'),
    }

def extrair_guias_internacao_relevantes(
    caminho_xml: str, fatura_pai: str, valor_minimo: float, codigos_a_ignorar: set
) -> List[Dict[str, Union[str, float]]]:
    """Extrai guias de internação com valor acima do mínimo."""
    arvore_xml = _parse_xml_file(caminho_xml)
    if not arvore_xml: 
        return []
        
    raiz = arvore_xml.getroot()
    guias_relevantes = []
    guias_encontradas = raiz.xpath('.//ptu:guiaInternacao', namespaces=NAMESPACES)
    
    for guia in guias_encontradas:
        try:
            dados_guia = _extrair_dados_guia(guia)
            valor_total_guia = _calcular_valor_total_guia(guia)
            
            if valor_total_guia >= valor_minimo:
                info_guia = { 
                    "fatura_pai": fatura_pai, 
                    "valor_filtro": valor_total_guia, 
                    "valor_total_real": valor_total_guia, 
                    **dados_guia 
                }
                guias_relevantes.append(info_guia)
        except Exception as e:
            logging.warning(f"Erro ao processar guia individual: {e}")
            continue
            
    return guias_relevantes

def extrair_guias_internacao_curta_para_sinalizacao(caminho_xml: str) -> List[Dict[str, str]]:
    """Extrai guias de internação com curta permanência para sinalização."""
    arvore_xml = _parse_xml_file(caminho_xml)
    if not arvore_xml: 
        return []
        
    raiz = arvore_xml.getroot()
    guias_para_sinalizar = []
    nome_arquivo = os.path.basename(caminho_xml)
    guias_internacao = raiz.xpath('.//ptu:guiaInternacao', namespaces=NAMESPACES)

    for guia in guias_internacao:
        try:
            dados_guia = _extrair_dados_guia(guia)
            dt_ini_str = _obter_texto_elemento(guia, './/ptu:dadosFaturamento/ptu:dt_IniFaturamento')
            dt_fim_str = _obter_texto_elemento(guia, './/ptu:dadosFaturamento/ptu:dt_FimFaturamento')
            
            if not dados_guia.get("regime_internacao") or not dados_guia.get("numero_guia"):
                continue

            duracao = _validar_e_calcular_duracao(dt_ini_str, dt_fim_str, dados_guia["numero_guia"])
            
            if (duracao is not None and 
                timedelta(hours=0) <= duracao <= timedelta(hours=12) and 
                dados_guia["regime_internacao"] != '2'):
                
                info_guia = {
                    "arquivo_origem": nome_arquivo,
                    "numero_guia": dados_guia["numero_guia"],
                    "nome_beneficiario": dados_guia["nome_beneficiario"],
                    "regime_informado": dados_guia["regime_internacao"],
                    "duracao": str(duracao),
                    "motivo": f"Permanência curta com regime '{dados_guia['regime_internacao']}'. Risco de glosa."
                }
                guias_para_sinalizar.append(info_guia)
                
        except Exception as e:
            logging.warning(f"Erro ao processar guia: {e}")
            continue
            
    return guias_para_sinalizar