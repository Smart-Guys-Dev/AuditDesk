# src/models/domain/user.py
"""
User domain model
Representa usuários do sistema.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    birth_date = Column(Date, nullable=True)
    role = Column(String(20), default='AUDITOR')  # ADMIN, AUDITOR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    executions = relationship("ExecutionLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

