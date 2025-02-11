# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dialogo_configuración.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_config_ventana(object):
    def setupUi(self, config_ventana):
        config_ventana.setObjectName("config_ventana")
        config_ventana.setWindowModality(QtCore.Qt.ApplicationModal)
        config_ventana.resize(534, 121)
        config_ventana.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.config_botones_ventana = QtWidgets.QDialogButtonBox(config_ventana)
        self.config_botones_ventana.setGeometry(QtCore.QRect(366, 90, 156, 23))
        self.config_botones_ventana.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.config_botones_ventana.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.config_botones_ventana.setObjectName("config_botones_ventana")
        self.widget = QtWidgets.QWidget(config_ventana)
        self.widget.setGeometry(QtCore.QRect(12, 3, 511, 80))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.config_selector_idioma = QtWidgets.QComboBox(self.widget)
        self.config_selector_idioma.setObjectName("config_selector_idioma")
        self.config_selector_idioma.addItem("")
        self.config_selector_idioma.addItem("")
        self.gridLayout.addWidget(self.config_selector_idioma, 0, 1, 1, 1)
        self.config_label_blender = QtWidgets.QLabel(self.widget)
        self.config_label_blender.setObjectName("config_label_blender")
        self.gridLayout.addWidget(self.config_label_blender, 1, 0, 1, 1)
        self.config_ubi_blender = QtWidgets.QLineEdit(self.widget)
        self.config_ubi_blender.setObjectName("config_ubi_blender")
        self.gridLayout.addWidget(self.config_ubi_blender, 1, 1, 1, 2)
        self.config_label_idioma = QtWidgets.QLabel(self.widget)
        self.config_label_idioma.setObjectName("config_label_idioma")
        self.gridLayout.addWidget(self.config_label_idioma, 0, 0, 1, 1)
        self.config_boton_explorar = QtWidgets.QPushButton(self.widget)
        self.config_boton_explorar.setObjectName("config_boton_explorar")
        self.gridLayout.addWidget(self.config_boton_explorar, 1, 3, 1, 1)

        self.retranslateUi(config_ventana)
        QtCore.QMetaObject.connectSlotsByName(config_ventana)

    def retranslateUi(self, config_ventana):
        _translate = QtCore.QCoreApplication.translate
        config_ventana.setWindowTitle(_translate("config_ventana", "Configurar Chuchurenderón!"))
        self.config_selector_idioma.setItemText(0, _translate("config_ventana", "Castellano"))
        self.config_selector_idioma.setItemText(1, _translate("config_ventana", "English"))
        self.config_label_blender.setText(_translate("config_ventana", "Blender:"))
        self.config_label_idioma.setText(_translate("config_ventana", "Idioma:"))
        self.config_boton_explorar.setText(_translate("config_ventana", "Explorar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    config_ventana = QtWidgets.QDialog()
    ui = Ui_config_ventana()
    ui.setupUi(config_ventana)
    config_ventana.show()
    sys.exit(app.exec_())

