from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QShortcut
from PyQt5.QtWidgets import QPushButton, QMenu
from PyQt5.QtCore import pyqtSignal


class ComboBoxSimple(QPushButton):
    cambio = pyqtSignal(bool)

    def __init__(self, parent=None, items=None):
        super().__init__(parent)

        # padding = "padding-left: 10px;"
        # self.setStyleSheet(padding)
        self.menu = QMenu(self)
        self.traduccion = None
        self.setMenu(self.menu)

        self._current_data = None

        # self.menu.setMaximumWidth(int(self.width()*.8))
        if items:
            self.agregar_items(items)

    def clear(self):
        self.menu.clear()

    def addItem(self, text, data):
        self.agregar_item(text, data)

    def agregar_items(self, lista_items):
        if not lista_items:
            return
        for item in lista_items:
            if isinstance(item, str):
                data = item
                nombre = item
            elif isinstance(item, tuple) and len(item) == 2:
                data = item[1]
                nombre = item[0]
            else:
                continue

            action = self.agregar_item(nombre, data)
        action.trigger()

    def agregar_item(self, nombre, data_item=None):
        action = QAction(nombre, self)
        if data_item:
            action.setData(data_item)
        action.triggered.connect(lambda _, act=action: self.set_item_by_action(act))
        self.menu.addAction(action)
        return action

    def set_item_by_data(self, data):
        for action in self.menu.actions():
            if action.data == data:
                self.set_item_by_action(action)
                break

    def set_item_by_action(self, action):
        self.setText(action.text())
        self._current_data = action.data()
        self.cambio.emit(True)

    def set_item(self, texto, data):
        self._current_data = data
        self.setText(texto)

    def set_data(self, data):
        self._current_data = data
        if data == "" and self.traduccion:
            nombre = self.traduccion.traducir("None")
        else:
            nombre = data
        self.setText(nombre)

    def setCurrentText(self, text):
        for item in self.menu.actions():
            if item.text() == text:
                self.set_item_by_action(item)
                break

    def currentData(self):
        return self._current_data

    def current_data(self):
        return self._current_data

class ComboBoxAlternativa(QPushButton):

    def __init__(self, parent):
        super().__init__(parent)

        self.accion_eligio = None
        self.elegido = None
        self.menu = QMenu(self)
        self.setMenu(self.menu)
        self.triggereo = None


    def filtro_nombre_visible(self, nombre):
        return nombre # je je estas cosas que hago me hago cagar de la risa

    def actualizar(self, lista_nombres):
        self.menu.clear()
        for item_i in lista_nombres:
            act_i = QAction(self)
            act_i.setText(self.filtro_nombre_visible(item_i))
            act_i.triggered.connect(self.eligio_opcion)
            act_i.triggered.connect(self.accion_eligio)
            act_i.setObjectName(item_i)
            self.menu.addAction(act_i)

    def eligio_opcion(self):
        self.triggereo = self.sender()

class ComboBoxModos(ComboBoxAlternativa):
    def __init__(self, parent):
        super().__init__(parent)
        self.modos = None

    def mostrar_actual(self):
        actual = self.modos.actual
        self.setText(self.modos.traducir(actual))
        self.setObjectName(actual)

    def actualizar(self, modos):
        super().actualizar(modos.lista_modos)
        self.set_shortcuts(modos)

    def set_shortcuts(self, modos):
        for accion in self.menu.actions():
            nombre = accion.objectName()
            atajo = modos.modo[nombre].atajo
            if not atajo:
                return
            shortcut = QShortcut(QKeySequence(atajo), self)
            shortcut.activated.connect(self.eligio_opcion)
            shortcut.activated.connect(self.accion_eligio)
            accion.setShortcut(atajo)


