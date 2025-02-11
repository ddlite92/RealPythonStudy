from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView


class HeaderTablas(QHeaderView):
    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(True)
        self.sectionResized.connect(self.updateHeaderAlignment)
        self.setSectionsClickable(True)


    def update_forzoso(self):
        for i in range(self.parent().columnCount()):
            self.updateHeaderAlignment(i)

    def updateHeaderAlignment(self, logicalIndex):
        header = self.parent().header()
        width = header.sectionSize(logicalIndex)
        title = header.model().headerData(logicalIndex, Qt.Orientation.Horizontal, Qt.DisplayRole)
        header_item = self.parent().headerItem()

        if header.fontMetrics().width(title) > width:
            header_item.setTextAlignment(logicalIndex, Qt.AlignLeft | Qt.AlignVCenter)
        else:
            header_item.setTextAlignment(logicalIndex, Qt.AlignHCenter | Qt.AlignVCenter)


