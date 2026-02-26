"""
Página de Boas-Vindas / Painel Principal
Dashboard premium com KPIs operacionais e atividade recente.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGraphicsDropShadowEffect,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QMouseEvent


class ClickableCard(QFrame):
    """Card que emite sinal ao ser clicado."""
    clicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)


class PaginaBoasVindas(QWidget):
    navigate_to = pyqtSignal(int)  # Emite índice da página

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 20)
        main_layout.setSpacing(20)

        # ── Header ──
        header = QHBoxLayout()
        header.setSpacing(0)

        header_left = QVBoxLayout()
        header_left.setSpacing(2)

        logo = QLabel("Audit+")
        logo.setObjectName("main_logo")

        subtitulo = QLabel("Enterprise Edition • v3.0")
        subtitulo.setObjectName("subtitulo")

        header_left.addWidget(logo)
        header_left.addWidget(subtitulo)

        header.addLayout(header_left)
        header.addStretch()

        # Badge do banco
        from src.database.db_manager import DB_PROVIDER
        badge_db = QLabel(f"⚡ {DB_PROVIDER.upper()}")
        badge_db.setStyleSheet("""
            QLabel {
                background-color: rgba(63, 185, 80, 0.12);
                color: #3FB950;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 12px;
                border-radius: 12px;
                border: 1px solid rgba(63, 185, 80, 0.25);
            }
        """)
        header.addWidget(badge_db, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_layout.addLayout(header)

        # ── KPI Cards — Operacional ──
        from src.database import db_manager
        stats = db_manager.get_dashboard_stats()

        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        self._add_kpi_card(kpi_layout, "EXECUÇÕES", str(stats['total_executions']),
                           "#58A6FF", "📊")
        self._add_kpi_card(kpi_layout, "ARQUIVOS", str(stats['total_files']),
                           "#D2A8FF", "📁")
        self._add_kpi_card(kpi_layout, "TAXA SUCESSO", f"{stats['success_rate']:.1f}%",
                           "#3FB950", "✓")
        self._add_kpi_card(kpi_layout, "ERROS", str(stats['error_count']),
                           "#DA3633" if stats['error_count'] > 0 else "#484F58", "⚠")

        main_layout.addLayout(kpi_layout)

        # ── Acesso Rápido ──
        lbl_quick = QLabel("Acesso Rápido")
        lbl_quick.setObjectName("section_title")
        main_layout.addWidget(lbl_quick)

        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(12)

        # page_index: 1=Processador, 2=Validador, 6=Consultar
        card1 = self._create_compact_card("⚙️", "Processador",
                                          "Importar e corrigir XMLs em lote", "#58A6FF", 1)
        card2 = self._create_compact_card("📋", "Validador TISS",
                                          "Verificar regras e estrutura XSD", "#3FB950", 2)
        card3 = self._create_compact_card("🔍", "Consultar Fatura",
                                          "Buscar status por número", "#D2A8FF", 6)

        grid_layout.addWidget(card1)
        grid_layout.addWidget(card2)
        grid_layout.addWidget(card3)

        main_layout.addLayout(grid_layout)

        # ── Admin Actions ──
        admin_actions_layout = QHBoxLayout()
        admin_actions_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_reset_db = QPushButton("🗑️ Limpar Histórico de Processamento")
        self.btn_reset_db.setObjectName("btn_danger")
        self.btn_reset_db.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_db.setFixedWidth(280)
        self.btn_reset_db.clicked.connect(self._confirm_reset_db)
        
        admin_actions_layout.addWidget(self.btn_reset_db)
        admin_actions_layout.addStretch()
        
        main_layout.addLayout(admin_actions_layout)


        # ── Atividade Recente ──
        lbl_activity = QLabel("Atividade Recente")
        lbl_activity.setObjectName("section_title")
        main_layout.addWidget(lbl_activity)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "TIPO", "USUÁRIO", "DATA", "STATUS"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(200)

        self._load_recent_activity()
        main_layout.addWidget(self.table)

        # ── Footer ──
        main_layout.addStretch()
        watermark = QLabel("Audit+ Enterprise • Desenvolvido por Pedro Lucas Lima de Freitas")
        watermark.setObjectName("watermark")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(watermark)

    def _add_kpi_card(self, layout, label, value, accent_color, icon):
        card = QFrame()
        card.setObjectName("kpi_card")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(12)

        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {accent_color}15;
                border-radius: 10px;
                font-size: 16px;
            }}
        """)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(0, 0, 0, 0)

        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 700;
                color: {accent_color};
                background: transparent;
                border: none;
            }}
        """)

        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("kpi_label")

        text_layout.addWidget(lbl_val)
        text_layout.addWidget(lbl_lbl)

        card_layout.addWidget(icon_lbl)
        card_layout.addLayout(text_layout)
        card_layout.addStretch()
        layout.addWidget(card)

    def _create_compact_card(self, icon, title, description, accent_color, page_index=0):
        card = ClickableCard()
        card.setObjectName("feature_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(12)

        # Icon
        lbl_icon = QLabel(icon)
        lbl_icon.setFixedSize(36, 36)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet(f"""
            QLabel {{
                background-color: {accent_color}12;
                border-radius: 8px;
                font-size: 16px;
            }}
        """)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #E6EDF3;")

        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet("font-size: 11px; color: #8B949E;")

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_desc)

        card_layout.addWidget(lbl_icon)
        card_layout.addLayout(text_layout)
        card_layout.addStretch()

        # Arrow
        arrow = QLabel("›")
        arrow.setStyleSheet("font-size: 18px; color: #30363D; font-weight: 300;")
        card_layout.addWidget(arrow)

        card.clicked.connect(lambda idx=page_index: self.navigate_to.emit(idx))
        return card

    def _load_recent_activity(self):
        from src.database import db_manager
        activities = db_manager.get_recent_activity(5)
        self.table.setRowCount(len(activities))

        for row, act in enumerate(activities):
            self.table.setItem(row, 0, QTableWidgetItem(str(act['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(act['tipo']))
            self.table.setItem(row, 2, QTableWidgetItem(act['usuario']))
            self.table.setItem(row, 3, QTableWidgetItem(act['data']))

            status_item = QTableWidgetItem(act['status'])
            if 'Sucesso' in act['status'] or 'COMPLETED' in act['status'].upper():
                status_item.setForeground(QColor("#3FB950"))
            elif 'Erro' in act['status'] or 'ERROR' in act['status'].upper():
                status_item.setForeground(QColor("#DA3633"))
            else:
                status_item.setForeground(QColor("#8B949E"))
            self.table.setItem(row, 4, status_item)

    def _confirm_reset_db(self):
        """Mostra confirmação antes de resetar o banco."""
        reply = QMessageBox.question(
            self, "Confirmar Reset",
            "Você tem certeza que deseja limpar todo o histórico de processamento?\n\n"
            "Isso permitirá re-validar arquivos que já foram processados anteriormente.\n"
            "⚠️ Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from src.database import db_manager
            success, message = db_manager.reset_processing_data()
            if success:
                QMessageBox.information(self, "Sucesso", message)
                # Recarregar estatísticas e tabela
                self.setup_ui() # Gamble: redesenha tudo
            else:
                QMessageBox.critical(self, "Erro", message)

