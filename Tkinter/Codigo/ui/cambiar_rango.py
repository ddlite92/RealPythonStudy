# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cambiar_rango.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ui_cambiar_rango(object):
    def setupUi(self, ui_cambiar_rango):
        ui_cambiar_rango.setObjectName("ui_cambiar_rango")
        ui_cambiar_rango.setWindowModality(QtCore.Qt.WindowModal)
        ui_cambiar_rango.setEnabled(True)
        ui_cambiar_rango.resize(196, 194)
        ui_cambiar_rango.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.verticalLayout = QtWidgets.QVBoxLayout(ui_cambiar_rango)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setContentsMargins(-1, 6, -1, -1)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_explicacion_vacios = QtWidgets.QLabel(ui_cambiar_rango)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lbl_explicacion_vacios.setFont(font)
        self.lbl_explicacion_vacios.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_explicacion_vacios.setObjectName("lbl_explicacion_vacios")
        self.verticalLayout.addWidget(self.lbl_explicacion_vacios)
        self.caja = QtWidgets.QGroupBox(ui_cambiar_rango)
        self.caja.setTitle("")
        self.caja.setAlignment(QtCore.Qt.AlignCenter)
        self.caja.setFlat(False)
        self.caja.setCheckable(False)
        self.caja.setObjectName("caja")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.caja)
        self.verticalLayout_2.setContentsMargins(4, 3, 4, 2)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbl_explicacion_relativos = QtWidgets.QLabel(self.caja)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lbl_explicacion_relativos.setFont(font)
        self.lbl_explicacion_relativos.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_explicacion_relativos.setObjectName("lbl_explicacion_relativos")
        self.verticalLayout_2.addWidget(self.lbl_explicacion_relativos)
        spacerItem = QtWidgets.QSpacerItem(6, 6, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_offset_fin = QtWidgets.QLabel(self.caja)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lbl_offset_fin.setFont(font)
        self.lbl_offset_fin.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_offset_fin.setObjectName("lbl_offset_fin")
        self.gridLayout.addWidget(self.lbl_offset_fin, 2, 6, 1, 1)
        self.campo_inicio = QtWidgets.QLineEdit(self.caja)
        self.campo_inicio.setMaximumSize(QtCore.QSize(40, 16777215))
        self.campo_inicio.setText("")
        self.campo_inicio.setAlignment(QtCore.Qt.AlignCenter)
        self.campo_inicio.setObjectName("campo_inicio")
        self.gridLayout.addWidget(self.campo_inicio, 1, 2, 1, 1)
        self.campo_fin = QtWidgets.QLineEdit(self.caja)
        self.campo_fin.setMaximumSize(QtCore.QSize(40, 16777215))
        self.campo_fin.setAlignment(QtCore.Qt.AlignCenter)
        self.campo_fin.setObjectName("campo_fin")
        self.gridLayout.addWidget(self.campo_fin, 1, 6, 1, 1)
        self.lbl_frame_fin_alt = QtWidgets.QLabel(self.caja)
        self.lbl_frame_fin_alt.setObjectName("lbl_frame_fin_alt")
        self.gridLayout.addWidget(self.lbl_frame_fin_alt, 1, 5, 1, 1)
        self.lbl_frame_inicio_alt = QtWidgets.QLabel(self.caja)
        self.lbl_frame_inicio_alt.setObjectName("lbl_frame_inicio_alt")
        self.gridLayout.addWidget(self.lbl_frame_inicio_alt, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.lbl_offset_inicio = QtWidgets.QLabel(self.caja)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_offset_inicio.sizePolicy().hasHeightForWidth())
        self.lbl_offset_inicio.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lbl_offset_inicio.setFont(font)
        self.lbl_offset_inicio.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_offset_inicio.setObjectName("lbl_offset_inicio")
        self.gridLayout.addWidget(self.lbl_offset_inicio, 2, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 7, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 3, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.btn_partir_rango = QtWidgets.QPushButton(self.caja)
        self.btn_partir_rango.setObjectName("btn_partir_rango")
        self.horizontalLayout.addWidget(self.btn_partir_rango)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.caja)
        self.groupBox = QtWidgets.QGroupBox(ui_cambiar_rango)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_5.setContentsMargins(4, 2, 4, 2)
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.lbl_frame_step = QtWidgets.QLabel(self.groupBox)
        self.lbl_frame_step.setObjectName("lbl_frame_step")
        self.horizontalLayout_5.addWidget(self.lbl_frame_step)
        self.campo_step = QtWidgets.QLineEdit(self.groupBox)
        self.campo_step.setMaximumSize(QtCore.QSize(40, 16777215))
        self.campo_step.setAlignment(QtCore.Qt.AlignCenter)
        self.campo_step.setObjectName("campo_step")
        self.horizontalLayout_5.addWidget(self.campo_step)
        spacerItem7 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem7)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem8 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem8)
        self.botones_generales = QtWidgets.QDialogButtonBox(ui_cambiar_rango)
        self.botones_generales.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.botones_generales.setCenterButtons(True)
        self.botones_generales.setObjectName("botones_generales")
        self.verticalLayout.addWidget(self.botones_generales)

        self.retranslateUi(ui_cambiar_rango)
        QtCore.QMetaObject.connectSlotsByName(ui_cambiar_rango)

    def retranslateUi(self, ui_cambiar_rango):
        _translate = QtCore.QCoreApplication.translate
        ui_cambiar_rango.setWindowTitle(_translate("ui_cambiar_rango", "Change frame range"))
        self.lbl_explicacion_vacios.setText(_translate("ui_cambiar_rango", "Dejar vacíos para..."))
        self.lbl_explicacion_relativos.setText(_translate("ui_cambiar_rango", "Empezar con +..."))
        self.lbl_offset_fin.setText(_translate("ui_cambiar_rango", "TextLabel"))
        self.lbl_frame_fin_alt.setText(_translate("ui_cambiar_rango", "Fin:"))
        self.lbl_frame_inicio_alt.setText(_translate("ui_cambiar_rango", "Inicio:"))
        self.lbl_offset_inicio.setText(_translate("ui_cambiar_rango", "TextLabel"))
        self.btn_partir_rango.setText(_translate("ui_cambiar_rango", "Split range"))
        self.lbl_frame_step.setText(_translate("ui_cambiar_rango", "Step:"))
