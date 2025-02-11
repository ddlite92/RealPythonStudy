from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItemIterator
from PyQt5.QtCore import Qt, QSize, pyqtSignal


class ArbolWgts(QTreeWidget):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.clicked.connect(self.click_expande)
        self.setAttribute(Qt.WA_TranslucentBackground)


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


    # def mousePressEvent(self, event):
    #     # Get the item under the mouse
    #     item = self.itemAt(event.pos())
    #     if item and item.flags() & Qt.ItemIsSelectable:  # Check if it's selectable
    #         super().mousePressEvent(event)  # Allow selection change
    #     else:
    #         event.ignore()  # Ignore the event, preventing selection change


    def setTransparente(self):
        self.setStyleSheet("QTreeWidget { background-color: lightgray; border: 0px solid black; } ")
#         self.setStyleSheet("""
#     QTreeWidget {
#         background-color: lightgray;
#         border: 0px solid black;
#     }
#     QHeaderView::section {
#         background-color: transparent;
#     }
# """)

    def click_expande(self, index):
        item = self.itemFromIndex(index)
        if item is not None:
            item.setExpanded(not item.isExpanded())

    def items(self):
        iterador = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.NoChildren)
        while iterador.value():
            yield iterador.value()
            iterador += 1

    def items_y_children(self):
        iterador = QTreeWidgetItemIterator(self)
        while iterador.value():
            yield iterador.value()
            iterador += 1

    def desactivar_seleccion(self):
        for item in self.items_y_children():
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

