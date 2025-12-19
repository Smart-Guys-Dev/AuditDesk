# src/infrastructure/security/session_manager.py
"""
Session Manager
Gerenciador de sessões com detecção de sessões concorrentes.

✅ SEGURANÇA: Previne múltiplos logins simultâneos
"""

import time
import secrets
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Gerenciador de sessões de usuário.
    
    Funcionalidades:
    - Geração de tokens únicos
    - Detecção de sessões concorrentes
    - Invalidação de sessões antigas
    - Tracking de última atividade
    """
    
    def __init__(self, allow_concurrent: bool = False):
        """
        Inicializa SessionManager.
        
        Args:
            allow_concurrent: Se True, permite múltiplas sessões por usuário
        """
        self.allow_concurrent = allow_concurrent
        
        # {user_id: {session_token: session_info}}
        self.active_sessions: Dict[int, Dict[str, dict]] = {}
        
        # Tempo de expiração de sessão (segundos)
        self.session_timeout = 3600  # 1 hora
        
        logger.info(
            f"SessionManager inicializado "
            f"(concurrent={allow_concurrent}, timeout={self.session_timeout}s)"
        )
    
    def create_session(self, user_id: int, ip_address: Optional[str] = None) -> Optional[str]:
        """
        Cria nova sessão para usuário.
        
        Args:
            user_id: ID do usuário
            ip_address: IP do cliente (opcional)
            
        Returns:
            Session token ou None se não permitido
        """
        # Verificar se há sessão ativa
        if user_id in self.active_sessions and not self.allow_concurrent:
            # Já existe sessão ativa
            existing_sessions = self.active_sessions[user_id]
            
            logger.warning(
                f"🚨 Tentativa de sessão concorrente detectada: "
                f"user_id={user_id}, sessões ativas={len(existing_sessions)}"
            )
            
            # Opção 1: Rejeitar nova sessão
            # return None
            
            # Opção 2: Invalidar sessões antigas (padrão)
            logger.info(f"Invalidando sessões antigas do user_id={user_id}")
            del self.active_sessions[user_id]
        
        # Gerar token único
        session_token = secrets.token_urlsafe(32)
        
        # Criar informações da sessão
        session_info = {
            'user_id': user_id,
            'token': session_token,
            'created_at': time.time(),
            'last_activity': time.time(),
            'ip_address': ip_address
        }
        
        # Armazenar sessão
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {}
        
        self.active_sessions[user_id][session_token] = session_info
        
        logger.info(f"✅ Sessão criada: user_id={user_id}, token={session_token[:8]}...")
        
        return session_token
    
    def validate_session(self, user_id: int, session_token: str) -> bool:
        """
        Valida se sessão é válida.
        
        Args:
            user_id: ID do usuário
            session_token: Token da sessão
            
        Returns:
            True se sessão válida
        """
        # Verificar se usuário tem sessões
        if user_id not in self.active_sessions:
            logger.warning(f"Nenhuma sessão ativa para user_id={user_id}")
            return False
        
        # Verificar se token existe
        if session_token not in self.active_sessions[user_id]:
            logger.warning(f"Token inválido para user_id={user_id}")
            return False
        
        session_info = self.active_sessions[user_id][session_token]
        
        # Verificar timeout
        elapsed = time.time() - session_info['last_activity']
        
        if elapsed > self.session_timeout:
            logger.info(f"⏱️ Sessão expirada: user_id={user_id} ({int(elapsed/60)} min)")
            # Remover sessão expirada
            del self.active_sessions[user_id][session_token]
            
            # Se não há mais sessões, remover user
            if not self.active_sessions[user_id]:
                del self.active_sessions[user_id]
            
            return False
        
        # Atualizar última atividade
        session_info['last_activity'] = time.time()
        
        return True
    
    def invalidate_session(self, user_id: int, session_token: Optional[str] = None):
        """
        Invalida sessão(ões) de um usuário.
        
        Args:
            user_id: ID do usuário
            session_token: Token específico (None = todas as sessões)
        """
        if user_id not in self.active_sessions:
            return
        
        if session_token:
            # Invalidar sessão específica
            if session_token in self.active_sessions[user_id]:
                del self.active_sessions[user_id][session_token]
                logger.info(f"Sessão invalidada: user_id={user_id}, token={session_token[:8]}...")
                
                # Se não há mais sessões, remover user
                if not self.active_sessions[user_id]:
                    del self.active_sessions[user_id]
        else:
            # Invalidar todas as sessões do usuário
            count = len(self.active_sessions[user_id])
            del self.active_sessions[user_id]
            logger.info(f"Todas as sessões invalidadas: user_id={user_id} ({count} sessões)")
    
    def get_active_sessions_count(self, user_id: int) -> int:
        """
        Retorna número de sessões ativas de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de sessões ativas
        """
        if user_id not in self.active_sessions:
            return 0
        
        return len(self.active_sessions[user_id])
    
    def get_session_info(self, user_id: int, session_token: str) -> Optional[dict]:
        """
        Retorna informações de uma sessão.
        
        Args:
            user_id: ID do usuário
            session_token: Token da sessão
            
        Returns:
            Dict com info da sessão ou None
        """
        if user_id not in self.active_sessions:
            return None
        
        if session_token not in self.active_sessions[user_id]:
            return None
        
        session_info = self.active_sessions[user_id][session_token].copy()
        
        # Calcular tempo restante
        elapsed = time.time() - session_info['last_activity']
        remaining = max(0, self.session_timeout - elapsed)
        
        session_info['elapsed_seconds'] = int(elapsed)
        session_info['remaining_seconds'] = int(remaining)
        
        return session_info
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove todas as sessões expiradas.
        
        Returns:
            Número de sessões removidas
        """
        removed_count = 0
        current_time = time.time()
        
        # Iterar sobre cópia para evitar modificação durante iteração
        for user_id in list(self.active_sessions.keys()):
            for token in list(self.active_sessions[user_id].keys()):
                session_info = self.active_sessions[user_id][token]
                elapsed = current_time - session_info['last_activity']
                
                if elapsed > self.session_timeout:
                    del self.active_sessions[user_id][token]
                    removed_count += 1
            
            # Remover user se não tem mais sessões
            if not self.active_sessions[user_id]:
                del self.active_sessions[user_id]
        
        if removed_count > 0:
            logger.info(f"🧹 Limpeza: {removed_count} sessões expiradas removidas")
        
        return removed_count


# Singleton global
_session_manager = None

def get_session_manager(allow_concurrent: bool = False) -> SessionManager:
    """
    Retorna instância singleton do SessionManager.
    
    Args:
        allow_concurrent: Permitir sessões concorrentes (apenas na primeira chamada)
        
    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(allow_concurrent=allow_concurrent)
    return _session_manager
