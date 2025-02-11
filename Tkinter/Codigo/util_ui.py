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

from PyQt5.QtWidgets import QStyledItemDelegate, QSlider, QAction
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QFontDatabase, QPalette


class NoIconDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Remove the icon by setting it to None
        # option.icon = None

        # Get the font for the current item and set it to the option
        font = QFontDatabase().font(index.data(), "Normal", 12)
        option.font = font

        # Call the base class method to draw the item without the icon
        QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        # Get the font for the current item
        font = QFontDatabase().font(index.data(), "Normal", 12)
        option.font = font  # Set the font on the option

        # Call the base class sizeHint method
        return QStyledItemDelegate.sizeHint(self, option, index)

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

class DelegadoEstilizado(ItemDelegate):
    def __init__(self, parent=None, height=-1):
        super().__init__(parent)
        self.height = height

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if not index.parent().isValid():  # Check if the item is a top-level item
            font = option.font
            font.setWeight(QFont.DemiBold)  # Make top-level items bold
            option.font = font

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if not index.parent().isValid() or index.child(0,0).isValid():
            size.setHeight(size.height() + 10)
        return size

    # def paint(self, painter, option, index):
    #     # Check if the item is disabled
    #     if not index.flags() & Qt.ItemIsEnabled:
    #         painter.setPen(self.palette.color(QPalette.Disabled, QPalette.Text))  # Use palette color for disabled text
    #
    #     super().paint(painter, option, index)  # Call base class implementation

class SliderReseteable(QSlider):
    def __init__(self, orientation, default_value=None, *args, **kwargs):
        super().__init__(orientation, *args, **kwargs)
        self.default_value = default_value
        self.initUI()

    def initUI(self):
        # Add context menu with reset action
        self.createContextMenu()

    def createContextMenu(self):
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.resetSlider)
        self.addAction(reset_action)

    def resetSlider(self):
        self.setValue(self.default_value)

    def mouseDoubleClickEvent(self, event):
        self.resetSlider()