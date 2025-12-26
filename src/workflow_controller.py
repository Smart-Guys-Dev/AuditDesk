# src/workflow_controller.py

import os
import shutil
import tempfile
import lxml.etree as etree
from typing import Callable, List, Optional

from . import (data_manager, distribution_engine, file_manager,
               hash_calculator, report_generator, xml_parser,
               rule_engine)
from .database import db_manager

class WorkflowController:
    VALOR_MINIMO_GUIA = 25000.0

    def __init__(self, user_id: int = None):
        self.user_id = user_id  # Para tracking de produtividade
        self.lista_faturas_processadas: List[dict] = []
        self.pasta_faturas_importadas_atual: Optional[str] = None
        self.plano_ultima_distribuicao: dict = {}
        self.guias_relevantes_por_fatura: dict = {}
        self.current_execution_id = -1  # Para tracking de ROI

        data_manager.carregar_dados_unimed()
        data_manager.carregar_codigos_hm_tabela00_a_ignorar()
        self.codigos_hm_t00_a_ignorar = data_manager.get_codigos_hm_tabela00_a_ignorar()

    def _log(self, message: str, log_callback: Optional[Callable[[str], None]] = None) -> None:
        """Método auxiliar para logging consistente."""
        if log_callback:
            log_callback(message)
        else:
            print(message)

    def processar_importacao_faturas(self, caminho_pasta_selecionada: str,
                                     log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        
        self.pasta_faturas_importadas_atual = caminho_pasta_selecionada
        self.lista_faturas_processadas = []
        self.guias_relevantes_por_fatura = {}

        pasta_backup = os.path.join(caminho_pasta_selecionada, "Backup")
        os.makedirs(pasta_backup, exist_ok=True)
        log(f"INFO: Pasta de backup pronta em: {pasta_backup}")

        arquivos_zip = file_manager.listar_arquivos_zip(caminho_pasta_selecionada)
        log(f"INFO: {len(arquivos_zip)} arquivo(s) .zip encontrado(s).")

        if not arquivos_zip:
            return False, "Nenhum arquivo .zip encontrado na pasta selecionada."

        pasta_temp = tempfile.mkdtemp(prefix="audit_")
        try:
            for i, caminho_zip in enumerate(arquivos_zip):
                nome_arquivo = os.path.basename(caminho_zip)
                log(f"INFO: Processando fatura {i+1}/{len(arquivos_zip)}: {nome_arquivo}")
                
                file_manager.fazer_backup_fatura(caminho_zip, pasta_backup)

                caminho_xml_extraido = file_manager.extrair_xml_fatura_do_zip(caminho_zip, pasta_temp)
                if not caminho_xml_extraido:
                    log(f"AVISO: Nenhum arquivo .051 encontrado em '{nome_arquivo}'. Pulando.")
                    continue

                dados_fatura = xml_parser.extrair_dados_fatura_xml(caminho_xml_extraido)
                if not dados_fatura:
                    log(f"AVISO: Falha ao ler XML para '{nome_arquivo}'. Pulando.")
                    continue

                dados_fatura['nome_zip'] = nome_arquivo
                dados_fatura['caminho_zip_original'] = caminho_zip

                cod_unimed = dados_fatura.get('codigo_unimed_destino')
                if cod_unimed:
                    nome_unimed = data_manager.obter_nome_unimed(cod_unimed)
                    dados_fatura['nome_unimed_destino'] = nome_unimed
                    log(f"  Unimed Destino: {cod_unimed} - {nome_unimed}")

                num_fatura = dados_fatura.get('numero_fatura')
                if num_fatura:
                    guias_relevantes = xml_parser.extrair_guias_internacao_relevantes(
                        caminho_xml_extraido,
                        num_fatura,
                        self.VALOR_MINIMO_GUIA,
                        self.codigos_hm_t00_a_ignorar
                    )
                    if guias_relevantes:
                        self.guias_relevantes_por_fatura[num_fatura] = guias_relevantes
                        log(f"  {len(guias_relevantes)} guia(s) relevante(s) armazenada(s).")

                self.lista_faturas_processadas.append(dados_fatura)
                
        finally:
            log("INFO: Limpando pasta de extração temporária...")
            shutil.rmtree(pasta_temp, ignore_errors=True)

        total_processadas = len(self.lista_faturas_processadas)
        return True, f"Processamento concluído. {total_processadas} fatura(s) processada(s)."

    def preparar_distribuicao_faturas(self, nomes_auditores: List[str],
                                       log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        
        if not self.lista_faturas_processadas or self.pasta_faturas_importadas_atual is None:
            return False, "Nenhuma fatura foi importada."

        log("INFO: Calculando plano de distribuição...")
        plano = distribution_engine.distribuir_faturas(self.lista_faturas_processadas, nomes_auditores)
        self.plano_ultima_distribuicao = plano
        
        pasta_dist_raiz = os.path.join(self.pasta_faturas_importadas_atual, "Distribuição")
        log("INFO: Organizando arquivos ZIP por auditor...")
        
        file_manager.organizar_faturas_por_auditor(plano, self.pasta_faturas_importadas_atual, pasta_dist_raiz)
        
        log("INFO: Gerando relatório Excel...")
        sucesso, caminho_relatorio = report_generator.gerar_relatorio_distribuicao(plano, pasta_dist_raiz)
        
        if sucesso and caminho_relatorio:
            return True, f"Distribuição concluída! Relatório salvo em: {caminho_relatorio}"
        else:
            return False, "Ocorreu um erro ao gerar o relatório."

    def preparar_xmls_para_correcao(self, nome_auditor: str, log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        
        if not self.plano_ultima_distribuicao or not self.pasta_faturas_importadas_atual:
            return False, "Nenhum plano de distribuição encontrado."
        
        log(f"INFO: Preparando XMLs para '{nome_auditor}'...")
        nome_pasta_auditor = nome_auditor.replace(' ', '_').replace('.', '')
        pasta_origem_zips_base = self.pasta_faturas_importadas_atual or ""
        pasta_origem_zips = os.path.join(pasta_origem_zips_base, "Distribuição", nome_pasta_auditor)
        pasta_destino_xmls = os.path.join(pasta_origem_zips_base, "Correção XML", nome_pasta_auditor)
        
        faturas_do_auditor = self.plano_ultima_distribuicao.get(nome_auditor, {}).get('faturas', [])
        lista_zips_para_extrair = [os.path.join(pasta_origem_zips, f['nome_zip']) for f in faturas_do_auditor]
        
        if not lista_zips_para_extrair:
            log(f"AVISO: Nenhum ZIP encontrado para '{nome_auditor}'.")
            return True, "Nenhum ZIP para extrair."
        
        log(f"INFO: Extraindo {len(lista_zips_para_extrair)} XML(s)...")
        file_manager.extrair_xmls_de_lista_zips(lista_zips_para_extrair, pasta_destino_xmls)
        log("INFO: Extração de XMLs concluída.")

        guias_para_csv = []
        for fatura_info in faturas_do_auditor:
            num_fatura = fatura_info.get('numero_fatura')
            if num_fatura and num_fatura in self.guias_relevantes_por_fatura:
                guias_encontradas = self.guias_relevantes_por_fatura[num_fatura]
                guias_para_csv.extend(guias_encontradas)
                log(f"  Coletadas {len(guias_encontradas)} guias da fatura {num_fatura}.")
        
        if guias_para_csv:
            log(f"INFO: {len(guias_para_csv)} guias relevantes encontradas. Gerando CSV...")
            report_generator.gerar_csv_internacao(guias_para_csv, pasta_destino_xmls)
            log("INFO: Relatório CSV de guias de internação gerado com sucesso.")
        
        return True, f"Preparação para '{nome_auditor}' concluída."

    def executar_validacao_xmls(self, caminho_pasta: str,
                                log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        
        try:
            log("INFO: Inicializando o motor de regras do Validador...")
            engine = rule_engine.RuleEngine()
            if not engine.load_all_rules():
                log("ERRO CRÍTICO: Falha ao carregar as regras de validação.")
                return False, "Falha ao carregar regras."

            log(f"INFO: Buscando arquivos .051 em: {caminho_pasta}")
            xml_files = file_manager.listar_arquivos_051(caminho_pasta)

            if not xml_files:
                log("AVISO: Nenhum arquivo .051 encontrado na pasta.")
                return True, "Nenhum arquivo .051 para validar."

            log(f"INFO: {len(xml_files)} arquivo(s) encontrados. Iniciando validação...")
            
            # Criar registro de execução para tracking de ROI
            self.current_execution_id = db_manager.log_execution_start(
                operation_type='VALIDATION',
                total_files=len(xml_files),
                user_id=self.user_id  # ✅ Agora passa o user_id para produtividade
            )
            log(f"INFO: Execução ID {self.current_execution_id} criada.")
            
            modificados = 0
            
            for xml_file in xml_files:
                nome_arquivo = os.path.basename(xml_file)
                log(f"--- Validando: {nome_arquivo} ---")
                
                xml_tree = engine.xml_reader.load_xml_tree(xml_file)
                if not xml_tree: 
                    log(f"ERRO: Falha ao ler o XML: {nome_arquivo}")
                    continue
                
                if engine.apply_rules_to_xml(xml_tree, self.current_execution_id, nome_arquivo):
                    engine.file_handler.save_xml_tree(xml_tree, xml_file)
                    log(f"INFO: Arquivo modificado e salvo.")
                    modificados += 1
                else:
                    log("INFO: Nenhuma regra aplicável encontrada.")
            
            msg_final = f"Validação concluída. {modificados} de {len(xml_files)} arquivo(s) foram modificados."
            log(f"SUCESSO: {msg_final}")
            
            # Finalizar registro de execução
            db_manager.log_execution_end(
                execution_id=self.current_execution_id,
                status='COMPLETED',
                success_count=modificados,
                error_count=len(xml_files) - modificados
            )
            
            return True, msg_final
            
        except Exception as e:
            error_msg = f"Erro inesperado na validação: {e}"
            log(f"ERRO CRÍTICO: {error_msg}")
            return False, error_msg

    def validar_pasta_com_xsd(self, caminho_pasta: str, log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        log("INFO: Iniciando validação estrutural com XSD...")
        
        caminho_base = os.path.dirname(__file__)
        caminho_xsd = os.path.join(caminho_base, "schemas", "ptu_CobrancaUtilizacao.xsd")
        if not os.path.exists(caminho_xsd):
            msg = "ERRO CRÍTICO: Arquivo ptu_CobrancaUtilizacao.xsd não encontrado na pasta 'src/schemas/'."
            log(msg)
            return False, msg

        xml_files = file_manager.listar_arquivos_051(caminho_pasta)
        if not xml_files:
            log("AVISO: Nenhum arquivo .051 encontrado para validar.")
            return True, "Nenhum arquivo XML encontrado."
        
        validos = 0
        total = len(xml_files)
        log(f"INFO: {total} arquivo(s) XML encontrados. Iniciando verificação...")
        for xml_file in xml_files:
            nome_arquivo = os.path.basename(xml_file)
            sucesso, mensagem = file_manager.validar_xml_com_xsd(caminho_xsd, xml_file)
            if sucesso:
                log(f"OK: '{nome_arquivo}' está estruturalmente válido.")
                validos += 1
            else:
                log(f"ERRO: '{nome_arquivo}' está inválido. Detalhes abaixo:")
                log(mensagem)
        msg_final = f"Validação XSD concluída. {validos} de {total} arquivo(s) são válidos."
        log(f"SUCESSO: {msg_final}")
        return True, msg_final

    def executar_atualizacao_hash(self, nome_auditor: str, arquivos_selecionados: Optional[List[str]] = None,
                                  log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        """
        Atualiza hash de arquivos específicos ou todos os arquivos.
        
        Args:
            nome_auditor: Nome do auditor
            arquivos_selecionados: Lista de nomes de arquivos ZIP (None = todos)
            log_callback: Função para logging
        
        Returns:
            (sucesso, mensagem)
        """
        log = lambda msg: self._log(msg, log_callback)
        
        if not self.pasta_faturas_importadas_atual:
            return False, "Pasta de importação não definida."
        
        nome_pasta_auditor = nome_auditor.replace(' ', '_').replace('.', '')
        pasta_correcao_base = self.pasta_faturas_importadas_atual or ""
        pasta_correcao = os.path.join(pasta_correcao_base, "Correção XML", nome_pasta_auditor)
        if not os.path.isdir(pasta_correcao):
            return False, f"Pasta de correção para '{nome_auditor}' não encontrada."
        
        xmls_corrigidos = file_manager.listar_arquivos_051(pasta_correcao)
        if not xmls_corrigidos:
            return True, "Nenhum arquivo .051 para processar."
        
        # NOVA FUNCIONALIDADE: Filtrar apenas arquivos selecionados
        if arquivos_selecionados:
            # Converter nomes de ZIP para nomes de XML
            xmls_selecionados_nomes = [nome.replace('.zip', '.051') for nome in arquivos_selecionados]
            # Filtrar apenas os XMLs correspondentes
            xmls_corrigidos = [
                xml_path for xml_path in xmls_corrigidos
                if os.path.basename(xml_path) in xmls_selecionados_nomes
            ]
            log(f"INFO: Modo seletivo - processando {len(xmls_corrigidos)} arquivo(s) selecionado(s)")
        else:
            log(f"INFO: Modo completo - processando todos os {len(xmls_corrigidos)} arquivo(s)")

        if not xmls_corrigidos:
            return True, "Nenhum arquivo selecionado para processar."

        log(f"INFO: Iniciando atualização..."); sucessos = 0
        parser_xml = etree.XMLParser(recover=True)

        for xml_path in xmls_corrigidos:
            nome_xml = os.path.basename(xml_path); log(f"--- Processando: {nome_xml} ---")
            nome_zip = nome_xml.replace('.051', '.zip')
            caminho_zip_original = os.path.join(pasta_correcao_base, "Backup", nome_zip)
            
            if not os.path.exists(caminho_zip_original):
                log(f"AVISO: ZIP original '{nome_zip}' não encontrado no Backup. Pulando."); continue
            
            try:
                arvore_xml = etree.parse(xml_path, parser=parser_xml)
                raiz = arvore_xml.getroot()
                novo_hash = hash_calculator.calcular_hash_bloco_guia_cobranca(raiz)
                if not novo_hash:
                    log(f"ERRO: Falha ao calcular o hash para '{nome_xml}'. Pulando.")
                    continue
                
                log(f"INFO: Novo hash: {novo_hash}")
                
                resultado = file_manager.recriar_zip_com_hash_atualizado(caminho_zip_original, xml_path, novo_hash)
                
                if resultado:
                    log(f"SUCESSO: Novo ZIP '{os.path.basename(str(resultado))}' criado."); sucessos += 1
                else:
                    log(f"ERRO: Falha ao recriar o ZIP para '{nome_xml}'.")
            except Exception as e:
                log(f"ERRO CRÍTICO ao processar '{nome_xml}': {e}")

        return True, f"Atualização concluída. {sucessos} de {len(xmls_corrigidos)} ZIPs foram recriados."

    def executar_verificacao_internacao_curta(self, caminho_pasta: str,
                                              log_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        log = lambda msg: self._log(msg, log_callback)
        log("INFO: Iniciando verificação de guias de internação com curta permanência...")
        
        try:
            xml_files = file_manager.listar_arquivos_051(caminho_pasta)
            if not xml_files:
                return True, "Nenhum arquivo .051 encontrado na pasta para verificação."

            log(f"INFO: {len(xml_files)} arquivo(s) XML encontrados. Analisando...")
            
            todas_as_guias_para_sinalizar = []
            for xml_file in xml_files:
                nome_arquivo = os.path.basename(xml_file)
                log(f"  Analisando arquivo: {nome_arquivo}")
                
                guias_encontradas = xml_parser.extrair_guias_internacao_curta_para_sinalizacao(xml_file)
                if guias_encontradas:
                    todas_as_guias_para_sinalizar.extend(guias_encontradas)
                    log(f"    → {len(guias_encontradas)} guia(s) problemática(s) encontrada(s)")
            
            log(f"INFO: Análise concluída. {len(todas_as_guias_para_sinalizar)} inconsistência(s) encontrada(s).")
            
            sucesso, mensagem = report_generator.gerar_csv_alertas_internacao_curta(
                todas_as_guias_para_sinalizar, caminho_pasta
            )
            
            return sucesso, mensagem

        except Exception as e:
            error_msg = f"Erro inesperado na verificação de internações curtas: {e}"
            log(f"ERRO CRÍTICO: {error_msg}")
            return False, error_msg