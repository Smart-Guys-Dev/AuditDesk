from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, 
                             QDialog, QFormLayout, QComboBox, QCheckBox, QHeaderView,
                             QFrame, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from src.database import db_manager
from src.database.db_manager import get_session
from src.database.models import User

class UserManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestão de Usuários")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Header ---
        header_layout = QHBoxLayout()
        
        lbl_title = QLabel("Usuários do Sistema")
        lbl_title.setStyleSheet("font-size: 28px; font-weight: 800; color: #ECEFF4;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        btn_add = QPushButton("+ Novo Usuário")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C; 
                color: #2E3440; 
                font-weight: bold; 
                padding: 10px 20px; 
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #B5D3A0; }
            QPushButton:pressed { background-color: #8FBCBB; }
        """)
        btn_add.clicked.connect(self.open_add_user_dialog)
        header_layout.addWidget(btn_add)
        
        layout.addLayout(header_layout)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Usuário", "Nome Completo", "Perfil", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        
        # Estilo da Tabela
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #434C5E;
                border-radius: 8px;
                gridline-color: #434C5E;
                selection-background-color: #4C566A;
                selection-color: #88C0D0;
                font-size: 14px;
                outline: 0;
            }
            QHeaderView::section {
                background-color: #2E3440;
                color: #D8DEE9;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #434C5E;
                font-weight: bold;
                font-size: 13px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #434C5E;
            }
            QTableWidget::item:selected {
                background-color: #4C566A;
                color: #88C0D0;
            }
        """)
        
        self.table.doubleClicked.connect(self.open_edit_user_dialog)
        layout.addWidget(self.table)

        # --- Botões de Ação Inferior ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        btn_refresh = QPushButton("Atualizar Lista")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #5E81AC; }
        """)
        btn_refresh.clicked.connect(self.load_users)
        action_layout.addWidget(btn_refresh)
        
        action_layout.addStretch()
        
        btn_edit = QPushButton("Editar Selecionado")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #81A1C1; }
        """)
        btn_edit.clicked.connect(self.open_edit_user_dialog)
        action_layout.addWidget(btn_edit)
        
        btn_delete = QPushButton("Excluir Selecionado")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: #ECEFF4;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #D08770; }
        """)
        btn_delete.clicked.connect(self.delete_selected_user)
        action_layout.addWidget(btn_delete)
        
        layout.addLayout(action_layout)

    def load_users(self):
        self.table.setRowCount(0)
        users = db_manager.get_all_users()
        for row, user in enumerate(users):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(user.role))
            
            status_item = QTableWidgetItem("Ativo" if user.is_active else "Inativo")
            if user.is_active:
                status_item.setForeground(QColor("#A3BE8C")) # Verde
            else:
                status_item.setForeground(QColor("#BF616A")) # Vermelho
            self.table.setItem(row, 4, status_item)

    def get_selected_user_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def open_add_user_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec():
            self.load_users()

    def open_edit_user_dialog(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Atenção", "Selecione um usuário para editar.")
            return
            
        # Buscar dados completos do banco (incluindo email e birth_date)
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                QMessageBox.warning(self, "Erro", "Usuário não encontrado.")
                return
            
            dialog = UserDialog(
                self, user_id, user.username, user.full_name or "",
                user.role, user.is_active,
                email=user.email or "",
                birth_date=user.birth_date
            )
        finally:
            session.close()
        
        if dialog.exec():
            self.load_users()

    def delete_selected_user(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Atenção", "Selecione um usuário para excluir.")
            return
            
        username = self.table.item(self.table.currentRow(), 1).text()
        
        confirm = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário '{username}'?\nEssa ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = db_manager.delete_user(user_id)
            if success:
                QMessageBox.information(self, "Sucesso", msg)
                self.load_users()
            else:
                QMessageBox.critical(self, "Erro", msg)


class UserDialog(QDialog):
    def __init__(self, parent=None, user_id=None, username="", full_name="", role="AUDITOR", is_active=True, email="", birth_date=None):
        super().__init__(parent)
        self.user_id = user_id
        self.is_edit = user_id is not None
        self._email = email
        self._birth_date = birth_date
        
        self.setWindowTitle("Editar Usuário" if self.is_edit else "Novo Usuário")
        self.setFixedSize(450, 500)
        
        # Estilo do Dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
                color: #ECEFF4;
            }
            QLabel {
                color: #D8DEE9;
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit, QComboBox {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 4px;
                padding: 8px;
                color: #ECEFF4;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #88C0D0;
                background-color: #434C5E;
            }
            QCheckBox {
                color: #ECEFF4;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #4C566A;
                border-radius: 3px;
                background-color: #3B4252;
            }
            QCheckBox::indicator:checked {
                background-color: #88C0D0;
                border: 1px solid #88C0D0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Título
        lbl_header = QLabel("Dados do Usuário")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #88C0D0; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.txt_username = QLineEdit(username)
        self.txt_username.setEnabled(not self.is_edit)
        if not self.is_edit: self.txt_username.setPlaceholderText("Ex: joao.silva")
        form_layout.addRow("Usuário:", self.txt_username)
        
        self.txt_full_name = QLineEdit(full_name)
        self.txt_full_name.setPlaceholderText("Nome completo")
        form_layout.addRow("Nome:", self.txt_full_name)
        
        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["AUDITOR", "ADMIN"])
        self.cmb_role.setCurrentText(role)
        form_layout.addRow("Perfil:", self.cmb_role)
        
        self.txt_email = QLineEdit(self._email)
        self.txt_email.setPlaceholderText("nome@unimed.com.br")
        form_layout.addRow("E-mail:", self.txt_email)
        
        self.date_birth = QDateEdit()
        self.date_birth.setCalendarPopup(True)
        self.date_birth.setDisplayFormat("dd/MM/yyyy")
        if self._birth_date:
            self.date_birth.setDate(QDate(self._birth_date.year, self._birth_date.month, self._birth_date.day))
        else:
            self.date_birth.setDate(QDate(1990, 1, 1))
        self.date_birth.setStyleSheet(self.date_birth.styleSheet() + """
            QDateEdit {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 4px;
                padding: 8px;
                color: #ECEFF4;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 1px solid #88C0D0;
                background-color: #434C5E;
            }
        """)
        form_layout.addRow("Nascimento:", self.date_birth)
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Deixe vazio para manter a atual" if self.is_edit else "Obrigatório")
        form_layout.addRow("Senha:", self.txt_password)
        
        layout.addLayout(form_layout)
        
        self.chk_active = QCheckBox("Usuário Ativo")
        self.chk_active.setChecked(is_active)
        layout.addWidget(self.chk_active)
        
        layout.addStretch()
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3B4252; }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Salvar Usuário")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #81A1C1; }
        """)
        btn_save.clicked.connect(self.save_user)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def save_user(self):
        username = self.txt_username.text().strip()
        full_name = self.txt_full_name.text().strip()
        role = self.cmb_role.currentText()
        is_active = self.chk_active.isChecked()
        password = self.txt_password.text().strip()
        email = self.txt_email.text().strip() or None
        birth_date = self.date_birth.date().toPyDate()
        
        if not username:
            QMessageBox.warning(self, "Erro", "O campo Usuário é obrigatório.")
            return

        if self.is_edit:
            success, msg = db_manager.update_user(
                self.user_id, full_name, role, is_active,
                email=email, birth_date=birth_date
            )
            if success and password:
                db_manager.change_password(self.user_id, password)
        else:
            if not password:
                QMessageBox.warning(self, "Erro", "A senha é obrigatória para novos usuários.")
                return
            success, msg = db_manager.create_user(
                username, password, full_name, role,
                email=email, birth_date=birth_date
            )
            
        if success:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)
