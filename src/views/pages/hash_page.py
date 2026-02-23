"""
Página de Atualização de Hash
Seleciona auditor e arquivos para recalcular hashes e recriar ZIPs.
"""
import os
import glob
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QInputDialog,
                             QMessageBox, QCheckBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QThread

from src.infrastructure.workers.worker import Worker
from src.ui_helpers import show_friendly_error, show_toast, show_warning


class PaginaHash(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.worker_thread = None
        self.worker = None
        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
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
        auditor_layout.addWidget(auditor_label)
        auditor_layout.addStretch()

        # Área de seleção de arquivos
        files_label = QLabel("Arquivos Disponíveis:")
        files_label.setObjectName("section_title")

        # Container com scroll para checkboxes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(250)

        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setSpacing(4)
        self.files_layout.setContentsMargins(8, 8, 8, 8)
        self.files_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.files_container)

        # Botões de seleção
        selection_buttons_layout = QHBoxLayout()

        self.btn_select_all = QPushButton("Selecionar Todos")
        self.btn_select_all.setToolTip("Selecionar todos os arquivos")
        self.btn_select_all.clicked.connect(self.select_all_files)

        self.btn_clear_all = QPushButton("Limpar Seleção")
        self.btn_clear_all.setToolTip("Desmarcar todos os arquivos")
        self.btn_clear_all.clicked.connect(self.clear_all_files)

        selection_buttons_layout.addWidget(self.btn_select_all)
        selection_buttons_layout.addWidget(self.btn_clear_all)
        selection_buttons_layout.addStretch()

        # Contador
        self.selection_counter = QLabel("0 arquivos selecionados")
        self.selection_counter.setObjectName("quick_stats")
        self.selection_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botão principal
        self.btn_atualizar_hash = QPushButton("Atualizar Hash dos Selecionados")
        self.btn_atualizar_hash.setObjectName("btn_primary")
        self.btn_atualizar_hash.setMinimumHeight(44)
        self.btn_atualizar_hash.setToolTip("Atualiza hash apenas dos arquivos selecionados")
        self.btn_atualizar_hash.clicked.connect(self.iniciar_atualizacao_hash)

        # Log
        log_label = QLabel("Log da Atualização de Hash:")
        log_label.setObjectName("section_title")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("O progresso da atualização aparecerá aqui...")

        # Montar layout
        layout.addLayout(auditor_layout)
        layout.addWidget(files_label)
        layout.addWidget(self.scroll_area)
        layout.addLayout(selection_buttons_layout)
        layout.addWidget(self.selection_counter)
        layout.addWidget(self.btn_atualizar_hash)
        layout.addWidget(log_label)
        layout.addWidget(self.log_area, 1)

    def select_all_files(self):
        for cb in self.checkboxes:
            cb.setChecked(True)
        self.update_counter()

    def clear_all_files(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.update_counter()

    def update_counter(self):
        selected = sum(1 for cb in self.checkboxes if cb.isChecked())
        total = len(self.checkboxes)
        self.selection_counter.setText(f"{selected} de {total} arquivos selecionados")

    def load_files_for_auditor(self, nome_auditor):
        # Limpar checkboxes anteriores
        for cb in self.checkboxes:
            cb.deleteLater()
        self.checkboxes.clear()

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

        arquivos_xml = glob.glob(os.path.join(pasta_auditor, "*.051"))

        if not arquivos_xml:
            self.log_area.append(f"⚠ AVISO: Nenhum arquivo XML (.051) encontrado para {nome_auditor}")
            return

        for arquivo_path in sorted(arquivos_xml):
            arquivo_nome = os.path.basename(arquivo_path)
            cb = QCheckBox(arquivo_nome)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_counter)
            self.checkboxes.append(cb)
            self.files_layout.addWidget(cb)

        self.update_counter()
        self.log_area.append(f"✓ INFO: {len(arquivos_xml)} arquivos encontrados para {nome_auditor}")

    def get_selected_files(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def iniciar_atualizacao_hash(self):
        if not self.controller.plano_ultima_distribuicao:
            show_warning(self, "Distribuição necessária",
                        "É necessário fazer a distribuição de faturas antes de atualizar o hash.")
            return

        auditores = list(self.controller.plano_ultima_distribuicao.keys())
        nome_auditor, ok = QInputDialog.getItem(
            self, "Selecionar Auditor",
            "Para qual auditor deseja atualizar o hash?",
            auditores, 0, False
        )

        if not ok or not nome_auditor:
            return

        self.load_files_for_auditor(nome_auditor)

        reply = QMessageBox.question(
            self,
            "Confirmar Seleção",
            f"Deseja atualizar hash dos arquivos selecionados?\n\n{self.selection_counter.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        arquivos_selecionados = self.get_selected_files()

        if not arquivos_selecionados:
            show_warning(self, "Seleção vazia",
                        "Por favor, selecione pelo menos um arquivo para atualizar o hash.")
            return

        self.log_area.clear()
        self.log_area.append(f"⏳ INFO: Iniciando atualização de HASH para: {nome_auditor}")
        self.log_area.append(f"📁 INFO: {len(arquivos_selecionados)} arquivo(s) selecionado(s)")

        self.btn_atualizar_hash.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_clear_all.setEnabled(False)

        self.worker_thread = QThread()
        self.worker = Worker(
            self.controller.executar_atualizacao_hash,
            nome_auditor,
            arquivos_selecionados
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.on_task_error)
        self.worker.progress.connect(self.log_area.append)
        self.worker_thread.start()

    def on_task_finished(self, result):
        if result and isinstance(result, tuple):
            sucesso, mensagem = result
            icon = "✓" if sucesso else "✗"
            self.log_area.append(f"{icon} {mensagem}")

            if sucesso:
                show_toast(self, "Hash atualizado com sucesso!", "success", 3000)
            else:
                show_toast(self, "Atualização concluída com erros", "warning", 3000)

        self.btn_atualizar_hash.setEnabled(True)
        self.btn_select_all.setEnabled(True)
        self.btn_clear_all.setEnabled(True)

        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def on_task_error(self, error_str):
        self.log_area.append(f"✗ ERRO CRÍTICO: {error_str}")
        show_friendly_error(
            self,
            "Erro na Atualização de Hash",
            "Ocorreu um erro ao atualizar o hash dos arquivos.\n\n"
            "Verifique se os arquivos XML estão acessíveis e tente novamente.",
            error_str
        )
        self.btn_atualizar_hash.setEnabled(True)
        self.btn_select_all.setEnabled(True)
        self.btn_clear_all.setEnabled(True)

        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
