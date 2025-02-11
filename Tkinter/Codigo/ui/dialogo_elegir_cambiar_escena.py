# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogo_elegir_cambiar_escena.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ventana_cambiar_escena(object):
    def setupUi(self, ventana_cambiar_escena):
        ventana_cambiar_escena.setObjectName("ventana_cambiar_escena")
        ventana_cambiar_escena.setWindowModality(QtCore.Qt.ApplicationModal)
        ventana_cambiar_escena.resize(267, 308)
        self.gridLayout_2 = QtWidgets.QGridLayout(ventana_cambiar_escena)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem, 7, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.opcion_escribir_escena = QtWidgets.QRadioButton(ventana_cambiar_escena)
        self.opcion_escribir_escena.setObjectName("opcion_escribir_escena")
        self.horizontalLayout.addWidget(self.opcion_escribir_escena)
        self.nombre_escena = QtWidgets.QLineEdit(ventana_cambiar_escena)
        self.nombre_escena.setMinimumSize(QtCore.QSize(120, 0))
        self.nombre_escena.setObjectName("nombre_escena")
        self.horizontalLayout.addWidget(self.nombre_escena)
        self.gridLayout_2.addLayout(self.horizontalLayout, 6, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem1, 5, 0, 1, 1)
        self.opcion_elegir_escenas = QtWidgets.QRadioButton(ventana_cambiar_escena)
        self.opcion_elegir_escenas.setObjectName("opcion_elegir_escenas")
        self.gridLayout_2.addWidget(self.opcion_elegir_escenas, 2, 0, 1, 1)
        self.lista_escenas = QtWidgets.QListWidget(ventana_cambiar_escena)
        self.lista_escenas.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.lista_escenas.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.lista_escenas.setObjectName("lista_escenas")
        self.gridLayout_2.addWidget(self.lista_escenas, 3, 0, 1, 1)
        self.boton_aceptar_cancelar = QtWidgets.QDialogButtonBox(ventana_cambiar_escena)
        self.boton_aceptar_cancelar.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.boton_aceptar_cancelar.setObjectName("boton_aceptar_cancelar")
        self.gridLayout_2.addWidget(self.boton_aceptar_cancelar, 8, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.boton_leer_escenas = QtWidgets.QPushButton(ventana_cambiar_escena)
        self.boton_leer_escenas.setMinimumSize(QtCore.QSize(120, 0))
        self.boton_leer_escenas.setObjectName("boton_leer_escenas")
        self.horizontalLayout_2.addWidget(self.boton_leer_escenas)
        self.boton_elegir_todas = QtWidgets.QPushButton(ventana_cambiar_escena)
        self.boton_elegir_todas.setMinimumSize(QtCore.QSize(80, 0))
        self.boton_elegir_todas.setObjectName("boton_elegir_todas")
        self.horizontalLayout_2.addWidget(self.boton_elegir_todas)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)

        self.retranslateUi(ventana_cambiar_escena)
        QtCore.QMetaObject.connectSlotsByName(ventana_cambiar_escena)

    def retranslateUi(self, ventana_cambiar_escena):
        _translate = QtCore.QCoreApplication.translate
        ventana_cambiar_escena.setWindowTitle(_translate("ventana_cambiar_escena", "Cambiar escena"))
        self.opcion_escribir_escena.setText(_translate("ventana_cambiar_escena", "Enter scene\'s name"))
        self.opcion_elegir_escenas.setText(_translate("ventana_cambiar_escena", "Select scene(s) to add to the queue:"))
        self.boton_leer_escenas.setText(_translate("ventana_cambiar_escena", "Read blend\'s scenes"))
        self.boton_elegir_todas.setText(_translate("ventana_cambiar_escena", "Choose all"))

