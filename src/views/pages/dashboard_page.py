from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QGraphicsDropShadowEffect,
                             QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

from src.database import db_manager

# ===== CORES UNIMED =====
UNIMED_GREEN = "#00A859"
UNIMED_DARK_GREEN = "#008C45"
UNIMED_LIGHT_GREEN = "#00C16E"

# ===== TEMA DARK MODERNO =====
BG_DARK = "#0D1117"
BG_CARD = "#161B22"
BG_CARD_HOVER = "#1C2128"
BORDER_COLOR = "#30363D"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"
ACCENT_BLUE = "#58A6FF"
ACCENT_PURPLE = "#A371F7"
ACCENT_YELLOW = "#F0C53E"
ACCENT_RED = "#F85149"


class ModernKPICard(QFrame):
    """Card KPI moderno com efeito glassmorphism e gradiente"""
    
    def __init__(self, title, value, icon_text="📊", gradient_start="#00A859", gradient_end="#008C45", size="normal"):
        super().__init__()
        
        self.size = size
        min_height = 180 if size == "large" else 140 if size == "normal" else 100
        
        self.setMinimumHeight(min_height)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {gradient_start},
                    stop:1 {gradient_end}
                );
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QLabel {{ 
                color: white; 
                border: none; 
                background: transparent; 
            }}
        """)
        
        # Sombra 3D
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(gradient_start))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Header com ícone e título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Ícone grande
        icon_label = QLabel(icon_text)
        icon_size = "36px" if size == "large" else "28px"
        icon_label.setStyleSheet(f"font-size: {icon_size};")
        
        # Título
        title_label = QLabel(title)
        title_size = "15px" if size == "large" else "13px"
        title_label.setStyleSheet(f"""
            font-size: {title_size}; 
            font-weight: 600; 
            color: rgba(255, 255, 255, 0.9);
            letter-spacing: 0.5px;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Valor grande
        self.value_label = QLabel(value)
        value_size = "38px" if size == "large" else "28px"
        self.value_label.setStyleSheet(f"""
            font-size: {value_size}; 
            font-weight: 800; 
            margin-top: 12px;
            letter-spacing: -1px;
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def update_value(self, value):
        self.value_label.setText(value)


class ModernSectionCard(QFrame):
    """Container moderno para seções"""
    
    def __init__(self, title, icon="📊"):
        super().__init__()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 16px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        
        # Header da seção
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-size: 16px; 
            font-weight: 700; 
            color: {TEXT_PRIMARY};
            letter-spacing: 0.3px;
        """)
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        
        self.main_layout.addLayout(header)
        
        # Linha separadora verde
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {UNIMED_GREEN},
                stop:0.5 {UNIMED_LIGHT_GREEN},
                stop:1 transparent
            );
            border-radius: 1px;
        """)
        self.main_layout.addWidget(separator)
    
    def add_content(self, widget):
        self.main_layout.addWidget(widget)


class PaginaDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # ScrollArea para conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {BG_DARK};
            }}
            QScrollBar:vertical {{
                background: {BG_DARK};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {UNIMED_GREEN};
                border-radius: 4px;
                min-height: 30px;
            }}
        """)
        
        # Container do conteúdo
        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_DARK};")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 25, 30, 30)
        layout.setSpacing(25)

        # ===== HEADER =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Título com destaque verde
        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        
        welcome_lbl = QLabel("👋 Bem-vindo ao")
        welcome_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        title = QLabel("Dashboard de Gestão & Economia")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: 800; 
            color: {TEXT_PRIMARY};
            letter-spacing: -0.5px;
        """)
        
        subtitle = QLabel("Unimed Campo Grande")
        subtitle.setStyleSheet(f"""
            font-size: 14px; 
            color: {UNIMED_GREEN}; 
            font-weight: 600;
            letter-spacing: 1px;
        """)
        
        title_container.addWidget(welcome_lbl)
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Filtro de período estilizado
        filter_container = QFrame()
        filter_container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
                padding: 8px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)
        
        period_icon = QLabel("📅")
        period_icon.setStyleSheet("font-size: 18px;")
        
        period_lbl = QLabel("Período:")
        period_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        
        self.period_filter = QComboBox()
        self.period_filter.addItems(["Todo o Período", "Este Mês", "Mês Anterior", "Últimos 7 dias"])
        self.period_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_DARK};
                color: {TEXT_PRIMARY};
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid {BORDER_COLOR};
                min-width: 160px;
                font-weight: 500;
            }}
            QComboBox:hover {{
                border-color: {UNIMED_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_CARD};
                color: {TEXT_PRIMARY};
                selection-background-color: {UNIMED_GREEN};
                border-radius: 8px;
            }}
        """)
        self.period_filter.currentIndexChanged.connect(self.load_data)
        
        filter_layout.addWidget(period_icon)
        filter_layout.addWidget(period_lbl)
        filter_layout.addWidget(self.period_filter)
        
        # Botão atualizar
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {UNIMED_GREEN};
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {UNIMED_LIGHT_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {UNIMED_DARK_GREEN};
            }}
        """)
        btn_refresh.clicked.connect(self.load_data)
        
        header_layout.addWidget(filter_container)
        header_layout.addWidget(btn_refresh)
        
        layout.addLayout(header_layout)

        # ===== KPIs EM GRID COMPACTO 2x4 =====
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(16)
        
        # ROW 1 - Métricas financeiras
        self.card_total = ModernKPICard(
            "Economia Total", "R$ 0,00", "💰",
            gradient_start=UNIMED_GREEN, gradient_end=UNIMED_DARK_GREEN,
            size="normal"
        )
        kpi_layout.addWidget(self.card_total, 0, 0)
        
        self.card_glosas = ModernKPICard(
            "Glosas Evitadas", "R$ 0,00", "✅",
            gradient_start="#2EA043", gradient_end="#238636",
            size="normal"
        )
        kpi_layout.addWidget(self.card_glosas, 0, 1)
        
        self.card_total_faturado = ModernKPICard(
            "Total Faturado", "R$ 0,00", "📊",
            gradient_start=ACCENT_YELLOW, gradient_end="#D4A72C",
            size="normal"
        )
        kpi_layout.addWidget(self.card_total_faturado, 0, 2)
        
        self.card_regras = ModernKPICard(
            "Regras Ativas", "0", "📋",
            gradient_start=ACCENT_PURPLE, gradient_end="#8B5CF6",
            size="normal"
        )
        kpi_layout.addWidget(self.card_regras, 0, 3)
        
        # ROW 2 - Métricas operacionais
        self.card_faturas = ModernKPICard(
            "Faturas Processadas", "0", "📦",
            gradient_start="#6E40C9", gradient_end="#553098",
            size="normal"
        )
        kpi_layout.addWidget(self.card_faturas, 1, 0)
        
        self.card_guias = ModernKPICard(
            "Guias Corrigidas", "0", "🔧",
            gradient_start=ACCENT_BLUE, gradient_end="#1F6FEB",
            size="normal"
        )
        kpi_layout.addWidget(self.card_guias, 1, 1)
        
        self.card_sucesso = ModernKPICard(
            "Taxa de Sucesso", "0%", "📊",
            gradient_start="#0EA5E9", gradient_end="#0284C7",
            size="normal"
        )
        kpi_layout.addWidget(self.card_sucesso, 1, 2)
        
        self.card_ultima_exec = ModernKPICard(
            "Última Execução", "--", "🕐",
            gradient_start="#64748B", gradient_end="#475569",
            size="normal"
        )
        kpi_layout.addWidget(self.card_ultima_exec, 1, 3)
        
        # Definir proporções iguais
        for i in range(4):
            kpi_layout.setColumnStretch(i, 1)
        
        layout.addLayout(kpi_layout)


        # ===== ÁREA CENTRAL ASSIMÉTRICA =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # --- TABELA DE TOP REGRAS ---
        table_section = ModernSectionCard("Top Regras que mais geraram economia", "🏆")
        
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Regra", "Aplicações", "Valor Economizado"])
        self.rules_table.verticalHeader().setVisible(False)
        self.rules_table.setShowGrid(False)
        self.rules_table.setAlternatingRowColors(True)
        
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.rules_table.setColumnWidth(1, 100)
        self.rules_table.setColumnWidth(2, 160)
        
        self.rules_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_DARK};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QTableWidget::item:alternate {{
                background-color: rgba(255, 255, 255, 0.02);
            }}
            QTableWidget::item:selected {{
                background-color: rgba(0, 168, 89, 0.2);
            }}
            QHeaderView::section {{
                background-color: {BG_CARD};
                color: {TEXT_SECONDARY};
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        
        table_section.add_content(self.rules_table)
        content_layout.addWidget(table_section, 3)

        # --- GRÁFICO ---
        chart_section = ModernSectionCard("Distribuição de Impacto", "📊")
        
        self.figure = plt.figure(figsize=(5, 4), facecolor=BG_CARD)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent; border-radius: 8px;")
        self.canvas.setMinimumHeight(300)
        
        chart_section.add_content(self.canvas)
        content_layout.addWidget(chart_section, 2)
        
        layout.addLayout(content_layout)
        
        # ===== SEÇÃO FATURAS POR AUDITOR =====
        auditor_section = ModernSectionCard("Faturas por Auditor", "👥")
        
        self.auditor_table = QTableWidget()
        self.auditor_table.setColumnCount(3)
        self.auditor_table.setHorizontalHeaderLabels(["Auditor", "Qtd Faturas", "Valor Total"])
        self.auditor_table.verticalHeader().setVisible(False)
        self.auditor_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.auditor_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.auditor_table.setShowGrid(False)
        self.auditor_table.setMaximumHeight(200)
        
        auditor_header = self.auditor_table.horizontalHeader()
        auditor_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        auditor_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        auditor_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.auditor_table.setColumnWidth(1, 100)
        self.auditor_table.setColumnWidth(2, 150)
        
        self.auditor_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_DARK};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QHeaderView::section {{
                background-color: {BG_CARD};
                color: {TEXT_SECONDARY};
                padding: 10px 8px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        
        auditor_section.add_content(self.auditor_table)
        layout.addWidget(auditor_section)
        
        # ===== RODAPÉ COM STATUS =====
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        
        # Status de conexão
        status_container = QFrame()
        status_container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
                padding: 8px 16px;
            }}
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(12, 8, 12, 8)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {UNIMED_GREEN}; font-size: 10px;")
        status_text = QLabel("Sistema operando normalmente")
        status_text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        
        self.last_update_lbl = QLabel("Última atualização: --")
        self.last_update_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        footer_layout.addWidget(status_container)
        footer_layout.addStretch()
        footer_layout.addWidget(self.last_update_lbl)
        
        layout.addLayout(footer_layout)
        
        # Adicionar ao scroll
        scroll.setWidget(content)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Carregar dados
        self.load_data()

    def load_data(self):
        from datetime import datetime
        
        # Carregar dados do banco
        roi_stats = db_manager.get_roi_stats()
        general_stats = db_manager.get_dashboard_stats()

        # ROW 1 - Métricas financeiras
        self.card_total.update_value(f"R$ {roi_stats['roi_total']:,.2f}")
        self.card_glosas.update_value(f"R$ {roi_stats['total_saved']:,.2f}")
        
        # Total Faturado - buscar das faturas importadas
        try:
            from src.database.fatura_repository import get_estatisticas_faturas
            fatura_stats = get_estatisticas_faturas()
            valor_faturado = fatura_stats.get('valor_total', 0)
            if valor_faturado > 0:
                self.card_total_faturado.update_value(f"R$ {valor_faturado:,.2f}")
            else:
                self.card_total_faturado.update_value("Importar")
        except:
            self.card_total_faturado.update_value("--")
        
        # Regras Ativas - buscar do banco de regras
        try:
            from src.database.rule_repository import RuleRepository
            rule_stats = RuleRepository.get_stats()
            self.card_regras.update_value(str(rule_stats.get('ativas', 0)))
        except:
            self.card_regras.update_value("--")
        
        # ROW 2 - Métricas operacionais
        total_faturas = general_stats.get('total_executions', 0)
        self.card_faturas.update_value(f"{total_faturas:,}")
        
        total_guias = general_stats.get('total_arquivos', 0)
        self.card_guias.update_value(f"{total_guias:,}")
        
        taxa_sucesso = general_stats.get('success_rate', 0)
        self.card_sucesso.update_value(f"{taxa_sucesso:.1f}%")
        
        # Última Execução - buscar do banco
        try:
            ultima_exec = db_manager.get_last_execution_time()
            if ultima_exec:
                self.card_ultima_exec.update_value(ultima_exec)
            else:
                self.card_ultima_exec.update_value("Nunca")
        except:
            self.card_ultima_exec.update_value("--")
        
        # Tabela de Faturas por Auditor
        try:
            from src.database.fatura_repository import get_faturas_por_auditor
            auditor_stats = get_faturas_por_auditor()
            
            self.auditor_table.setRowCount(len(auditor_stats))
            
            for row, stats in enumerate(auditor_stats):
                # Auditor
                item_auditor = QTableWidgetItem(stats['auditor'])
                item_auditor.setForeground(QColor(TEXT_PRIMARY))
                self.auditor_table.setItem(row, 0, item_auditor)
                
                # Quantidade
                item_qtd = QTableWidgetItem(f"{stats['total']:,}")
                item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_qtd.setForeground(QColor(UNIMED_GREEN))
                self.auditor_table.setItem(row, 1, item_qtd)
                
                # Valor
                item_valor = QTableWidgetItem(f"R$ {stats['valor']:,.2f}")
                item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                item_valor.setForeground(QColor(ACCENT_BLUE))
                self.auditor_table.setItem(row, 2, item_valor)
        except Exception as e:
            print(f"Erro ao carregar auditores: {e}")
        
        # Atualizar timestamp
        self.last_update_lbl.setText(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")


        # Atualizar Tabela
        self.rules_table.setRowCount(0)
        for rule in roi_stats['top_rules']:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)
            
            # Nome da regra formatado
            rule_name = rule['rule_id']
            if len(rule_name) > 50:
                rule_name = rule_name[:47] + "..."
            
            desc = f"{rule_name}"
            item_desc = QTableWidgetItem(desc)
            item_desc.setToolTip(f"{rule['rule_id']} - {rule['description']}")
            
            # Quantidade com badge
            item_qtd = QTableWidgetItem(str(rule['count']))
            item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Impacto formatado
            item_impact = QTableWidgetItem(f"R$ {rule['total_impact']:,.2f}")
            item_impact.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_impact.setForeground(QColor(UNIMED_GREEN))
            
            self.rules_table.setItem(row, 0, item_desc)
            self.rules_table.setItem(row, 1, item_qtd)
            self.rules_table.setItem(row, 2, item_impact)
            self.rules_table.setRowHeight(row, 50)

        # Atualizar Gráfico (Donut moderno)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(BG_CARD)
        
        labels = [r['rule_id'][:20] for r in roi_stats['top_rules']]
        sizes = []
        for r in roi_stats['top_rules']:
            try:
                val = float(r['total_impact'])
                if val != val:
                    val = 0.0
            except (ValueError, TypeError):
                val = 0.0
            sizes.append(val)
        
        if sum(sizes) == 0:
            # Mostrar mensagem quando não há dados
            ax.text(0.5, 0.5, 'Sem dados\npara exibir', 
                   horizontalalignment='center', verticalalignment='center',
                   fontsize=14, color=TEXT_SECONDARY,
                   transform=ax.transAxes)
            ax.axis('off')
        else:
            # Cores modernas
            colors = [UNIMED_GREEN, ACCENT_BLUE, ACCENT_PURPLE, ACCENT_YELLOW, '#EC6547']
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=None, 
                autopct='%1.1f%%',
                startangle=90, 
                colors=colors[:len(sizes)],
                wedgeprops=dict(width=0.6, edgecolor=BG_CARD, linewidth=2),
                pctdistance=0.75
            )
            
            # Estilizar texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
            
            # Centro do donut
            centre_circle = plt.Circle((0, 0), 0.35, fc=BG_CARD)
            ax.add_patch(centre_circle)
            
            # Legenda moderna
            ax.legend(
                wedges, labels, 
                title="Regras", 
                loc="center left", 
                bbox_to_anchor=(1.05, 0.5),
                fontsize=9,
                frameon=False,
                labelcolor=TEXT_PRIMARY,
                title_fontsize=10
            )
            
            ax.axis('equal')
        
        self.figure.tight_layout()
        self.canvas.draw()
