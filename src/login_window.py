from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.database import db_manager

class LoginWindow(QWidget):
    # Sinal emitido quando o login é bem sucedido, passando o objeto User
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audit+ Login")
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # Opcional: Janela sem borda para estilo moderno
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Para sombras
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container Principal (Card)
        self.container = QFrame()
        self.container.setObjectName("login_container")
        self.container.setStyleSheet("""
            QFrame#login_container {
                background-color: #2E3440;
                border: 1px solid #434C5E;
                border-radius: 16px;
            }
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)
        
        # Layout do Container
        card_layout = QVBoxLayout(self.container)
        card_layout.setContentsMargins(40, 50, 40, 40)
        card_layout.setSpacing(20)

        # Logo / Título
        lbl_logo = QLabel("Audit+")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("""
            font-size: 42px; 
            font-weight: 800; 
            color: #88C0D0;
            margin-bottom: 5px;
        """)
        
        lbl_subtitle = QLabel("Enterprise Edition")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitle.setStyleSheet("""
            font-size: 14px; 
            color: #D8DEE9;
            margin-bottom: 30px;
            opacity: 0.7;
        """)
        
        card_layout.addWidget(lbl_logo)
        card_layout.addWidget(lbl_subtitle)

        # Campo Usuário
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Usuário")
        self.txt_user.setStyleSheet(self._get_input_style())
        card_layout.addWidget(self.txt_user)

        # Campo Senha
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Senha")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setStyleSheet(self._get_input_style())
        self.txt_pass.returnPressed.connect(self.do_login)
        card_layout.addWidget(self.txt_pass)

        card_layout.addSpacing(10)

        # Botão Entrar
        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                font-weight: bold;
                padding: 14px;
                border-radius: 8px;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        self.btn_login.clicked.connect(self.do_login)
        card_layout.addWidget(self.btn_login)

        # Botão Fechar (já que removemos a borda padrão)
        self.btn_close = QPushButton("Sair")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFlat(True)
        self.btn_close.setStyleSheet("""
            QPushButton {
                color: #4C566A;
                background: transparent;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #BF616A;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        card_layout.addWidget(self.btn_close)

        card_layout.addStretch()

        # Rodapé
        lbl_footer = QLabel("Powered by BisonCode")
        lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_footer.setStyleSheet("color: #4C566A; font-size: 10px;")
        card_layout.addWidget(lbl_footer)

    def _get_input_style(self):
        return """
            QLineEdit {
                padding: 12px;
                border: 2px solid #3B4252;
                border-radius: 8px;
                background-color: #3B4252;
                color: #ECEFF4;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #88C0D0;
                background-color: #434C5E;
            }
        """

    def do_login(self):
        username = self.txt_user.text().strip()
        password = self.txt_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha usuário e senha.")
            return

        user = db_manager.authenticate_user(username, password)

        if user:
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.critical(self, "Erro de Login", "Usuário ou senha incorretos.")
            self.txt_pass.clear()
            self.txt_pass.setFocus()
    
    # Permitir arrastar a janela (já que removemos a barra de título)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos'):
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'old_pos'):
            del self.old_pos
