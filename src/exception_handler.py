import sys
import traceback
import logging
from PyQt6.QtWidgets import QMessageBox, QApplication
from src.database import db_manager

def install_exception_handler():
    """Instala o hook global de exceções."""
    sys.excepthook = global_exception_handler

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Trata exceções não capturadas globalmente.
    1. Loga no arquivo de log padrão.
    2. Loga no banco de dados como 'CRASHED'.
    3. Exibe mensagem amigável ao usuário.
    """
    # Ignora KeyboardInterrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"Exceção não tratada capturada:\n{error_msg}")

    # Tenta logar no banco de dados
    try:
        # Cria uma execução especial para o crash ou anexa a uma existente se tivéssemos contexto global
        # Por simplificação, criamos um registro de crash isolado
        exec_id = db_manager.log_execution_start("APP_CRASH", 0)
        db_manager.log_execution_end(exec_id, "CRASHED", 0, 1)
        
        # Poderíamos criar uma tabela específica para erros de sistema no futuro,
        # mas por enquanto vamos usar o log de arquivo processado como "SYSTEM_ERROR"
        db_manager.log_file_processed(exec_id, "SYSTEM", "CRASH_REPORT", "CRITICAL", error_msg[:500]) # Limita tamanho
    except Exception as db_error:
        logging.error(f"Falha ao logar crash no banco de dados: {db_error}")

    # Salvar traceback em arquivo local para debug
    try:
        with open("last_crash.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
    except:
        pass

    # Exibe mensagem na GUI se houver uma aplicação ativa
    app = QApplication.instance()
    if app:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Erro Inesperado")
        msg_box.setText("Ocorreu um erro inesperado e o aplicativo precisa ser verificado.")
        msg_box.setInformativeText("O erro foi registrado automaticamente para análise técnica.\n\n"
                                   f"Detalhe: {str(exc_value)}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
