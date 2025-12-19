# src/infrastructure/security/input_sanitizer.py
"""
Input Sanitizer
Sanitização abrangente de inputs para prevenir XSS, injection, etc.

✅ SEGURANÇA: Sanitização de HTML, SQL, filenames, paths
"""

import re
import html
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Sanitizador de inputs para proteção contra ataques.
    
    Protege contra:
    - XSS (Cross-Site Scripting)
    - HTML Injection
    - Path Traversal
    - Filename Injection
    - SQL Injection (complementar ao ORM)
    """
    
    @staticmethod
    def sanitize_html(text: str, allow_tags: bool = False) -> str:
        """
        Remove ou escapa HTML de input.
        
        Args:
            text: Texto a sanitizar
            allow_tags: Se False, escapa todo HTML. Se True, permite tags seguras.
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        if not allow_tags:
            # Escapar todo HTML
            sanitized = html.escape(text)
            logger.debug(f"HTML escapado: {len(text)} chars")
            return sanitized
        else:
            # Permitir apenas tags seguras (usar bleach seria ideal)
            # Por enquanto, apenas escape
            return html.escape(text)
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitiza nome de arquivo.
        
        Args:
            filename: Nome do arquivo
            max_length: Comprimento máximo
            
        Returns:
            Nome de arquivo seguro
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path separators e caracteres perigosos
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        safe_name = re.sub(dangerous_chars, '_', filename)
        
        # Remove .. (path traversal)
        safe_name = safe_name.replace('..', '_')
        
        # Limitar comprimento
        if len(safe_name) > max_length:
            name, ext = Path(safe_name).stem, Path(safe_name).suffix
            safe_name = name[:max_length - len(ext)] + ext
        
        # Garantir que não está vazio
        if not safe_name or safe_name.isspace():
            safe_name = "unnamed_file"
        
        logger.debug(f"Filename sanitizado: '{filename}' → '{safe_name}'")
        return safe_name
    
    @staticmethod
    def sanitize_path(path: str) -> Optional[str]:
        """
        Valida e sanitiza caminho de arquivo/diretório.
        
        Args:
            path: Caminho a validar
            
        Returns:
            Caminho sanitizado ou None se inválido
        """
        if not path:
            return None
        
        # Prevenir path traversal
        dangerous_patterns = ['..', '~/', '/etc/', '/var/', 'C:\\Windows', '\\\\']
        
        for pattern in dangerous_patterns:
            if pattern in path:
                logger.warning(f"🚨 Path perigoso detectado: {pattern} em {path[:50]}")
                return None
        
        # Normalizar path
        try:
            normalized = str(Path(path).resolve())
            return normalized
        except Exception as e:
            logger.error(f"Erro ao normalizar path: {e}")
            return None
    
    @staticmethod
    def sanitize_sql_like(text: str) -> str:
        """
        Escapa caracteres especiais para LIKE SQL.
        
        Args:
            text: Texto para usar em LIKE
            
        Returns:
            Texto escapado
        """
        if not text:
            return ""
        
        # Escapar wildcards SQL LIKE
        escaped = text.replace('%', '\\%').replace('_', '\\_')
        
        return escaped
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """
        Valida e sanitiza email.
        
        Args:
            email: Email a validar
            
        Returns:
            Email sanitizado ou None se inválido
        """
        if not email:
            return None
        
        # Regex básico para email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        email = email.strip().lower()
        
        if re.match(email_pattern, email):
            return email
        
        logger.warning(f"Email inválido: {email[:20]}...")
        return None
    
    @staticmethod
    def sanitize_number(value: str, allow_decimal: bool = False, allow_negative: bool = False) -> Optional[float]:
        """
        Sanitiza e valida número.
        
        Args:
            value: Valor a converter
            allow_decimal: Permitir decimais
            allow_negative: Permitir negativos
            
        Returns:
            Número convertido ou None se inválido
        """
        if not value:
            return None
        
        try:
            # Remove espaços
            value = str(value).strip()
            
            # Converter
            if allow_decimal:
                num = float(value)
            else:
                num = int(value)
            
            # Verificar se negativo é permitido
            if not allow_negative and num < 0:
                logger.warning(f"Número negativo não permitido: {num}")
                return None
            
            return num
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Valor não é número: {value}")
            return None
    
    @staticmethod
    def sanitize_alphanumeric(text: str, allow_spaces: bool = False, allow_special: str = "") -> str:
        """
        Mantém apenas caracteres alfanuméricos.
        
        Args:
            text: Texto a sanitizar
            allow_spaces: Permitir espaços
            allow_special: String com caracteres especiais permitidos (ex: "._-")
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Criar padrão de caracteres permitidos
        allowed = r'a-zA-Z0-9'
        
        if allow_spaces:
            allowed += r'\s'
        
        if allow_special:
            # Escapar caracteres especiais regex
            allowed += re.escape(allow_special)
        
        pattern = f'[^{allowed}]'
        
        sanitized = re.sub(pattern, '', text)
        
        return sanitized
    
    @staticmethod
    def sanitize_json_key(key: str) -> str:
        """
        Sanitiza chave para uso em JSON/dict.
        
        Args:
            key: Chave a sanitizar
            
        Returns:
            Chave sanitizada (apenas alfanumérico e underscore)
        """
        if not key:
            return "unknown_key"
        
        # Apenas alfanumérico e underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', key)
        
        # Não pode começar com número
        if sanitized[0].isdigit():
            sanitized = '_' + sanitized
        
        return sanitized or "unknown_key"


# Funções de conveniência para importação direta
sanitize_html = InputSanitizer.sanitize_html
sanitize_filename = InputSanitizer.sanitize_filename
sanitize_path = InputSanitizer.sanitize_path
sanitize_email = InputSanitizer.sanitize_email
sanitize_number = InputSanitizer.sanitize_number
