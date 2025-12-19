
import sys, os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QStackedWidget, QLineEdit, QTextEdit,
                             QFileDialog, QInputDialog, QMessageBox, QProgressBar, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QScrollArea)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QThread, QSize, QTimer, pyqtSignal

from .workflow_controller import WorkflowController
from .worker import Worker
from .history_page import PaginaHistorico
from .dashboard_page import PaginaDashboard
from src.utils import resource_path

def load_stylesheet():
    """Carrega o arquivo de estilos QSS externo."""
    try:
        style_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles.qss')
        with open(style_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"AVISO: Arquivo de estilos não encontrado em {style_path}")
        return ""
    except Exception as e:
        print(f"ERRO ao carregar estilos: {e}")
        return ""

class PaginaBoasVindas(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # --- Header ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        logo = QLabel("Audit+")
        logo.setObjectName("main_logo")
        subtitulo = QLabel("Enterprise Edition • v3.0")
        subtitulo.setObjectName("subtitulo")
        
        header_layout.addWidget(logo)
        header_layout.addWidget(subtitulo)
        main_layout.addLayout(header_layout)
        
        # --- KPI Cards (Estatísticas) ---
        from src.database import db_manager
        stats = db_manager.get_dashboard_stats()
        
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        self._add_kpi_card(kpi_layout, "Execuções", str(stats['total_executions']))
        self._add_kpi_card(kpi_layout, "Arquivos", str(stats['total_files']))
        self._add_kpi_card(kpi_layout, "Sucesso", f"{stats['success_rate']:.1f}%")
        self._add_kpi_card(kpi_layout, "Erros", str(stats['error_count']))
        
        main_layout.addLayout(kpi_layout)
        
        # --- Funcionalidades (Grid) ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)
        
        card1 = self._create_feature_card("📄", "Processador", "Importação e processamento em lote")
        card2 = self._create_feature_card("👥", "Distribuição", "Divisão inteligente de carga de trabalho")
        card3 = self._create_feature_card("✓", "Validação TISS", "Verificação de regras e estrutura XSD")
        
        grid_layout.addWidget(card1)
        grid_layout.addWidget(card2)
        grid_layout.addWidget(card3)
        
        main_layout.addLayout(grid_layout)
        
        # --- Atividade Recente (Tabela) ---
        lbl_activity = QLabel("Atividade Recente")
        lbl_activity.setStyleSheet("font-size: 18px; font-weight: 700; color: #ECEFF4; margin-top: 10px;")
        main_layout.addWidget(lbl_activity)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tipo", "Usuário", "Data", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setFixedHeight(200) # Altura fixa para não ocupar tudo
        
        self._load_recent_activity()
        main_layout.addWidget(self.table)
        
        # --- Footer ---
        main_layout.addStretch()
        watermark = QLabel("Audit+ Enterprise • Powered by BisonCode")
        watermark.setObjectName("watermark")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(watermark)

    def _add_kpi_card(self, layout, label, value):
        card = QFrame()
        card.setObjectName("kpi_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_val = QLabel(value)
        lbl_val.setObjectName("kpi_value")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("kpi_label")
        lbl_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(lbl_val)
        card_layout.addWidget(lbl_lbl)
        layout.addWidget(card)

    def _create_feature_card(self, icon, title, description):
        card = QFrame()
        card.setObjectName("feature_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 32px;")
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("card_title")
        
        lbl_desc = QLabel(description)
        lbl_desc.setObjectName("card_description")
        lbl_desc.setWordWrap(True)
        
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_desc)
        card_layout.addStretch()
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
            self.table.setItem(row, 4, QTableWidgetItem(act['status']))

class PaginaProcessador(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Processador de Faturas")
        titulo.setObjectName("titulo_pagina")
        layout.addWidget(titulo)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        selecao_layout = QHBoxLayout()
        selecao_layout.setSpacing(10)
        
        label_pasta = QLabel("Pasta das Faturas:")
        label_pasta.setMinimumWidth(120)
        
        self.caminho_pasta_edit = QLineEdit()
        self.caminho_pasta_edit.setReadOnly(True)
        self.caminho_pasta_edit.setPlaceholderText("Selecione a pasta contendo os arquivos ZIP...")
        self.caminho_pasta_edit.setToolTip("Pasta contendo os arquivos ZIP das faturas a serem processadas")
        
        btn_procurar = QPushButton("📁 Procurar...")
        btn_procurar.setToolTip("Selecionar pasta com arquivos ZIP")
        btn_procurar.setMinimumWidth(120)
        
        selecao_layout.addWidget(label_pasta)
        selecao_layout.addWidget(self.caminho_pasta_edit, 1)
        selecao_layout.addWidget(btn_procurar)

        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        
        self.btn_iniciar_importacao = QPushButton("1️⃣ Importar Faturas")
        self.btn_iniciar_importacao.setToolTip("Importa e processa arquivos ZIP das faturas")
        self.btn_iniciar_importacao.setMinimumHeight(45)
        
        self.btn_iniciar_distribuicao = QPushButton("2️⃣ Distribuir Faturas")
        self.btn_iniciar_distribuicao.setToolTip("Distribui faturas entre auditores")
        self.btn_iniciar_distribuicao.setMinimumHeight(45)
        
        self.btn_preparar_correcao = QPushButton("3️⃣ Preparar Correção XML")
        self.btn_preparar_correcao.setToolTip("Prepara arquivos XML para correção")
        self.btn_preparar_correcao.setMinimumHeight(45)
        
        botoes_layout.addWidget(self.btn_iniciar_importacao)
        botoes_layout.addWidget(self.btn_iniciar_distribuicao)
        botoes_layout.addWidget(self.btn_preparar_correcao)

        self.btn_iniciar_distribuicao.setEnabled(False)
        self.btn_preparar_correcao.setEnabled(False)
        
        # Área de log com título
        log_label = QLabel("📋 Log de Execução:")
        log_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-top: 10px;")
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("As mensagens de execução aparecerão aqui...")
        
        layout.addLayout(selecao_layout)
        layout.addLayout(botoes_layout)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)
        
        btn_procurar.clicked.connect(self.selecionar_pasta)
        self.btn_iniciar_importacao.clicked.connect(self.iniciar_importacao)
        self.btn_iniciar_distribuicao.clicked.connect(self.iniciar_distribuicao)
        self.btn_preparar_correcao.clicked.connect(self.iniciar_preparacao_correcao)

    def log_message(self, message):
        self.log_area.append(message)
        
    def set_ui_enabled(self, enabled):
        self.btn_iniciar_importacao.setEnabled(enabled)
        faturas_processadas = bool(self.controller.lista_faturas_processadas)
        self.btn_iniciar_distribuicao.setEnabled(faturas_processadas and enabled)
        distribuicao_feita = bool(self.controller.plano_ultima_distribuicao)
        self.btn_preparar_correcao.setEnabled(distribuicao_feita and enabled)
        self.progress_bar.setVisible(not enabled)
        
    def selecionar_pasta(self):
        caminho_pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta com Faturas ZIP")
        if caminho_pasta:
            self.caminho_pasta_edit.setText(caminho_pasta)
            self.log_message(f"✓ INFO: Pasta selecionada: {caminho_pasta}")
            
    def iniciar_importacao(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta primeiro.")
            return
            
        self.log_area.clear()
        self.log_message("⏳ INFO: Iniciando importação...")
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.set_ui_enabled(False)
        
        self.worker_thread = QThread()
        self.worker = Worker(self.controller.processar_importacao_faturas, caminho_pasta)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_message)
        self.worker_thread.start()
        
    def iniciar_distribuicao(self):
        nomes_str, ok = QInputDialog.getText(
            self, "Definir Auditores",
            "Digite os nomes dos auditores, separados por vírgula:"
        )
        if ok and nomes_str:
            nomes_auditores = [nome.strip() for nome in nomes_str.split(',') if nome.strip()]
            if not nomes_auditores:
                self.log_message("⚠ AVISO: Nenhum nome de auditor válido fornecido.")
                return
                
            self.progress_bar.setRange(0, 0)
            self.set_ui_enabled(False)
            
            self.worker_thread = QThread()
            self.worker = Worker(self.controller.preparar_distribuicao_faturas, nomes_auditores)
            self.worker.moveToThread(self.worker_thread)
            
            self.worker_thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_task_finished)
            self.worker.error.connect(self.on_task_error)
            self.worker.progress.connect(self.log_message)
            self.worker_thread.start()
        else:
            self.log_message("⚠ AVISO: Distribuição cancelada pelo usuário.")
            
    def iniciar_preparacao_correcao(self):
        auditores = list(self.controller.plano_ultima_distribuicao.keys())
        if not auditores:
            QMessageBox.warning(self, "Aviso", "Nenhuma distribuição foi realizada ainda.")
            return
            
        nome_auditor, ok = QInputDialog.getItem(
            self, "Selecionar Auditor",
            "Para qual auditor deseja preparar os arquivos?",
            auditores, 0, False
        )
        if ok and nome_auditor:
            self.log_message(f"⏳ INFO: Preparando arquivos para o auditor: {nome_auditor}...")
            self.progress_bar.setRange(0, 0)
            self.set_ui_enabled(False)
            
            self.worker_thread = QThread()
            self.worker = Worker(self.controller.preparar_xmls_para_correcao, nome_auditor)
            self.worker.moveToThread(self.worker_thread)
            
            self.worker_thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_task_finished)
            self.worker.error.connect(self.on_task_error)
            self.worker.progress.connect(self.log_message)
            self.worker_thread.start()
            
    def on_task_finished(self, result=None):
        if result:
            sucesso, mensagem = result if isinstance(result, tuple) else (True, result)
            icon = "✓" if sucesso else "✗"
            log_level = "SUCESSO" if sucesso else "ERRO"
            self.log_message(f"{icon} {log_level}: {mensagem}")
        else:
            self.log_message("✓ SUCESSO: Tarefa concluída.")
            
        self.set_ui_enabled(True)
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
            
    def on_task_error(self, error_str):
        self.log_message(f"✗ ERRO CRÍTICO: {error_str}")
        QMessageBox.critical(self, "Erro na Execução", error_str)
        self.set_ui_enabled(True)
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

class PaginaValidador(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Validador PTU XML")
        titulo.setObjectName("titulo_pagina")
        layout.addWidget(titulo)

        selecao_layout = QHBoxLayout()
        selecao_layout.setSpacing(10)
        
        label_pasta = QLabel("Pasta dos XMLs:")
        label_pasta.setMinimumWidth(120)
        
        self.caminho_pasta_edit = QLineEdit()
        self.caminho_pasta_edit.setReadOnly(True)
        self.caminho_pasta_edit.setPlaceholderText("Selecione a pasta com arquivos XML...")
        self.caminho_pasta_edit.setToolTip("Pasta contendo os arquivos .051 para validação")
        
        btn_procurar = QPushButton("📁 Procurar...")
        btn_procurar.setToolTip("Selecionar pasta com arquivos XML")
        btn_procurar.setMinimumWidth(120)
        
        selecao_layout.addWidget(label_pasta)
        selecao_layout.addWidget(self.caminho_pasta_edit, 1)
        selecao_layout.addWidget(btn_procurar)

        botoes_validador_layout = QHBoxLayout()
        botoes_validador_layout.setSpacing(10)
        
        self.btn_iniciar_validacao = QPushButton("✓ Validar Regras (Lógica)")
        self.btn_iniciar_validacao.setToolTip("Valida regras de negócio nos arquivos XML")
        self.btn_iniciar_validacao.setMinimumHeight(45)
        
        self.btn_validar_xsd = QPushButton("📋 Validar Estrutura (XSD)")
        self.btn_validar_xsd.setToolTip("Valida estrutura XML contra schema XSD")
        self.btn_validar_xsd.setMinimumHeight(45)
        
        self.btn_verificar_internacao = QPushButton("🏥 Verificar Internações Curtas")
        self.btn_verificar_internacao.setToolTip("Verifica internações com curta permanência")
        self.btn_verificar_internacao.setMinimumHeight(45)

        botoes_validador_layout.addWidget(self.btn_iniciar_validacao)
        botoes_validador_layout.addWidget(self.btn_validar_xsd)
        botoes_validador_layout.addWidget(self.btn_verificar_internacao)

        log_label = QLabel("📋 Log da Validação:")
        log_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-top: 10px;")
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Os resultados da validação aparecerão aqui...")

        layout.addLayout(selecao_layout)
        layout.addLayout(botoes_validador_layout)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)

        btn_procurar.clicked.connect(self.selecionar_pasta)
        self.btn_iniciar_validacao.clicked.connect(self.iniciar_validacao)
        self.btn_validar_xsd.clicked.connect(self.iniciar_validacao_xsd)
        self.btn_verificar_internacao.clicked.connect(self.iniciar_verificacao_internacao_curta)

    def selecionar_pasta(self):
        pasta_sugerida = os.path.join(self.controller.pasta_faturas_importadas_atual or "", "Correção XML")
        caminho_pasta = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta com XMLs para Validar", pasta_sugerida
        )
        if caminho_pasta:
            self.caminho_pasta_edit.setText(caminho_pasta)
            self.log_area.append(f"✓ INFO: Pasta para validação selecionada: {caminho_pasta}")

    def iniciar_validacao(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta para validar.")
            return
            
        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando validação de regras (lógica)...")
        self.btn_iniciar_validacao.setEnabled(False)
        self.btn_validar_xsd.setEnabled(False)
        self.btn_verificar_internacao.setEnabled(False)
        
        self.worker_thread = QThread()
        self.worker = Worker(self.controller.executar_validacao_xmls, caminho_pasta)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

    def iniciar_validacao_xsd(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta para validar.")
            return
            
        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando validação de estrutura (XSD)...")
        self.btn_iniciar_validacao.setEnabled(False)
        self.btn_validar_xsd.setEnabled(False)
        self.btn_verificar_internacao.setEnabled(False)
        
        self.worker_thread = QThread()
        self.worker = Worker(self.controller.validar_pasta_com_xsd, caminho_pasta)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

    def iniciar_verificacao_internacao_curta(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta para verificar.")
            return

        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando verificação de internações curtas...")
        self.btn_iniciar_validacao.setEnabled(False)
        self.btn_validar_xsd.setEnabled(False)
        self.btn_verificar_internacao.setEnabled(False)

        self.worker_thread = QThread()
        self.worker = Worker(self.controller.executar_verificacao_internacao_curta, caminho_pasta)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

    def on_task_finished(self, result):
        sucesso, mensagem = result
        icon = "✓" if sucesso else "✗"
        self.log_area.append(f"{icon} {mensagem}")
        
        self.btn_iniciar_validacao.setEnabled(True)
        self.btn_validar_xsd.setEnabled(True)
        self.btn_verificar_internacao.setEnabled(True)
        
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_task_error(self, error_str):
        self.log_area.append(f"✗ ERRO CRÍTICO: {error_str}")
        QMessageBox.critical(self, "Erro na Validação", error_str)
        
        self.btn_iniciar_validacao.setEnabled(True)
        self.btn_validar_xsd.setEnabled(True)
        self.btn_verificar_internacao.setEnabled(True)
        
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

class PaginaHash(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None
        self.checkboxes = []  # Lista de checkboxes de arquivos
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Atualização de Hash")
        titulo.setObjectName("titulo_pagina")
        layout.addWidget(titulo)

        info_label = QLabel(
            "Selecione o auditor e os arquivos específicos para atualizar hash e recriar ZIPs."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Seleção de auditor
        auditor_layout = QHBoxLayout()
        auditor_label = QLabel("Auditor:")
        auditor_label.setMinimumWidth(80)
        
        self.auditor_combo = QInputDialog()  # Placeholder - será substituído por seleção dinâmica
        auditor_layout.addWidget(auditor_label)
        auditor_layout.addStretch()
        
        # Área de seleção de arquivos
        files_label = QLabel("📁 Arquivos Disponíveis:")
        files_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-top: 10px;")
        
        # Container com scroll para checkboxes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(250)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #4C566A;
                border-radius: 4px;
                background-color: #2E3440;
            }
            QScrollBar:vertical {
                border: none;
                background: #2E3440;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4C566A;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Container para checkboxes (será populado dinamicamente)
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setSpacing(5)
        self.files_layout.setContentsMargins(10, 10, 10, 10)
        self.files_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.files_container)

        # Botões de seleção
        selection_buttons_layout = QHBoxLayout()
        
        self.btn_select_all = QPushButton("✓ Selecionar Todos")
        self.btn_select_all.setToolTip("Selecionar todos os arquivos")
        self.btn_select_all.clicked.connect(self.select_all_files)
        
        self.btn_clear_all = QPushButton("✗ Limpar Seleção")
        self.btn_clear_all.setToolTip("Desmarcar todos os arquivos")
        self.btn_clear_all.clicked.connect(self.clear_all_files)
        
        selection_buttons_layout.addWidget(self.btn_select_all)
        selection_buttons_layout.addWidget(self.btn_clear_all)
        selection_buttons_layout.addStretch()
        
        # Contador de arquivos selecionados
        self.selection_counter = QLabel("0 arquivos selecionados")
        self.selection_counter.setObjectName("quick_stats")
        self.selection_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botão principal
        self.btn_atualizar_hash = QPushButton("# Atualizar Hash dos Selecionados")
        self.btn_atualizar_hash.setMinimumHeight(45)
        self.btn_atualizar_hash.setToolTip("Atualiza hash apenas dos arquivos selecionados")
        self.btn_atualizar_hash.clicked.connect(self.iniciar_atualizacao_hash)
        
        # Log
        log_label = QLabel("📋 Log da Atualização de Hash:")
        log_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-top: 10px;")
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("O progresso da atualização aparecerá aqui...")

        # Adicionar tudo ao layout
        layout.addLayout(auditor_layout)
        layout.addWidget(files_label)
        layout.addWidget(self.scroll_area)
        layout.addLayout(selection_buttons_layout)
        layout.addWidget(self.selection_counter)
        layout.addWidget(self.btn_atualizar_hash)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)
    
    def select_all_files(self):
        """Seleciona todos os checkboxes."""
        for cb in self.checkboxes:
            cb.setChecked(True)
        self.update_counter()
    
    def clear_all_files(self):
        """Desmarca todos os checkboxes."""
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.update_counter()
    
    def update_counter(self):
        """Atualiza o contador de arquivos selecionados."""
        selected = sum(1 for cb in self.checkboxes if cb.isChecked())
        total = len(self.checkboxes)
        self.selection_counter.setText(f"{selected} de {total} arquivos selecionados")
    
    def load_files_for_auditor(self, nome_auditor):
        """Carrega lista de arquivos para o auditor selecionado."""
        import os
        import glob
        
        # Limpar checkboxes anteriores
        for cb in self.checkboxes:
            cb.deleteLater()
        self.checkboxes.clear()
        
        # Obter pasta do auditor
        if not self.controller.pasta_faturas_importadas_atual:
            return
        
        pasta_auditor = os.path.join(
            self.controller.pasta_faturas_importadas_atual,
            "Correção XML",
            nome_auditor
        )
        
        if not os.path.exists(pasta_auditor):
            self.log_area.append(f"⚠ AVISO: Pasta não encontrada: {pasta_auditor}")
            return
        
        # Listar arquivos XML (.051)
        arquivos_xml = glob.glob(os.path.join(pasta_auditor, "*.051"))
        
        if not arquivos_xml:
            self.log_area.append(f"⚠ AVISO: Nenhum arquivo XML (.051) encontrado para {nome_auditor}")
            return
        
        # Criar checkboxes
        for arquivo_path in sorted(arquivos_xml):
            arquivo_nome = os.path.basename(arquivo_path)
            cb = QCheckBox(arquivo_nome)
            cb.setChecked(True)  # Todos selecionados por padrão
            cb.stateChanged.connect(self.update_counter)
            self.checkboxes.append(cb)
            self.files_layout.addWidget(cb)
        
        self.update_counter()
        self.log_area.append(f"✓ INFO: {len(arquivos_xml)} arquivos encontrados para {nome_auditor}")

    def get_selected_files(self):
        """Retorna lista de arquivos selecionados."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def on_task_finished(self, result):
        if result and isinstance(result, tuple):
            sucesso, mensagem = result
            icon = "✓" if sucesso else "✗"
            self.log_area.append(f"{icon} {mensagem}")
            
        self.btn_atualizar_hash.setEnabled(True)
        self.btn_select_all.setEnabled(True)
        self.btn_clear_all.setEnabled(True)
        
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_task_error(self, error_str):
        self.log_area.append(f"✗ ERRO CRÍTICO: {error_str}")
        QMessageBox.critical(self, "Erro na Atualização de Hash", error_str)
        
        self.btn_atualizar_hash.setEnabled(True)
        self.btn_select_all.setEnabled(True)
        self.btn_clear_all.setEnabled(True)
        
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def iniciar_atualizacao_hash(self):
        if not self.controller.plano_ultima_distribuicao:
            QMessageBox.warning(self, "Aviso", "Nenhuma distribuição foi realizada.")
            return
            
        auditores = list(self.controller.plano_ultima_distribuicao.keys())
        nome_auditor, ok = QInputDialog.getItem(
            self, "Selecionar Auditor",
            "Para qual auditor deseja atualizar o hash?",
            auditores, 0, False
        )
        
        if not ok or not nome_auditor:
            return
        
        # Carregar arquivos do auditor
        self.load_files_for_auditor(nome_auditor)
        
        # Aguardar seleção do usuário
        reply = QMessageBox.question(
            self,
            "Confirmar Seleção",
            f"Deseja atualizar hash dos arquivos selecionados?\n\n{self.selection_counter.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Obter arquivos selecionados
        arquivos_selecionados = self.get_selected_files()
        
        if not arquivos_selecionados:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo selecionado.")
            return
        
        self.log_area.clear()
        self.log_area.append(f"⏳ INFO: Iniciando atualização de HASH para: {nome_auditor}")
        self.log_area.append(f"📁 INFO: {len(arquivos_selecionados)} arquivo(s) selecionado(s)")
        
        self.btn_atualizar_hash.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_clear_all.setEnabled(False)
        
        self.worker_thread = QThread()
        # Passar lista de arquivos selecionados para o controller
        self.worker = Worker(
            self.controller.executar_atualizacao_hash,
            nome_auditor,
            arquivos_selecionados  # Nova funcionalidade!
        )
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

from src.utils import resource_path

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal() # Sinal para solicitar logout

    def __init__(self, user=None):
        super().__init__()
        self.controller = WorkflowController()
        self.user = user
        self.setWindowTitle("Audit+ v2.0")
        
        # Definir ícone da aplicação
        # Usando resource_path para funcionar no executável
        icon_path = resource_path(os.path.join('src', 'assets', 'icon.png'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setGeometry(200, 200, 1200, 800)
        
        # Carregar estilos do arquivo externo
        self.load_styles()

        # Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(5)

        btn_painel_principal = QPushButton("  🏠 Painel Principal")
        btn_painel_principal.setCheckable(True)
        btn_painel_principal.setChecked(True)

        btn_processador_xml = QPushButton("  📄 Processador")
        btn_processador_xml.setCheckable(True)

        btn_validador_tiss = QPushButton("  ✓ Validador PTU XML")
        btn_validador_tiss.setCheckable(True)

        btn_atualizar_hash = QPushButton("  # Atualizar HASH")
        btn_atualizar_hash.setCheckable(True)

        btn_historico = QPushButton("  📜 Histórico")
        btn_historico.setCheckable(True)

        btn_relatorios = QPushButton("  📊 Relatórios")
        btn_relatorios.setCheckable(True)

        sidebar_layout.addWidget(btn_painel_principal)
        sidebar_layout.addWidget(btn_processador_xml)
        sidebar_layout.addWidget(btn_validador_tiss)
        sidebar_layout.addWidget(btn_atualizar_hash)
        sidebar_layout.addWidget(btn_historico)
        sidebar_layout.addWidget(btn_relatorios)
        
        # Botão de Gestão de Usuários (Apenas Admin)
        self.btn_gestao_usuarios = None
        if self.user and self.user.role == 'ADMIN':
            self.btn_gestao_usuarios = QPushButton("  👥 Gestão de Usuários")
            self.btn_gestao_usuarios.setCheckable(False) # Abre modal, não muda página
            self.btn_gestao_usuarios.clicked.connect(self.abrir_gestao_usuarios)
            sidebar_layout.addWidget(self.btn_gestao_usuarios)

        sidebar_layout.addStretch()
        
        # Rodapé da Sidebar com info do usuário e Logout
        if self.user:
            user_container = QWidget()
            user_layout = QVBoxLayout(user_container)
            user_layout.setSpacing(5)
            
            user_info = QLabel(f"👤 {self.user.username}\n({self.user.role})")
            user_info.setStyleSheet("color: #D8DEE9; font-size: 12px; font-weight: bold;")
            user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_logout = QPushButton("Sair / Logoff")
            btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_logout.setStyleSheet("""
                QPushButton {
                    background-color: #BF616A;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    margin-top: 5px;
                }
                QPushButton:hover { background-color: #D08770; }
            """)
            btn_logout.clicked.connect(self.logout_requested.emit)
            
            user_layout.addWidget(user_info)
            user_layout.addWidget(btn_logout)
            sidebar_layout.addWidget(user_container)

        # Páginas
        self.pages_widget = QStackedWidget()
        self.page_painel_principal = PaginaDashboard()
        self.page_processador = PaginaProcessador(self.controller)
        self.page_validador = PaginaValidador(self.controller)
        self.page_hash = PaginaHash(self.controller)
        self.page_historico = PaginaHistorico()
        
        from src.reports_page import PaginaRelatorios
        self.page_relatorios = PaginaRelatorios()

        self.pages_widget.addWidget(self.page_painel_principal)
        self.pages_widget.addWidget(self.page_processador)
        self.pages_widget.addWidget(self.page_validador)
        self.pages_widget.addWidget(self.page_hash)
        self.pages_widget.addWidget(self.page_historico)
        self.pages_widget.addWidget(self.page_relatorios)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages_widget)

        # Conectar botões
        botoes = [btn_painel_principal, btn_processador_xml, btn_validador_tiss, btn_atualizar_hash, btn_historico, btn_relatorios]
        btn_painel_principal.clicked.connect(lambda: self.mudar_pagina(0, botoes))
        btn_processador_xml.clicked.connect(lambda: self.mudar_pagina(1, botoes))
        btn_validador_tiss.clicked.connect(lambda: self.mudar_pagina(2, botoes))
        btn_atualizar_hash.clicked.connect(lambda: self.mudar_pagina(3, botoes))
        btn_historico.clicked.connect(lambda: self.mudar_pagina(4, botoes))
        btn_relatorios.clicked.connect(lambda: self.mudar_pagina(5, botoes))

    def load_styles(self):
        """Carrega e aplica os estilos QSS."""
        try:
            style_path = resource_path(os.path.join('src', 'assets', 'styles.qss'))
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erro ao carregar estilos: {e}")

    def mudar_pagina(self, index, botoes):
        self.pages_widget.setCurrentIndex(index)
        for i, btn in enumerate(botoes):
            btn.setChecked(i == index)
            
    def abrir_gestao_usuarios(self):
        from src.user_management import UserManagementWindow
        self.gestao_window = UserManagementWindow()
        self.gestao_window.show()
