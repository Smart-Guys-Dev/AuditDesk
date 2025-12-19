"""
UI Helpers - Componentes reutilizáveis para melhorar UX.

Inclui:
- Mensagens de erro amigáveis
- Progress dialogs melhorados
- Notificações toast
- Status feedback
"""
from PyQt6.QtWidgets import (QMessageBox, QProgressDialog, QWidget, QLabel,
                             QVBoxLayout, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)


def show_friendly_error(parent, title, friendly_msg, technical_details="", icon=QMessageBox.Icon.Warning):
    """
    Mostra erro de forma amigável com opção de ver detalhes técnicos.
    
    Args:
        parent: Widget pai
        title: Título da janela
        friendly_msg: Mensagem user-friendly
        technical_details: Detalhes técnicos (opcional)
        icon: Ícone da mensagem
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(friendly_msg)
    
    if technical_details:
        msg_box.setDetailedText(f"Detalhes técnicos:\n{technical_details}")
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
    
    logger.error(f"{title}: {friendly_msg} | Details: {technical_details}")


def show_success(parent, title, message):
    """
    Mostra mensagem de sucesso.
    
    Args:
        parent: Widget pai
        title: Título
        message: Mensagem
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_warning(parent, title, message):
    """
    Mostra aviso.
    
    Args:
        parent: Widget pai
        title: Título
        message: Mensagem
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


class EnhancedProgressDialog(QProgressDialog):
    """
    Progress dialog melhorado com estimativa de tempo.
    """
    
    def __init__(self, title, cancel_text, min_val, max_val, parent=None):
        super().__init__(title, cancel_text, min_val, max_val, parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setAutoClose(True)
        self.setAutoReset(True)
        self.setMinimumDuration(500)  # Mostra após 500ms
        
        # Formato com porcentagem
        self.setLabelText(title)
        
    def update_progress(self, current, total, message=""):
        """
        Atualiza progresso com mensagem customizada.
        
        Args:
            current: Valor atual
            total: Total
            message: Mensagem adicional
        """
        self.setMaximum(total)
        self.setValue(current)
        
        percentage = int((current / total) * 100) if total > 0 else 0
        
        if message:
            self.setLabelText(f"{message}\n{current} de {total} ({percentage}%)")
        else:
            self.setLabelText(f"{current} de {total} ({percentage}%)")


class ToastNotification(QWidget):
    """
    Notificação toast não-bloqueante que desaparece automaticamente.
    """
    
    def __init__(self, message, toast_type="info", duration=3000, parent=None):
        super().__init__(parent)
        
        # Configuração da janela
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.Tool |
                           Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame com conteúdo
        self.frame = QFrame()
        self.frame.setObjectName("toastFrame")
        
        # Cores baseadas no tipo
        colors = {
            "success": "#48bb78",
            "error": "#f56565",
            "warning": "#ed8936",
            "info": "#4299e1"
        }
        
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        bg_color = colors.get(toast_type, "#4299e1")
        icon = icons.get(toast_type, "ℹ️")
        
        self.frame.setStyleSheet(f"""
            #toastFrame {{
                background: {bg_color};
                color: white;
                border-radius: 8px;
                padding: 15px 20px;
            }}
        """)
        
        # Label com mensagem
        frame_layout = QVBoxLayout(self.frame)
        label = QLabel(f"{icon} {message}")
        label.setStyleSheet("font-size: 14px; font-weight: 500;")
        frame_layout.addWidget(label)
        
        layout.addWidget(self.frame)
        
        # Animação de fade in
        self.opacity_effect = QGraphicsOpacityEffect(self.frame)
        self.frame.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Timer para fechar
        QTimer.singleShot(duration, self._fade_out)
        
    def showEvent(self, event):
        """Executado ao mostrar - inicia fade in"""
        super().showEvent(event)
        self.fade_in_animation.start()
        
        # Posicionar no canto superior direito
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.width() - self.width() - 20
            y = 20
            self.move(x, y)
    
    def _fade_out(self):
        """Fade out e fechar"""
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade_out.finished.connect(self.close)
        fade_out.start()


def show_toast(parent, message, toast_type="info", duration=3000):
    """
    Mostra notificação toast.
    
    Args:
        parent: Widget pai
        message: Mensagem
        toast_type: Tipo (success, error, warning, info)
        duration: Duração em ms
    """
    toast = ToastNotification(message, toast_type, duration, parent)
    toast.show()
    return toast


# Mapeamento de erros comuns para mensagens amigáveis
ERROR_MESSAGES = {
    "FileNotFoundError": {
        "title": "Arquivo não encontrado",
        "message": "O arquivo selecionado não foi encontrado.\n\nVerifique se o arquivo ainda existe e tente novamente."
    },
    "PermissionError": {
        "title": "Sem permissão",
        "message": "Não foi possível acessar o arquivo.\n\nVerifique se você tem permissão para acessar este arquivo."
    },
    "XMLSyntaxError": {
        "title": "XML inválido",
        "message": "O arquivo XML está malformado ou corrompido.\n\nVerifique se o arquivo está correto e tente novamente."
    },
    "TimeoutError": {
        "title": "Tempo esgotado",
        "message": "A operação demorou muito tempo.\n\nTente processar menos arquivos de uma vez."
    },
    "MemoryError": {
        "title": "Memória insuficiente",
        "message": "Não há memória suficiente para processar.\n\nFeche outros programas e tente novamente."
    },
}


def handle_exception(parent, exception, context="operação"):
    """
    Trata exceção e mostra erro amigável.
    
    Args:
        parent: Widget pai
        exception: Exceção capturada
        context: Contexto da operação
    """
    exception_type = type(exception).__name__
    error_info = ERROR_MESSAGES.get(exception_type, None)
    
    if error_info:
        show_friendly_error(
            parent,
            error_info["title"],
            error_info["message"],
            str(exception)
        )
    else:
        show_friendly_error(
            parent,
            "Erro ao executar operação",
            f"Ocorreu um erro ao executar a {context}.\n\n"
            f"Se o problema persistir, entre em contato com o suporte.",
            f"{exception_type}: {str(exception)}"
        )
