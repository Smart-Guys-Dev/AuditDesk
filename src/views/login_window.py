from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QPalette, QFont
from src.database import db_manager

class LoginWindow(QWidget):
    # Sinal emitido quando o login é bem sucedido, passando o objeto User
    login_successful = pyqtSignal(object)
    
    # Cores institucionais Unimed
    UNIMED_GREEN = "#00A859"
    UNIMED_DARK_GREEN = "#008C45"
    UNIMED_LIGHT_GREEN = "#00C16E"
    
    # Cores do tema dark
    BG_DARK = "#0D1117"
    BG_CARD = "#161B22"
    BG_INPUT = "#21262D"
    BORDER_COLOR = "#30363D"
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glox - Login")
        self.setFixedSize(420, 580)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Container Principal (Card) com efeito 3D
        self.container = QFrame()
        self.container.setObjectName("login_container")
        self.container.setStyleSheet(f"""
            QFrame#login_container {{
                background-color: {self.BG_CARD};
                border: 2px solid {self.UNIMED_GREEN};
                border-radius: 20px;
            }}
        """)
        
        # Sombra 3D externa (verde Unimed)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 168, 89, 80))  # Verde Unimed com transparência
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)
        
        # Layout do Container
        card_layout = QVBoxLayout(self.container)
        card_layout.setContentsMargins(45, 50, 45, 40)
        card_layout.setSpacing(18)

        # ===== LOGO / TÍTULO =====
        lbl_logo = QLabel("Glox")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet(f"""
            font-size: 48px; 
            font-weight: 800; 
            color: {self.UNIMED_GREEN};
            margin-bottom: 0px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        
        lbl_subtitle = QLabel("Validação e Correção PTU/TISS")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitle.setStyleSheet(f"""
            font-size: 12px; 
            color: {self.TEXT_SECONDARY};
            margin-bottom: 25px;
            letter-spacing: 1px;
        """)
        
        card_layout.addWidget(lbl_logo)
        card_layout.addWidget(lbl_subtitle)

        # ===== CAMPOS DE LOGIN =====
        # Campo Usuário com borda 3D
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("👤  Usuário")
        self.txt_user.setStyleSheet(self._get_input_style_3d())
        card_layout.addWidget(self.txt_user)

        # Campo Senha com borda 3D
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("🔒  Senha")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setStyleSheet(self._get_input_style_3d())
        self.txt_pass.returnPressed.connect(self.do_login)
        card_layout.addWidget(self.txt_pass)

        card_layout.addSpacing(15)

        # ===== BOTÃO ENTRAR (3D com verde Unimed) =====
        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.UNIMED_LIGHT_GREEN},
                    stop:0.5 {self.UNIMED_GREEN},
                    stop:1 {self.UNIMED_DARK_GREEN}
                );
                color: white;
                font-weight: bold;
                padding: 16px;
                border-radius: 10px;
                font-size: 15px;
                letter-spacing: 2px;
                border: none;
                border-top: 2px solid {self.UNIMED_LIGHT_GREEN};
                border-bottom: 3px solid #006633;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00D46A,
                    stop:0.5 {self.UNIMED_LIGHT_GREEN},
                    stop:1 {self.UNIMED_GREEN}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.UNIMED_DARK_GREEN},
                    stop:1 #005522
                );
                border-top: 1px solid {self.UNIMED_GREEN};
                border-bottom: 1px solid #004422;
                padding-top: 18px;
                padding-bottom: 14px;
            }}
        """)
        self.btn_login.clicked.connect(self.do_login)
        card_layout.addWidget(self.btn_login)

        # ===== BOTÃO SAIR =====
        self.btn_close = QPushButton("Sair")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFlat(True)
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                color: {self.TEXT_SECONDARY};
                background: transparent;
                font-size: 12px;
                padding: 8px;
            }}
            QPushButton:hover {{
                color: #FF6B6B;
                text-decoration: underline;
            }}
        """)
        self.btn_close.clicked.connect(self.close)
        card_layout.addWidget(self.btn_close)

        card_layout.addStretch()

        # ===== RODAPÉ COM UNIMED =====
        lbl_dev = QLabel("Desenvolvido por Pedro Lucas Lima de Freitas")
        lbl_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_dev.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 10px;")
        card_layout.addWidget(lbl_dev)
        
        lbl_unimed = QLabel("Unimed Campo Grande")
        lbl_unimed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_unimed.setStyleSheet(f"""
            color: {self.UNIMED_GREEN}; 
            font-size: 11px; 
            font-weight: bold;
            margin-top: 5px;
        """)
        card_layout.addWidget(lbl_unimed)

    def _get_input_style_3d(self):
        """Retorna estilo dos inputs com efeito 3D inset"""
        return f"""
            QLineEdit {{
                padding: 14px 16px;
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 10px;
                background-color: {self.BG_INPUT};
                color: {self.TEXT_PRIMARY};
                font-size: 14px;
                /* Efeito 3D inset */
                border-top: 2px solid #1a1f26;
                border-left: 2px solid #1a1f26;
                border-bottom: 2px solid #3a4252;
                border-right: 2px solid #3a4252;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.UNIMED_GREEN};
                background-color: #2a3040;
                /* Efeito 3D focus */
                border-top: 2px solid {self.UNIMED_DARK_GREEN};
                border-left: 2px solid {self.UNIMED_DARK_GREEN};
                border-bottom: 2px solid {self.UNIMED_LIGHT_GREEN};
                border-right: 2px solid {self.UNIMED_LIGHT_GREEN};
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_SECONDARY};
            }}
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
