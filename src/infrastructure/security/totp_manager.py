# src/infrastructure/security/totp_manager.py
"""
TOTP Manager (Two-Factor Authentication)
Gerenciador de autenticação de dois fatores usando TOTP.

✅ SEGURANÇA: MFA/2FA usando Google Authenticator / Authy
"""

import logging
from typing import Optional, Tuple

# ✅ SEGURANÇA: TOTP para 2FA
try:
    import pyotp
    import qrcode
    from io import BytesIO
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False

logger = logging.getLogger(__name__)


class TOTPManager:
    """
    Gerenciador de TOTP (Time-based One-Time Password) para 2FA.
    
    Compatível com:
    - Google Authenticator
    - Microsoft Authenticator
    - Authy
    - FreeOTP
    """
    
    def __init__(self):
        if not TOTP_AVAILABLE:
            logger.warning(
                "⚠️ pyotp não instalado. 2FA não disponível. "
                "Instale com: pip install pyotp qrcode"
            )
    
    @staticmethod
    def generate_secret() -> Optional[str]:
        """
        Gera secret key para TOTP.
        
        Returns:
            Secret key (base32) ou None se pyotp não disponível
        """
        if not TOTP_AVAILABLE:
            logger.error("pyotp não disponível")
            return None
        
        secret = pyotp.random_base32()
        logger.info("✅ Secret TOTP gerado")
        return secret
    
    @staticmethod
    def get_provisioning_uri(secret: str, username: str, issuer: str = "AuditPlus") -> Optional[str]:
        """
        Gera URI de provisionamento para QR code.
        
        Args:
            secret: Secret key do usuário
            username: Nome de usuário
            issuer: Nome do emissor (padrão: AuditPlus)
            
        Returns:
            URI otpauth:// ou None
        """
        if not TOTP_AVAILABLE:
            return None
        
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=username, issuer_name=issuer)
        
        return uri
    
    @staticmethod
    def generate_qr_code(provisioning_uri: str) -> Optional[bytes]:
        """
        Gera QR code em formato PNG.
        
        Args:
            provisioning_uri: URI otpauth://
            
        Returns:
            Bytes do PNG ou None
        """
        if not TOTP_AVAILABLE:
            return None
        
        try:
            qr = qrcode.make(provisioning_uri)
            
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR code: {e}")
            return None
    
    @staticmethod
    def verify_code(secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verifica código TOTP fornecido pelo usuário.
        
        Args:
            secret: Secret key do usuário
            code: Código de 6 dígitos fornecido
            valid_window: Janela de validade (padrão: 1 = 30s antes/depois)
            
        Returns:
            True se código válido
        """
        if not TOTP_AVAILABLE:
            logger.error("pyotp não disponível")
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code, valid_window=valid_window)
            
            if is_valid:
                logger.info("✅ Código TOTP válido")
            else:
                logger.warning("❌ Código TOTP inválido")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erro ao verificar código TOTP: {e}")
            return False
    
    @staticmethod
    def get_current_code(secret: str) -> Optional[str]:
        """
        Obtém código atual (para debug/testes).
        
        Args:
            secret: Secret key
            
        Returns:
            Código de 6 dígitos ou None
        """
        if not TOTP_AVAILABLE:
            return None
        
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @staticmethod
    def setup_2fa_for_user(username: str) -> Optional[Tuple[str, str, bytes]]:
        """
        Configura 2FA completo para um usuário.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Tuple (secret, uri, qr_code_png) ou None
        """
        if not TOTP_AVAILABLE:
            logger.error("pyotp não disponível para setup 2FA")
            return None
        
        try:
            # 1. Gerar secret
            secret = TOTPManager.generate_secret()
            if not secret:
                return None
            
            # 2. Gerar URI
            uri = TOTPManager.get_provisioning_uri(secret, username)
            if not uri:
                return None
            
            # 3. Gerar QR code
            qr_code = TOTPManager.generate_qr_code(uri)
            if not qr_code:
                return None
            
            logger.info(f"✅ 2FA configurado para usuário: {username}")
            
            return (secret, uri, qr_code)
            
        except Exception as e:
            logger.error(f"Erro ao configurar 2FA: {e}")
            return None
