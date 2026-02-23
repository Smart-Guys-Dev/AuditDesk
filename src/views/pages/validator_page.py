"""
Página do Validador PTU XML
Valida regras de negócio, estrutura XSD e internações curtas.
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QThread

from src.infrastructure.workers.worker import Worker
from src.ui_helpers import show_friendly_error, show_toast, show_warning
from src.app_settings import app_settings
from src.drag_drop_widgets import DragDropLineEdit


class PaginaValidador(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Validador PTU XML")
        titulo.setObjectName("titulo_pagina")
        layout.addWidget(titulo)

        # Seleção de pasta
        selecao_layout = QHBoxLayout()
        selecao_layout.setSpacing(8)

        label_pasta = QLabel("Pasta dos XMLs:")
        label_pasta.setMinimumWidth(120)

        self.caminho_pasta_edit = DragDropLineEdit(accept_folders=True, accept_files=False)
        self.caminho_pasta_edit.setReadOnly(True)
        self.caminho_pasta_edit.setPlaceholderText("Selecione a pasta ou arraste aqui...")
        self.caminho_pasta_edit.setToolTip("Pasta contendo os arquivos .051 para validação")
        self.caminho_pasta_edit.folder_dropped.connect(self._on_folder_dropped)

        btn_procurar = QPushButton("Procurar...")
        btn_procurar.setToolTip("Selecionar pasta com arquivos XML")
        btn_procurar.setMinimumWidth(120)

        selecao_layout.addWidget(label_pasta)
        selecao_layout.addWidget(self.caminho_pasta_edit, 1)
        selecao_layout.addWidget(btn_procurar)

        # Botões de validação
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(8)

        self.btn_iniciar_validacao = QPushButton("Validar Regras (Lógica)")
        self.btn_iniciar_validacao.setToolTip("Valida regras de negócio nos arquivos XML")
        self.btn_iniciar_validacao.setMinimumHeight(44)

        self.btn_validar_xsd = QPushButton("Validar Estrutura (XSD)")
        self.btn_validar_xsd.setToolTip("Valida estrutura XML contra schema XSD")
        self.btn_validar_xsd.setMinimumHeight(44)

        self.btn_verificar_internacao = QPushButton("Verificar Internações Curtas")
        self.btn_verificar_internacao.setToolTip("Verifica internações com curta permanência")
        self.btn_verificar_internacao.setMinimumHeight(44)

        botoes_layout.addWidget(self.btn_iniciar_validacao)
        botoes_layout.addWidget(self.btn_validar_xsd)
        botoes_layout.addWidget(self.btn_verificar_internacao)

        # Log
        log_label = QLabel("Log da Validação:")
        log_label.setObjectName("section_title")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Os resultados da validação aparecerão aqui...")

        layout.addLayout(selecao_layout)
        layout.addLayout(botoes_layout)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)

        # Conexões
        btn_procurar.clicked.connect(self.selecionar_pasta)
        self.btn_iniciar_validacao.clicked.connect(self.iniciar_validacao)
        self.btn_validar_xsd.clicked.connect(self.iniciar_validacao_xsd)
        self.btn_verificar_internacao.clicked.connect(self.iniciar_verificacao_internacao_curta)

    def selecionar_pasta(self):
        pasta_sugerida = os.path.join(self.controller.pasta_faturas_importadas_atual or "", "Correção XML")
        last_folder = app_settings.get_last_folder("validador_xmls", pasta_sugerida)
        caminho_pasta = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta com XMLs para Validar", last_folder
        )
        if caminho_pasta:
            self.caminho_pasta_edit.setText(caminho_pasta)
            self.log_area.append(f"✓ INFO: Pasta para validação selecionada: {caminho_pasta}")
            app_settings.save_last_folder("validador_xmls", caminho_pasta)

    def _on_folder_dropped(self, folder_path):
        self.log_area.append(f"✓ INFO: Pasta selecionada via drag & drop: {folder_path}")
        app_settings.save_last_folder("validador_xmls", folder_path)

    def iniciar_validacao(self):
        caminho_pasta = self.caminho_pasta_edit.text()
        if not caminho_pasta:
            show_warning(self, "Pasta não selecionada",
                        "Por favor, selecione uma pasta contendo os arquivos XML para validar.")
            return

        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando validação de regras (lógica)...")
        self._disable_buttons()

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
            show_warning(self, "Pasta não selecionada",
                        "Por favor, selecione uma pasta contendo os arquivos XML para validar.")
            return

        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando validação de estrutura (XSD)...")
        self._disable_buttons()

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
            show_warning(self, "Pasta não selecionada",
                        "Por favor, selecione uma pasta contendo os arquivos XML para verificar.")
            return

        self.log_area.clear()
        self.log_area.append("⏳ INFO: Iniciando verificação de internações curtas...")
        self._disable_buttons()

        self.worker_thread = QThread()
        self.worker = Worker(self.controller.executar_verificacao_internacao_curta, caminho_pasta)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

    def _disable_buttons(self):
        self.btn_iniciar_validacao.setEnabled(False)
        self.btn_validar_xsd.setEnabled(False)
        self.btn_verificar_internacao.setEnabled(False)

    def _enable_buttons(self):
        self.btn_iniciar_validacao.setEnabled(True)
        self.btn_validar_xsd.setEnabled(True)
        self.btn_verificar_internacao.setEnabled(True)

    def on_task_finished(self, result):
        sucesso, mensagem = result
        icon = "✓" if sucesso else "✗"
        self.log_area.append(f"{icon} {mensagem}")

        if sucesso:
            show_toast(self, mensagem, "success", 3000)
        else:
            show_toast(self, "Validação concluída com erros", "warning", 3000)

        self._enable_buttons()
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_task_error(self, error_str):
        self.log_area.append(f"✗ ERRO CRÍTICO: {error_str}")
        show_friendly_error(
            self,
            "Erro na Validação",
            "Ocorreu um erro ao processar os arquivos XML.\n\n"
            "Verifique se os arquivos estão corretos e tente novamente.",
            error_str
        )
        self._enable_buttons()
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
