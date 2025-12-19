# src/controllers/hash_controller.py
"""
Hash Controller
Gerencia operações de atualização de hash de arquivos.
"""

from typing import Optional, Callable, List
from .base_controller import BaseController


class HashController(BaseController):
    """
    Controller para operações de hash.
    """
    
    def __init__(self):
        super().__init__()
    
    def update_hash(self, auditor_name: str, selected_files: Optional[List[str]] = None, 
                   callback: Optional[Callable] = None) -> dict:
        """
        Atualiza hash de arquivos de um auditor.
        
        Args:
            auditor_name: Nome do auditor
            selected_files: Lista de arquivos selecionados (None = todos)
            callback: Função de callback para progresso
            
        Returns:
            dict com status da operação
        """
        self.log_info(f"Atualizando hash para auditor: {auditor_name}")
        
        try:
            from src.workflow_controller import WorkflowController
            wf = WorkflowController()
            result = wf.executar_atualizacao_hash(auditor_name, selected_files, callback)
            
            self.log_info("Atualização de hash concluída")
            return {"success": True, "result": result}
            
        except Exception as e:
            self.log_error(f"Erro na atualização de hash: {e}")
            return {"success": False, "error": str(e)}
    
    def get_files_for_auditor(self, auditor_name: str) -> dict:
        """
        Obtém lista de arquivos de um auditor.
        
        Args:
            auditor_name: Nome do auditor
            
        Returns:
            dict com lista de arquivos
        """
        self.log_info(f"Obtendo arquivos para auditor: {auditor_name}")
        
        try:
            from src.infrastructure.files.file_manager import FileManager
            fm = FileManager()
            files = fm.listar_arquivos_auditor(auditor_name)
            
            return {"success": True, "files": files}
            
        except Exception as e:
            self.log_error(f"Erro ao obter arquivos: {e}")
            return {"success": False, "error": str(e)}
