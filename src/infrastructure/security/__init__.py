# src/infrastructure/security/__init__.py
"""
Security package
Funcionalidades de segurança centralizadas.
"""

from .password_manager import PasswordManager
from .rate_limiter import RateLimiter
from .validator import SecurityValidator
from .audit_logger import AuditLogger  # ✅ LGPD Compliance
from .file_permissions import FilePermissionsManager  # ✅ File Security
from .backup_manager import BackupManager, get_backup_key_from_env  # ✅ Encrypted Backups
from .totp_manager import TOTPManager  # ✅ 2FA/MFA
from .input_sanitizer import InputSanitizer, sanitize_html, sanitize_filename  # ✅ Input Sanitization
from .session_manager import SessionManager, get_session_manager  # ✅ Session Management

__all__ = [
    'PasswordManager', 
    'RateLimiter', 
    'SecurityValidator', 
    'AuditLogger',
    'FilePermissionsManager',
    'BackupManager',
    'get_backup_key_from_env',
    'TOTPManager',
    'InputSanitizer',
    'sanitize_html',
    'sanitize_filename',
    'SessionManager',
    'get_session_manager'
]
