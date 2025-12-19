# src/views/components/kpi_card.py
"""
KPI Card Component
Componente reutilizável para exibir KPIs.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt


class KPICard(QFrame):
    """
    Card para exibir um KPI (Key Performance Indicator).
    
    Usage:
        card = KPICard("Total de Faturas", "1,234")
        layout.addWidget(card)
    """
    
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do card"""
        self.setFrameShape(QFrame.Shape.Box)
        self.setObjectName("kpiCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Label do KPI
        label = QLabel(self.label_text)
        label.setObjectName("kpiLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valor do KPI
        value = QLabel(self.value_text)
        value.setObjectName("kpiValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label)
        layout.addWidget(value)
        
        self.setStyleSheet("""
            #kpiCard {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                padding: 15px;
            }
            #kpiLabel {
                font-size: 12px;
                color: #666;
            }
            #kpiValue {
                font-size: 24px;
                font-weight: bold;
                color: #2196F3;
            }
        """)
    
    def update_value(self, new_value: str):
        """
        Atualiza o valor do KPI.
        
        Args:
            new_value: Novo valor a exibir
        """
        self.value_text = new_value
        # Encontra o label de valor e atualiza
        for child in self.children():
            if isinstance(child, QLabel) and child.objectName() == "kpiValue":
                child.setText(new_value)
                break
