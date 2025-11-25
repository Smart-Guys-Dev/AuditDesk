# src/main_window.py

import sys, os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QStackedWidget, QLineEdit, QTextEdit,
                             QFileDialog, QInputDialog, QMessageBox, QProgressBar, QFrame)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, QSize, QTimer

# --- IMPORTAÇÕES CORRIGIDAS ---
from .workflow_controller import WorkflowController
from .worker import Worker

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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header Section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        
        # Logo e título
        logo_titulo = QLabel("Audit+")
        logo_titulo.setObjectName("main_logo")
        logo_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        subtitulo = QLabel("Automação e validação de arquivos PTU")
        subtitulo.setObjectName("main_subtitle")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        header_layout.addWidget(logo_titulo)
        header_layout.addWidget(subtitulo)
        
        # Cards de funcionalidades em grid 2x2
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(20)
        
        # Primeira linha de cards
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        card1 = self._create_feature_card(
            "📄", "Processador XML",
            "Importe e processe faturas automaticamente"
        )
        card2 = self._create_feature_card(
            "👥", "Distribuição",
            "Distribua faturas entre auditores de forma inteligente"
        )
        
        row1.addWidget(card1)
        row1.addWidget(card2)
        
        # Segunda linha de cards
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        
        card3 = self._create_feature_card(
            "✓", "Validação TISS",
            "Valide regras de negócio e estrutura XSD"
        )
        card4 = self._create_feature_card(
            "#", "Hash & Empacotamento",
            "Atualize hash e recrie arquivos ZIP finais"
        )
        
        row2.addWidget(card3)
        row2.addWidget(card4)
        
        cards_layout.addLayout(row1)
        cards_layout.addLayout(row2)
        
        # Quick Stats (opcional - pode ser expandido futuramente)
        stats_label = QLabel("Selecione uma opção no menu lateral para começar →")
        stats_label.setObjectName("quick_stats")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Adicionar tudo ao layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(cards_container)
        main_layout.addStretch()
        main_layout.addWidget(stats_label)
        
        # Marca d'água no canto inferior
        watermark = QLabel("Audit+ v2.0  •  Powered by BisonCode")
        watermark.setObjectName("watermark")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        main_layout.addWidget(watermark)
    
    def _create_feature_card(self, icon, title, description):
        """Cria um card de funcionalidade com ícone, título e descrição."""
        card = QFrame()
        card.setObjectName("feature_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        # Ícone
        icon_label = QLabel(icon)
        icon_label.setObjectName("card_icon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Descrição
        desc_label = QLabel(description)
        desc_label.setObjectName("card_description")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc_label.setWordWrap(True)
        
        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addStretch()
        
        return card

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

        titulo = QLabel("Validador TISS")
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
        self.files_scroll = QTextEdit()
        self.files_scroll.setReadOnly(True)
        self.files_scroll.setMaximumHeight(200)
        self.files_scroll.setPlaceholderText("Selecione um auditor para ver os arquivos disponíveis...")
        
        # Container para checkboxes (será populado dinamicamente)
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setSpacing(8)
        self.files_layout.setContentsMargins(10, 10, 10, 10)
        
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
        layout.addWidget(self.files_container)
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
        
        # Listar arquivos ZIP
        arquivos_zip = glob.glob(os.path.join(pasta_auditor, "*.zip"))
        
        if not arquivos_zip:
            self.log_area.append(f"⚠ AVISO: Nenhum arquivo ZIP encontrado para {nome_auditor}")
            return
        
        # Criar checkboxes
        for arquivo_path in sorted(arquivos_zip):
            arquivo_nome = os.path.basename(arquivo_path)
            cb = QCheckBox(arquivo_nome)
            cb.setChecked(True)  # Todos selecionados por padrão
            cb.stateChanged.connect(self.update_counter)
            self.checkboxes.append(cb)
            self.files_layout.addWidget(cb)
        
        self.update_counter()
        self.log_area.append(f"✓ INFO: {len(arquivos_zip)} arquivos encontrados para {nome_auditor}")

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = WorkflowController()
        self.setWindowTitle("Audit+ v2.0")
        
        # Definir ícone da aplicação
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setGeometry(200, 200, 1200, 800)
        
        # Carregar estilos do arquivo externo
        stylesheet = load_stylesheet()
        if stylesheet:
            self.setStyleSheet(stylesheet)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
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

        btn_processador_xml = QPushButton("  📄 Processador XML")
        btn_processador_xml.setCheckable(True)

        btn_validador_tiss = QPushButton("  ✓ Validador TISS")
        btn_validador_tiss.setCheckable(True)

        btn_atualizar_hash = QPushButton("  # Atualizar HASH")
        btn_atualizar_hash.setCheckable(True)

        sidebar_layout.addWidget(btn_painel_principal)
        sidebar_layout.addWidget(btn_processador_xml)
        sidebar_layout.addWidget(btn_validador_tiss)
        sidebar_layout.addWidget(btn_atualizar_hash)
        sidebar_layout.addStretch()

        # Páginas
        self.pages_widget = QStackedWidget()
        self.page_painel_principal = PaginaBoasVindas()
        self.page_processador = PaginaProcessador(self.controller)
        self.page_validador = PaginaValidador(self.controller)
        self.page_hash = PaginaHash(self.controller)

        self.pages_widget.addWidget(self.page_painel_principal)
        self.pages_widget.addWidget(self.page_processador)
        self.pages_widget.addWidget(self.page_validador)
        self.pages_widget.addWidget(self.page_hash)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages_widget)

        # Conectar botões
        btn_painel_principal.clicked.connect(lambda: self.mudar_pagina(0, [btn_painel_principal, btn_processador_xml, btn_validador_tiss, btn_atualizar_hash]))
        btn_processador_xml.clicked.connect(lambda: self.mudar_pagina(1, [btn_painel_principal, btn_processador_xml, btn_validador_tiss, btn_atualizar_hash]))
        btn_validador_tiss.clicked.connect(lambda: self.mudar_pagina(2, [btn_painel_principal, btn_processador_xml, btn_validador_tiss, btn_atualizar_hash]))
        btn_atualizar_hash.clicked.connect(lambda: self.mudar_pagina(3, [btn_painel_principal, btn_processador_xml, btn_validador_tiss, btn_atualizar_hash]))

    def mudar_pagina(self, index, botoes):
        self.pages_widget.setCurrentIndex(index)
        for i, btn in enumerate(botoes):
            btn.setChecked(i == index)
