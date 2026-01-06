"""
Glox - Página de Consulta de Faturas

Permite buscar faturas por número e visualizar status/histórico.
Também permite importar dados de planilhas Excel.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QScrollArea, QFileDialog, QMessageBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import os


# Cores Unimed
UNIMED_GREEN = "#00A859"
UNIMED_DARK = "#1A1F2E"
STATUS_COLORS = {
    'ENVIADA': '#00C16E',
    'PENDENTE': '#FFB300',
    'CANCELADA': '#FF5252',
    'GLOSADA': '#9C27B0'
}


class ImportWorker(QThread):
    """Worker para importação em background"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
    
    def run(self):
        try:
            from src.infrastructure.parsers.excel_parser import parse_arquivo
            from src.database.fatura_repository import importar_lote
            
            self.progress.emit("Lendo arquivo Excel...")
            faturas = parse_arquivo(self.filepath)
            
            self.progress.emit(f"Importando {len(faturas)} faturas...")
            origem = os.path.basename(self.filepath)
            stats = importar_lote(faturas, origem)
            
            self.finished.emit(stats)
        except Exception as e:
            self.finished.emit({'erro': str(e)})


class PaginaConsultaFaturas(QWidget):
    """
    Tela de consulta e importação de faturas.
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("🔍 Consulta de Faturas")
        titulo.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(titulo)
        
        # Barra de busca
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.input_fatura = QLineEdit()
        self.input_fatura.setPlaceholderText("Digite o número da fatura...")
        self.input_fatura.setStyleSheet(f"""
            QLineEdit {{
                padding: 15px 20px;
                font-size: 16px;
                border: 2px solid #3B4252;
                border-radius: 10px;
                background: #2E3440;
                color: white;
            }}
            QLineEdit:focus {{
                border-color: {UNIMED_GREEN};
            }}
        """)
        self.input_fatura.returnPressed.connect(self.buscar_fatura)
        search_layout.addWidget(self.input_fatura, 1)
        
        btn_buscar = QPushButton("🔎 Buscar")
        btn_buscar.setStyleSheet(f"""
            QPushButton {{
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                background: {UNIMED_GREEN};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: #00C16E;
            }}
        """)
        btn_buscar.clicked.connect(self.buscar_fatura)
        search_layout.addWidget(btn_buscar)
        
        layout.addLayout(search_layout)
        
        # Área de resultado
        self.resultado_frame = QFrame()
        self.resultado_frame.setStyleSheet("""
            QFrame {
                background: #2E3440;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        self.resultado_frame.setMinimumHeight(350)
        
        resultado_layout = QVBoxLayout(self.resultado_frame)
        resultado_layout.setSpacing(15)
        
        # Placeholder inicial
        self.resultado_placeholder = QLabel("Digite um número de fatura para buscar")
        self.resultado_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resultado_placeholder.setStyleSheet("color: #4C566A; font-size: 16px;")
        resultado_layout.addWidget(self.resultado_placeholder)
        
        # Labels para dados da fatura (inicialmente ocultos)
        self.lbl_numero = QLabel()
        self.lbl_numero.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        self.lbl_numero.hide()
        resultado_layout.addWidget(self.lbl_numero)
        
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.lbl_status.hide()
        resultado_layout.addWidget(self.lbl_status)
        
        # Grid de informações
        self.info_frame = QFrame()
        self.info_frame.hide()
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(8)
        
        self.lbl_unimed = QLabel()
        self.lbl_unimed.setStyleSheet("color: #D8DEE9; font-size: 14px;")
        info_layout.addWidget(self.lbl_unimed)
        
        self.lbl_valor = QLabel()
        self.lbl_valor.setStyleSheet("color: #A3BE8C; font-size: 16px; font-weight: bold;")
        info_layout.addWidget(self.lbl_valor)
        
        self.lbl_competencia = QLabel()
        self.lbl_competencia.setStyleSheet("color: #D8DEE9; font-size: 14px;")
        info_layout.addWidget(self.lbl_competencia)
        
        self.lbl_responsavel = QLabel()
        self.lbl_responsavel.setStyleSheet("color: #D8DEE9; font-size: 14px;")
        info_layout.addWidget(self.lbl_responsavel)
        
        self.lbl_envio = QLabel()
        self.lbl_envio.setStyleSheet("color: #D8DEE9; font-size: 14px;")
        info_layout.addWidget(self.lbl_envio)
        
        self.lbl_Glox = QLabel()
        self.lbl_Glox.setStyleSheet("color: #88C0D0; font-size: 14px;")
        info_layout.addWidget(self.lbl_Glox)
        
        resultado_layout.addWidget(self.info_frame)
        
        # Histórico
        self.historico_label = QLabel("📋 Histórico:")
        self.historico_label.setStyleSheet("color: #ECEFF4; font-size: 16px; font-weight: bold; margin-top: 15px;")
        self.historico_label.hide()
        resultado_layout.addWidget(self.historico_label)
        
        self.historico_area = QScrollArea()
        self.historico_area.setWidgetResizable(True)
        self.historico_area.setMaximumHeight(150)
        self.historico_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QWidget { background: transparent; }
        """)
        self.historico_area.hide()
        
        self.historico_widget = QWidget()
        self.historico_layout = QVBoxLayout(self.historico_widget)
        self.historico_layout.setSpacing(5)
        self.historico_area.setWidget(self.historico_widget)
        resultado_layout.addWidget(self.historico_area)
        
        resultado_layout.addStretch()
        layout.addWidget(self.resultado_frame)
        
        # Barra de ações
        action_layout = QHBoxLayout()
        
        btn_importar = QPushButton("📥 Importar Planilha")
        btn_importar.setStyleSheet("""
            QPushButton {
                padding: 12px 25px;
                font-size: 14px;
                background: #5E81AC;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background: #81A1C1; }
        """)
        btn_importar.clicked.connect(self.importar_planilha)
        action_layout.addWidget(btn_importar)
        
        btn_estatisticas = QPushButton("📊 Estatísticas")
        btn_estatisticas.setStyleSheet("""
            QPushButton {
                padding: 12px 25px;
                font-size: 14px;
                background: #4C566A;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background: #5E6779; }
        """)
        btn_estatisticas.clicked.connect(self.mostrar_estatisticas)
        action_layout.addWidget(btn_estatisticas)
        
        action_layout.addStretch()
        
        # Status da importação
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #88C0D0; font-size: 12px;")
        action_layout.addWidget(self.status_label)
        
        layout.addLayout(action_layout)
    
    def buscar_fatura(self):
        """Busca fatura pelo número digitado"""
        numero = self.input_fatura.text().strip()
        if not numero:
            return
        
        from src.database.fatura_repository import buscar_fatura
        resultado = buscar_fatura(numero)
        
        if resultado:
            self.exibir_resultado(resultado)
        else:
            self.exibir_nao_encontrado(numero)
    
    def exibir_resultado(self, dados):
        """Exibe os dados da fatura encontrada"""
        self.resultado_placeholder.hide()
        
        # Número
        self.lbl_numero.setText(f"📄 FATURA: {dados['nro_fatura']}")
        self.lbl_numero.show()
        
        # Status com cor
        status = dados['status']
        emoji = dados.get('status_emoji', '❓')
        cor = STATUS_COLORS.get(status, '#FFFFFF')
        self.lbl_status.setText(f"{emoji} {status}")
        self.lbl_status.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {cor};")
        self.lbl_status.show()
        
        # Info frame
        self.info_frame.show()
        self.lbl_unimed.setText(f"🏥 Unimed: {dados.get('unimed', 'N/A')}")
        self.lbl_valor.setText(f"💰 Valor: R$ {dados.get('valor', 0):,.2f}")
        self.lbl_competencia.setText(f"📅 Competência: {dados.get('competencia', 'N/A')}")
        self.lbl_responsavel.setText(f"👤 Responsável: {dados.get('responsavel', 'N/A')}")
        self.lbl_envio.setText(f"📤 Data Envio: {dados.get('data_envio') or 'Não enviada'}")
        
        if dados.get('corrigida_Glox'):
            self.lbl_Glox.setText("✅ Corrigida pelo Glox")
        else:
            self.lbl_Glox.setText("")
        
        # Histórico
        historico = dados.get('historico', [])
        if historico:
            self.historico_label.show()
            self.historico_area.show()
            
            # Limpar histórico anterior
            for i in reversed(range(self.historico_layout.count())):
                self.historico_layout.itemAt(i).widget().deleteLater()
            
            for h in historico:
                lbl = QLabel(f"• {h['data_hora']} - {h['acao']}")
                lbl.setStyleSheet("color: #D8DEE9; font-size: 12px;")
                self.historico_layout.addWidget(lbl)
        else:
            self.historico_label.hide()
            self.historico_area.hide()
    
    def exibir_nao_encontrado(self, numero):
        """Exibe mensagem de fatura não encontrada"""
        self.resultado_placeholder.setText(f"❌ Fatura '{numero}' não encontrada\n\nImporte uma planilha para adicionar dados.")
        self.resultado_placeholder.setStyleSheet("color: #BF616A; font-size: 16px;")
        self.resultado_placeholder.show()
        
        self.lbl_numero.hide()
        self.lbl_status.hide()
        self.info_frame.hide()
        self.historico_label.hide()
        self.historico_area.hide()
    
    def importar_planilha(self):
        """Abre diálogo para importar planilha Excel"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Planilha",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if filepath:
            self.status_label.setText("⏳ Importando...")
            
            self.worker = ImportWorker(filepath)
            self.worker.progress.connect(lambda msg: self.status_label.setText(msg))
            self.worker.finished.connect(self.importacao_concluida)
            self.worker.start()
    
    def importacao_concluida(self, stats):
        """Callback quando importação termina"""
        if 'erro' in stats:
            self.status_label.setText(f"❌ Erro: {stats['erro']}")
            QMessageBox.critical(self, "Erro", f"Falha na importação:\n{stats['erro']}")
        else:
            msg = f"✅ {stats['criadas']} criadas, {stats['atualizadas']} atualizadas"
            self.status_label.setText(msg)
            QMessageBox.information(
                self, 
                "Importação Concluída",
                f"Faturas criadas: {stats['criadas']}\n"
                f"Faturas atualizadas: {stats['atualizadas']}\n"
                f"Erros: {stats.get('erros', 0)}"
            )
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas das faturas importadas"""
        from src.database.fatura_repository import get_estatisticas_faturas
        stats = get_estatisticas_faturas()
        
        msg = f"""📊 ESTATÍSTICAS DE FATURAS

Total importadas: {stats['total']:,}

Por Status:
  ✅ Enviadas: {stats['por_status'].get('ENVIADA', 0):,}
  ⏳ Pendentes: {stats['por_status'].get('PENDENTE', 0):,}
  ❌ Canceladas: {stats['por_status'].get('CANCELADA', 0):,}
  ⚠️ Glosadas: {stats['por_status'].get('GLOSADA', 0):,}

Valor Total: R$ {stats['valor_total']:,.2f}

Corrigidas pelo Glox: {stats['corrigidas_Glox']:,}
Taxa de Correção: {stats['taxa_correcao']:.1f}%
"""
        QMessageBox.information(self, "Estatísticas", msg)
