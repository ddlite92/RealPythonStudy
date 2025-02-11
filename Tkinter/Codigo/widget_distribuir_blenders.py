# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_distribuir_blenders.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_widget_distribuir_blenders(object):
    def setupUi(self, widget_distribuir_blenders):
        widget_distribuir_blenders.setObjectName("widget_distribuir_blenders")
        widget_distribuir_blenders.setWindowModality(QtCore.Qt.ApplicationModal)
        widget_distribuir_blenders.resize(192, 270)
        self.verticalLayout = QtWidgets.QVBoxLayout(widget_distribuir_blenders)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lista_blenders = QtWidgets.QListWidget(widget_distribuir_blenders)
        self.lista_blenders.setObjectName("lista_blenders")
        self.verticalLayout.addWidget(self.lista_blenders)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_distribuir = QtWidgets.QPushButton(widget_distribuir_blenders)
        self.btn_distribuir.setObjectName("btn_distribuir")
        self.horizontalLayout.addWidget(self.btn_distribuir)
        self.btn_cancelar = QtWidgets.QPushButton(widget_distribuir_blenders)
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.horizontalLayout.addWidget(self.btn_cancelar)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(widget_distribuir_blenders)
        QtCore.QMetaObject.connectSlotsByName(widget_distribuir_blenders)

    def retranslateUi(self, widget_distribuir_blenders):
        _translate = QtCore.QCoreApplication.translate
        widget_distribuir_blenders.setWindowTitle(_translate("widget_distribuir_blenders", "Auto-asignar blenders"))
        self.btn_distribuir.setText(_translate("widget_distribuir_blenders", "Distribuir"))
        self.btn_cancelar.setText(_translate("widget_distribuir_blenders", "Cancelar"))

