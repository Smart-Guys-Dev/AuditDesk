import sys
from PyQt6.QtWidgets import QApplication
import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.logger_config import setup_logging
from src.database import db_manager
from src.exception_handler import install_exception_handler
from src.login_window import LoginWindow

def main():
    # 1. Configurar Logging
    logger = setup_logging()
    logger.info("=== Iniciando Audit+ v2.0 ===")
    
    # 2. Instalar Tratamento Global de Erros
    install_exception_handler()
    
    # 3. Inicializar Banco de Dados
    db_manager.init_db()
    
    app = QApplication(sys.argv)
    
    # Variáveis para manter referência
    login_window = None
    main_window = None

    def start_login():
        nonlocal login_window
        login_window = LoginWindow()
        login_window.login_successful.connect(on_login_success)
        login_window.show()

    def on_login_success(user):
        nonlocal main_window, login_window
        logger.info(f"Login efetuado com sucesso: {user.username} ({user.role})")
        
        # Fechar login
        if login_window:
            login_window.close()
            login_window = None
        
        # Abrir Main Window
        main_window = MainWindow(user)
        main_window.logout_requested.connect(on_logout)
        main_window.show()
        
        # Configurar título
        main_window.setWindowTitle(f"Audit+ - Logado como: {user.full_name or user.username}")

    def on_logout():
        nonlocal main_window
        logger.info("Logout solicitado pelo usuário.")
        
        # Fechar Main Window
        if main_window:
            main_window.close()
            main_window = None
            
        # Reiniciar Login
        start_login()

    # Iniciar aplicação
    start_login()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()