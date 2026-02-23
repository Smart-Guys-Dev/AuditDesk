"""
Página do Processador de Faturas
Importa, distribui e prepara arquivos XML para correção.
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QProgressBar,
                             QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt, QThread

from src.infrastructure.workers.worker import Worker
from src.ui_helpers import show_friendly_error, show_toast, show_warning
from src.app_settings import app_settings
from src.drag_drop_widgets import DragDropLineEdit


class PaginaProcessador(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Processador de Faturas")
        titulo.setObjectName("titulo_pagina")
        layout.addWidget(titulo)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Seleção de pasta
        selecao_layout = QHBoxLayout()
        selecao_layout.setSpacing(8)

        label_pasta = QLabel("Pasta das Faturas:")
        label_pasta.setMinimumWidth(120)

        self.caminho_pasta_edit = DragDropLineEdit(accept_folders=True, accept_files=False)
        self.caminho_pasta_edit.setReadOnly(True)
        self.caminho_pasta_edit.setPlaceholderText("Selecione a pasta ou arraste aqui...")
        self.caminho_pasta_edit.setToolTip("Pasta contendo os arquivos ZIP das faturas")
        self.caminho_pasta_edit.folder_dropped.connect(self._on_folder_dropped)

        btn_procurar = QPushButton("Procurar...")
        btn_procurar.setToolTip("Selecionar pasta com arquivos ZIP")
        btn_procurar.setMinimumWidth(120)

        selecao_layout.addWidget(label_pasta)
        selecao_layout.addWidget(self.caminho_pasta_edit, 1)
        selecao_layout.addWidget(btn_procurar)

        # Botões de ação
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)

        self.btn_iniciar_importacao = QPushButton("1. Importar Faturas")
        self.btn_iniciar_importacao.setToolTip("Importa e processa arquivos ZIP")
        self.btn_iniciar_importacao.setMinimumHeight(44)

        self.btn_iniciar_distribuicao = QPushButton("2. Distribuir Faturas")
        self.btn_iniciar_distribuicao.setToolTip("Distribui faturas entre auditores")
        self.btn_iniciar_distribuicao.setMinimumHeight(44)

        self.btn_preparar_correcao = QPushButton("3. Preparar Correção XML")
        self.btn_preparar_correcao.setToolTip("Prepara arquivos XML para correção")
        self.btn_preparar_correcao.setMinimumHeight(44)

        botoes_layout.addWidget(self.btn_iniciar_importacao)
        botoes_layout.addWidget(self.btn_iniciar_distribuicao)
        botoes_layout.addWidget(self.btn_preparar_correcao)

        self.btn_iniciar_distribuicao.setEnabled(False)
        self.btn_preparar_correcao.setEnabled(False)

        # Log
        log_label = QLabel("Log de Execução:")
        log_label.setObjectName("section_title")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("As mensagens de execução aparecerão aqui...")

        layout.addLayout(selecao_layout)
        layout.addLayout(botoes_layout)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)

        # Conexões
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
        last_folder = app_settings.get_last_folder("processador_faturas", "")
        caminho_pasta = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta com Faturas ZIP", last_folder
        )
        if caminho_pasta:
            self.caminho_pasta_edit.setText(caminho_pasta)
            self.log_message(f"✓ INFO: Pasta selecionada: {caminho_pasta}")
            app_settings.save_last_folder("processador_faturas", caminho_pasta)

    def _on_folder_dropped(self, folder_path):
        self.log_message(f"✓ INFO: Pasta selecionada via drag & drop: {folder_path}")
        app_settings.save_last_folder("processador_faturas", folder_path)

    def iniciar_importacao(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            show_warning(self, "Pasta não selecionada",
                        "Por favor, selecione a pasta contendo os arquivos ZIP das faturas.")
            return

        self.log_area.clear()
        self.log_message("⏳ INFO: Iniciando importação...")
        self.progress_bar.setRange(0, 0)
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
            show_warning(self, "Distribuição necessária",
                        "É necessário fazer a distribuição de faturas antes de preparar para correção.")
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
            self.log_message(f"{icon} {'SUCESSO' if sucesso else 'ERRO'}: {mensagem}")

            if sucesso:
                show_toast(self, "Processamento concluído com sucesso!", "success", 3000)
            else:
                show_toast(self, "Processamento concluído com erros", "warning", 3000)
        else:
            self.log_message("✓ SUCESSO: Tarefa concluída.")
            show_toast(self, "Tarefa concluída!", "success", 3000)

        self.set_ui_enabled(True)
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_task_error(self, error_str):
        self.log_message(f"✗ ERRO CRÍTICO: {error_str}")
        show_friendly_error(
            self,
            "Erro no Processamento",
            "Ocorreu um erro ao processar as faturas.\n\n"
            "Verifique se os arquivos ZIP estão corretos e tente novamente.",
            error_str
        )
        self.set_ui_enabled(True)
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
