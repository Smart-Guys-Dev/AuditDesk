"""
Configurações persistentes do usuário.

Salva e restaura preferências automaticamente.
"""
from PyQt6.QtCore import QSettings


class AppSettings:
    """Gerencia configurações persistentes da aplicação"""
    
    def __init__(self):
        self.settings = QSettings("PedroLucas", "Glox")
    
    # Últimas pastas usadas
    def save_last_folder(self, key: str, path: str):
        """Salva última pasta usada"""
        self.settings.setValue(f"last_folder/{key}", path)
    
    def get_last_folder(self, key: str, default: str = "") -> str:
        """Recupera última pasta usada"""
        return self.settings.value(f"last_folder/{key}", default)
    
    # Geometria da janela
    def save_window_geometry(self, geometry):
        """Salva posição e tamanho da janela"""
        self.settings.setValue("window/geometry", geometry)
    
    def get_window_geometry(self):
        """Recupera geometria da janela"""
        return self.settings.value("window/geometry")
    
    # Estado da janela
    def save_window_state(self, state):
        """Salva estado da janela (maximizado, etc)"""
        self.settings.setValue("window/state", state)
    
    def get_window_state(self):
        """Recupera estado da janela"""
        return self.settings.value("window/state")
    
    # Preferências gerais
    def save_preference(self, key: str, value):
        """Salva preferência genérica"""
        self.settings.setValue(f"preferences/{key}", value)
    
    def get_preference(self, key: str, default=None):
        """Recupera preferência genérica"""
        return self.settings.value(f"preferences/{key}", default)
    
    # Auditores recentes
    def save_recent_auditors(self, auditors: list):
        """Salva lista de auditores recentes"""
        self.settings.setValue("recent/auditors", auditors)
    
    def get_recent_auditors(self) -> list:
        """Recupera auditores recentes"""
        return self.settings.value("recent/auditors", [])
    
    # Limpar tudo
    def clear_all(self):
        """Limpa todas as configurações"""
        self.settings.clear()


# Instância global
app_settings = AppSettings()
