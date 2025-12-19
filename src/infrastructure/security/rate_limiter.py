# src/infrastructure/security/rate_limiter.py
"""
Rate Limiter
Proteção contra brute force attacks.
"""

import time
import logging
from typing import Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter para prevenir ataques de força bruta.
    """
    
    def __init__(self, max_attempts: int = 5, lockout_duration: int = 900):
        """
        Inicializa rate limiter.
        
        Args:
            max_attempts: Número máximo de tentativas
            lockout_duration: Duração do bloqueio em segundos (padrão: 15 min)
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        
        # {identifier: (attempt_count, first_attempt_time, lockout_until)}
        self._attempts: Dict[str, Tuple[int, float, float]] = {}
        
        logger.info(f"RateLimiter configurado: {max_attempts} tentativas, {lockout_duration}s lockout")
    
    def is_locked_out(self, identifier: str) -> bool:
        """
        Verifica se o identificador está bloqueado.
        
        Args:
            identifier: Username, IP, ou outro identificador
            
        Returns:
            True se bloqueado
        """
        if identifier not in self._attempts:
            return False
        
        count, first_time, lockout_until = self._attempts[identifier]
        
        # Verifica se ainda está no período de lockout
        if lockout_until and time.time() < lockout_until:
            remaining = int(lockout_until - time.time())
            logger.warning(f"Identificador '{self._mask_identifier(identifier)}' bloqueado por mais {remaining}s")
            return True
        
        # Lockout expirou, limpar
        if lockout_until and time.time() >= lockout_until:
            del self._attempts[identifier]
            logger.info(f"Lockout expirado para '{self._mask_identifier(identifier)}'")
        
        return False
    
    def record_attempt(self, identifier: str, success: bool):
        """
        Registra uma tentativa de autenticação.
        
        Args:
            identifier: Username, IP, ou outro identificador
            success: Se a tentativa foi bem sucedida
        """
        current_time = time.time()
        
        # Se sucesso, limpar tentativas
        if success:
            if identifier in self._attempts:
                del self._attempts[identifier]
                logger.info(f"Tentativas limpas para '{self._mask_identifier(identifier)}' após sucesso")
            return
        
        # Registrar tentativa falhada
        if identifier not in self._attempts:
            self._attempts[identifier] = (1, current_time, None)
            logger.warning(f"Tentativa #1 falhada para '{self._mask_identifier(identifier)}'")
        else:
            count, first_time, lockout_until = self._attempts[identifier]
            
            # Incrementar contador
            count += 1
            logger.warning(f"Tentativa #{count} falhada para '{self._mask_identifier(identifier)}'")
            
            # Se atingiu o máximo, ativar lockout
            if count >= self.max_attempts:
                lockout_until = current_time + self.lockout_duration
                logger.error(
                    f"🔒 LOCKOUT ativado para '{self._mask_identifier(identifier)}' "
                    f"após {count} tentativas. Bloqueado por {self.lockout_duration}s"
                )
            
            self._attempts[identifier] = (count, first_time, lockout_until)
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Retorna número de tentativas restantes antes do lockout.
        
        Args:
            identifier: Username, IP, ou outro identificador
            
        Returns:
            Número de tentativas restantes
        """
        if identifier not in self._attempts:
            return self.max_attempts
        
        count, _, lockout_until = self._attempts[identifier]
        
        if lockout_until and time.time() < lockout_until:
            return 0
        
        return max(0, self.max_attempts - count)
    
    def _mask_identifier(self, identifier: str) -> str:
        """
        Mascara identificador para logs (privacidade).
        
        Args:
            identifier: Identificador completo
            
        Returns:
            Identificador mascarado
        """
        if len(identifier) <= 3:
            return "***"
        return identifier[:2] + "***" + identifier[-1]
    
    def clear_attempts(self, identifier: str):
        """
        Limpa tentativas de um identificador (uso administrativo).
        
        Args:
            identifier: Identificador a limpar
        """
        if identifier in self._attempts:
            del self._attempts[identifier]
            logger.info(f"Tentativas limpas manualmente para '{self._mask_identifier(identifier)}'")
    
    def cleanup_expired(self):
        """
        Remove entradas expiradas (manutenção periódica).
        """
        current_time = time.time()
        expired = []
        
        for identifier, (count, first_time, lockout_until) in self._attempts.items():
            # Remove se lockout expirou há mais de 1 hora
            if lockout_until and (current_time - lockout_until) > 3600:
                expired.append(identifier)
        
        for identifier in expired:
            del self._attempts[identifier]
        
        if expired:
            logger.info(f"Limpeza: {len(expired)} entradas expiradas removidas")
