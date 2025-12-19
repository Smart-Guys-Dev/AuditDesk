# src/models/domain/roi_metrics.py
"""
ROIMetrics domain model
Representa métricas de ROI (retorno sobre investimento) das correções.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from . import Base


class ROIMetrics(Base):
    __tablename__ = 'roi_metrics'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('execution_logs.id'), nullable=True)
    file_name = Column(String(255), nullable=False)
    rule_id = Column(String(100), nullable=False)
    rule_description = Column(String(255), nullable=True)
    correction_type = Column(String(20), nullable=False)  # 'GUIA' ou 'ITEM'
    financial_impact = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ROIMetrics(rule={self.rule_id}, impact={self.financial_impact})>"
