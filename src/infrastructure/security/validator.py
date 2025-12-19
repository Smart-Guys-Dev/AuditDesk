# src/infrastructure/security/validator.py
"""
Security Validator
Validações de segurança (senhas fortes, inputs, etc).
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Validador de segurança para inputs e políticas.
    """
    
    # Requisitos de senha forte
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    
    # Caracteres especiais permitidos
    SPECIAL_CHARS = r"!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, str]:
        """
        Valida força da senha contra política de segurança.
        
        Args:
            password: Senha a validar
            
        Returns:
            Tupla (válido: bool, mensagem: str)
        """
        if not password:
            return False, "Senha não pode ser vazia"
        
        # Comprimento mínimo
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, f"Senha deve ter no mínimo {cls.MIN_PASSWORD_LENGTH} caracteres"
        
        # Letras maiúsculas
        if cls.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
        
        # Letras minúsculas
        if cls.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            return False, "Senha deve conter pelo menos uma letra minúscula"
        
        # Dígitos
        if cls.REQUIRE_DIGITS and not re.search(r"\d", password):
            return False, "Senha deve conter pelo menos um número"
        
        # Caracteres especiais
        if cls.REQUIRE_SPECIAL and not re.search(f"[{re.escape(cls.SPECIAL_CHARS)}]", password):
            return False, f"Senha deve conter pelo menos um caractere especial ({cls.SPECIAL_CHARS[:10]}...)"
        
        # Senhas comuns (pequena lista, expandir conforme necessário)
        common_passwords = [
            "password123", "admin123", "12345678901", "qwerty123456",
            "Password@123", "Admin@12345"
        ]
        if password.lower() in [p.lower() for p in common_passwords]:
            return False, "Senha muito comum, escolha uma senha mais forte"
        
        logger.info("Senha validada com sucesso (atende política de segurança)")
        return True, "Senha segura"
    
    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, str]:
        """
        Valida format de username.
        
        Args:
            username: Username a validar
            
        Returns:
            Tupla (válido: bool, mensagem: str)
        """
        if not username:
            return False, "Username não pode ser vazio"
        
        if len(username) < 3:
            return False, "Username deve ter no mínimo 3 caracteres"
        
        if len(username) > 50:
            return False, "Username deve ter no máximo 50 caracteres"
        
        # Apenas alfanuméricos e alguns caracteres especiais
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            return False, "Username deve conter apenas letras, números, '_', '.' ou '-'"
        
        # Não pode começar com número
        if username[0].isdigit():
            return False, "Username não pode começar com número"
        
        return True, "Username válido"
    
    @classmethod
    def sanitize_log_message(cls, message: str, sensitive_fields: list = None) -> str:
        """
        Sanitiza mensagem de log removendo informações sensíveis.
        
        Args:
            message: Mensagem original
            sensitive_fields: Lista de campos sensíveis a mascarar
            
        Returns:
            Mensagem sanitizada
        """
        if sensitive_fields is None:
            sensitive_fields = ['password', 'senha', 'token', 'secret', 'key', 'apikey']
        
        sanitized = message
        
        # Padrões comuns de dados sensíveis
        patterns = [
            # password=xxxx, senha=xxxx
            (r'(password|senha|pass|pwd)\s*=\s*["\']?([^"\'\s,}]+)', r'\1=***'),
            # "password": "xxxx"
            (r'(["\'])(password|senha|token|secret|key)(["\'])\s*:\s*(["\'])([^"\']+)(["\'])', r'\1\2\3:\4***\6'),
            # Tokens longos (20+ caracteres alfanuméricos)
            (r'\b([a-zA-Z0-9]{20,})\b', r'***TOKEN***'),
        ]
        
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def validate_file_path(cls, file_path: str) -> Tuple[bool, str]:
        """
        Valida caminho de arquivo (previne path traversal).
        
        Args:
            file_path: Caminho a validar
            
        Returns:
            Tupla (válido: bool, mensagem: str)
        """
        if not file_path:
            return False, "Caminho não pode ser vazio"
        
        # Previne path traversal
        dangerous_patterns = ['..', '~/', '/etc/', '/var/', 'C:\\Windows', '\\\\']
        
        for pattern in dangerous_patterns:
            if pattern in file_path:
                logger.warning(f"🚨 Path traversal attempt detectado: {pattern} em {file_path[:50]}")
                return False, f"Caminho contém padrão perigoso: {pattern}"
        
        return True, "Caminho válido"
