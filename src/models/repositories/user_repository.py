# src/models/repositories/user_repository.py
"""
User Repository
Repositório para operações com usuários.
"""

from typing import Optional
from .base_repository import BaseRepository
from src.models.domain.user import User


class UserRepository(BaseRepository[User]):
    """
    Repositório para entidade User.
    """
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Busca usuário por username.
        
        Args:
            username: Nome de usuário
            
        Returns:
            User ou None
        """
        return self.session.query(User).filter_by(username=username).first()
    
    def get_active_users(self) -> list:
        """
        Retorna apenas usuários ativos.
        
        Returns:
            Lista de usuários ativos
        """
        return self.session.query(User).filter_by(is_active=True).all()
    
    def get_by_role(self, role: str) -> list:
        """
        Retorna usuários por função.
        
        Args:
            role: Função do usuário (ADMIN, AUDITOR)
            
        Returns:
            Lista de usuários com a função especificada
        """
        return self.session.query(User).filter_by(role=role).all()
