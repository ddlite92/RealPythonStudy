# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_consola2.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ui_ventana_consola(object):
    def setupUi(self, ui_ventana_consola):
        ui_ventana_consola.setObjectName("ui_ventana_consola")
        ui_ventana_consola.resize(764, 621)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ui_ventana_consola)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_blend = QtWidgets.QLabel(ui_ventana_consola)
        self.lbl_blend.setObjectName("lbl_blend")
        self.horizontalLayout.addWidget(self.lbl_blend)
        self.numero_blend = QtWidgets.QLabel(ui_ventana_consola)
        self.numero_blend.setObjectName("numero_blend")
        self.horizontalLayout.addWidget(self.numero_blend)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lbl_nombre = QtWidgets.QLabel(ui_ventana_consola)
        self.lbl_nombre.setObjectName("lbl_nombre")
        self.horizontalLayout.addWidget(self.lbl_nombre)
        self.nombre_archivo = QtWidgets.QLabel(ui_ventana_consola)
        self.nombre_archivo.setObjectName("nombre_archivo")
        self.horizontalLayout.addWidget(self.nombre_archivo)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_anterior = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_anterior.setMinimumSize(QtCore.QSize(0, 0))
        self.btn_anterior.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btn_anterior.setObjectName("btn_anterior")
        self.horizontalLayout.addWidget(self.btn_anterior)
        self.btn_siguiente = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_siguiente.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btn_siguiente.setObjectName("btn_siguiente")
        self.horizontalLayout.addWidget(self.btn_siguiente)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.info = QtWidgets.QPlainTextEdit(ui_ventana_consola)
        self.info.setObjectName("info")
        self.verticalLayout_2.addWidget(self.info)

        self.retranslateUi(ui_ventana_consola)
        QtCore.QMetaObject.connectSlotsByName(ui_ventana_consola)

    def retranslateUi(self, ui_ventana_consola):
        _translate = QtCore.QCoreApplication.translate
        ui_ventana_consola.setWindowTitle(_translate("ui_ventana_consola", "Form"))
        self.lbl_blend.setText(_translate("ui_ventana_consola", "Blend N°:"))
        self.numero_blend.setText(_translate("ui_ventana_consola", "0"))
        self.lbl_nombre.setText(_translate("ui_ventana_consola", "Nombre:"))
        self.nombre_archivo.setText(_translate("ui_ventana_consola", "blend"))
        self.btn_anterior.setText(_translate("ui_ventana_consola", "|<"))
        self.btn_siguiente.setText(_translate("ui_ventana_consola", ">|"))

