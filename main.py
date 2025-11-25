import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.logger_config import setup_logging

if __name__ == '__main__':
    # Configurar logging centralizado
    logger = setup_logging()
    logger.info("=== Iniciando Audit+ v2.0 ===")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    logger.info("Interface gráfica carregada com sucesso")
    sys.exit(app.exec())