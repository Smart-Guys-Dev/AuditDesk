# src/models/domain/file_log.py
"""
FileLog domain model
Representa logs de processamento de arquivos individuais.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class FileLog(Base):
    __tablename__ = 'file_logs'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('execution_logs.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(32), nullable=True, index=True)  # MD5 hash para deduplicação
    status = Column(String(20), default='PENDING')  # SUCCESS, ERROR, SKIPPED
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    execution = relationship("ExecutionLog", back_populates="files")

    def __repr__(self):
        return f"<FileLog(file={self.file_name}, status={self.status})>"

