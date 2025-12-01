from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

from src.database import db_manager

class KPICard(QFrame):
    def __init__(self, title, value, icon_text="📊", color="#4C566A"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{ color: white; border: none; background: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; opacity: 0.8;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold; margin-top: 10px;")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)

    def update_value(self, value):
        self.value_label.setText(value)

class PaginaDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard de Gestão & ROI")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ECEFF4;")
        
        self.period_filter = QComboBox()
        self.period_filter.addItems(["Todo o Período", "Este Mês", "Mês Anterior"])
        self.period_filter.setStyleSheet("""
            QComboBox {
                background-color: #3B4252;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        self.period_filter.currentIndexChanged.connect(self.load_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Período:"))
        header_layout.addWidget(self.period_filter)
        
        layout.addLayout(header_layout)

        # KPIs
        self.kpi_layout = QHBoxLayout()
        self.card_roi_realizado = KPICard("ROI Realizado", "R$ 0,00", "✅", "#A3BE8C") # Verde
        self.card_roi_potencial = KPICard("ROI Potencial", "R$ 0,00", "⚠️", "#EBCB8B") # Amarelo
        self.card_roi_total = KPICard("ROI Total", "R$ 0,00", "💰", "#88C0D0") # Azul
        self.card_alertas = KPICard("Alertas Pendentes", "0", "🔔", "#B48EAD") # Roxo

        self.kpi_layout.addWidget(self.card_roi_realizado)
        self.kpi_layout.addWidget(self.card_roi_potencial)
        self.kpi_layout.addWidget(self.card_roi_total)
        self.kpi_layout.addWidget(self.card_alertas)
        
        layout.addLayout(self.kpi_layout)

        # Área Central (Gráficos e Tabela)
        content_layout = QHBoxLayout()

        # Tabela de Top Regras
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #2E3440; border-radius: 8px;")
        table_layout = QVBoxLayout(table_container)
        
        lbl_table = QLabel("🏆 Top Regras que mais geraram economia")
        lbl_table.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECEFF4; margin-bottom: 10px;")
        table_layout.addWidget(lbl_table)

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Regra", "Qtd.", "Impacto (R$)"])
        
        # Configurar larguras das colunas
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Regra: estica
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)     # Qtd: fixa
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)     # Impacto: fixa
        self.rules_table.setColumnWidth(1, 80)   # Qtd: 80px
        self.rules_table.setColumnWidth(2, 150)  # Impacto: 150px
        self.rules_table.setStyleSheet("""
            QTableWidget {
                background-color: #3B4252;
                color: #ECEFF4;
                border: none;
                gridline-color: #4C566A;
            }
            QHeaderView::section {
                background-color: #434C5E;
                color: #ECEFF4;
                padding: 5px;
                border: none;
            }
        """)
        table_layout.addWidget(self.rules_table)
        
        content_layout.addWidget(table_container, 3) # Peso 3 (maior)

        # Gráfico
        chart_container = QFrame()
        chart_container.setStyleSheet("background-color: #2E3440; border-radius: 8px; padding: 10px;")
        chart_layout = QVBoxLayout(chart_container)
        
        lbl_chart = QLabel("📊 Distribuição de Impacto")
        lbl_chart.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECEFF4; margin-bottom: 10px;")
        chart_layout.addWidget(lbl_chart)
        
        # Figura maior e com melhor proporção
        self.figure = plt.figure(figsize=(6, 5), facecolor='#2E3440')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.canvas.setMinimumSize(400, 350)  # Tamanho mínimo
        chart_layout.addWidget(self.canvas)

        content_layout.addWidget(chart_container, 2) # Peso 2

        layout.addLayout(content_layout)

    def load_data(self):
        # Carregar dados do banco
        roi_stats = db_manager.get_roi_stats()
        general_stats = db_manager.get_dashboard_stats()

        # Atualizar KPIs com ROI Realizado vs Potencial
        self.card_roi_realizado.update_value(f"R$ {roi_stats['total_saved']:,.2f}")
        self.card_roi_potencial.update_value(f"R$ {roi_stats['roi_potencial']:,.2f}")
        self.card_roi_total.update_value(f"R$ {roi_stats['roi_total']:,.2f}")
        self.card_alertas.update_value(str(roi_stats['total_alertas'])) 

        # Atualizar Tabela
        self.rules_table.setRowCount(0)
        for rule in roi_stats['top_rules']:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)
            
            # Nome da regra (truncado se muito longo)
            rule_name = rule['rule_id']
            if len(rule_name) > 60:
                rule_name = rule_name[:57] + "..."
            
            desc = f"{rule_name} - {rule['description'][:50]}..."
            item_desc = QTableWidgetItem(desc)
            item_desc.setToolTip(f"{rule['rule_id']} - {rule['description']}")  # Tooltip completo
            
            item_qtd = QTableWidgetItem(str(rule['count']))
            item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            item_impact = QTableWidgetItem(f"R$ {rule['total_impact']:,.2f}")
            item_impact.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            self.rules_table.setItem(row, 0, item_desc)
            self.rules_table.setItem(row, 1, item_qtd)
            self.rules_table.setItem(row, 2, item_impact)
            
            # Ajustar altura da linha
            self.rules_table.setRowHeight(row, 40)

        # Atualizar Gráfico (Rosca)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = [r['rule_id'] for r in roi_stats['top_rules']]
        # Sanitizar sizes para evitar erro "cannot convert float NaN to integer" no matplotlib
        # Sanitizar sizes para evitar erro "cannot convert float NaN to integer" no matplotlib
        sizes = []
        for r in roi_stats['top_rules']:
            try:
                val = float(r['total_impact'])
                if val != val: # Check for NaN (float('nan') != float('nan'))
                    val = 0.0
            except (ValueError, TypeError):
                val = 0.0
            sizes.append(val)
        
        # Se a soma for 0, não desenhar o gráfico para evitar problemas visuais ou erros
        if sum(sizes) == 0:
            sizes = []
        
        if sizes:
            colors = ['#A3BE8C', '#88C0D0', '#81A1C1', '#5E81AC', '#B48EAD']
            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', 
                                            startangle=90, colors=colors[:len(sizes)])
            
            # Estilizar texto do gráfico
            for text in texts + autotexts:
                text.set_color('white')
                
            ax.legend(wedges, labels, title="Regras", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
        self.canvas.draw()
