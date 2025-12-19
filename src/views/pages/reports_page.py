from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from src.database import db_manager
import csv

class PaginaRelatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        titulo = QLabel("Relatórios Gerenciais")
        titulo.setObjectName("titulo_pagina")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E3440;")
        layout.addWidget(titulo)
        
        subtitulo = QLabel("Produtividade da Equipe")
        subtitulo.setStyleSheet("font-size: 16px; color: #4C566A; margin-bottom: 10px;")
        layout.addWidget(subtitulo)

        # Botões de Ação
        action_layout = QHBoxLayout()
        
        btn_refresh = QPushButton("🔄 Atualizar Dados")
        btn_refresh.clicked.connect(self.load_data)
        action_layout.addWidget(btn_refresh)
        
        action_layout.addStretch()
        
        btn_export = QPushButton("💾 Exportar CSV")
        btn_export.setStyleSheet("background-color: #A3BE8C; color: white; font-weight: bold;")
        btn_export.clicked.connect(self.export_csv)
        action_layout.addWidget(btn_export)
        
        layout.addLayout(action_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Usuário", "Nome Completo", "Execuções", 
            "Arquivos Processados", "Taxa de Sucesso", "Última Atividade"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Carregar dados iniciais
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        data = db_manager.get_productivity_report()
        
        for row, item in enumerate(data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item['usuario']))
            self.table.setItem(row, 1, QTableWidgetItem(item['nome_completo']))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['total_execucoes'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['total_arquivos'])))
            self.table.setItem(row, 4, QTableWidgetItem(item['taxa_sucesso']))
            self.table.setItem(row, 5, QTableWidgetItem(item['ultima_atividade']))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Relatório", "relatorio_produtividade.csv", "CSV Files (*.csv)"
        )
        
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Cabeçalho
                    headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                    writer.writerow(headers)
                    
                    # Dados
                    for row in range(self.table.rowCount()):
                        row_data = []
                        for col in range(self.table.columnCount()):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                        
                QMessageBox.information(self, "Sucesso", "Relatório exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {e}")
