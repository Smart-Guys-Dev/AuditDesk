# src/gui/worker.py

from PyQt6.QtCore import QObject, pyqtSignal
import traceback

class Worker(QObject):
    """
    Worker genérico que executa uma função em uma thread separada.
    """
    finished = pyqtSignal(object)  # Sinal emitido quando a tarefa termina, com o resultado
    error = pyqtSignal(str)        # Sinal emitido em caso de erro
    progress = pyqtSignal(str)     # Sinal para enviar mensagens de log durante a execução

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Executa a função de trabalho.
        """
        try:
            # Passamos a nossa função de log como um argumento para a função de trabalho
            # Isso permite que a lógica do controller envie mensagens para a GUI
            kwargs_com_log = self.kwargs.copy()
            kwargs_com_log['log_callback'] = self.progress.emit
            
            resultado = self.fn(*self.args, **kwargs_com_log)
            self.finished.emit(resultado)
        except Exception:
            # Em caso de erro, captura o traceback e o emite como uma string
            error_str = traceback.format_exc()
            self.error.emit(error_str)