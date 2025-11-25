"""
Configuração centralizada de logging para Audit+ v2.0.
"""

import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, log_file='audit_plus.log'):
    """
    Configura logging centralizado para toda a aplicação.
    
    Args:
        level: Nível de logging (INFO, DEBUG, WARNING, ERROR)
        log_file: Nome do arquivo de log
    
    Returns:
        Logger configurado
    """
    # Criar diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato de logging
    log_format = '%(asctime)s - %(levelname)s - (%(name)s) - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar handlers
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
    
    # Configurar logging básico
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # Retornar logger principal
    logger = logging.getLogger('audit_plus')
    logger.setLevel(level)
    
    return logger

def get_logger(name):
    """
    Obtém um logger específico para um módulo.
    
    Args:
        name: Nome do módulo
    
    Returns:
        Logger configurado para o módulo
    """
    return logging.getLogger(f'audit_plus.{name}')
