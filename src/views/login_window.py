"""
Login Window - Tela de login minimalista.
Usa QSS centralizado ao invés de estilos inline.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame, QCheckBox,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QColor
from src.database import db_manager
from src.views.forgot_password_dialog import ForgotPasswordDialog

# Cores do tema (constantes para manter consistência)
_GREEN = "#00A859"
_TEXT = "#E6EDF3"
_MUTED = "#8B949E"
_DARK_MUTED = "#484F58"
_BG_INPUT = "#21262D"
_BORDER = "#30363D"
_BG_CARD = "#161B22"


class LoginWindow(QWidget):
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audit+ - Login")
        self.setFixedSize(420, 620)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._settings = QSettings("SmartGuys", "AuditPlus")
        self._setup_ui()
        self._load_saved_credentials()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Card container
        self.container = QFrame()
        self.container.setObjectName("login_container")
        self.container.setStyleSheet(f"""
            QFrame#login_container {{
                background-color: {_BG_CARD};
                border: 1px solid {_BORDER};
                border-radius: 16px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        layout.addWidget(self.container)

        card = QVBoxLayout(self.container)
        card.setContentsMargins(40, 40, 40, 32)
        card.setSpacing(0)

        # ── Logo (rich text, single label, no clipping) ──
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setTextFormat(Qt.TextFormat.RichText)
        lbl_logo.setText(
            '<span style="font-size:42px; font-weight:300; color:#E6EDF3; '
            'font-family: Segoe UI, Inter, sans-serif;">Audit</span>'
            '<span style="font-size:48px; font-weight:800; color:#00A859; '
            'font-family: Segoe UI, Inter, sans-serif;">+</span>'
        )
        lbl_logo.setFixedHeight(64)
        card.addWidget(lbl_logo)

        # Glow no logo
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 168, 89, 80))
        glow.setOffset(0, 0)
        lbl_logo.setGraphicsEffect(glow)

        card.addSpacing(8)

        # ── Subtítulo ──
        lbl_subtitle = QLabel("VALIDAÇÃO E CORREÇÃO PTU/TISS")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitle.setFixedHeight(20)
        lbl_subtitle.setStyleSheet(f"""
            font-size: 10px; color: {_MUTED};
            letter-spacing: 2px;
        """)
        card.addWidget(lbl_subtitle)

        card.addSpacing(8)

        # ── Linha decorativa ──
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.25 {_GREEN},
                stop:0.75 {_GREEN},
                stop:1 transparent
            );
        """)
        card.addWidget(separator)

        card.addSpacing(24)

        # ── Campo Usuário ──
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Usuário")
        self.txt_user.setFixedHeight(48)
        self.txt_user.setStyleSheet(self._input_style())
        card.addWidget(self.txt_user)

        card.addSpacing(12)

        # ── Campo Senha + Olhinho ──
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        password_container.setContentsMargins(0, 0, 0, 0)

        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Senha")
        self.txt_pass.setFixedHeight(48)
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setStyleSheet(self._input_style(right_rounded=False))
        self.txt_pass.returnPressed.connect(self._do_login)

        self.btn_eye = QPushButton("👁")
        self.btn_eye.setFixedSize(48, 48)
        self.btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye.setCheckable(True)
        self.btn_eye.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_INPUT};
                border: 1px solid {_BORDER};
                border-left: none;
                border-radius: 0px 8px 8px 0px;
                font-size: 16px;
                color: {_DARK_MUTED};
            }}
            QPushButton:hover {{
                color: {_TEXT};
                background-color: #1C2128;
            }}
            QPushButton:checked {{
                color: {_GREEN};
                background-color: #1C2128;
                border-color: {_GREEN};
            }}
        """)
        self.btn_eye.clicked.connect(self._toggle_password_visibility)

        password_container.addWidget(self.txt_pass)
        password_container.addWidget(self.btn_eye)
        card.addLayout(password_container)

        card.addSpacing(12)

        # ── Linha: Manter conectado + Esqueci senha ──
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(4, 0, 4, 0)

        self.chk_remember = QCheckBox("Manter-me conectado")
        self.chk_remember.setStyleSheet(f"""
            QCheckBox {{
                color: {_MUTED};
                font-size: 11px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid {_BORDER};
                background-color: {_BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {_GREEN};
                border-color: {_GREEN};
            }}
            QCheckBox::indicator:hover {{
                border-color: {_GREEN};
            }}
        """)

        lbl_forgot = QLabel('<a style="color: #58A6FF; text-decoration: none; font-size: 11px;" href="#">Esqueci minha senha</a>')
        lbl_forgot.setTextFormat(Qt.TextFormat.RichText)
        lbl_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl_forgot.linkActivated.connect(self._show_forgot_dialog)

        options_layout.addWidget(self.chk_remember)
        options_layout.addStretch()
        options_layout.addWidget(lbl_forgot)

        card.addLayout(options_layout)

        card.addSpacing(20)

        # ── Botão Entrar ──
        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setFixedHeight(48)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00C16E, stop:1 #008C45);
                color: white; font-weight: 700; font-size: 13px;
                letter-spacing: 2px; border: none; border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00D67E, stop:1 #00A859);
            }
            QPushButton:pressed { background: #008C45; }
        """)
        self.btn_login.clicked.connect(self._do_login)
        card.addWidget(self.btn_login)

        card.addSpacing(8)

        # ── Botão Sair ──
        btn_close = QPushButton("Sair")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                color: {_MUTED}; background-color: {_BG_INPUT};
                font-size: 12px; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
            QPushButton:hover {{
                color: #DA3633; border-color: #DA3633; background-color: #1C2128;
            }}
        """)
        btn_close.clicked.connect(self.close)
        card.addWidget(btn_close)

        card.addSpacing(24)

        # ── Rodapé ──
        lbl_dev = QLabel("Desenvolvido por Pedro Lucas Lima de Freitas")
        lbl_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_dev.setFixedHeight(16)
        lbl_dev.setStyleSheet(f"color: {_DARK_MUTED}; font-size: 10px;")
        card.addWidget(lbl_dev)

        card.addSpacing(4)

        lbl_company = QLabel("Unimed Campo Grande")
        lbl_company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_company.setFixedHeight(18)
        lbl_company.setStyleSheet(f"color: {_GREEN}; font-size: 11px; font-weight: 600;")
        card.addWidget(lbl_company)

        card.addSpacing(6)

        lbl_version = QLabel("v3.0")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_version.setFixedHeight(22)
        lbl_version.setStyleSheet(f"""
            font-size: 10px; font-weight: 600; color: {_GREEN};
            background-color: rgba(0, 168, 89, 30);
            border: 1px solid rgba(0, 168, 89, 60);
            border-radius: 4px; padding: 2px 8px; max-width: 40px;
        """)
        card.addWidget(lbl_version, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── Estilos ──

    def _input_style(self, right_rounded=True):
        radius = "8px" if right_rounded else "8px 0px 0px 8px"
        return f"""
            QLineEdit {{
                padding: 8px 16px; border: 1px solid {_BORDER};
                border-radius: {radius}; background-color: {_BG_INPUT};
                color: {_TEXT}; font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {_GREEN}; background-color: #1C2128;
            }}
            QLineEdit::placeholder {{ color: {_DARK_MUTED}; }}
        """

    # ── Ações ──

    def _toggle_password_visibility(self):
        if self.btn_eye.isChecked():
            self.txt_pass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye.setText("🙈")
        else:
            self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye.setText("👁")

    def _show_forgot_dialog(self):
        dialog = ForgotPasswordDialog(self)
        dialog.exec()

    def _load_saved_credentials(self):
        """Carrega credenciais salvas se 'manter conectado' estava ativo."""
        remember = self._settings.value("login/remember", False, type=bool)
        if remember:
            saved_user = self._settings.value("login/username", "", type=str)
            self.txt_user.setText(saved_user)
            self.chk_remember.setChecked(True)
            self.txt_pass.setFocus()

    def _save_credentials(self, username: str):
        """Salva credenciais se checkbox ativo. Nunca salva a senha."""
        if self.chk_remember.isChecked():
            self._settings.setValue("login/remember", True)
            self._settings.setValue("login/username", username)
        else:
            self._settings.remove("login/remember")
            self._settings.remove("login/username")

    def _do_login(self):
        username = self.txt_user.text().strip()
        password = self.txt_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha usuário e senha.")
            return

        user = db_manager.authenticate_user(username, password)

        if user:
            self._save_credentials(username)
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.critical(self, "Erro de Login", "Usuário ou senha incorretos.")
            self.txt_pass.clear()
            self.txt_pass.setFocus()

    # Permitir arrastar a janela
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

