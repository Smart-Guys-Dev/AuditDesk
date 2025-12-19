# src/controllers/report_controller.py
"""
Report Controller
Gerencia geração de relatórios.
"""

from typing import Optional
from .base_controller import BaseController


class ReportController(BaseController):
    """
    Controller para geração de relatórios.
    """
    
    def __init__(self):
        super().__init__()
    
    def generate_distribution_report(self, distribution_plan: dict, output_folder: str) -> dict:
        """
        Gera relatório de distribuição.
        
        Args:
            distribution_plan: Plano de distribuição
            output_folder: Pasta de saída
            
        Returns:
            dict com status e caminho do arquivo
        """
        self.log_info("Gerando relatório de distribuição")
        
        try:
            from src.infrastructure.reports.report_generator import gerar_relatorio_distribuicao
            success, file_path = gerar_relatorio_distribuicao(distribution_plan, output_folder)
            
            if success:
                self.log_info(f"Relatório gerado: {file_path}")
                return {"success": True, "file_path": file_path}
            else:
                return {"success": False, "error": "Falha ao gerar relatório"}
                
        except Exception as e:
            self.log_error(f"Erro ao gerar relatório: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_glosa_report(self, execution_id: Optional[int] = None) -> dict:
        """
        Gera relatório de glosas.
        
        Args:
            execution_id: ID da execução (None = última)
            
        Returns:
            dict com status
        """
        self.log_info(f"Gerando relatório de glosas - Execução: {execution_id}")
        
        try:
            from src.relatorio_glosas.reporter import GlosaReporter
            reporter = GlosaReporter()
            result = reporter.gerar_relatorio(execution_id)
            
            self.log_info("Relatório de glosas gerado")
            return {"success": True, "result": result}
            
        except Exception as e:
            self.log_error(f"Erro ao gerar relatório de glosas: {e}")
            return {"success": False, "error": str(e)}
