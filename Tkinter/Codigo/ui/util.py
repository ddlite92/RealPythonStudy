from PyQt5.QtWidgets import QStyledItemDelegate


class ItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, height=-1):
        super().__init__(parent)
        self.height = height

    def setHeight(self, height):
        self.height = height

    # Override sizeHint to set the tree item height.
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)

        if self.height != -1:
            # Set tree item height.
            size.setHeight(self.height)

        return size