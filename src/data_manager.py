import json
import os
import logging

# --- ATUALIZAÇÃO 1: Definir um logger específico para este módulo ---
# A linha basicConfig foi removida para não afetar outros módulos.
logger = logging.getLogger(__name__)

codigos_hm_tabela00_a_ignorar_set = set()
hm_tabela00_carregados_com_sucesso = False

mapa_unimeds = {}
unimeds_carregadas = False

def carregar_codigos_hm_tabela00_a_ignorar():
    """
    Carrega a lista de códigos de serviço HM da Tabela 00 a serem ignorados.
    """
    global codigos_hm_tabela00_a_ignorar_set, hm_tabela00_carregados_com_sucesso
    hm_tabela00_carregados_com_sucesso = False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config', 'ignore_00.json')

    # --- ATUALIZAÇÃO 2: Usar o logger específico ---
    logger.info(f"Tentando carregar códigos a ignorar de: {config_path}")

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                lista_de_objetos_json = json.load(f)
                
                if isinstance(lista_de_objetos_json, list):
                    # Remove o cabeçalho se existir
                    if lista_de_objetos_json and "Código" in lista_de_objetos_json[0]:
                        lista_de_objetos_json = lista_de_objetos_json[1:]

                    temp_codigos = [str(item["Código"]).strip() for item in lista_de_objetos_json if isinstance(item, dict) and "Código" in item]
                    codigos_hm_tabela00_a_ignorar_set = set(temp_codigos)
                    hm_tabela00_carregados_com_sucesso = True
                    logger.info(f"Sucesso! {len(codigos_hm_tabela00_a_ignorar_set)} códigos a ignorar carregados.")
                else:
                    logger.error(f"Estrutura inesperada em '{config_path}'. Esperava uma lista.")
                    codigos_hm_tabela00_a_ignorar_set = set()
        else:
            logger.warning(f"Arquivo de configuração '{config_path}' não encontrado. A lista de códigos a ignorar estará vazia.")
            codigos_hm_tabela00_a_ignorar_set = set()

    except Exception as e:
        logger.exception(f"Erro ao carregar configurações de {config_path}: {e}")
        codigos_hm_tabela00_a_ignorar_set = set()

def carregar_dados_unimed():
    """
    Carrega os dados de mapeamento das Unimeds do arquivo config/unimed_map.json.
    """
    global mapa_unimeds, unimeds_carregadas
    unimeds_carregadas = False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(base_dir, 'config', 'unimed_map.json')

    logger.info(f"Tentando carregar mapa de Unimeds de: {map_path}")
    try:
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                mapa_unimeds = json.load(f)
                if isinstance(mapa_unimeds, dict):
                    unimeds_carregadas = True
                    logger.info(f"{len(mapa_unimeds)} Unimeds carregadas.")
                else:
                    logger.error(f"Estrutura inesperada em '{map_path}'. Esperava um dicionário.")
                    mapa_unimeds = {}
        else:
            logger.warning(f"Arquivo de mapa de Unimeds '{map_path}' não encontrado. O mapa de Unimeds estará vazio.")
            mapa_unimeds = {}
            
    except Exception as e:
        logger.exception(f"Erro ao carregar mapa de Unimeds de {map_path}: {e}")
        mapa_unimeds = {}

def get_codigos_hm_tabela00_a_ignorar():
    return codigos_hm_tabela00_a_ignorar_set

def is_hm_tabela00_carregados():
    return hm_tabela00_carregados_com_sucesso

def is_unimeds_carregadas():
    return unimeds_carregadas

def obter_nome_unimed(codigo_unimed):
    if not unimeds_carregadas:
        return f"MAPA NÃO CARREGADO (Cód: {str(codigo_unimed).strip()})"
    codigo_str = str(codigo_unimed).strip()
    return mapa_unimeds.get(codigo_str, f"CÓDIGO {codigo_str} NÃO MAPEADO")