# src/controllers/base_controller.py
"""
Base Controller
Classe base para controllers com funcionalidade comum.
"""

import logging

class BaseController:
    """
    Classe base para todos os controllers.
    Fornece funcionalidade comum como logging.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log mensagem de informação"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log mensagem de erro"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log mensagem de aviso"""
        self.logger.warning(message)
