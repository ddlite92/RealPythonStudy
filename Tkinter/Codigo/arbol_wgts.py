from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5 import QtCore, QtWidgets


class ArbolWgts(QTreeWidget):

    def __init__(self, parent):
        super().__init__(parent)


    def cochis(self):
        print("totora")

    def crear_item_basico(self, tipo, texto=None, texto_aux=None, parent=None):
        match tipo:
            case "linea":
                wgt = QLineEdit()
                wgt.setAlignment(QtCore.Qt.AlignCenter)
            case "chk":
                wgt = QtWidgets.QCheckBox()
            case "radio":
                wgt = QtWidgets.QRadioButton()
            case "boton":
                wgt = QtWidgets.QPushButton()
            case "titulo":
                wgt = None
            case _:
                return None
        if texto_aux:
            wgt.setText(texto_aux)
        return self.aux_creacion_item(texto, wgt_opcion=wgt, parent=parent), wgt

    def aux_creacion_item(self, texto=None, wgt_opcion=None, layout=None, parent=None,  columna=0):
        parent = parent if parent else self
        item = QTreeWidgetItem(parent)
        if texto:
            wgtaux = QWidget()
            layaux = QHBoxLayout(wgtaux)
            txt = QLabel(texto)
            layaux.addWidget(txt)
            self.setItemWidget(item, columna, wgtaux)
            # uso esto en vez de set text directo para que sean parejas las alturas de los items por más que sean solo textoo
            # item.setText(0, texto)
            columna += 1
        if wgt_opcion or layout:
            self.aux_agregar_widget(wgt_opcion, item, columna, layout)
        item.setExpanded(True)
        return item

    def aux_agregar_widget(self, wgt_opcion, item, columna, layout=None):
        wgt_contenedor_opcion = QtWidgets.QWidget()
        if not layout:
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(wgt_opcion)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.addItem(QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        wgt_contenedor_opcion.setLayout(layout)
        self.setItemWidget(item, columna, wgt_contenedor_opcion)