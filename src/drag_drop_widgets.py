"""
Extensão de QLineEdit com drag & drop de arquivos/pastas.
"""
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import pyqtSignal
from pathlib import Path


class DragDropLineEdit(QLineEdit):
    """
    QLineEdit que aceita drag & drop de arquivos e pastas.
    
    Signals:
        folder_dropped: Emitido quando uma pasta é solta
        file_dropped: Emitido quando um arquivo é solto
    """
    
    folder_dropped = pyqtSignal(str)
    file_dropped = pyqtSignal(str)
    
    def __init__(self, accept_folders=True, accept_files=True, parent=None):
        super().__init__(parent)
        self.accept_folders = accept_folders
        self.accept_files = accept_files
        self.setAcceptDrops(True)
        
        # Visual feedback
        self.default_stylesheet = self.styleSheet()
        self.drag_stylesheet = """
            QLineEdit {
                border: 2px dashed #4299e1;
                background-color: rgba(66, 153, 225, 0.1);
            }
        """
    
    def dragEnterEvent(self, event):
        """Verifica se pode aceitar o drop"""
        if event.mimeData().hasUrls():
            # Verificar se tem pelo menos uma URL válida
            urls = event.mimeData().urls()
            for url in urls:
                path = Path(url.toLocalFile())
                
                if self.accept_folders and path.is_dir():
                    event.accept()
                    self.setStyleSheet(self.drag_stylesheet)
                    return
                elif self.accept_files and path.is_file():
                    event.accept()
                    self.setStyleSheet(self.drag_stylesheet)
                    return
            
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Remove visual feedback"""
        self.setStyleSheet(self.default_stylesheet)
    
    def dropEvent(self, event):
        """Processa o drop"""
        self.setStyleSheet(self.default_stylesheet)
        
        urls = event.mimeData().urls()
        if not urls:
            return
        
        # Pegar apenas o primeiro item
        path = Path(urls[0].toLocalFile())
        
        if path.is_dir() and self.accept_folders:
            self.setText(str(path))
            self.folder_dropped.emit(str(path))
            event.accept()
        elif path.is_file() and self.accept_files:
            self.setText(str(path))
            self.file_dropped.emit(str(path))
            event.accept()
        else:
            event.ignore()


class DragDropTextEdit(QLineEdit):
    """
    Área de texto que aceita múltiplos arquivos via drag & drop.
    
    Signals:
        files_dropped: Emitido com lista de caminhos quando arquivos são soltos
    """
    
    files_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.setPlaceholderText("Arraste arquivos/pastas aqui ou clique em Procurar...")
    
    def dragEnterEvent(self, event):
        """Aceita drag de URLs"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Processa múltiplos arquivos/pastas"""
        urls = event.mimeData().urls()
        paths = [Path(url.toLocalFile()) for url in urls]
        
        # Filtrar apenas existentes
        valid_paths = [str(p) for p in paths if p.exists()]
        
        if valid_paths:
            # Mostrar primeiro path no campo
            self.setText(valid_paths[0])
            self.files_dropped.emit(valid_paths)
            event.accept()
