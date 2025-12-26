"""
UI Helpers - Componentes reutilizáveis para melhorar UX.

Inclui:
- Mensagens de erro amigáveis
- Progress dialogs melhorados
- Notificações toast
- Status feedback
"""
from PyQt6.QtWidgets import (QMessageBox, QProgressDialog, QWidget, QLabel,
                             QVBoxLayout, QFrame, QGraphicsOpacityEffect,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
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


class ToastNotification(QFrame):
    """
    Notificação embutida que aparece dentro da janela pai.
    Design moderno com gradiente e fade automático.
    """
    
    def __init__(self, message, toast_type="info", duration=3500, parent=None):
        super().__init__(parent)
        
        self.setObjectName("toastFrame")
        
        # Cores por tipo
        colors = {
            "success": ("#00C16E", "#00A859", "✓"),
            "error": ("#FF5252", "#D32F2F", "✕"),
            "warning": ("#FFB300", "#FF8F00", "!"),
            "info": ("#29B6F6", "#0288D1", "i")
        }
        
        bg_start, bg_end, icon = colors.get(toast_type, colors["info"])
        
        # Estilo premium
        self.setStyleSheet(f"""
            #toastFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {bg_start},
                    stop:1 {bg_end}
                );
                border-radius: 8px;
                padding: 10px 20px;
                margin: 10px;
            }}
        """)
        
        # Layout horizontal
        from PyQt6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)
        
        # Ícone
        icon_label = QLabel(icon)
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            background: rgba(255,255,255,0.25);
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(icon_label)
        
        # Mensagem
        text_label = QLabel(message)
        text_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 500;
            color: white;
        """)
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Fechar automaticamente
        QTimer.singleShot(duration, self._fade_out)
        
        # Posicionar no topo do parent
        self.adjustSize()
        if parent:
            self.setFixedWidth(parent.width() - 40)
            self.move(20, 20)
        
        self.show()
        self.raise_()
    
    def _fade_out(self):
        """Fechar com fade"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()


def show_toast(parent, message, toast_type="info", duration=3500):
    """
    Mostra notificação toast dentro do parent.
    
    Args:
        parent: Widget pai (onde o toast vai aparecer)
        message: Mensagem
        toast_type: Tipo (success, error, warning, info)
        duration: Duração em ms
    """
    # Encontrar o widget de conteúdo principal
    main_content = parent
    
    # Se o parent for a janela principal, tentar encontrar o stacked widget
    if hasattr(parent, 'stacked_widget'):
        main_content = parent.stacked_widget
    elif hasattr(parent, 'central_widget'):
        main_content = parent.central_widget
    
    toast = ToastNotification(message, toast_type, duration, main_content)
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
