# src/infrastructure/security/password_manager.py
"""
Password Manager
Gerenciamento seguro de senhas usando bcrypt.
"""

import bcrypt
import logging

logger = logging.getLogger(__name__)


class PasswordManager:
    """
    Gerenciador de senhas com bcrypt.
    Substitui SHA-256 inseguro por bcrypt com salt.
    """
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """
        Cria hash seguro da senha usando bcrypt.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash bcrypt da senha (bytes)
        """
        if not password:
            raise ValueError("Senha não pode ser vazia")
        
        # bcrypt automaticamente adiciona salt único
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
        
        logger.debug("Senha hasheada com bcrypt (salt único gerado)")
        return hashed
    
    @staticmethod
    def verify_password(password: str, password_hash: bytes) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            password_hash: Hash bcrypt armazenado
            
        Returns:
            True se senha correta, False caso contrário
        """
        if not password or not password_hash:
            return False
        
        try:
            password_bytes = password.encode('utf-8')
            
            # Se password_hash é string (migração de SHA-256), converter
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            
            result = bcrypt.checkpw(password_bytes, password_hash)
            logger.debug(f"Verificação de senha: {'✓ Sucesso' if result else '✗ Falhou'}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na verificação de senha: {e}")
            return False
    
    @staticmethod
    def needs_rehash(password_hash: bytes, rounds: int = 12) -> bool:
        """
        Verifica se o hash precisa ser atualizado (custo mudou).
        
        Args:
            password_hash: Hash atual
            rounds: Número de rounds desejado
            
        Returns:
            True se precisa rehash
        """
        try:
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            
            # Verifica se é bcrypt válido
            if not password_hash.startswith(b'$2b$'):
                return True  # Não é bcrypt, precisa migration
            
            # Extrai custo atual do hash
            parts = password_hash.split(b'$')
            if len(parts) >= 3:
                current_rounds = int(parts[2])
                return current_rounds < rounds
            
            return True
        except:
            return True
