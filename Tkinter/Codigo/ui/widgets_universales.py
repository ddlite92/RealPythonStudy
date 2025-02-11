from enum import Enum

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QHBoxLayout

from traducciones import traducir
import iconos_app as iconos


class BotonBrowse(QtWidgets.QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def conectar(self, funcion):
        self.clicked.connect(funcion)

    def vestir(self):
        self.setIcon(iconos.icono_browse)
        text = traducir("Explorar")
        self.setText(text)
        self.setToolTip(text)

    def inicializar(self, funcion):
        self.conectar(funcion)
        self.vestir()


class TipoBrowse(Enum):
    PATH = 1
    FILE = 2


class PathExplorable(QtWidgets.QWidget):
    path_encontrado = pyqtSignal(str)

    def __init__(self, parent=None, path_inicial="", titulo=""):
        super().__init__(parent)
        self.campo_path = QLineEdit(self)
        self.btn_browse = BotonBrowse(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.campo_path)
        layout.addWidget(self.btn_browse)
        layout.setContentsMargins(4, 4, 4, 4)
        self.titulo = titulo
        self.ruta_base = path_inicial or ""
        self.path = path_inicial
        self.btn_browse.inicializar(self.explorar)

    @property
    def path(self):
        return self.campo_path.text()

    @path.setter
    def path(self, nuevo_path):
        self.campo_path.setText(nuevo_path)

    def explorar(self):
        ruta_base = self.path if self.path else self.ruta_base
        try:
            ruta_nueva, _ = QFileDialog.getOpenFileName(self, traducir(self.titulo), ruta_base)
        except Exception as e:
            print("Exception", e)
            ruta_nueva, _ = QFileDialog.getOpenFileName(self, traducir(self.titulo))

        if not ruta_nueva:
            self.explorar()
            return

        self.path = ruta_nueva
        self.path_encontrado.emit(ruta_nueva)
