# src/controllers/auth_controller.py
"""
Authentication Controller
Gerencia autenticação e sessões de usuário.

✅ SEGURANÇA: Implementa rate limiting, session timeout e audit logging
"""

from typing import Optional
import time
import logging
from .base_controller import BaseController

# ✅ SEGURANÇA: Importar módulos de segurança
from src.infrastructure.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class AuthController(BaseController):
    """
    Controller para autenticação de usuários.
    
    ✅ SEGURANÇA IMPLEMENTADA:
    - Rate limiting (5 tentativas / 15 minutos)
    - Session timeout (1 hora de inatividade)
    - Audit logging de tentativas
    - Proteção contra enumeração de usuários
    """
    
    # ✅ SEGURANÇA: Configurações de sessão
    SESSION_TIMEOUT = 3600  # 1 hora em segundos
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.last_activity = None
        
        # ✅ SEGURANÇA: Rate limiter para prevenir brute force
        self.rate_limiter = RateLimiter(max_attempts=5, lockout_duration=900)
        
        logger.info("AuthController inicializado com rate limiting e session timeout")
    
    def login(self, username: str, password: str):
        """
        Autentica usuário com proteção contra brute force.
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            User object se sucesso, None se falhou
            
        Raises:
            Exception: Se conta está bloqueada por rate limiting
        """
        # ✅ SEGURANÇA: Verificar se está em lockout
        if self.rate_limiter.is_locked_out(username):
            remaining_attempts = self.rate_limiter.get_remaining_attempts(username)
            error_msg = f"Conta temporariamente bloqueada. Muitas tentativas falhadas. Aguarde 15 minutos."
            self.log_error(f"Tentativa de login bloqueada (rate limit): {username[:3]}***")
            raise Exception(error_msg)
        
        # Tentar autenticar
        from src.database import db_manager
        
        try:
            user = db_manager.authenticate_user(username, password)
            
            if user:
                # ✅ SUCESSO: Login bem-sucedido
                self.current_user = user
                self.last_activity = time.time()
                
                # ✅ SEGURANÇA: Limpar tentativas falhadas
                self.rate_limiter.record_attempt(username, success=True)
                
                self.log_info(f"✅ Login bem-sucedido: {username} (ID: {user.id}, Role: {user.role})")
                return user
            else:
                # ❌ FALHA: Credenciais inválidas
                # ✅ SEGURANÇA: Registrar tentativa falhada para rate limiting
                self.rate_limiter.record_attempt(username, success=False)
                
                remaining = self.rate_limiter.get_remaining_attempts(username)
                self.log_warning(
                    f"❌ Falha de autenticação: {username[:3]}*** "
                    f"(Tentativas restantes: {remaining})"
                )
                return None
                
        except Exception as e:
            self.log_error(f"Erro crítico ao autenticar: {str(e)[:100]}")
            # ✅ SEGURANÇA: Também conta como tentativa falhada em caso de erro
            self.rate_limiter.record_attempt(username, success=False)
            return None
    
    def logout(self):
        """Desloga usuário atual"""
        if self.current_user:
            username = self.current_user.username
            self.log_info(f"👋 Logout: {username}")
            self.current_user = None
            self.last_activity = None
    
    def get_current_user(self):
        """
        Retorna usuário logado atualmente.
        
        ✅ SEGURANÇA: Verifica timeout de sessão
        
        Returns:
            User object ou None se sessão expirou
        """
        # ✅ SEGURANÇA: Verificar timeout de sessão
        if self.current_user and self.last_activity:
            elapsed = time.time() - self.last_activity
            
            if elapsed > self.SESSION_TIMEOUT:
                username = self.current_user.username
                self.log_warning(
                    f"⏱️ Sessão expirada após {int(elapsed/60)} minutos de inatividade: {username}"
                )
                self.logout()
                return None
            
            # Atualizar última atividade
            self.last_activity = time.time()
        
        return self.current_user
    
    def check_session_valid(self) -> bool:
        """
        Verifica se a sessão atual é válida.
        
        Returns:
            True se sessão válida e ativa
        """
        user = self.get_current_user()  # Já verifica timeout internamente
        return user is not None
    
    def get_session_info(self) -> dict:
        """
        Retorna informações sobre a sessão atual.
        
        Returns:
            Dict com informações da sessão
        """
        if not self.current_user:
            return {"active": False}
        
        elapsed = time.time() - self.last_activity if self.last_activity else 0
        remaining = max(0, self.SESSION_TIMEOUT - elapsed)
        
        return {
            "active": True,
            "username": self.current_user.username,
            "user_id": self.current_user.id,
            "role": self.current_user.role,
            "elapsed_seconds": int(elapsed),
            "remaining_seconds": int(remaining),
            "timeout_minutes": int(self.SESSION_TIMEOUT / 60)
        }
    
    def admin_clear_lockout(self, username: str):
        """
        Limpa lockout de um usuário (função administrativa).
        
        Args:
            username: Username do usuário
        """
        if self.current_user and self.current_user.role == 'ADMIN':
            self.rate_limiter.clear_attempts(username)
            self.log_info(f"🔓 Admin {self.current_user.username} limpou lockout de: {username}")
        else:
            self.log_warning("Tentativa não autorizada de limpar lockout")
