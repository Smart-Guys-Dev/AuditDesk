# src/models/domain/audit_log.py
"""
Audit Log Model
Registro de auditoria para compliance (LGPD).
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class AuditLog(Base):
    """
    Log de auditoria para rastreamento de ações.
    
    ✅ COMPLIANCE: Requisito LGPD Art. 46
    """
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Ação realizada
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    resource = Column(String(100), nullable=False)  # users, executions, files, etc
    
    # Detalhes da ação (JSON ou texto)
    details = Column(Text, nullable=True)
    
    # Informações de contexto
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(255), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relacionamento
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource}', user_id={self.user_id})>"
