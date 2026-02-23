# src/database/models.py
"""
BACKWARD COMPATIBILITY LAYER
Este arquivo mantém a compatibilidade com código existente que importa de database.models
Todos os imports agora redirecionam para a nova estrutura MVC em models/domain/

DEPRECATED: Use imports diretos de src.models.domain ao invés deste arquivo.
"""

# Import Base e todos os modelos da nova estrutura
from src.models.domain import (
    Base,
    User,
    ExecutionLog,
    FileLog,
    ROIMetrics,
    AlertMetrics,
    AuditLog
)

# Re-export tudo para manter compatibilidade
__all__ = [
    'Base',
    'User',
    'ExecutionLog',
    'FileLog',
    'ROIMetrics',
    'AlertMetrics',
    'AuditLog'
]

