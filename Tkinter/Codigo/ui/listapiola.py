from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidget, QApplication, QTreeWidgetItemIterator, QTreeWidgetItem
from util_ui import ItemDelegate


class ListaPiola(QTreeWidget):
    dobleclick_item = QtCore.pyqtSignal()
    dobleclick_espacio = QtCore.pyqtSignal()

    click_release = QtCore.pyqtSignal()
    drop_interno = QtCore.pyqtSignal()
    drop_interno_post_acomodo = QtCore.pyqtSignal()
    items_comidos = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.ventana_principal = None
        self.setAcceptDrops(True)
        self.seleccion_programatica = False
        self.itemDoubleClicked.connect(self.doble_click_item)
        # self.itemClicked.connect(self.clickeo)

    def doble_click_item(self, item: QTreeWidgetItem, columna):
        item.doble_click(columna)

    def clickeo(self, item):
        if not QApplication.keyboardModifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
            self.clearSelection()
            item.setSelected(True)

    def set_altura_filas(self, altura):
        self.setItemDelegate(ItemDelegate(height=altura))

    def recuperar_scrollbar(self):
        self.verticalScrollBar().setStyleSheet("")
        self.viewport().updateGeometry()

    def ocultar_scrollbar(self):
        self.verticalScrollBar().setStyleSheet("QScrollBar {width:0px;}")

    def selectionCommand(self, index, event):
        self.seleccion_programatica = False
        return super().selectionCommand(index, event)

    # def hay_menores(self):
    #     for item in self.selectedItems():
    #         indice = self.indexOfTopLevelItem(item)
    #         if indice <= self.ventana_principal.cola.siguiente_item_render():
    #             return True
    #     return False

    # def destino_prohibido(self, evento, limite):
    #     indice_destino = self.indexAt(evento.pos()).row()
    #     arriba_o_abajo = self.dropIndicatorPosition()
    #     if indice_destino >= 0 and arriba_o_abajo == 2:  # abajo. La comprobación (indice_destino >0 es necesaria por macana)
    #         indice_destino += 1
    #     if indice_destino is not None and 0 <= indice_destino <= limite:
    #         return True
    #     else:
    #         return False
    #
    # def verifica_y_draguea(self, evento, tipo_evento):
    #     evento.accept()
    #     tipo_evento(self, evento)
    #

    def borrar_item(self, index):
        item = self.topLevelItem(index)
        if item:
            item.consola.borrar_archivo_livelog()
            super().takeTopLevelItem(index)

    def items(self):
        iterador = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.NoChildren)
        while iterador.value():
            yield iterador.value()
            iterador += 1

    def dragMoveEvent(self, evento):
        evento.accept()
        # self.verifica_y_draguea(evento, QTreeWidget.dragMoveEvent)

    def dragEnterEvent(self, evento):
        # self.verifica_y_draguea(evento, QTreeWidget.dragEnterEvent)
        evento.accept()

    def dropEvent(self, evento):
        modificadoras = QApplication.keyboardModifiers()
        numero_items = self.topLevelItemCount()

        # print("evento.", evento.mimeData().formats()) # debug print
        # if evento.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
        #     print("drop de coso",) # debug print
        #     print("mimedata", evento.mimeData().data("text/plain")) # debug print

        if evento.source():
            self.drop_interno.emit()

            items_elegidos = self.selectedItems()  # .copy()
            current_item = self.currentItem()
            QTreeWidget.dropEvent(self, evento)
            self.setCurrentItem(current_item)
            for item in items_elegidos:
                item.setSelected(True)

            self.drop_interno_post_acomodo.emit()

            if self.topLevelItemCount() < numero_items:
                print("Error dropping")
                self.items_comidos.emit()
            return

        archivos_a_agregar = []
        db = QtCore.QMimeDatabase()
        # print(evento.mimeData().formats())

        for url in evento.mimeData().urls():
            archivo_i = url.toLocalFile()
            if db.mimeTypeForFile(archivo_i).inherits("text/plain"):
                # if self.ventana_principal.cola.estado == "renderizando":
                self.ventana_principal.lectura_de_cola(archivo_i, switchear=True)
            else:
                archivos_a_agregar.append(archivo_i)
        if archivos_a_agregar:
            if modificadoras == QtCore.Qt.ControlModifier:
                con_escenas = "elegir"
            elif modificadoras == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                con_escenas = "todas"
            else:
                con_escenas = None
            self.ventana_principal.agregar_archivos(archivos_a_agregar, con_escenas)

    def mouseReleaseEvent(self, evento):
        self.click_release.emit()
        QTreeWidget.mouseReleaseEvent(self, evento)
        # self.ventana_principal.cambio_seleccion()

    # def mousePressEvent(self, evento):
    #     QTreeWidget.mousePressEvent(self, evento)

    def mouseDoubleClickEvent(self, evento):
        if self.itemAt(evento.pos()) is None:
            self.dobleclick_espacio.emit()
        else:
            self.dobleclick_item.emit()
        QTreeWidget.mouseDoubleClickEvent(self, evento)  # no recuerdo si sería nesario esto ahora
