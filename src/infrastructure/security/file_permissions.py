# src/infrastructure/security/file_permissions.py
"""
File Permissions Manager
Gerencia permissões seguras de arquivos e diretórios.

✅ SEGURANÇA: chmod 600 em arquivos sensíveis
"""

import os
import stat
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FilePermissionsManager:
    """
    Gerenciador de permissões de arquivos para segurança.
    
    Define permissões apropriadas em:
    - Banco de dados (600 - rw-------)
    - Logs (600)
    - Arquivos de configuração (600)
    - Diretórios sensíveis (700 - rwx------)
    """
    
    @staticmethod
    def secure_file(file_path: str, mode: int = 0o600) -> bool:
        """
        Define permissões seguras em um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            mode: Permissões (default: 0o600 = rw-------)
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"Arquivo não existe: {file_path}")
                return False
            
            if not path.is_file():
                logger.warning(f"Caminho não é um arquivo: {file_path}")
                return False
            
            # Aplicar permissões
            os.chmod(file_path, mode)
            
            # Verificar
            current_mode = stat.S_IMODE(os.stat(file_path).st_mode)
            
            logger.info(f"✅ Permissões aplicadas: {file_path} → {oct(current_mode)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar permissões em {file_path}: {e}")
            return False
    
    @staticmethod
    def secure_directory(dir_path: str, mode: int = 0o700) -> bool:
        """
        Define permissões seguras em um diretório.
        
        Args:
            dir_path: Caminho do diretório
            mode: Permissões (default: 0o700 = rwx------)
            
        Returns:
            True se sucesso
        """
        try:
            path = Path(dir_path)
            
            if not path.exists():
                logger.warning(f"Diretório não existe: {dir_path}")
                return False
            
            if not path.is_dir():
                logger.warning(f"Caminho não é um diretório: {dir_path}")
                return False
            
            # Aplicar permissões
            os.chmod(dir_path, mode)
            
            current_mode = stat.S_IMODE(os.stat(dir_path).st_mode)
            logger.info(f"✅ Permissões aplicadas: {dir_path}/ → {oct(current_mode)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar permissões em {dir_path}: {e}")
            return False
    
    @staticmethod
    def secure_all_files_in_directory(dir_path: str, file_mode: int = 0o600) -> int:
        """
        Aplica permissões seguras em todos os arquivos de um diretório.
        
        Args:
            dir_path: Caminho do diretório
            file_mode: Permissões para arquivos
            
        Returns:
            Número de arquivos protegidos
        """
        count = 0
        try:
            path = Path(dir_path)
            
            if not path.exists() or not path.is_dir():
                return 0
            
            for file_path in path.glob('*'):
                if file_path.is_file():
                    if FilePermissionsManager.secure_file(str(file_path), file_mode):
                        count += 1
            
            logger.info(f"✅ {count} arquivos protegidos em {dir_path}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Erro ao proteger arquivos em {dir_path}: {e}")
            return count
    
    @staticmethod
    def secure_application() -> dict:
        """
        Aplica permissões seguras em toda a aplicação.
        
        Returns:
            Dict com estatísticas da operação
        """
        stats = {
            "database": False,
            "logs_dir": False,
            "logs_files": 0,
            "config_dir": False,
            "config_files": 0,
            "total_success": 0
        }
        
        logger.info("🔒 Iniciando hardening de permissões de arquivos...")
        
        # 1. Banco de dados
        if os.path.exists("audit_plus.db"):
            stats["database"] = FilePermissionsManager.secure_file("audit_plus.db", 0o600)
            if stats["database"]:
                stats["total_success"] += 1
        
        # 2. Diretório de logs
        if os.path.exists("logs"):
            stats["logs_dir"] = FilePermissionsManager.secure_directory("logs", 0o700)
            stats["logs_files"] = FilePermissionsManager.secure_all_files_in_directory("logs", 0o600)
            if stats["logs_dir"]:
                stats["total_success"] += 1
            stats["total_success"] += stats["logs_files"]
        
        # 3. Diretório de configuração
        if os.path.exists("config"):
            stats["config_dir"] = FilePermissionsManager.secure_directory("config", 0o700)
            stats["config_files"] = FilePermissionsManager.secure_all_files_in_directory("config", 0o600)
            if stats["config_dir"]:
                stats["total_success"] += 1
            stats["total_success"] += stats["config_files"]
        
        # 4. Outros arquivos sensíveis
        sensitive_files = [
            ".env",
            "requirements.txt",
            "secrets.json"
        ]
        
        for file in sensitive_files:
            if os.path.exists(file):
                if FilePermissionsManager.secure_file(file, 0o600):
                    stats["total_success"] += 1
        
        logger.info(f"✅ Hardening completo: {stats['total_success']} itens protegidos")
        return stats
    
    @staticmethod
    def check_file_permissions(file_path: str) -> Optional[str]:
        """
        Verifica permissões de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            String com permissões em formato octal ou None se erro
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            mode = stat.S_IMODE(os.stat(file_path).st_mode)
            return oct(mode)
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissões de {file_path}: {e}")
            return None
