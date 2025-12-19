# src/infrastructure/security/backup_manager.py
"""
Encrypted Backup Manager
Sistema de backup automático criptografado.

✅ SEGURANÇA: Backups criptografados com Fernet (AES-256)
"""

import os
import tarfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# ✅ SEGURANÇA: Criptografia de backups
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Gerenciador de backups criptografados.
    
    Cria backups tar.gz criptografados de:
    - Banco de dados
    - Arquivos de configuração
    - Logs (opcional)
    """
    
    def __init__(self, backup_key: Optional[bytes] = None):
        """
        Inicializa BackupManager.
        
        Args:
            backup_key: Chave de criptografia (bytes). Se None, gera nova chave.
        """
        if backup_key is None:
            # Gerar nova chave (armazenar em variável de ambiente em produção!)
            self.key = Fernet.generate_key()
            logger.warning(
                "⚠️ Nova chave de backup gerada. "
                "IMPORTANTE: Armazene em variável de ambiente: "
                f"BACKUP_KEY={self.key.decode()}"
            )
        else:
            self.key = backup_key
        
        self.cipher = Fernet(self.key)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, include_logs: bool = False) -> Optional[str]:
        """
        Cria backup criptografado da aplicação.
        
        Args:
            include_logs: Se True, inclui logs no backup
            
        Returns:
            Caminho do arquivo de backup criado ou None se erro
        """
        try:
            # Timestamp para nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tar_file = self.backup_dir / f"backup_{timestamp}.tar.gz"
            encrypted_file = self.backup_dir / f"backup_{timestamp}.tar.gz.enc"
            
            logger.info(f"🔄 Iniciando backup criptografado: {encrypted_file.name}")
            
            # 1. Criar tar.gz
            with tarfile.open(tar_file, "w:gz") as tar:
                # Banco de dados
                if os.path.exists("audit_plus.db"):
                    tar.add("audit_plus.db")
                    logger.debug("  ✓ audit_plus.db adicionado")
                
                # Config
                if os.path.exists("config"):
                    tar.add("config/")
                    logger.debug("  ✓ config/ adicionado")
                
                # Logs (opcional)
                if include_logs and os.path.exists("logs"):
                    tar.add("logs/")
                    logger.debug("  ✓ logs/ adicionado")
            
            # 2. Criptografar
            with open(tar_file, 'rb') as f:
                plaintext = f.read()
            
            encrypted_data = self.cipher.encrypt(plaintext)
            
            with open(encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            # 3. Remover tar.gz original (não criptografado)
            tar_file.unlink()
            
            file_size = encrypted_file.stat().st_size / 1024  # KB
            logger.info(f"✅ Backup criado: {encrypted_file.name} ({file_size:.1f} KB)")
            
            return str(encrypted_file)
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            # Limpar arquivos temporários
            if tar_file.exists():
                tar_file.unlink()
            return None
    
    def restore_backup(self, encrypted_file: str, restore_dir: str = "restore") -> bool:
        """
        Restaura backup criptografado.
        
        Args:
            encrypted_file: Caminho do arquivo .enc
            restore_dir: Diretório onde restaurar
            
        Returns:
            True se sucesso
        """
        try:
            encrypted_path = Path(encrypted_file)
            
            if not encrypted_path.exists():
                logger.error(f"Arquivo de backup não encontrado: {encrypted_file}")
                return False
            
            logger.info(f"🔄 Restaurando backup: {encrypted_path.name}")
            
            # 1. Descriptografar
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            plaintext = self.cipher.decrypt(encrypted_data)
            
            # 2. Salvar tar.gz temporário
            temp_tar = encrypted_path.with_suffix('')  # Remove .enc
            
            with open(temp_tar, 'wb') as f:
                f.write(plaintext)
            
            # 3. Extrair
            restore_path = Path(restore_dir)
            restore_path.mkdir(exist_ok=True)
            
            with tarfile.open(temp_tar, "r:gz") as tar:
                tar.extractall(restore_path)
            
            # 4. Limpar temporário
            temp_tar.unlink()
            
            logger.info(f"✅ Backup restaurado em: {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def list_backups(self) -> list:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de dicts com informações dos backups
        """
        backups = []
        
        for enc_file in self.backup_dir.glob("*.enc"):
            try:
                stat_info = enc_file.stat()
                backups.append({
                    "filename": enc_file.name,
                    "path": str(enc_file),
                    "size_kb": stat_info.st_size / 1024,
                    "created": datetime.fromtimestamp(stat_info.st_ctime),
                    "modified": datetime.fromtimestamp(stat_info.st_mtime)
                })
            except Exception as e:
                logger.warning(f"Erro ao ler info de {enc_file}: {e}")
        
        # Ordenar por data de criação (mais recente primeiro)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove backups antigos, mantendo apenas os N mais recentes.
        
        Args:
            keep_count: Número de backups a manter
            
        Returns:
            Número de backups removidos
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        removed_count = 0
        for backup in backups[keep_count:]:
            try:
                Path(backup['path']).unlink()
                logger.info(f"🗑️ Backup antigo removido: {backup['filename']}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Erro ao remover backup {backup['filename']}: {e}")
        
        return removed_count


def get_backup_key_from_env() -> Optional[bytes]:
    """
    Obtém chave de backup de variável de ambiente.
    
    Returns:
        Chave em bytes ou None se não definida
    """
    key_str = os.getenv("BACKUP_KEY")
    
    if key_str:
        return key_str.encode()
    
    return None
