from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default='AUDITOR') # ADMIN, AUDITOR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    executions = relationship("ExecutionLog", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

class ExecutionLog(Base):
    __tablename__ = 'execution_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Nullable para compatibilidade
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    operation_type = Column(String(50), nullable=False)  # ex: 'HASH_UPDATE', 'VALIDATION'
    status = Column(String(20), default='RUNNING')  # RUNNING, COMPLETED, FAILED
    total_files = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    files = relationship("FileLog", back_populates="execution")
    user = relationship("User", back_populates="executions")
    alerts = relationship("AlertMetrics", back_populates="execution")  # NOVO

    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, op={self.operation_type}, status={self.status})>"

class FileLog(Base):
    __tablename__ = 'file_logs'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('execution_logs.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(20), default='PENDING')  # SUCCESS, ERROR, SKIPPED
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    execution = relationship("ExecutionLog", back_populates="files")

    def __repr__(self):
        return f"<FileLog(file={self.file_name}, status={self.status})>"

class ROIMetrics(Base):
    __tablename__ = 'roi_metrics'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('execution_logs.id'), nullable=True)
    file_name = Column(String(255), nullable=False)
    rule_id = Column(String(100), nullable=False)
    rule_description = Column(String(255), nullable=True)
    correction_type = Column(String(20), nullable=False) # 'GUIA' ou 'ITEM'
    financial_impact = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ROIMetrics(rule={self.rule_id}, impact={self.financial_impact})>"

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
