"""
AuditPlus v2.0 - Página de Importação de Relatórios

Permite ao auditor importar os 3 tipos de relatórios Excel
para as pastas padrão do sistema.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import shutil
from datetime import datetime


# Cores
UNIMED_GREEN = "#00A859"
CARD_BG = "#2E3440"


# Configuração das pastas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
RELATORIOS_DIR = os.path.join(BASE_DIR, 'data', 'relatorios')

TIPOS_RELATORIO = {
    'A500': {
        'nome': 'A500 Enviados',
        'pasta': 'A500_Enviados',
        'icone': '📤',
        'cor': '#00C16E'
    },
    'DISTRIBUICAO': {
        'nome': 'Distribuição de Faturas',
        'pasta': 'Distribuicao_Faturas',
        'icone': '📊',
        'cor': '#5E81AC'
    },
    'EMITIDAS': {
        'nome': 'Faturas Emitidas',
        'pasta': 'Faturas_Emitidas',
        'icone': '📋',
        'cor': '#B48EAD'
    }
}


class ProcessWorker(QThread):
    """Worker para processar todos os arquivos"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def run(self):
        stats = {'total': 0, 'criadas': 0, 'atualizadas': 0, 'erros': 0}
        
        try:
            from src.infrastructure.parsers.excel_parser import parse_arquivo
            from src.database.fatura_repository import importar_lote
            
            for tipo_key, tipo_info in TIPOS_RELATORIO.items():
                pasta = os.path.join(RELATORIOS_DIR, tipo_info['pasta'])
                if not os.path.exists(pasta):
                    continue
                
                for arquivo in os.listdir(pasta):
                    if arquivo.endswith('.xlsx'):
                        filepath = os.path.join(pasta, arquivo)
                        self.progress.emit(f"Processando: {arquivo}")
                        
                        try:
                            faturas = parse_arquivo(filepath)
                            if faturas:
                                result = importar_lote(faturas, arquivo)
                                stats['criadas'] += result.get('criadas', 0)
                                stats['atualizadas'] += result.get('atualizadas', 0)
                                stats['total'] += len(faturas)
                        except Exception as e:
                            stats['erros'] += 1
                            print(f"Erro ao processar {arquivo}: {e}")
            
            self.finished.emit(stats)
            
        except Exception as e:
            stats['erros'] += 1
            self.finished.emit(stats)


class CardImportacao(QFrame):
    """Card para cada tipo de relatório"""
    
    def __init__(self, tipo_key: str, tipo_info: dict):
        super().__init__()
        self.tipo_key = tipo_key
        self.tipo_info = tipo_info
        self.setup_ui()
        self.atualizar_info()
    
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG};
                border-radius: 12px;
                border: 1px solid #3B4252;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Ícone
        icone = QLabel(self.tipo_info['icone'])
        icone.setStyleSheet(f"""
            font-size: 32px;
            background: {self.tipo_info['cor']};
            padding: 10px;
            border-radius: 10px;
        """)
        layout.addWidget(icone)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.lbl_titulo = QLabel(self.tipo_info['nome'])
        self.lbl_titulo.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(self.lbl_titulo)
        
        self.lbl_ultimo = QLabel("Nenhum arquivo")
        self.lbl_ultimo.setStyleSheet("color: #8B949E; font-size: 12px;")
        info_layout.addWidget(self.lbl_ultimo)
        
        layout.addLayout(info_layout, 1)
        
        # Botão
        btn_selecionar = QPushButton("📂 Selecionar")
        btn_selecionar.setStyleSheet(f"""
            QPushButton {{
                background: {self.tipo_info['cor']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        btn_selecionar.clicked.connect(self.selecionar_arquivo)
        layout.addWidget(btn_selecionar)
    
    def get_pasta_destino(self):
        return os.path.join(RELATORIOS_DIR, self.tipo_info['pasta'])
    
    def atualizar_info(self):
        """Atualiza info do último arquivo na pasta"""
        pasta = self.get_pasta_destino()
        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
            return
        
        arquivos = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
        if arquivos:
            # Pegar o mais recente
            arquivos_com_data = []
            for arq in arquivos:
                caminho = os.path.join(pasta, arq)
                mtime = os.path.getmtime(caminho)
                arquivos_com_data.append((arq, mtime))
            
            arquivos_com_data.sort(key=lambda x: x[1], reverse=True)
            ultimo = arquivos_com_data[0]
            
            data_mod = datetime.fromtimestamp(ultimo[1]).strftime("%d/%m/%Y %H:%M")
            self.lbl_ultimo.setText(f"📁 {ultimo[0]} ({data_mod})")
            self.lbl_ultimo.setStyleSheet("color: #A3BE8C; font-size: 12px;")
        else:
            self.lbl_ultimo.setText("Nenhum arquivo")
            self.lbl_ultimo.setStyleSheet("color: #8B949E; font-size: 12px;")
    
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            f"Selecionar {self.tipo_info['nome']}",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if filepath:
            try:
                pasta_destino = self.get_pasta_destino()
                os.makedirs(pasta_destino, exist_ok=True)
                
                nome_arquivo = os.path.basename(filepath)
                destino = os.path.join(pasta_destino, nome_arquivo)
                
                shutil.copy2(filepath, destino)
                
                self.atualizar_info()
                QMessageBox.information(
                    self, 
                    "Sucesso", 
                    f"Arquivo importado para:\n{pasta_destino}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao copiar arquivo:\n{e}")


class PaginaImportarRelatorios(QWidget):
    """Página principal de importação de relatórios"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("📥 Importar Relatórios")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(titulo)
        
        subtitulo = QLabel("Importe os relatórios Excel para alimentar o Dashboard")
        subtitulo.setStyleSheet("color: #8B949E; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(subtitulo)
        
        # Cards de importação
        self.cards = {}
        for tipo_key, tipo_info in TIPOS_RELATORIO.items():
            card = CardImportacao(tipo_key, tipo_info)
            self.cards[tipo_key] = card
            layout.addWidget(card)
        
        layout.addSpacing(20)
        
        # Barra de ações
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background: #3B4252;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        action_layout = QHBoxLayout(action_frame)
        
        self.status_label = QLabel("Pronto para processar")
        self.status_label.setStyleSheet("color: #D8DEE9; font-size: 13px;")
        action_layout.addWidget(self.status_label, 1)
        
        btn_processar = QPushButton("🔄 Processar Todos e Atualizar Dashboard")
        btn_processar.setStyleSheet(f"""
            QPushButton {{
                background: {UNIMED_GREEN};
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #00C16E;
            }}
        """)
        btn_processar.clicked.connect(self.processar_todos)
        action_layout.addWidget(btn_processar)
        
        layout.addWidget(action_frame)
        
        # Info da pasta
        info_pasta = QLabel(f"📁 Pasta de relatórios: {RELATORIOS_DIR}")
        info_pasta.setStyleSheet("color: #6E7681; font-size: 11px;")
        layout.addWidget(info_pasta)
        
        layout.addStretch()
    
    def processar_todos(self):
        """Processa todos os arquivos das pastas"""
        self.status_label.setText("⏳ Processando...")
        
        self.worker = ProcessWorker()
        self.worker.progress.connect(lambda msg: self.status_label.setText(msg))
        self.worker.finished.connect(self.processamento_concluido)
        self.worker.start()
    
    def processamento_concluido(self, stats):
        """Callback quando processamento termina"""
        msg = f"✅ {stats['total']} faturas | {stats['criadas']} novas | {stats['atualizadas']} atualizadas"
        self.status_label.setText(msg)
        
        # Atualizar cards
        for card in self.cards.values():
            card.atualizar_info()
        
        QMessageBox.information(
            self,
            "Processamento Concluído",
            f"Total de faturas: {stats['total']}\n"
            f"Novas: {stats['criadas']}\n"
            f"Atualizadas: {stats['atualizadas']}\n"
            f"Erros: {stats['erros']}\n\n"
            "O Dashboard será atualizado automaticamente!"
        )
