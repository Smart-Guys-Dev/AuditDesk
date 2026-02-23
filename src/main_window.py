"""
MainWindow - Janela principal do AuditPlus v3.0
Responsável apenas pela estrutura: sidebar, navegação e composição de páginas.
"""
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QStackedWidget, QFrame)
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal

from src.workflow_controller import WorkflowController
from src.views.pages.welcome_page import PaginaBoasVindas
from src.views.pages.processor_page import PaginaProcessador
from src.views.pages.validator_page import PaginaValidador
from src.views.pages.hash_page import PaginaHash
from src.views.pages.history_page import PaginaHistorico
from src.views.pages.dashboard_page import PaginaDashboard
from src.views.pages.consulta_faturas_page import PaginaConsultaFaturas
from src.views.pages.importar_relatorios_page import PaginaImportarRelatorios
from src.views.pages.reports_page import PaginaRelatorios
from src.utils import resource_path
from src.ui_helpers import show_toast
from src.app_settings import app_settings


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user=None):
        super().__init__()
        user_id = user.id if user else None
        self.controller = WorkflowController(user_id=user_id)
        self.user = user
        self.setWindowTitle("Glox")

        # Ícone da aplicação
        icon_path = resource_path(os.path.join('src', 'assets', 'icon.png'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Detectar resolução e adaptar
        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()

        if screen_w <= 1366:
            self.sidebar_width = 210
            win_w, win_h = min(1300, screen_w - 30), min(720, screen_h - 50)
        elif screen_w <= 1920:
            self.sidebar_width = 230
            win_w, win_h = min(1400, screen_w - 100), min(850, screen_h - 100)
        else:
            self.sidebar_width = 260
            win_w, win_h = min(1600, screen_w - 150), min(950, screen_h - 100)

        # Restaurar ou centralizar
        saved_geo = app_settings.get_window_geometry()
        if saved_geo:
            self.restoreGeometry(saved_geo)
        else:
            self.setGeometry(
                (screen_w - win_w) // 2, (screen_h - win_h) // 2, win_w, win_h
            )

        saved_state = app_settings.get_window_state()
        if saved_state:
            self.restoreState(saved_state)

        # Estilos
        self.load_styles()

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # Páginas
        self.pages_widget = QStackedWidget()
        self._build_pages()
        main_layout.addWidget(self.pages_widget)

        # Atalhos
        self._setup_shortcuts()

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(self.sidebar_width)

        layout = QVBoxLayout(sidebar)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(2)

        # Logo
        logo_container = QFrame()
        logo_container.setObjectName("logo_container")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(12, 10, 12, 10)
        logo_layout.setSpacing(2)

        logo_label = QLabel("Audit+")
        logo_label.setStyleSheet(
            "font-size: 20px; font-weight: 800; letter-spacing: -0.5px;"
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel("Enterprise v3.0")
        version_label.setStyleSheet("font-size: 9px; color: rgba(255,255,255,0.7); font-weight: 500;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(version_label)
        layout.addWidget(logo_container)
        layout.addSpacing(16)

        # Navegação
        nav_label = QLabel("NAVEGAÇÃO")
        nav_label.setObjectName("nav_label")
        layout.addWidget(nav_label)
        layout.addSpacing(4)

        # Botões de navegação com ícones
        nav_items = [
            ("🏠  Painel", "Ctrl+Home"),
            ("⚙️  Processador", "Ctrl+P"),
            ("📋  Validador XML", "Ctrl+Shift+V"),
            ("🔑  Atualizar HASH", None),
            ("📊  Histórico", "Ctrl+H"),
            ("📈  Relatórios", "Ctrl+D"),
            ("🔍  Consultar", None),
            ("📥  Importar", None),
        ]

        self.nav_buttons = []
        for label, shortcut in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if shortcut:
                btn.setToolTip(f"{label.split('  ')[-1]} ({shortcut})")
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        self.nav_buttons[0].setChecked(True)

        # Admin section
        self.btn_gestao_usuarios = None
        if self.user and self.user.role == 'ADMIN':
            layout.addSpacing(12)
            admin_label = QLabel("ADMINISTRAÇÃO")
            admin_label.setObjectName("nav_label")
            layout.addWidget(admin_label)
            layout.addSpacing(4)

            self.btn_gestao_usuarios = QPushButton("👥  Usuários")
            self.btn_gestao_usuarios.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_gestao_usuarios.clicked.connect(self._abrir_gestao_usuarios)
            layout.addWidget(self.btn_gestao_usuarios)

        layout.addStretch()

        # Rodapé com info do usuário
        if self.user:
            user_container = QFrame()
            user_container.setObjectName("user_container")
            user_layout = QVBoxLayout(user_container)
            user_layout.setSpacing(6)
            user_layout.setContentsMargins(12, 10, 12, 10)

            # Nome do usuário
            user_info = QLabel(f"👤 {self.user.full_name or self.user.username}")
            user_info.setStyleSheet("font-size: 12px; font-weight: 600; color: #E6EDF3;")

            # Badge de role
            role_text = self.user.role
            role_color = "#3FB950" if role_text == "ADMIN" else "#58A6FF"
            role_label = QLabel(role_text)
            role_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 9px;
                    font-weight: 700;
                    color: {role_color};
                    background-color: {role_color}20;
                    padding: 2px 8px;
                    border-radius: 4px;
                    border: 1px solid {role_color}40;
                }}
            """)
            role_label.setFixedWidth(65)
            role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_logout = QPushButton("Sair")
            btn_logout.setObjectName("btn_danger")
            btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_logout.clicked.connect(self.logout_requested.emit)

            user_layout.addWidget(user_info)
            user_layout.addWidget(role_label)
            user_layout.addWidget(btn_logout)
            layout.addWidget(user_container)

        # Conectar navegação
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, idx=i: self._mudar_pagina(idx))

        return sidebar


    def _build_pages(self):
        self.page_painel = PaginaBoasVindas()
        self.page_painel.navigate_to.connect(self._mudar_pagina)

        self.page_processador = PaginaProcessador(self.controller)
        self.page_validador = PaginaValidador(self.controller)
        self.page_hash = PaginaHash(self.controller)
        self.page_historico = PaginaHistorico()
        self.page_relatorios = PaginaRelatorios()
        self.page_consulta = PaginaConsultaFaturas()
        self.page_importar = PaginaImportarRelatorios()

        for page in [
            self.page_painel, self.page_processador, self.page_validador,
            self.page_hash, self.page_historico, self.page_relatorios,
            self.page_consulta, self.page_importar
        ]:
            self.pages_widget.addWidget(page)

    def _mudar_pagina(self, index):
        self.pages_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _abrir_gestao_usuarios(self):
        from src.views.user_management import UserManagementWindow
        self.gestao_window = UserManagementWindow()
        self.gestao_window.show()

    def _setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+Home", 0),
            ("Ctrl+P", 1),
            ("Ctrl+Shift+V", 2),
            ("Ctrl+H", 4),
            ("Ctrl+D", 5),
        ]

        for key, idx in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(lambda checked, i=idx: self._mudar_pagina(i))
            self.addAction(action)

        # F5: Refresh
        action_refresh = QAction(self)
        action_refresh.setShortcut(QKeySequence("F5"))
        action_refresh.triggered.connect(self._refresh_stats)
        self.addAction(action_refresh)

        self.statusBar().showMessage(
            "Atalhos: Ctrl+P (Processador) | Ctrl+Shift+V (Validador) | "
            "Ctrl+H (Histórico) | Ctrl+D (Relatórios) | F5 (Atualizar)",
            10000
        )

    def _refresh_stats(self):
        current = self.pages_widget.currentIndex()
        if current == 0:
            old = self.pages_widget.widget(0)
            self.page_painel = PaginaBoasVindas()
            self.pages_widget.removeWidget(old)
            self.pages_widget.insertWidget(0, self.page_painel)
            self.pages_widget.setCurrentIndex(0)
            old.deleteLater()
            show_toast(self, "Estatísticas atualizadas!", "success", 2000)

    def load_styles(self):
        try:
            style_path = resource_path(os.path.join('src', 'assets', 'styles.qss'))
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erro ao carregar estilos: {e}")

    def closeEvent(self, event):
        app_settings.save_window_geometry(self.saveGeometry())
        app_settings.save_window_state(self.saveState())
        event.accept()
