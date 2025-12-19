# src/controllers/dashboard_controller.py
"""
Dashboard Controller
Gerencia dados e métricas do dashboard.
"""

from typing import Optional
from .base_controller import BaseController


class DashboardController(BaseController):
    """
    Controller para dashboard e métricas.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_roi_metrics(self, execution_id: Optional[int] = None) -> dict:
        """
        Obtém métricas de ROI.
        
        Args:
            execution_id: ID da execução (None = todas)
            
        Returns:
            dict com métricas de ROI
        """
        self.log_info(f"Obtendo métricas ROI - Execução: {execution_id}")
        
        try:
            from src.database import db_manager
            metrics = db_manager.get_roi_stats(execution_id)
            
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            self.log_error(f"Erro ao obter métricas ROI: {e}")
            return {"success": False, "error": str(e)}
    
    def get_execution_stats(self, limit: int = 10) -> dict:
        """
        Obtém estatísticas de execuções.
        
        Args:
            limit: Número de execuções a retornar
            
        Returns:
            dict com estatísticas
        """
        self.log_info(f"Obtendo estatísticas de execuções (limit={limit})")
        
        try:
            from src.database import db_manager
            stats = db_manager.get_recent_executions(limit)
            
            return {"success": True, "stats": stats}
            
        except Exception as e:
            self.log_error(f"Erro ao obter estatísticas: {e}")
            return {"success": False, "error": str(e)}
    
    def get_kpi_data(self) -> dict:
        """
        Obtém dados de KPIs para dashboard.
        
        Returns:
            dict com KPIs
        """
        self.log_info("Obtendo KPIs do dashboard")
        
        try:
            from src.database import db_manager
            
            total_executions = db_manager.count_executions()
            total_files = db_manager.count_processed_files()
            avg_success_rate = db_manager.get_success_rate()
            
            return {
                "success": True,
                "kpis": {
                    "total_executions": total_executions,
                    "total_files": total_files,
                    "success_rate": avg_success_rate
                }
            }
            
        except Exception as e:
            self.log_error(f"Erro ao obter KPIs: {e}")
            return {"success": False, "error": str(e)}
