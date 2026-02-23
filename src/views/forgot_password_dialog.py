"""
Forgot Password Dialog - Recuperação de senha self-service.
Verifica e-mail corporativo + data de nascimento para permitir redefinição.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFrame, QMessageBox, QDateEdit,
                             QGraphicsDropShadowEffect, QStackedWidget)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from src.database.db_manager import get_session
from src.database.models import User
from src.infrastructure.security.password_manager import PasswordManager
import logging

logger = logging.getLogger(__name__)

# Cores do tema
_GREEN = "#00A859"
_TEXT = "#E6EDF3"
_MUTED = "#8B949E"
_DARK_MUTED = "#484F58"
_BG_INPUT = "#21262D"
_BORDER = "#30363D"
_BG_CARD = "#161B22"
_BLUE = "#58A6FF"
_RED = "#DA3633"


class ForgotPasswordDialog(QDialog):
    """Diálogo de recuperação de senha em duas etapas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recuperação de Senha")
        self.setFixedSize(420, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._verified_user = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Card container
        container = QFrame()
        container.setObjectName("forgot_container")
        container.setStyleSheet(f"""
            QFrame#forgot_container {{
                background-color: {_BG_CARD};
                border: 1px solid {_BORDER};
                border-radius: 16px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout.addWidget(container)

        card = QVBoxLayout(container)
        card.setContentsMargins(40, 32, 40, 32)
        card.setSpacing(0)

        # ── Stacked Widget (2 pages) ──
        self.stack = QStackedWidget()
        card.addWidget(self.stack)

        # Page 1: Verification
        self._build_verify_page()
        # Page 2: New Password
        self._build_reset_page()

    def _build_verify_page(self):
        page = QFrame()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Título
        title = QLabel("🔐 Recuperar Senha")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {_TEXT};")
        title.setFixedHeight(36)
        lay.addWidget(title)

        lay.addSpacing(8)

        subtitle = QLabel("Informe seus dados de cadastro para verificação")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"font-size: 11px; color: {_MUTED};")
        subtitle.setFixedHeight(20)
        lay.addWidget(subtitle)

        lay.addSpacing(24)

        # E-mail
        lbl_email = QLabel("E-mail corporativo")
        lbl_email.setStyleSheet(f"font-size: 11px; color: {_MUTED}; font-weight: 600;")
        lay.addWidget(lbl_email)
        lay.addSpacing(4)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("nome@unimed.com.br")
        self.txt_email.setFixedHeight(44)
        self.txt_email.setStyleSheet(self._input_style())
        lay.addWidget(self.txt_email)

        lay.addSpacing(16)

        # Data de Nascimento
        lbl_birth = QLabel("Data de nascimento")
        lbl_birth.setStyleSheet(f"font-size: 11px; color: {_MUTED}; font-weight: 600;")
        lay.addWidget(lbl_birth)
        lay.addSpacing(4)

        self.date_birth = QDateEdit()
        self.date_birth.setCalendarPopup(True)
        self.date_birth.setDisplayFormat("dd/MM/yyyy")
        self.date_birth.setDate(QDate(1990, 1, 1))
        self.date_birth.setFixedHeight(44)
        self.date_birth.setStyleSheet(f"""
            QDateEdit {{
                padding: 8px 16px; border: 1px solid {_BORDER};
                border-radius: 8px; background-color: {_BG_INPUT};
                color: {_TEXT}; font-size: 14px;
            }}
            QDateEdit:focus {{
                border: 1px solid {_GREEN}; background-color: #1C2128;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
            }}
            QDateEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {_MUTED};
                margin-right: 8px;
            }}
        """)
        lay.addWidget(self.date_birth)

        lay.addSpacing(24)

        # Feedback (inicialmente oculta)
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(f"font-size: 11px; color: {_RED};")
        self.lbl_error.setFixedHeight(18)
        self.lbl_error.hide()
        lay.addWidget(self.lbl_error)

        lay.addSpacing(4)

        # Botão Verificar
        btn_verify = QPushButton("VERIFICAR")
        btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_verify.setFixedHeight(44)
        btn_verify.setStyleSheet(self._btn_green_style())
        btn_verify.clicked.connect(self._verify_identity)
        lay.addWidget(btn_verify)

        lay.addSpacing(8)

        # Botão Cancelar
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(self._btn_cancel_style())
        btn_cancel.clicked.connect(self.reject)
        lay.addWidget(btn_cancel)

        lay.addStretch()

        self.stack.addWidget(page)

    def _build_reset_page(self):
        page = QFrame()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Título
        title = QLabel("🔑 Nova Senha")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {_TEXT};")
        title.setFixedHeight(36)
        lay.addWidget(title)

        lay.addSpacing(8)

        self.lbl_welcome = QLabel("Identidade verificada!")
        self.lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_welcome.setStyleSheet(f"font-size: 11px; color: {_GREEN};")
        self.lbl_welcome.setFixedHeight(20)
        lay.addWidget(self.lbl_welcome)

        lay.addSpacing(24)

        # Nova senha
        lbl_new = QLabel("Nova senha")
        lbl_new.setStyleSheet(f"font-size: 11px; color: {_MUTED}; font-weight: 600;")
        lay.addWidget(lbl_new)
        lay.addSpacing(4)

        # Container nova senha + olhinho
        new_pass_container = QHBoxLayout()
        new_pass_container.setSpacing(0)
        new_pass_container.setContentsMargins(0, 0, 0, 0)

        self.txt_new_pass = QLineEdit()
        self.txt_new_pass.setPlaceholderText("Mínimo 12 caracteres")
        self.txt_new_pass.setFixedHeight(44)
        self.txt_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_pass.setStyleSheet(self._input_style(right_rounded=False))

        self.btn_eye_new = QPushButton("👁")
        self.btn_eye_new.setFixedSize(44, 44)
        self.btn_eye_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye_new.setCheckable(True)
        self.btn_eye_new.setStyleSheet(self._eye_style())
        self.btn_eye_new.clicked.connect(lambda: self._toggle_eye(self.txt_new_pass, self.btn_eye_new))

        new_pass_container.addWidget(self.txt_new_pass)
        new_pass_container.addWidget(self.btn_eye_new)
        lay.addLayout(new_pass_container)

        lay.addSpacing(16)

        # Confirmar senha
        lbl_confirm = QLabel("Confirmar nova senha")
        lbl_confirm.setStyleSheet(f"font-size: 11px; color: {_MUTED}; font-weight: 600;")
        lay.addWidget(lbl_confirm)
        lay.addSpacing(4)

        # Container confirmar + olhinho
        confirm_container = QHBoxLayout()
        confirm_container.setSpacing(0)
        confirm_container.setContentsMargins(0, 0, 0, 0)

        self.txt_confirm_pass = QLineEdit()
        self.txt_confirm_pass.setPlaceholderText("Repita a nova senha")
        self.txt_confirm_pass.setFixedHeight(44)
        self.txt_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm_pass.setStyleSheet(self._input_style(right_rounded=False))

        self.btn_eye_confirm = QPushButton("👁")
        self.btn_eye_confirm.setFixedSize(44, 44)
        self.btn_eye_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye_confirm.setCheckable(True)
        self.btn_eye_confirm.setStyleSheet(self._eye_style())
        self.btn_eye_confirm.clicked.connect(lambda: self._toggle_eye(self.txt_confirm_pass, self.btn_eye_confirm))

        confirm_container.addWidget(self.txt_confirm_pass)
        confirm_container.addWidget(self.btn_eye_confirm)
        lay.addLayout(confirm_container)

        lay.addSpacing(8)

        # Feedback
        self.lbl_reset_error = QLabel("")
        self.lbl_reset_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reset_error.setWordWrap(True)
        self.lbl_reset_error.setStyleSheet(f"font-size: 11px; color: {_RED};")
        self.lbl_reset_error.setFixedHeight(18)
        self.lbl_reset_error.hide()
        lay.addWidget(self.lbl_reset_error)

        lay.addSpacing(16)

        # Botão Redefinir
        btn_reset = QPushButton("REDEFINIR SENHA")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setFixedHeight(44)
        btn_reset.setStyleSheet(self._btn_green_style())
        btn_reset.clicked.connect(self._reset_password)
        lay.addWidget(btn_reset)

        lay.addSpacing(8)

        # Botão Voltar
        btn_back = QPushButton("Voltar")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setFixedHeight(36)
        btn_back.setStyleSheet(self._btn_cancel_style())
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        lay.addWidget(btn_back)

        lay.addStretch()

        self.stack.addWidget(page)

    # ── Lógica ──

    def _verify_identity(self):
        email = self.txt_email.text().strip().lower()
        birth_date = self.date_birth.date().toPyDate()

        if not email:
            self._show_error(self.lbl_error, "Informe o e-mail corporativo.")
            return

        session = get_session()
        try:
            user = session.query(User).filter(
                User.email == email,
                User.birth_date == birth_date,
                User.is_active == True
            ).first()

            if user:
                self._verified_user = user.id
                self.lbl_welcome.setText(f"✅ Identidade verificada para: {user.full_name or user.username}")
                self.stack.setCurrentIndex(1)
                self.txt_new_pass.setFocus()
                logger.info(f"Recuperação de senha: identidade verificada para user_id={user.id}")
            else:
                self._show_error(self.lbl_error, "E-mail ou data de nascimento não correspondem a nenhum usuário ativo.")
                logger.warning(f"Recuperação de senha falhada: email={email[:20]}...")
        finally:
            session.close()

    def _reset_password(self):
        new_pass = self.txt_new_pass.text()
        confirm = self.txt_confirm_pass.text()

        if not new_pass:
            self._show_error(self.lbl_reset_error, "Digite a nova senha.")
            return

        if new_pass != confirm:
            self._show_error(self.lbl_reset_error, "As senhas não coincidem.")
            return

        if len(new_pass) < 12:
            self._show_error(self.lbl_reset_error, "A senha deve ter no mínimo 12 caracteres.")
            return

        session = get_session()
        try:
            user = session.query(User).filter_by(id=self._verified_user).first()
            if not user:
                self._show_error(self.lbl_reset_error, "Erro interno. Tente novamente.")
                return

            pwd_hash = PasswordManager.hash_password(new_pass)
            user.password_hash = pwd_hash
            session.commit()

            logger.info(f"Senha redefinida com sucesso para user_id={user.id}")

            QMessageBox.information(
                self,
                "Senha Redefinida",
                f"✅ Senha alterada com sucesso!\n\nUsuário: {user.username}\n\nFaça login com sua nova senha."
            )
            self.accept()

        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao redefinir senha: {e}")
            self._show_error(self.lbl_reset_error, "Erro ao redefinir senha. Tente novamente.")
        finally:
            session.close()

    def _show_error(self, label, text):
        label.setText(text)
        label.show()

    def _toggle_eye(self, field, button):
        if button.isChecked():
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁")

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

    def _eye_style(self):
        return f"""
            QPushButton {{
                background-color: {_BG_INPUT};
                border: 1px solid {_BORDER};
                border-left: none;
                border-radius: 0px 8px 8px 0px;
                font-size: 14px;
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
        """

    def _btn_green_style(self):
        return """
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
        """

    def _btn_cancel_style(self):
        return f"""
            QPushButton {{
                color: {_MUTED}; background-color: {_BG_INPUT};
                font-size: 12px; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
            QPushButton:hover {{
                color: {_RED}; border-color: {_RED}; background-color: #1C2128;
            }}
        """

    # Permitir arrastar
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
