import sys
import os

def resource_path(relative_path):
    """ 
    Obtém o caminho absoluto para recursos.
    Funciona tanto para desenvolvimento (caminho local) 
    quanto para quando empacotado com PyInstaller (pasta temporária _MEIPASS).
    """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
