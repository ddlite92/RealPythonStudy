# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_consola.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ui_ventana_consola(object):
    def setupUi(self, ui_ventana_consola):
        ui_ventana_consola.setObjectName("ui_ventana_consola")
        ui_ventana_consola.resize(764, 621)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(ui_ventana_consola)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.info = QtWidgets.QPlainTextEdit(ui_ventana_consola)
        self.info.setObjectName("info")
        self.horizontalLayout.addWidget(self.info)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btn_subir_a_tope = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_subir_a_tope.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_subir_a_tope.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_subir_a_tope.setFont(font)
        self.btn_subir_a_tope.setObjectName("btn_subir_a_tope")
        self.verticalLayout.addWidget(self.btn_subir_a_tope)
        self.btn_subir_blend = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_subir_blend.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_subir_blend.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_subir_blend.setFont(font)
        self.btn_subir_blend.setObjectName("btn_subir_blend")
        self.verticalLayout.addWidget(self.btn_subir_blend)
        self.btn_bajar_blend = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_bajar_blend.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_bajar_blend.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_bajar_blend.setFont(font)
        self.btn_bajar_blend.setObjectName("btn_bajar_blend")
        self.verticalLayout.addWidget(self.btn_bajar_blend)
        self.btn_bajar_a_tope = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_bajar_a_tope.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_bajar_a_tope.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_bajar_a_tope.setFont(font)
        self.btn_bajar_a_tope.setCheckable(True)
        self.btn_bajar_a_tope.setObjectName("btn_bajar_a_tope")
        self.verticalLayout.addWidget(self.btn_bajar_a_tope)
        self.btn_limpiar_log = QtWidgets.QPushButton(ui_ventana_consola)
        self.btn_limpiar_log.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_limpiar_log.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btn_limpiar_log.setFont(font)
        self.btn_limpiar_log.setObjectName("btn_limpiar_log")
        self.verticalLayout.addWidget(self.btn_limpiar_log)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(ui_ventana_consola)
        QtCore.QMetaObject.connectSlotsByName(ui_ventana_consola)

    def retranslateUi(self, ui_ventana_consola):
        _translate = QtCore.QCoreApplication.translate
        ui_ventana_consola.setWindowTitle(_translate("ui_ventana_consola", "Form"))
        self.btn_subir_a_tope.setText(_translate("ui_ventana_consola", "⭱"))
        self.btn_subir_blend.setText(_translate("ui_ventana_consola", "⇑"))
        self.btn_bajar_blend.setText(_translate("ui_ventana_consola", "⇓"))
        self.btn_bajar_a_tope.setText(_translate("ui_ventana_consola", "⭳"))
        self.btn_limpiar_log.setText(_translate("ui_ventana_consola", "☒"))


