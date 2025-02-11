from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeWidget, QApplication, QTreeWidgetItemIterator
from util_ui import ItemDelegate



class TablaEstados(QTreeWidget):
    dobleclick_item = QtCore.pyqtSignal()
    dobleclick_espacio = QtCore.pyqtSignal()
    click_release = QtCore.pyqtSignal()
    drop_interno = QtCore.pyqtSignal()
    items_comidos = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.seleccion_programatica = False
        self.ventana_principal = None
        self.setAcceptDrops(True)

    def set_altura_filas(self, altura):
        self.setItemDelegate(ItemDelegate(height=altura))


    def items(self):
        iterador = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.NoChildren)
        while iterador.value():
            yield iterador.value()
            iterador += 1



    def selectionCommand(self, index, event):
        self.seleccion_programatica = False
        return super().selectionCommand(index, event)

    # def selectionCommand(self, index, event):
    #     return QtCore.QItemSelectionModel.NoUpdate
    #     # Handle the selection events and return the desired selection behavior
    #     # By default, the selectionCommand method returns QItemSelectionModel.Select
    #
    #     # For example, let's disable the selection when the user clicks on an item:
    #     if event.type() == event.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
    #         return QtCore.QItemSelectionModel.NoUpdate
    #
    #     # If you want to retain the default selection behavior for other cases:
    #     return super().selectionCommand(index, event)

    # def dragMoveEvent(self, evento):
    #     evento.accept()
        # self.verifica_y_draguea(evento, QTreeWidget.dragMoveEvent)

    # def dragEnterEvent(self, evento):
    #     # self.verifica_y_draguea(evento, QTreeWidget.dragEnterEvent)
    #     evento.accept()

    def dropEvent(self, evento):
        modificadoras = QApplication.keyboardModifiers()
        numero_items = self.topLevelItemCount()

        if evento.source():
            self.drop_interno.emit()
            items_elegidos = self.selectedItems()  # .copy()
            current_item = self.currentItem()
            QTreeWidget.dropEvent(self, evento)
            self.setCurrentItem(current_item)
            for item in items_elegidos:
                item.setSelected(True)

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
            self.ventana_principal.agregar_archivos(archivos_a_agregar,
                                     modificadoras == QtCore.Qt.ControlModifier)

    # def mouseReleaseEvent(self, evento):
    #     # self.click_release.emit()
    #     QTreeWidget.mouseReleaseEvent(self, evento)
    #     # self.ventana_principal.cambio_seleccion()

    # def mousePressEvent(self, evento):
    #     QTreeWidget.mousePressEvent(self, evento)


    def mouseDoubleClickEvent(self, evento):
        if self.itemAt(evento.pos()) is None:
            self.dobleclick_espacio.emit()
        else:
            self.dobleclick_item.emit()
        QTreeWidget.mouseDoubleClickEvent(self, evento)  # no recuerdo si sería nesario esto ahora

