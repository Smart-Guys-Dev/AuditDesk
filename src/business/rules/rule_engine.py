# src/business/rules/rule_engine.py

import json
import os
import logging
import lxml.etree as etree

# Updated imports for MVC structure
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES
from src.infrastructure.files.file_handler import FileHandler
from src.database import db_manager

# Tracker de glosas evitadas (valores REAIS do XML)
try:
    from src.relatorio_glosas import tracker
except ImportError:
    tracker = None

logger = logging.getLogger(__name__)

# Centraliza as configurações das listas para evitar erros de digitação e facilitar a manutenção.
LIST_CONFIG = {
    "codigos_terapias_seriadas": {"key": "ITENS QUE OBRIGAM PARTICIPAÇÃO", "type": "map"},
    "codigos_equipe_obrigatoria": {"key": "ITENS QUE OBRIGAM PARTICIPAÇÃO", "type": "set"},
    "codigos_cbo_medicos": {"key": "cbo", "type": "set"},
    "ignore_00": {"key": "Código", "type": "set"}
}

class RuleEngine:
    """
    Motor de regras para carregar, interpretar e aplicar correções em arquivos XML
    baseado em um conjunto de regras declarativas definidas em arquivos JSON.
    """
    def __init__(self, config_dir=None):
        # ✅ Fix: Apontar para src/config/ ao invés de src/business/rules/config/
        if config_dir is None:
            # Caminho base do projeto
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config_dir = os.path.join(project_root, "config")
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            self.config_dir = os.path.join(base_path, config_dir)
        
        self.rules_config_master = {}
        self.loaded_rules = []
        self.external_lists = {}
        self.xml_reader = XMLReader()
        self.file_handler = FileHandler()
        
        # Carregar configuração de regras
        rules_config_path = os.path.join(self.config_dir, "rules_config.json")
        self.rules_config_master = self._load_json_file(rules_config_path) or {}

    def _load_json_file(self, file_path):
        """Carrega e decodifica um arquivo JSON de forma segura."""
        if not os.path.exists(file_path): 
            logger.error(f"Arquivo de configuração não encontrado: {file_path}")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except json.JSONDecodeError as e: 
            logger.error(f"Erro de sintaxe no JSON {os.path.basename(file_path)}: {e}")
            return None
        except Exception as e: 
            logger.error(f"Erro inesperado ao ler o arquivo {os.path.basename(file_path)}: {e}")
            return None

    def _load_list_from_json(self, list_id, file_name):
        """
        Carrega uma lista de dados de um arquivo JSON e a armazena de forma otimizada.
        Utiliza o dicionário LIST_CONFIG para determinar como processar cada arquivo.
        """
        json_path = os.path.join(self.config_dir, file_name)
        raw_list = self._load_json_file(json_path)
        if not isinstance(raw_list, list) or not raw_list: 
            logger.error(f"Conteúdo da lista '{list_id}' em '{file_name}' é inválido ou está vazio.")
            return False
        
        config = LIST_CONFIG.get(list_id)
        if not config:
            logger.error(f"Configuração para a lista '{list_id}' não encontrada em LIST_CONFIG.")
            return False

        # Remove a primeira linha se for um cabeçalho
        first_item = raw_list[0]
        if isinstance(first_item, dict) and any(str(v).lower() in ["código", "tabela", "descrição", "cbo"] for v in first_item.values()):
            raw_list = raw_list[1:]

        key_name = config["key"]
        storage_type = config["type"]

        if storage_type == "map":
            mapped_codes = {
                str(item[key_name]): {
                    "Especialidade": item.get("Especialidade"), 
                    "CBO": str(item.get("CBO")) if item.get("CBO") else None
                } 
                for item in raw_list if item.get(key_name)
            }
            self.external_lists[list_id] = mapped_codes
        else: # storage_type == "set"
            self.external_lists[list_id] = {str(item.get(key_name)) for item in raw_list if item.get(key_name)}
        
        logger.info(f"Lista '{list_id}' carregada com {len(self.external_lists[list_id])} itens.")
        return True

    def load_all_rules(self, use_database: bool = True):
        """
        Carrega todas as regras ativas.
        
        Args:
            use_database: Se True, carrega do SQLite. Se False, carrega dos JSONs.
        
        Returns:
            bool: True se carregou com sucesso
        """
        # Carregar configuração mestre (sempre do JSON para listas e config)
        master_config_path = os.path.join(self.config_dir, "rules_config.json")
        self.rules_config_master = self._load_json_file(master_config_path)
        if not self.rules_config_master: 
            return False
        
        # Carregar listas de dados (ainda do JSON por enquanto)
        for list_id, file_name in self.rules_config_master.get("listas_comuns", {}).items():
            if not self._load_list_from_json(list_id, file_name): 
                return False
        
        # Tentar carregar regras do SQLite primeiro
        if use_database:
            try:
                from src.database.rule_repository import get_active_rules
                self.loaded_rules = get_active_rules()
                
                if self.loaded_rules:
                    logger.info(f"✅ {len(self.loaded_rules)} regras carregadas do banco de dados.")
                    return True
                else:
                    logger.warning("Banco de regras vazio, tentando carregar do JSON...")
            except Exception as e:
                logger.warning(f"Erro ao carregar regras do banco: {e}. Usando JSON como fallback.")
        
        # Fallback: Carregar dos arquivos JSON
        return self._load_rules_from_json()
    
    def _load_rules_from_json(self):
        """Carrega regras dos arquivos JSON (fallback)."""
        self.loaded_rules = []
        
        for group in self.rules_config_master.get("grupos_para_carregar", []):
            if group.get("ativo", False):
                rules_file = group.get("arquivo_regras")
                if not rules_file: 
                    continue
                
                rules_path = os.path.join(self.config_dir, rules_file)
                group_rules = self._load_json_file(rules_path)
                
                if group_rules and isinstance(group_rules, list):
                    self.loaded_rules.extend(rule for rule in group_rules if rule.get("ativo", False))
                    logger.info(f"Grupo '{group.get('nome_grupo')}' carregado do JSON.")
        
        logger.info(f"Total de {len(self.loaded_rules)} regras ativas carregadas do JSON.")
        return True

    def _evaluate_condition(self, element, condition):
        """Avalia recursivamente se um elemento XML atende a um conjunto de condições."""
        if not condition:
            return True

        if "condicao_multipla" in condition:
            multi_cond = condition["condicao_multipla"]
            sub_conditions = multi_cond.get("sub_condicoes", [])
            logic_type = multi_cond.get("tipo")
            if logic_type == "AND": 
                return all(self._evaluate_condition(element, sc) for sc in sub_conditions)
            if logic_type == "OR": 
                return any(self._evaluate_condition(element, sc) for sc in sub_conditions)

        if "condicao_tag_valor" in condition:
            tag_cond = condition["condicao_tag_valor"]
            xpath_expr = tag_cond.get("xpath")
            compare_type = tag_cond.get("tipo_comparacao", "valor_permitido")
            
            nodes = self.xml_reader.find_elements_by_xpath(element, xpath_expr)
            
            if compare_type == "existe": return bool(nodes)
            if compare_type == "nao_existe": return not bool(nodes)
            if not nodes: return False
            
            node_text = self.xml_reader.get_element_text(nodes[0])
            if node_text is None: return False
            
            list_id = tag_cond.get("id_lista")
            
            if compare_type == "not_in_lista":
                return list_id in self.external_lists and node_text not in self.external_lists[list_id]
            elif compare_type == "in_lista":
                return list_id in self.external_lists and node_text in self.external_lists[list_id]
            elif compare_type == "contem_e_especialidade":
                specialty = tag_cond.get("especialidade_esperada")
                return (list_id in self.external_lists and 
                        node_text in self.external_lists[list_id] and 
                        self.external_lists[list_id].get(node_text, {}).get("Especialidade") == specialty)
            elif compare_type == "valor_atual_diferente":
                return str(node_text) != str(tag_cond.get("valor_atual"))
            elif compare_type == "valor_atual_igual":
                return str(node_text) == str(tag_cond.get("valor_atual"))
            elif compare_type == "contem_inicio":
                # Verifica se o texto começa com o valor especificado
                valor_inicio = str(tag_cond.get("valor_atual", ""))
                return str(node_text).startswith(valor_inicio)
            elif compare_type == "nao_contem_inicio":
                # Verifica se o texto NÃO começa com o valor especificado
                valor_inicio = str(tag_cond.get("valor_atual", ""))
                return not str(node_text).startswith(valor_inicio)
            elif compare_type == "contem":
                # Verifica se o texto contém o valor especificado
                valor = str(tag_cond.get("valor", ""))
                return valor in str(node_text)
            elif "valor_permitido" in tag_cond:
                return node_text in tag_cond["valor_permitido"]
        
        return True

    def _apply_action(self, element, action_config):
        """Aplica uma ação de modificação em um elemento XML com base na configuração da regra."""
        action_type = action_config.get("tipo_acao")
        tag_alvo_xpath = action_config.get("tag_alvo")

        if action_type == "multiplas_acoes":
            modified = False
            for sub_action in action_config.get("sub_acoes", []):
                if self._apply_action(element, sub_action):
                    modified = True
            return modified

        if action_type == "reordenar_elementos_filhos":
            target_node_for_reorder = element
            if tag_alvo_xpath:
                found_nodes = self.xml_reader.find_elements_by_xpath(element, tag_alvo_xpath)
                if not found_nodes: return False
                target_node_for_reorder = found_nodes[0]

            ordem_correta = action_config.get("ordem_correta", [])
            if not ordem_correta: return False

            all_children = list(target_node_for_reorder)
            children_map = {etree.QName(child).localname: child for child in all_children}
            
            # ✅ FIX: Verificar se a ordem atual JÁ está correta (idempotência)
            current_order = [etree.QName(child).localname for child in all_children]
            # Filtrar apenas os elementos que estão na ordem_correta
            relevant_current_order = [tag for tag in current_order if tag in ordem_correta]
            # Filtrar apenas os elementos que existem no XML
            relevant_expected_order = [tag for tag in ordem_correta if tag in children_map]
            
            # Se a ordem atual já está correta, não fazer nada
            if relevant_current_order == relevant_expected_order:
                return False  # ✅ Não houve mudança
            
            # Ordem está incorreta, precisa reordenar
            order_set = set(ordem_correta)
            new_children_sequence = [children_map[tag_name] for tag_name in ordem_correta if tag_name in children_map]
            new_children_sequence.extend(child for child in all_children if etree.QName(child).localname not in order_set)
            
            target_node_for_reorder.clear()
            for child in new_children_sequence:
                target_node_for_reorder.append(child)
            
            return True  # ✅ Houve mudança

        # Ação especial que não requer tag_alvo
        if action_type == "corrigir_dia_31_internacao":
            import re
            modified = False
            
            def tem_dia_31(texto):
                """Verifica se o texto contém dia 31 em qualquer formato"""
                if not texto:
                    return False
                # Formato YYYY/MM/DD (ex: 2025/10/3123:59:00-04)
                if '/31' in texto:
                    return True
                # Formato YYYYMMDD (ex: 20251031)
                if re.search(r'\d{4}(01|03|05|07|08|10|12)31', texto):
                    return True
                return False
            
            def substituir_dia_31(texto):
                """Substitui dia 31 por dia 30 em ambos formatos de data"""
                if not texto:
                    return texto
                
                resultado = texto
                
                # Formato YYYY/MM/DD (ex: 2025/10/3123:59:00-04)
                if '/31' in resultado:
                    resultado = re.sub(r'/31(?=\d{2}:\d{2}:\d{2}|$)', '/30', resultado)
                
                # Formato YYYYMMDD (ex: 20251031 -> 20251030)
                # Meses com 31 dias: 01, 03, 05, 07, 08, 10, 12
                resultado = re.sub(r'(\d{4})(01|03|05|07|08|10|12)31', r'\g<1>\g<2>30', resultado)
                
                return resultado
            
            # Corrigir dt_FimFaturamento
            dt_fim_nodes = self.xml_reader.find_elements_by_xpath(element, ".//ptu:dt_FimFaturamento")
            for dt_node in dt_fim_nodes:
                if tem_dia_31(dt_node.text):
                    novo_valor = substituir_dia_31(dt_node.text)
                    logger.info(f"Corrigindo dt_FimFaturamento: {dt_node.text} -> {novo_valor}")
                    dt_node.text = novo_valor
                    modified = True
            
            # Corrigir dt_Execucao em todos os procedimentosExecutados
            procs = self.xml_reader.find_elements_by_xpath(element, ".//ptu:procedimentosExecutados")
            for proc in procs:
                dt_exec_nodes = self.xml_reader.find_elements_by_xpath(proc, ".//ptu:dt_Execucao")
                for dt_node in dt_exec_nodes:
                    if tem_dia_31(dt_node.text):
                        novo_valor = substituir_dia_31(dt_node.text)
                        logger.info(f"Corrigindo dt_Execucao: {dt_node.text} -> {novo_valor}")
                        dt_node.text = novo_valor
                        modified = True
                
                for tag_data in ["dt_Atendimento", "dt_Inicial", "dt_Final"]:
                    dt_nodes = self.xml_reader.find_elements_by_xpath(proc, f".//ptu:{tag_data}")
                    for dt_node in dt_nodes:
                        if tem_dia_31(dt_node.text):
                            novo_valor = substituir_dia_31(dt_node.text)
                            logger.info(f"Corrigindo {tag_data}: {dt_node.text} -> {novo_valor}")
                            dt_node.text = novo_valor
                            modified = True
            
            return modified
        
        # Ação especial: Converte PJ para PF com rotação de profissionais
        if action_type == "corrigir_pj_para_pf_rotativo":
            # Lista de profissionais para rotação (evita glosa de Consulta Retorno)
            PROFISSIONAIS = [
                {
                    "nome": "RODRIGO DOMINGUES LARAYA",
                    "cpf": "20034717153",
                    "cd_prest": "11021",
                    "crm": "5432",
                    "uf": "50",
                    "cbo": "225125"
                },
                {
                    "nome": "ROTTERDAM PEREIRA GUIMARAES",
                    "cpf": "60829800182",
                    "cd_prest": "198063",
                    "crm": "10730",
                    "uf": "50",
                    "cbo": "225125"
                },
                {
                    "nome": "JUSTINIANO BARBOSA VAVAS",
                    "cpf": "20033389187",
                    "cd_prest": "559",
                    "crm": "1491",
                    "uf": "50",
                    "cbo": "225125"
                },
                {
                    "nome": "VICTOR H. M. BONOMO",
                    "cpf": "04700094117",
                    "cd_prest": "18763",
                    "crm": "8108",
                    "uf": "50",
                    "cbo": "225125"
                }
            ]
            
            # Contador para rotação (usa atributo da instância para manter estado entre chamadas)
            if not hasattr(self, '_pf_rotation_counter'):
                self._pf_rotation_counter = {}
            
            # Obter beneficiário para agrupar
            beneficiario = None
            parent_guia = element.getparent()
            if parent_guia is not None:
                nr_inscricao = self.xml_reader.find_elements_by_xpath(parent_guia, "./ptu:nr_Inscricao")
                if nr_inscricao and nr_inscricao[0].text:
                    beneficiario = nr_inscricao[0].text
            
            # Se não conseguiu identificar beneficiário, usa contador global
            key = beneficiario or "_global"
            
            # Incrementar contador e obter profissional
            if key not in self._pf_rotation_counter:
                self._pf_rotation_counter[key] = 0
            
            idx = self._pf_rotation_counter[key] % len(PROFISSIONAIS)
            prof = PROFISSIONAIS[idx]
            self._pf_rotation_counter[key] += 1
            
            modified = False
            
            # Remover CNPJ se existir
            cnpj_nodes = self.xml_reader.find_elements_by_xpath(element, "./ptu:equipe_Profissional/ptu:cdCnpjCpf/ptu:cd_cnpj")
            for cnpj_node in cnpj_nodes:
                parent = cnpj_node.getparent()
                if parent is not None:
                    parent.remove(cnpj_node)
                    modified = True
            
            # Função auxiliar para garantir tag com conteúdo
            def set_tag(xpath, valor):
                nonlocal modified
                nodes = self.xml_reader.find_elements_by_xpath(element, xpath)
                if nodes:
                    if nodes[0].text != valor:
                        nodes[0].text = valor
                        modified = True
            
            # Atualizar dados do profissional
            set_tag("./ptu:equipe_Profissional/ptu:Prestador/ptu:cd_Uni_Prest", "51")
            set_tag("./ptu:equipe_Profissional/ptu:Prestador/ptu:cd_Prest", prof["cd_prest"])
            set_tag("./ptu:equipe_Profissional/ptu:cdCnpjCpf/ptu:cd_cpf", prof["cpf"])
            set_tag("./ptu:equipe_Profissional/ptu:nm_Profissional", prof["nome"])
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:sg_Conselho", "CRM")
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:nr_Conselho", prof["crm"])
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:UF", prof["uf"])
            set_tag("./ptu:equipe_Profissional/ptu:CBO", prof["cbo"])
            
            if modified:
                logger.info(f"PJ→PF Rotativo: Beneficiário {key} → {prof['nome']}")
            
            return modified
        
        # Ação especial: Normaliza equipe para médico intensivista (CBO 225150)
        if action_type == "corrigir_para_intensivista_rotativo":
            # Lista de médicos intensivistas para rotação
            INTENSIVISTAS = [
                {
                    "nome": "SYLVIA CAROLINA ARAUJO BORGES",
                    "cpf": "96522585120",
                    "cd_prest": "2320",
                    "crm": "6087",
                    "uf": "50",
                    "cbo": "225150",
                    "tp_participacao": "13"
                },
                {
                    "nome": "ANDRE PAULO DE MEDEIROS OLIVEIRA",
                    "cpf": "47812443272",
                    "cd_prest": "1764",
                    "crm": "3959",
                    "uf": "50",
                    "cbo": "225150",
                    "tp_participacao": "13"
                },
                {
                    "nome": "ODINILSON ALMEIDA FONSECA",
                    "cpf": "86220152972",
                    "cd_prest": "1494",
                    "crm": "3786",
                    "uf": "50",
                    "cbo": "225150",
                    "tp_participacao": "13"
                }
            ]
            
            # Contador para rotação
            if not hasattr(self, '_intensivista_rotation_counter'):
                self._intensivista_rotation_counter = 0
            
            idx = self._intensivista_rotation_counter % len(INTENSIVISTAS)
            prof = INTENSIVISTAS[idx]
            self._intensivista_rotation_counter += 1
            
            modified = False
            
            # Função auxiliar para garantir tag com conteúdo
            def set_tag(xpath, valor):
                nonlocal modified
                nodes = self.xml_reader.find_elements_by_xpath(element, xpath)
                if nodes:
                    if nodes[0].text != valor:
                        nodes[0].text = valor
                        modified = True
            
            # Remover CNPJ se existir (caso seja PJ)
            cnpj_nodes = self.xml_reader.find_elements_by_xpath(element, "./ptu:equipe_Profissional/ptu:cdCnpjCpf/ptu:cd_cnpj")
            for cnpj_node in cnpj_nodes:
                parent = cnpj_node.getparent()
                if parent is not None:
                    parent.remove(cnpj_node)
                    modified = True
            
            # Atualizar dados do intensivista
            set_tag("./ptu:equipe_Profissional/ptu:tp_Participacao", prof["tp_participacao"])
            set_tag("./ptu:equipe_Profissional/ptu:Prestador/ptu:cd_Uni_Prest", "51")
            set_tag("./ptu:equipe_Profissional/ptu:Prestador/ptu:cd_Prest", prof["cd_prest"])
            set_tag("./ptu:equipe_Profissional/ptu:cdCnpjCpf/ptu:cd_cpf", prof["cpf"])
            set_tag("./ptu:equipe_Profissional/ptu:nm_Profissional", prof["nome"])
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:sg_Conselho", "CRM")
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:nr_Conselho", prof["crm"])
            set_tag("./ptu:equipe_Profissional/ptu:dadosConselho/ptu:UF", prof["uf"])
            set_tag("./ptu:equipe_Profissional/ptu:CBO", prof["cbo"])
            
            if modified:
                logger.info(f"Intensivista Rotativo: {prof['nome']} (CRM {prof['crm']})")
            
            return modified

        if not tag_alvo_xpath: return False

        modified = False
        target_nodes = self.xml_reader.find_elements_by_xpath(element, tag_alvo_xpath)

        if action_type == "substituir_conteudo_tag":
            if target_nodes:
                new_content = str(action_config.get("novo_conteudo", ""))
                if target_nodes[0].text != new_content:
                    target_nodes[0].text = new_content
                    modified = True
        
        elif action_type == "remover_tag_inteira":
            for node in target_nodes:
                parent = node.getparent()
                if parent is not None:
                    parent.remove(node)
                    modified = True

        elif action_type == "garantir_tag_com_conteudo":
            novo_conteudo = str(action_config.get("novo_conteudo", ""))
            if target_nodes:
                if target_nodes[0].text != novo_conteudo:
                    target_nodes[0].text = novo_conteudo
                    modified = True
            else:
                parts = tag_alvo_xpath.split('/')
                tag_parts = parts[-1].split(':')
                prefix = tag_parts[0] if len(tag_parts) > 1 else 'ptu'
                tag_name = tag_parts[-1]
                ns = NAMESPACES.get(prefix)

                if not ns: return False

                new_tag = etree.Element(f"{{{ns}}}{tag_name}", nsmap=NAMESPACES)
                new_tag.text = novo_conteudo
                
                parent_xpath = '/'.join(parts[:-1]) if len(parts) > 1 else '.'
                parent_nodes = self.xml_reader.find_elements_by_xpath(element, parent_xpath)
                if not parent_nodes: return False
                parent_node = parent_nodes[0]
                
                tag_ref_xpath = action_config.get("tag_referencia_posicao")
                posicao_insercao = action_config.get("posicao_insercao")

                if tag_ref_xpath and (ref_nodes := self.xml_reader.find_elements_by_xpath(element, tag_ref_xpath)):
                    ref_nodes[0].addnext(new_tag)
                elif posicao_insercao == "primeiro_filho":
                    parent_node.insert(0, new_tag)
                else:
                    parent_node.append(new_tag)
                modified = True
        
        elif action_type == "gerar_alerta":
            # Gera um alerta para o usuário (não modifica o XML)
            mensagem = action_config.get("mensagem_alerta", "Alerta gerado")
            dados_alerta = action_config.get("dados_alerta", [])
            
            # Coletar dados do contexto do XML
            alerta_info = {"mensagem": mensagem, "dados": {}}
            
            # Buscar dados no contexto do XML (elemento pai = procedimentosExecutados)
            parent_guia = element.getparent()  # guiasSP_SADT
            if parent_guia is not None:
                parent_fatura = parent_guia.getparent()  # faturaSP_SADT
                
                # Número da guia
                nr_guia = self.xml_reader.find_elements_by_xpath(parent_guia, "./ptu:nr_Guia")
                if nr_guia:
                    alerta_info["dados"]["guia"] = nr_guia[0].text
                
                # Número do beneficiário (inscrição)
                nr_inscricao = self.xml_reader.find_elements_by_xpath(parent_guia, "./ptu:nr_Inscricao")
                if nr_inscricao:
                    alerta_info["dados"]["beneficiario"] = nr_inscricao[0].text
                
                # Código do serviço
                cd_servico = self.xml_reader.find_elements_by_xpath(element, "./ptu:procedimentos/ptu:cd_Servico")
                if cd_servico:
                    alerta_info["dados"]["codigo"] = cd_servico[0].text
            
            # Armazenar alerta na lista de alertas do engine
            if not hasattr(self, 'alertas'):
                self.alertas = []
            
            # Adicionar nome do arquivo se disponível
            if hasattr(self, '_current_file_name'):
                alerta_info["dados"]["arquivo"] = self._current_file_name
            
            self.alertas.append(alerta_info)
            
            logger.warning(f"ALERTA: {mensagem} - Dados: {alerta_info['dados']}")
            # Não modifica o XML, mas retorna True para indicar que a regra foi processada
            modified = True
                
        return modified
    
    def apply_rules_to_xml(self, xml_tree, execution_id=-1, file_name=""):
        """
        Aplica todo o conjunto de regras carregadas a uma árvore XML.

        Args:
            xml_tree (lxml.etree._ElementTree): A árvore XML a ser modificada.
            execution_id (int): ID da execução para tracking de ROI
            file_name (str): Nome do arquivo sendo processado

        Returns:
            bool: True se alguma alteração foi feita, False caso contrário.
        """
        alterations_made = False
        root = xml_tree.getroot()
        
        # Armazenar o nome do arquivo para uso nos alertas
        self._current_file_name = file_name
        
        for rule in self.loaded_rules:
            try:
                conditions = rule.get("condicoes", {})
                tipo_elemento = conditions.get("tipo_elemento")
                
                target_elements = self.xml_reader.find_elements_by_xpath(root, f".//ptu:{tipo_elemento}") if tipo_elemento else [root]
                
                for element in target_elements:
                    if self._evaluate_condition(element, conditions):
                        if self._apply_action(element, rule.get("acao", {})):
                            logger.info(f"Regra '{rule.get('id')}' aplicada com sucesso.")
                            alterations_made = True
                            
                            # Tracking de glosas evitadas (valores REAIS do XML)
                            if execution_id != -1 and tracker is not None:
                                try:
                                    tracker.processar_correcao(
                                        execution_id=execution_id,
                                        file_name=file_name,
                                        xml_tree=xml_tree,
                                        rule=rule,
                                        elemento_afetado=element
                                    )
                                except Exception as tracking_error:
                                    logger.warning(f"Erro ao tracking glosa: {tracking_error}")
                            
                            # Tracking de ROI Realizado
                            if execution_id != -1:
                                try:
                                    # Obter metadados da regra
                                    metadados = rule.get("metadata_glosa", {})
                                    categoria = metadados.get("categoria", "VALIDACAO")
                                    
                                    # Calcular impacto financeiro
                                    if categoria == "GLOSA_GUIA":
                                        # Valor médio de uma guia: R$ 5000
                                        financial_impact = 15.0
                                    elif categoria == "GLOSA_ITEM":
                                        # Valor médio de um item/procedimento: R$ 300
                                        financial_impact = 7.9
                                    else:
                                        # Validação: impacto indireto (evita retrabalho)
                                        financial_impact = 5.5
                                    
                                    # Salvar no banco
                                    db_manager.log_roi_metric(
                                        execution_id=execution_id,
                                        file_name=file_name,
                                        rule_id=rule.get('id', 'UNKNOWN'),
                                        rule_description=rule.get('descricao', ''),
                                        correction_type=categoria,
                                        financial_impact=financial_impact
                                    )
                                except Exception as roi_error:
                                    logger.warning(f"Erro ao logar ROI: {roi_error}")
            except Exception as e:
                logger.error(f"ERRO na regra {rule.get('id')}: {e}")
                continue
                        
        return alterations_made