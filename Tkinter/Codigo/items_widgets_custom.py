#
# B-renderon is a render manager for Blender 3d.
# Copyright (C) 2024  Tomas Fenoglio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# -*- coding: utf-8 -*-

from Pyqt5 import QtWidgets, QtCore.Qt





class ItemWidgetBasico(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = [None, None]
        self.wgt_aux = None

    def crear_wgt(self, widget, columna, spacerL=False, spacerR=False, debug=False):
        self.wgt_aux = QtWidgets.QWidget()
        self.layout[columna] = QtWidgets.QHBoxLayout()
        params_spacer = (5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        if spacerL:
            self.layout[columna].addItem(QtWidgets.QSpacerItem(*params_spacer))
        # self.layout.setContentsMargins(5, 4, 5, 4)
        self.layout[columna].addWidget(widget)
        if spacerR:
            self.layout[columna].addItem(QtWidgets.QSpacerItem(*params_spacer))
        self.wgt_aux.setLayout(self.layout[columna])

        if not self.parent:
            return
        self.aplicar_wgt(columna)

    def agregar_layout_wgt(self, layout, columna, spacerL=False, spacerR=False):
        self.wgt_aux = QtWidgets.QWidget()
        self.layout[columna] = layout
        spacer = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        if spacerL:
            self.layout[columna].addItem(spacer)
        # self.layout.setContentsMargins(5, 4, 5, 4)
        if spacerR:
            self.layout[columna].addItem(spacer)
        self.wgt_aux.setLayout(self.layout[columna])

        if not self.parent:
            return
        self.aplicar_wgt(columna)

    def aplicar_wgt(self, columna):
        self.treeWidget().setItemWidget(self, columna, self.wgt_aux)

    def agregar_wgt(self, columna, widget, spacerL=False, spacerR=False):
        # self.wgt_extras[widget.objectName()] = widget

        if self.layout[columna]:
            spacer = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            if spacerL:
                self.layout[columna].addItem(spacer)
            self.layout[columna].addWidget(widget)
            if spacerR:
                self.layout[columna].addItem(spacer)
            return
        self.crear_wgt(widget, columna, spacerL, spacerR)


class ItemSelector(ItemWidgetBasico):
    def __init__(self, lista_opciones, lista_datas=None, titulo="", spacerR=False, parent=None):
        super().__init__(parent)

        self.selector = QtWidgets.QComboBox()
        if not lista_datas:
            self.selector.addItems(lista_opciones)
        else:
            for nombre_ui, nombre_original in zip(lista_opciones, lista_datas):
                self.selector.addItem(nombre_ui, nombre_original)

        if titulo:
            self.lbl_titulo = QtWidgets.QLabel(titulo)
            self.crear_wgt(self.lbl_titulo, 0)
        else:
            self.lbl_titulo = None

        self.crear_wgt(self.selector, 1, spacerR=spacerR)

    def text(self):
        return self.selector.currentText()

    def elegido(self):
        return self.selector.currentData()

    def setDisabled(self, disabled):
        self.selector.setDisabled(disabled)
        if self.lbl_titulo:
            self.lbl_titulo.setDisabled(disabled)
        super().setDisabled(disabled)

    def set_actual(self, nombre):
        self.selector.setCurrentText(nombre)


class ItemLinea(ItemWidgetBasico):
    def __init__(self, titulo="", texto_base="", texto_boton="", parent=None):
        super().__init__(parent)

        self.linea = QtWidgets.QLineEdit(texto_base)
        self.linea.setAlignment(Qt.AlignCenter)

        if titulo:
            self.lbl_titulo = QLabel(titulo)
            self.crear_wgt(self.lbl_titulo, 0)
        else:
            self.lbl_titulo = None

        self.crear_wgt(self.linea, 1, spacerR=texto_boton == "")
        if texto_boton:
            self.boton = QtWidgets.QPushButton(texto_boton)
            self.agregar_wgt(1, self.boton, spacerR=True)

    def text(self):
        return self.linea.text()

    def setText(self, texto):
        self.linea.setText(texto)

    def setDisabled(self, disabled):
        self.linea.setDisabled(disabled)
        if self.lbl_titulo:
            self.lbl_titulo.setDisabled(disabled)
        super().setDisabled(disabled)


class ItemBoton(ItemWidgetBasico):
    def __init__(self, texto, columna=0, spacerL=False, spacerR=False, parent=None):
        super().__init__(parent)
        self.btn = QtWidgets.QPushButton(texto)
        self.crear_wgt(self.btn, columna, spacerL, spacerR, debug=True)


class ItemTitulo(ItemWidgetBasico):
    def __init__(self, texto, columna=0, parent=None, centrado=False):
        super().__init__(parent)
        self.texto = QLabel(texto)
        self.crear_wgt(self.texto, columna)
        if centrado:
            self.texto.setAlignment(Qt.AlignCenter)


class ItemChk(ItemWidgetBasico):
    def __init__(self, texto="", columna=0, parent=None, handle_toggle=True):
        super().__init__(parent)
        self.chk = QtWidgets.QCheckBox(texto)
        self.crear_wgt(self.chk, columna)
        if handle_toggle:
            self.chk.toggled.connect(self.handle_chk_toggle)

    def handle_chk_toggle(self, check):
        self.setExpanded(check)
        try:
            if not self.parent.isChecked():
                return
        except (NameError, AttributeError):
            pass
        if check:
            self.chk.setEnabled(True)

    def setChecked(self, check):
        self.chk.setChecked(check)

    def isChecked(self):
        return self.chk.isChecked()


class ItemRadio(ItemWidgetBasico):
    def __init__(self, texto="", columna=0, parent=None):
        super().__init__(parent)
        self.opcion = QtWidgets.QRadioButton(texto)
        self.crear_wgt(self.opcion, columna)
        self.opcion.toggled.connect(self.expansion_toggle)

    def expansion_toggle(self, check):
        self.setExpanded(check)

    def setChecked(self, check):
        self.opcion.setChecked(check)
