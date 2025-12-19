# src/models/domain/__init__.py
"""
Domain models package
Contém os modelos de entidades do banco de dados.
"""

from sqlalchemy.orm import declarative_base

# Base compartilhada para todos os modelos
Base = declarative_base()

# Import all models
from .user import User
from .execution_log import ExecutionLog
from .file_log import FileLog
from .roi_metrics import ROIMetrics
from .alert_metrics import AlertMetrics

__all__ = [
    'Base',
    'User',
    'ExecutionLog',
    'FileLog',
    'ROIMetrics',
    'AlertMetrics'
]
