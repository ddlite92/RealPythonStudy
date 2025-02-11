from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionButton
from PyQt5.QtWidgets import QComboBox, QStyleOptionComboBox, QStylePainter, QStyle
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPainter

class CenteredItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

class ComboBoxCentrada(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setItemDelegate(CenteredItemDelegate(self))

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))

        # Draw the combobox frame, focusrect and selected etc.
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)

        if self.currentIndex() < 0 and not self.placeholderText():
            opt.palette.setBrush(QPalette.ButtonText, opt.palette.placeholderText())
            opt.currentText = self.placeholderText()

        # Draw the icon and text
        # painter.drawControl(QStyle.CE_ComboBoxLabel, opt)

        painter2 = QPainter(self)
        buttonOpt = QStyleOptionButton()
        buttonOpt.initFrom(self)  # Init states, such as hover, disable

        editRect = self.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxEditField, self)
        buttonOpt.rect = editRect  # Text rect
        buttonOpt.text = opt.currentText
        self.style().drawControl(QStyle.CE_PushButtonLabel, buttonOpt, painter2, self)  # As button text


