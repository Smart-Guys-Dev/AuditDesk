from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
from src.database import db_manager, models

class PaginaHistorico(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Histórico de Execuções")
        titulo.setObjectName("page_title")
        layout.addWidget(titulo)

        # Botão de Atualizar
        btn_refresh = QPushButton("Atualizar Lista")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh, alignment=Qt.AlignmentFlag.AlignRight)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Operação", "Status", "Sucesso", "Erros"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Carregar dados iniciais
        self.load_data()

    def load_data(self):
        """Carrega os dados do banco de dados para a tabela."""
        session = db_manager.get_session()
        try:
            logs = session.query(models.ExecutionLog).order_by(models.ExecutionLog.start_time.desc()).all()
            
            self.table.setRowCount(len(logs))
            
            for row, log in enumerate(logs):
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(log.id)))
                
                # Data
                data_fmt = log.start_time.strftime("%d/%m/%Y %H:%M")
                self.table.setItem(row, 1, QTableWidgetItem(data_fmt))
                
                # Operação
                self.table.setItem(row, 2, QTableWidgetItem(log.operation_type))
                
                # Status
                item_status = QTableWidgetItem(log.status)
                if log.status == "COMPLETED":
                    item_status.setForeground(Qt.GlobalColor.green)
                elif "ERROR" in log.status:
                    item_status.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 3, item_status)
                
                # Sucesso
                self.table.setItem(row, 4, QTableWidgetItem(str(log.success_count)))
                
                # Erros
                item_erro = QTableWidgetItem(str(log.error_count))
                if log.error_count > 0:
                    item_erro.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 5, item_erro)
                
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
        finally:
            session.close()
