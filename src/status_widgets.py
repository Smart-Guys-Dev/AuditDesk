"""
Status icons com animações para feedback visual melhorado.
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QGraphicsOpacityEffect


class StatusIcon(QLabel):
    """
    Label animado para status (⏳, ✅, ❌, ⚠️)
    """
    
    ICONS = {
        'loading': '⏳',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    
    def __init__(self, initial_status='info', parent=None):
        super().__init__(parent)
        self.set_status(initial_status)
        self.setStyleSheet("font-size: 24px;")
    
    def set_status(self, status: str, animate=True):
        """
        Define o status e opcionalmente anima.
        
        Args:
            status: 'loading', 'success', 'error', 'warning', 'info'
            animate: Se True, faz animação fade in
        """
        icon = self.ICONS.get(status, self.ICONS['info'])
        self.setText(icon)
        
        if animate:
            self._animate_fade_in()
        
        # Girar ⏳ se loading
        if status == 'loading':
            self._start_loading_animation()
    
    def _animate_fade_in(self):
        """Animação fade in"""
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
    
    def _start_loading_animation(self):
        """Piscar enquanto loading"""
        self.timer = QTimer(self)
        self.loading_state = True
        
        def toggle():
            self.loading_state = not self.loading_state
            self.setStyleSheet(
                f"font-size: 24px; opacity: {'1.0' if self.loading_state else '0.3'};"
            )
        
        self.timer.timeout.connect(toggle)
        self.timer.start(500)  # Pisca a cada 500ms


class ProgressLabel(QLabel):
    """
    Label que mostra progresso textual com animação.
    Exemplo: "Processando... 10/100"
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.base_text = text
        self.dots = 0
        self.timer = None
    
    def start_animation(self, base_text="Processando"):
        """Inicia animação de pontos"""
        self.base_text = base_text
        self.dots = 0
        
        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._update_dots)
        
        self.timer.start(500)
    
    def stop_animation(self, final_text="Concluído"):
        """Para animação"""
        if self.timer:
            self.timer.stop()
        self.setText(final_text)
    
    def _update_dots(self):
        """Atualiza pontos animados"""
        self.dots = (self.dots + 1) % 4
        dots_str = "." * self.dots
        self.setText(f"{self.base_text}{dots_str}")
    
    def set_progress(self, current, total):
        """Define progresso numérico"""
        if self.timer and self.timer.isActive():
            self.timer.stop()
        
        percentage = int((current / total) * 100) if total > 0 else 0
        self.setText(f"{self.base_text}: {current}/{total} ({percentage}%)")
