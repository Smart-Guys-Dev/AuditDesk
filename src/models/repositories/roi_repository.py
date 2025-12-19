# src/models/repositories/roi_repository.py
"""
ROI Repository
Repositório para métricas de ROI.
"""

from typing import Optional, List
from .base_repository import BaseRepository
from src.models.domain.roi_metrics import ROIMetrics


class ROIRepository(BaseRepository[ROIMetrics]):
    """
    Repositório para ROIMetrics.
    """
    
    def __init__(self):
        super().__init__(ROIMetrics)
    
    def get_by_execution(self, execution_id: int) -> List[ROIMetrics]:
        """
        Retorna métricas ROI de uma execução.
        
        Args:
            execution_id: ID da execução
            
        Returns:
            Lista de métricas ROI
        """
        return self.session.query(ROIMetrics).filter_by(execution_id=execution_id).all()
    
    def get_by_rule(self, rule_id: str) -> List[ROIMetrics]:
        """
        Retorna métricas ROI de uma regra específica.
        
        Args:
            rule_id: ID da regra
            
        Returns:
            Lista de métricas ROI para a regra
        """
        return self.session.query(ROIMetrics).filter_by(rule_id=rule_id).all()
    
    def get_total_impact(self, execution_id: Optional[int] = None) -> float:
        """
        Calcula impacto financeiro total.
        
        Args:
            execution_id: ID da execução (None = todas)
            
        Returns:
            Soma do impacto financeiro
        """
        query = self.session.query(ROIMetrics)
        if execution_id:
            query = query.filter_by(execution_id=execution_id)
        
        total = sum(metric.financial_impact for metric in query.all())
        return total
