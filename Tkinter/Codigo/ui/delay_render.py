# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'delay_render.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_selector_delay(object):
    def setupUi(self, selector_delay):
        selector_delay.setObjectName("selector_delay")
        selector_delay.resize(176, 109)
        self.verticalLayout = QtWidgets.QVBoxLayout(selector_delay)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_mensaje = QtWidgets.QLabel(selector_delay)
        self.lbl_mensaje.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_mensaje.setObjectName("lbl_mensaje")
        self.verticalLayout.addWidget(self.lbl_mensaje)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.selector_horas = QtWidgets.QSpinBox(selector_delay)
        self.selector_horas.setAccessibleName("")
        self.selector_horas.setObjectName("selector_horas")
        self.gridLayout.addWidget(self.selector_horas, 1, 0, 1, 1)
        self.lbl_minutos = QtWidgets.QLabel(selector_delay)
        self.lbl_minutos.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_minutos.setObjectName("lbl_minutos")
        self.gridLayout.addWidget(self.lbl_minutos, 0, 2, 1, 1)
        self.lbl_horas = QtWidgets.QLabel(selector_delay)
        self.lbl_horas.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_horas.setObjectName("lbl_horas")
        self.gridLayout.addWidget(self.lbl_horas, 0, 0, 1, 1)
        self.selector_minutos = QtWidgets.QSpinBox(selector_delay)
        self.selector_minutos.setProperty("showGroupSeparator", True)
        self.selector_minutos.setMaximum(60)
        self.selector_minutos.setSingleStep(10)
        self.selector_minutos.setProperty("value", 0)
        self.selector_minutos.setObjectName("selector_minutos")
        self.gridLayout.addWidget(self.selector_minutos, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(selector_delay)
        self.label.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_setear = QtWidgets.QPushButton(selector_delay)
        self.btn_setear.setObjectName("btn_setear")
        self.horizontalLayout_2.addWidget(self.btn_setear)
        self.btn_cancelar = QtWidgets.QPushButton(selector_delay)
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.horizontalLayout_2.addWidget(self.btn_cancelar)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(selector_delay)
        QtCore.QMetaObject.connectSlotsByName(selector_delay)

    def retranslateUi(self, selector_delay):
        _translate = QtCore.QCoreApplication.translate
        selector_delay.setWindowTitle(_translate("selector_delay", "Demorar render"))
        self.lbl_mensaje.setText(_translate("selector_delay", "Comenzar a renderizar en:"))
        self.lbl_minutos.setText(_translate("selector_delay", "minutos"))
        self.lbl_horas.setText(_translate("selector_delay", "horas"))
        self.label.setText(_translate("selector_delay", ":"))
        self.btn_setear.setText(_translate("selector_delay", "Establecer"))
        self.btn_cancelar.setText(_translate("selector_delay", "Cancelar"))

