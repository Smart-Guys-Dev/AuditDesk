# src/controllers/workflow_controller.py
"""
Workflow Controller
Orquestra os workflows principais da aplicação.
Coordena entre Views e Business Logic.
"""

from typing import Optional, Callable, List
from .base_controller import BaseController


class WorkflowController(BaseController):
    """
    Controller para workflows principais:
    - Importação de faturas
    - Distribuição para auditores
    - Preparação de XMLs para correção
    """
    
    def __init__(self):
        super().__init__()
        self.current_invoices = []
        self.distribution_plan = {}
    
    def import_invoices(self, folder_path: str, callback: Optional[Callable] = None) -> dict:
        """
        Importa faturas de uma pasta.
        
        Args:
            folder_path: Caminho da pasta com XMLs
            callback: Função de callback para progresso
            
        Returns:
            dict com status e informações da importação
        """
        self.log_info(f"Iniciando importação de faturas de: {folder_path}")
        
        try:
            # Delega para o workflow_controller original
            from src.workflow_controller import WorkflowController as OriginalWF
            original = OriginalWF()
            result = original.processar_importacao_faturas(folder_path, callback)
            
            if result:
                self.current_invoices = original.lista_faturas_processadas
                self.log_info(f"Importação concluída: {len(self.current_invoices)} faturas")
            
            return {"success": True, "count": len(self.current_invoices)}
            
        except Exception as e:
            self.log_error(f"Erro na importação: {e}")
            return {"success": False, "error": str(e)}
    
    def distribute_invoices(self, auditor_names: List[str], callback: Optional[Callable] = None) -> dict:
        """
        Distribui faturas entre auditores.
        
        Args:
            auditor_names: Lista de nomes dos auditores
            callback: Função de callback para progresso
            
        Returns:
            dict com status e plano de distribuição
        """
        self.log_info(f"Distribuindo faturas para {len(auditor_names)} auditores")
        
        try:
            from src.workflow_controller import WorkflowController as OriginalWF
            original = OriginalWF()
            original.lista_faturas_processadas = self.current_invoices
            
            result = original.preparar_distribuicao_faturas(auditor_names, callback)
            
            if result:
                self.distribution_plan = original.plano_ultima_distribuicao
                self.log_info("Distribuição concluída com sucesso")
            
            return {"success": True, "plan": self.distribution_plan}
            
        except Exception as e:
            self.log_error(f"Erro na distribuição: {e}")
            return {"success": False, "error": str(e)}
    
    def prepare_for_correction(self, auditor_name: str, callback: Optional[Callable] = None) -> dict:
        """
        Prepara XMLs para correção de um auditor.
        
        Args:
            auditor_name: Nome do auditor
            callback: Função de callback para progresso
            
        Returns:
            dict com status
        """
        self.log_info(f"Preparando XMLs para correção - Auditor: {auditor_name}")
        
        try:
            from src.workflow_controller import WorkflowController as OriginalWF
            original = OriginalWF()
            
            result = original.preparar_xmls_para_correcao(auditor_name, callback)
            
            self.log_info("Preparação para correção concluída")
            return {"success": True}
            
        except Exception as e:
            self.log_error(f"Erro na preparação: {e}")
            return {"success": False, "error": str(e)}
