# src/models/repositories/base_repository.py
"""
Base Repository
Classe base para todos os repositórios com operações CRUD genéricas.
"""

from typing import TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from src.database import db_manager

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositório base com operações CRUD genéricas.
    
    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self):
                super().__init__(User)
    """
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self.session = db_manager.get_session()
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Busca entidade por ID"""
        return self.session.query(self.model_class).filter_by(id=id).first()
    
    def get_all(self) -> List[T]:
        """Retorna todas as entidades"""
        return self.session.query(self.model_class).all()
    
    def create(self, **kwargs) -> T:
        """
        Cria nova entidade.
        
        Args:
            **kwargs: Atributos da entidade
            
        Returns:
            Entidade criada
        """
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Atualiza entidade existente.
        
        Args:
            id: ID da entidade
            **kwargs: Atributos a atualizar
            
        Returns:
            Entidade atualizada ou None se não encontrada
        """
        entity = self.get_by_id(id)
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            self.session.commit()
        return entity
    
    def delete(self, id: int) -> bool:
        """
        Deleta entidade.
        
        Args:
            id: ID da entidade
            
        Returns:
            True se deletado, False se não encontrado
        """
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """Retorna contagem total de entidades"""
        return self.session.query(self.model_class).count()
