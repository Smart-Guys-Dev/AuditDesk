import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from src.exception_handler import install_exception_handler
from src.database import db_manager

def trigger_crash():
    print("Simulando crash...")
    raise ValueError("Erro de teste simulado para verificar o Global Exception Handler!")

def main():
    # Inicializa DB para ter onde logar
    db_manager.init_db()
    
    app = QApplication(sys.argv)
    
    # Instala o handler
    install_exception_handler()
    
    window = QWidget()
    window.setWindowTitle("Teste de Crash")
    layout = QVBoxLayout(window)
    
    btn = QPushButton("CRASH ME!")
    btn.clicked.connect(trigger_crash)
    layout.addWidget(btn)
    
    window.show()
    
    print("Janela aberta. Clique no botão para testar.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
