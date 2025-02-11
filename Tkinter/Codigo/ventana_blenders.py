#
# B-renderon is a render manager for Blender 3d.
# Copyright (C) 2024  Tomas Fenoglio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the h ope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

from PyQt5.QtGui import QPalette, QKeySequence
from PyQt5.QtWidgets import QLineEdit, QMenu, QAction, QInputDialog

import alertas
import iconos_app
import util_ui
import ui.ui_ventana_blenders
import configuracion_general
import blenders
from ui.widgets_universales import PathExplorable
from utils import set_cursor_espera, restore_cursor
from traducciones import traducir

params = blenders.ParamsBlender


class VentanaBlenders(QtWidgets.QDialog, ui.ui_ventana_blenders.Ui_ventana_blenders):
    fileDropped = pyqtSignal(str)
    tagSelected = pyqtSignal(str)

    def __init__(self, ventana):
        super().__init__(ventana)
        self.setupUi(self)
        try:
            elegido = ventana.tablaPrincipal.selectedItems()[0]
            tag_inicial = elegido.tag_blender
        except (AttributeError, KeyError) as e:
            print("Exception", e)  # debug print
            tag_inicial = ""

        self.configurar_arbol()
        self.leer_blenders(tag_inicial)
        self.btn_agregar.setIcon(iconos_app.icono_agregar_blender)
        self.btn_agregar.clicked.connect(self.agregar_blender)

        atajos_delete = ['Delete', 'Backspace', 'X']
        for atajo in atajos_delete:
            atajo = QtWidgets.QShortcut(QKeySequence(atajo), self)
            atajo.activated.connect(self.quitar_elegido)

        self.fileDropped.connect(self.check_ruta_version)

        self.btn_aceptar_cancelar.accepted.connect(self.aceptar)
        self.btn_aceptar_cancelar.rejected.connect(self.close)

        self.adjustSize()
        self.retraducir()

    def mostrar_contextual(self, position: QPoint):
        item = self.arbol.itemAt(position)
        if item:
            menu = QMenu(self)
            delete_action = QAction(traducir("Borrar"), self)
            delete_action.setShortcut(QKeySequence('Delete'))
            menu.addAction(delete_action)
            delete_action.triggered.connect(
                self.quitar_elegido)  # aquí podría conectar con item.quitar pero se complica el adjustsize así
            menu.exec_(self.arbol.viewport().mapToGlobal(position))

    def quitar_elegido(self):
        elegidos = self.arbol.selectedItems()
        if not elegidos:
            return
        elegido = self.arbol.selectedItems()[0]
        elegido.quitar()
        self.adjustSize()

    def leer_blenders(self, tag_inicial):
        lista_blenders = blenders.versiones_blender.blenders
        item_default = None
        for tag, data in lista_blenders.items():
            version = data[params.VERSION]
            ruta = data[params.RUTA]
            item_nuevo = ItemBlender(self.arbol, nombre=tag, version=version, ruta=ruta)
            if tag == blenders.tag_default:
                item_default = item_nuevo
            if tag == tag_inicial:
                item_nuevo.setSelected(True)
        if tag_inicial not in lista_blenders:
            item_default.setSelected(True)

    def configurar_arbol(self):
        self.arbol.setContextMenuPolicy(Qt.CustomContextMenu)
        self.arbol.customContextMenuRequested.connect(self.mostrar_contextual)
        self.arbol.setAcceptDrops(True)
        self.arbol.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.arbol.setTransparente()
        self.arbol.fileDropped.connect(self.check_ruta_version)
        self.setAcceptDrops(True)

        header = self.arbol.header()
        color = self.palette().color(QPalette.Window).name()
        header.setStyleSheet(f"""
    QHeaderView::section {{
        background-color: {color};
        }}
        """)
        for i, nombre in enumerate(params):
            self.arbol.headerItem().setText(i, traducir(nombre))
        # item_btn_agregar = QtWidgets.QTreeWidgetItem(self.arbol)
        # item_btn_agregar.setFirstColumnSpanned(True)
        # self.arbol.setItemWidget(item_btn_agregar, 0, self.btn_agregar)

    def agregar_blender(self):
        ruta_nueva, version = self.explorar_ubi_blender()
        if ruta_nueva:
            self.pedir_tag_y_agregar(ruta_nueva, version)

    def check_ruta_version(self, ruta):
        es_valido, version = blenders.validar_ruta_y_obtener_version(ruta, cursor_espera=True)
        if not es_valido:
            return
        self.pedir_tag_y_agregar(ruta=ruta, version=version)

    def pedir_tag_y_agregar(self, ruta, version):
        carpeta = os.path.basename(os.path.dirname(ruta))
        filename = os.path.basename(ruta)
        nombre_pelado = os.path.splitext(filename)[0]
        if nombre_pelado != "blender":
            sugerencia = nombre_pelado
        else:
            sugerencia = carpeta

        ruta_resumida = os.path.join('..', carpeta, filename)
        texto = "\n".join([ruta_resumida, f"Version: {version}", traducir("ingresar_tag_blender")])
        while True:
            tag, ok = QInputDialog.getText(self, traducir("Blender tag"), texto, text=sugerencia)
            if not ok:  # User pressed cancel
                return
            if tag:  # User entered valid input
                break

        if ok and tag:
            ItemBlender(self.arbol, nombre=tag, version=version, ruta=ruta)
            self.adjustSize()

    def explorar_ubi_blender(self, ruta_base=""):
        ruta_nueva = blenders.explorar(self, ruta_base, validar=False)
        if not ruta_nueva:
            return None, None
        es_valida, version = blenders.validar_ruta_y_obtener_version(ruta_nueva, cursor_espera=True)
        if not es_valida:
            blenders.alerta_ubicacion_erronea()
            return None, None
        return ruta_nueva, version

    def aceptar(self):
        elegidos = self.arbol.selectedItems()
        if not elegidos:
            return
        elegido = elegidos[0]
        tag_elegido = elegido.tag
        if tag_elegido == blenders.versiones_blender.tag_eevee:
            alertas.alerta_generica("alerta_tag_eevee")
            return
        lista_blenders = {}
        for item in self.arbol.items():
            lista_blenders[item.tag] = {params.RUTA: item.ruta, params.VERSION: item.version}

        blenders.versiones_blender.blenders = lista_blenders
        blenders.versiones_blender.guardar()
        self.tagSelected.emit(tag_elegido)
        self.close()

    def retraducir(self):
        self.setWindowTitle(traducir("Versión de Blender"))
        self.btn_agregar.setToolTip(traducir("tooltip_add_blender"))

    def dragEnterEvent(self, event):
        # Check if the dragged data is a file URL
        if event.mimeData().hasUrls():
            event.accept()  # Accept the event to allow the drop
        else:
            event.ignore()  # Ignore the event if it's not a file URL

    def dragMoveEvent(self, event):
        # This is necessary to update the cursor and allow movement within the widget
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # Accept the event
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            local_file_path = url.toLocalFile()
            if local_file_path:  # Check if it's a valid path
                self.fileDropped.emit(local_file_path)
        event.accept()  # Accept the drop event


class ItemBlender(QtWidgets.QTreeWidgetItem):
    columnas = {nombre: index for index, nombre in enumerate(params)}

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        tag = kwargs.get(blenders.ParamsBlender.NOMBRE, "")
        editable = tag != blenders.tag_default
        self.version = kwargs.get(params.VERSION, "")
        ruta = kwargs.get(params.RUTA, "")
        self.widget_ruta = PathExplorable(parent, ruta)
        self.widget_ruta.campo_path.editingFinished.connect(self.verificar)
        self.widget_ruta.path_encontrado.connect(self.cambio_path)
        self.campo_tag = QLineEdit(tag)
        if not editable:
            self.campo_tag.setEnabled(False)
        self.campo_tag.setAlignment(Qt.AlignCenter)
        self.campo_tag.setContentsMargins(4, 4, 4, 4)
        self.treeWidget().setItemWidget(self, self.columnas[params.NOMBRE], self.campo_tag)
        self.treeWidget().setItemWidget(self, self.columnas[params.RUTA], self.widget_ruta)
        self.setup_columnas()

    @property
    def ruta(self):
        return self.widget_ruta.path

    @property
    def tag(self):
        return self.campo_tag.text()

    def quitar(self):
        parent = self.treeWidget()
        if parent:
            index = parent.indexOfTopLevelItem(self)
            if index != -1:
                parent.takeTopLevelItem(index)

    def verificar(self):
        self.cambio_path(self.ruta)

    def cambio_path(self, path_nuevo):
        set_cursor_espera()
        es_valido, version = blenders.validar_ruta_y_obtener_version(path_nuevo)
        restore_cursor()
        if not es_valido:
            blenders.alerta_ubicacion_erronea()
            self.widget_ruta.explorar()
            return
        self.version = version

    def setup_columnas(self):
        for col in self.columnas.values():
            self.setTextAlignment(col, Qt.AlignmentFlag.AlignCenter)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == params.VERSION:
            self.setText(self.columnas[name], value)
        if name == params.RUTA:
            self.widget_ruta.path = value


configuracion = configuracion_general.configuracion
