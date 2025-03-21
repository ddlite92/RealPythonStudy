# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_nombrado_arbol.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(295, 231)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.wgt_output_respetar = QtWidgets.QWidget(Form)
        self.wgt_output_respetar.setObjectName("wgt_output_respetar")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wgt_output_respetar)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.opcion_no_cambiar = QtWidgets.QRadioButton(self.wgt_output_respetar)
        self.opcion_no_cambiar.setChecked(True)
        self.opcion_no_cambiar.setObjectName("opcion_no_cambiar")
        self.horizontalLayout.addWidget(self.opcion_no_cambiar)
        self.verticalLayout.addWidget(self.wgt_output_respetar)
        self.wgt_output_preset = QtWidgets.QWidget(Form)
        self.wgt_output_preset.setObjectName("wgt_output_preset")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.wgt_output_preset)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.opcion_usar_preset = QtWidgets.QRadioButton(self.wgt_output_preset)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.opcion_usar_preset.sizePolicy().hasHeightForWidth())
        self.opcion_usar_preset.setSizePolicy(sizePolicy)
        self.opcion_usar_preset.setObjectName("opcion_usar_preset")
        self.horizontalLayout_2.addWidget(self.opcion_usar_preset)
        self.selector_preset = ComboBoxSimple(self.wgt_output_preset)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selector_preset.sizePolicy().hasHeightForWidth())
        self.selector_preset.setSizePolicy(sizePolicy)
        self.selector_preset.setObjectName("selector_preset")
        self.horizontalLayout_2.addWidget(self.selector_preset)
        self.verticalLayout.addWidget(self.wgt_output_preset)
        self.wgt_output_custom = QtWidgets.QWidget(Form)
        self.wgt_output_custom.setObjectName("wgt_output_custom")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.wgt_output_custom)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.opcion_custom = QtWidgets.QRadioButton(self.wgt_output_custom)
        self.opcion_custom.setObjectName("opcion_custom")
        self.horizontalLayout_3.addWidget(self.opcion_custom)
        self.btn_opciones_nombrado = QtWidgets.QPushButton(self.wgt_output_custom)
        self.btn_opciones_nombrado.setStyleSheet("")
        self.btn_opciones_nombrado.setObjectName("btn_opciones_nombrado")
        self.horizontalLayout_3.addWidget(self.btn_opciones_nombrado)
        self.verticalLayout.addWidget(self.wgt_output_custom)
        self.wgt_output_path = QtWidgets.QWidget(Form)
        self.wgt_output_path.setObjectName("wgt_output_path")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.wgt_output_path)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lbl_ruta = QtWidgets.QLabel(self.wgt_output_path)
        self.lbl_ruta.setEnabled(True)
        self.lbl_ruta.setObjectName("lbl_ruta")
        self.gridLayout_3.addWidget(self.lbl_ruta, 0, 0, 1, 1)
        self.lbl_nombre = QtWidgets.QLabel(self.wgt_output_path)
        self.lbl_nombre.setObjectName("lbl_nombre")
        self.gridLayout_3.addWidget(self.lbl_nombre, 1, 0, 1, 1)
        self.muestra_nombre = QtWidgets.QLineEdit(self.wgt_output_path)
        self.muestra_nombre.setEnabled(False)
        self.muestra_nombre.setMinimumSize(QtCore.QSize(120, 0))
        self.muestra_nombre.setObjectName("muestra_nombre")
        self.gridLayout_3.addWidget(self.muestra_nombre, 1, 1, 1, 1)
        self.muestra_ruta = QtWidgets.QLineEdit(self.wgt_output_path)
        self.muestra_ruta.setEnabled(False)
        self.muestra_ruta.setMinimumSize(QtCore.QSize(80, 0))
        self.muestra_ruta.setBaseSize(QtCore.QSize(0, 0))
        self.muestra_ruta.setObjectName("muestra_ruta")
        self.gridLayout_3.addWidget(self.muestra_ruta, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_3)
        self.verticalLayout.addWidget(self.wgt_output_path)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.opcion_no_cambiar.setText(_translate("Form", "No cambiar"))
        self.opcion_usar_preset.setText(_translate("Form", "Usar preset"))
        self.selector_preset.setText(_translate("Form", "a\n"
"b"))
        self.opcion_custom.setText(_translate("Form", "Nombrado custom"))
        self.btn_opciones_nombrado.setText(_translate("Form", "Opciones"))
        self.lbl_ruta.setText(_translate("Form", "Ruta"))
        self.lbl_nombre.setText(_translate("Form", "Nombre"))
from ui.combobox_alternativa import ComboBoxSimple
