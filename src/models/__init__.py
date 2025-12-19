# src/models/__init__.py
"""
Models package - Camada de Dados
Contém modelos de domínio, repositórios e serviços de dados.
"""

from .domain import *
from .repositories import *
from .services import *

__all__ = ['domain', 'repositories', 'services']
