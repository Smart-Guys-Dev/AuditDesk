# src/controllers/validation_controller.py
"""
Validation Controller
Gerencia operações de validação de XMLs.
"""

from typing import Optional, Callable
from .base_controller import BaseController


class ValidationController(BaseController):
    """
    Controller para validações de XMLs.
    """
    
    def __init__(self):
        super().__init__()
    
    def validate_xmls(self, folder_path: str, callback: Optional[Callable] = None) -> dict:
        """
        Valida XMLs de uma pasta.
        
        Args:
            folder_path: Caminho da pasta com XMLs
            callback: Função de callback para progresso
            
        Returns:
            dict com resultados da validação
        """
        self.log_info(f"Validando XMLs em: {folder_path}")
        
        try:
            from src.workflow_controller import WorkflowController
            wf = WorkflowController()
            result = wf.executar_validacao_xmls(folder_path, callback)
            
            self.log_info("Validação concluída")
            return {"success": True, "result": result}
            
        except Exception as e:
            self.log_error(f"Erro na validação: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_with_xsd(self, folder_path: str, callback: Optional[Callable] = None) -> dict:
        """
        Valida XMLs com schema XSD.
        
        Args:
            folder_path: Caminho da pasta com XMLs
            callback: Função de callback para progresso
            
        Returns:
            dict com resultados da validação
        """
        self.log_info(f"Validando XMLs com XSD: {folder_path}")
        
        try:
            from src.workflow_controller import WorkflowController
            wf = WorkflowController()
            result = wf.validar_pasta_com_xsd(folder_path, callback)
            
            self.log_info("Validação XSD concluída")
            return {"success": True, "result": result}
            
        except Exception as e:
            self.log_error(f"Erro na validação XSD: {e}")
            return {"success": False, "error": str(e)}
