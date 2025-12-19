# src/models/domain/alert_metrics.py
"""
AlertMetrics domain model
Representa alertas identificados pelo sistema (ex: internações curtas).
Representa ROI POTENCIAL - glosas evitáveis com revisão manual.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class AlertMetrics(Base):
    """
    Armazena alertas identificados pelo sistema (ex: internações curtas).
    Representa ROI POTENCIAL - glosas evitáveis com revisão manual.
    """
    __tablename__ = 'alert_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey('execution_logs.id'))
    file_name = Column(String(255), nullable=False)
    alert_type = Column(String(100))  # 'INTERNACAO_CURTA', futuramente outros tipos
    alert_description = Column(String(255))
    financial_impact = Column(Float, default=0.0)  # ROI potencial
    status = Column(String(20), default='POTENCIAL')  # POTENCIAL, REVISADO, IGNORADO
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relacionamento
    execution = relationship("ExecutionLog", back_populates="alerts")

    def __repr__(self):
        return f"<AlertMetrics(type={self.alert_type}, impact=R${self.financial_impact:.2f})>"
