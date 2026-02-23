"""
Configuração centralizada de logging para Audit+ v3.0.
"""

import logging
import sys
from pathlib import Path


class CleanFormatter(logging.Formatter):
    """Formatter que mostra só a última parte do nome do módulo."""

    def format(self, record):
        # 'src.database.db_manager' → 'db_manager'
        record.short_name = record.name.rsplit('.', 1)[-1]
        return super().format(record)


def setup_logging(level=logging.INFO, log_file='audit_plus.log'):
    """
    Configura logging centralizado para toda a aplicação.

    Returns:
        Logger configurado
    """
    # Criar diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Formato limpo — terminal mostra só o essencial
    fmt = CleanFormatter(
        fmt='%(asctime)s - %(levelname)s - (%(short_name)s) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Handler: Terminal (stdout)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.setLevel(level)

    # Handler: Arquivo (mais detalhado)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(CleanFormatter(
        fmt='%(asctime)s - %(levelname)s - (%(name)s) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    ))
    file_handler.setLevel(logging.DEBUG)

    # Root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console)
    root.addHandler(file_handler)

    # Silenciar bibliotecas ruidosas
    for noisy in ('matplotlib', 'PIL', 'sqlalchemy.engine', 'urllib3', 'chardet'):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Logger principal da aplicação
    logger = logging.getLogger('audit_plus')
    logger.setLevel(level)

    return logger


def get_logger(name):
    """Obtém um logger específico para um módulo."""
    return logging.getLogger(f'audit_plus.{name}')
