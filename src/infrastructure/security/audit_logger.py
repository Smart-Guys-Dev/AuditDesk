# src/infrastructure/security/audit_logger.py
"""
Audit Logger
Sistema de auditoria para compliance LGPD Art. 46.

✅ COMPLIANCE: Registra WHO DID WHAT WHEN para todas operações sensíveis
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralizador de logs de auditoria para compliance.
    
    Registra todas as operações sensíveis:
    - CREATE, READ, UPDATE, DELETE de dados
    - LOGIN, LOGOUT de usuários
    - EXPORT de relatórios  
    - Acesso a dados pessoais
    - Alterações de configuração
    """
    
    # Ações permitidas
    ACTION_CREATE = "CREATE"
    ACTION_READ = "READ"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_EXPORT = "EXPORT"
    ACTION_ACCESS = "ACCESS"
    
    # Recursos
    RESOURCE_USERS = "users"
    RESOURCE_EXECUTIONS = "executions"
    RESOURCE_FILES = "files"
    RESOURCE_REPORTS = "reports"
    RESOURCE_SETTINGS = "settings"
    RESOURCE_AUTH = "authentication"
    
    @staticmethod
    def log(user_id: Optional[int], action: str, resource: str, 
            details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """
        Registra ação de auditoria no banco de dados.
        
        Args:
            user_id: ID do usuário que realizou a ação (None se sistema)
            action: Tipo de ação (CREATE, READ, UPDATE, DELETE, etc)
            resource: Recurso afetado (users, executions, files, etc)
            details: Detalhes adicionais em formato dict
            ip_address: IP do cliente (se aplicável)
        """
        from src.database import db_manager
        
        try:
            session = db_manager.get_session()
            
            # Importar modelo AuditLog
            from src.models.domain.audit_log import AuditLog
            
            # Serializar detalhes para JSON
            details_json = json.dumps(details) if details else None
            
            # Criar registro de auditoria
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                details=details_json,
                ip_address=ip_address,
                timestamp=datetime.now()
            )
            
            session.add(audit_entry)
            session.commit()
            
            # Log também no logger padrão
            user_info = f"User {user_id}" if user_id else "System"
            logger.info(
                f"📋 AUDIT: {user_info} - {action} on {resource} "
                f"{f'(IP: {ip_address})' if ip_address else ''}"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar auditoria: {e}")
            # Não propagar exceção - auditoria não deve quebrar operação principal
        
        finally:
            if 'session' in locals():
                session.close()
    
    @staticmethod
    def log_user_action(user_id: int, action: str, resource: str, 
                       record_id: Optional[int] = None, changes: Optional[Dict] = None):
        """
        Atalho para logar ações de usuário.
        
        Args:
            user_id: ID do usuário
            action: Ação realizada
            resource: Recurso afetado
            record_id: ID do registro afetado (se aplicável)
            changes: Mudanças realizadas (para UPDATE)
        """
        details = {}
        if record_id:
            details['record_id'] = record_id
        if changes:
            details['changes'] = changes
        
        AuditLogger.log(user_id, action, resource, details)
    
    @staticmethod
    def log_login(user_id: int, username: str, success: bool, ip_address: Optional[str] = None):
        """
        Registra tentativa de login.
        
        Args:
            user_id: ID do usuário (se sucesso)
            username: Nome de usuário
            success: Se login foi bem-sucedido
            ip_address: IP do cliente
        """
        action = AuditLogger.ACTION_LOGIN if success else "LOGIN_FAILED"
        details = {
            "username": username,
            "success": success
        }
        
        AuditLogger.log(
            user_id if success else None,
            action,
            AuditLogger.RESOURCE_AUTH,
            details,
            ip_address
        )
    
    @staticmethod
    def log_logout(user_id: int, username: str):
        """
        Registra logout de usuário.
        
        Args:
            user_id: ID do usuário
            username: Nome de usuário
        """
        AuditLogger.log(
            user_id,
            AuditLogger.ACTION_LOGOUT,
            AuditLogger.RESOURCE_AUTH,
            {"username": username}
        )
    
    @staticmethod
    def log_data_export(user_id: int, export_type: str, record_count: int):
        """
        Registra exportação de dados (crítico para LGPD).
        
        Args:
            user_id: ID do usuário que exportou
            export_type: Tipo de exportação (relatorio_roi, relatorio_glosas, etc)
            record_count: Quantidade de registros exportados
        """
        details = {
            "export_type": export_type,
            "record_count": record_count
        }
        
        AuditLogger.log(
            user_id,
            AuditLogger.ACTION_EXPORT,
            AuditLogger.RESOURCE_REPORTS,
            details
        )
    
    @staticmethod
    def get_user_audit_trail(user_id: int, limit: int = 100):
        """
        Retorna trilha de auditoria de um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Limite de registros
            
        Returns:
            Lista de registros de auditoria
        """
        from src.database import db_manager
        from src.models.domain.audit_log import AuditLog
        
        session = db_manager.get_session()
        try:
            records = (session.query(AuditLog)
                      .filter_by(user_id=user_id)
                      .order_by(AuditLog.timestamp.desc())
                      .limit(limit)
                      .all())
            
            return records
        finally:
            session.close()
    
    @staticmethod
    def get_resource_audit_trail(resource: str, record_id: Optional[int] = None, limit: int = 100):
        """
        Retorna trilha de auditoria de um recurso.
        
        Args:
            resource: Tipo de recurso (users, executions, etc)
            record_id: ID específico do registro (opcional)
            limit: Limite de registros
            
        Returns:
            Lista de registros de auditoria
        """
        from src.database import db_manager
        from src.models.domain.audit_log import AuditLog
        
        session = db_manager.get_session()
        try:
            query = session.query(AuditLog).filter_by(resource=resource)
            
            if record_id:
                # Filtrar por record_id nos detalhes JSON
                query = query.filter(AuditLog.details.like(f'%"record_id": {record_id}%'))
            
            records = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            
            return records
        finally:
            session.close()
