# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogo_elegir_cambiar_escena2.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ventana_elegir_escenas(object):
    def setupUi(self, ventana_elegir_escenas):
        ventana_elegir_escenas.setObjectName("ventana_elegir_escenas")
        ventana_elegir_escenas.setWindowModality(QtCore.Qt.ApplicationModal)
        ventana_elegir_escenas.resize(267, 255)
        self.gridLayout_2 = QtWidgets.QGridLayout(ventana_elegir_escenas)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lista_escenas = QtWidgets.QListWidget(ventana_elegir_escenas)
        self.lista_escenas.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.lista_escenas.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.lista_escenas.setObjectName("lista_escenas")
        self.gridLayout_2.addWidget(self.lista_escenas, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.boton_elegir_todas = QtWidgets.QPushButton(ventana_elegir_escenas)
        self.boton_elegir_todas.setMinimumSize(QtCore.QSize(80, 0))
        self.boton_elegir_todas.setObjectName("boton_elegir_todas")
        self.horizontalLayout_2.addWidget(self.boton_elegir_todas)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.boton_aceptar_cancelar = QtWidgets.QDialogButtonBox(ventana_elegir_escenas)
        self.boton_aceptar_cancelar.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.boton_aceptar_cancelar.setObjectName("boton_aceptar_cancelar")
        self.gridLayout_2.addWidget(self.boton_aceptar_cancelar, 3, 0, 1, 1)

        self.retranslateUi(ventana_elegir_escenas)
        QtCore.QMetaObject.connectSlotsByName(ventana_elegir_escenas)

    def retranslateUi(self, ventana_elegir_escenas):
        _translate = QtCore.QCoreApplication.translate
        ventana_elegir_escenas.setWindowTitle(_translate("ventana_elegir_escenas", "Elegir escenas"))
        self.boton_elegir_todas.setText(_translate("ventana_elegir_escenas", "Choose all"))

