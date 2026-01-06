# src/models/repositories/execution_repository.py
"""
Execution Repository
Repositório para logs de execução.
"""

from typing import Optional, List
from datetime import datetime
from .base_repository import BaseRepository
from src.models.domain.execution_log import ExecutionLog
from src.models.domain.file_log import FileLog


class ExecutionRepository(BaseRepository[ExecutionLog]):
    """
    Repositório para ExecutionLog.
    """
    
    def __init__(self):
        super().__init__(ExecutionLog)
    
    def get_recent(self, limit: int = 10) -> List[ExecutionLog]:
        """
        Retorna execuções recentes.
        
        Args:
            limit: Número de execuções a retornar
            
        Returns:
            Lista de execuções ordenadas por data
        """
        return (self.session.query(ExecutionLog)
                .order_by(ExecutionLog.start_time.desc())
                .limit(limit)
                .all())
    
    def get_by_user(self, user_id: int) -> List[ExecutionLog]:
        """
        Retorna execuções de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de execuções do usuário
        """
        return (self.session.query(ExecutionLog)
                .filter_by(user_id=user_id)
                .order_by(ExecutionLog.start_time.desc())
                .all())
    
    def get_by_status(self, status: str) -> List[ExecutionLog]:
        """
        Retorna execuções por status.
        
        Args:
            status: Status da execução (RUNNING, COMPLETED, FAILED)
            
        Returns:
            Lista de execuções com o status especificado
        """
        return self.session.query(ExecutionLog).filter_by(status=status).all()
    
    def is_file_processed(self, file_hash: str) -> bool:
        """
        Verifica se um arquivo já foi processado com sucesso.
        
        Args:
            file_hash: Hash MD5 do conteúdo do arquivo
            
        Returns:
            True se o arquivo já foi processado, False caso contrário
        """
        existing = (self.session.query(FileLog)
                    .filter(FileLog.file_hash == file_hash)
                    .filter(FileLog.status == 'SUCCESS')
                    .first())
        return existing is not None
    
    def get_processed_file_info(self, file_hash: str) -> Optional[FileLog]:
        """
        Retorna informações de um arquivo já processado.
        
        Args:
            file_hash: Hash MD5 do conteúdo do arquivo
            
        Returns:
            FileLog se encontrado, None caso contrário
        """
        return (self.session.query(FileLog)
                .filter(FileLog.file_hash == file_hash)
                .filter(FileLog.status == 'SUCCESS')
                .first())

