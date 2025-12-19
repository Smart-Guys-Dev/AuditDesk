# src/models/domain/execution_log.py
"""
ExecutionLog domain model
Representa logs de execução de operações do sistema.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class ExecutionLog(Base):
    __tablename__ = 'execution_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable para compatibilidade
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    operation_type = Column(String(50), nullable=False)  # ex: 'HASH_UPDATE', 'VALIDATION'
    status = Column(String(20), default='RUNNING')  # RUNNING, COMPLETED, FAILED
    total_files = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    files = relationship("FileLog", back_populates="execution")
    user = relationship("User", back_populates="executions")
    alerts = relationship("AlertMetrics", back_populates="execution")

    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, op={self.operation_type}, status={self.status})>"
