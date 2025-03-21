# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dispositivos.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dispositivos_cycles(object):
    def setupUi(self, dispositivos_cycles):
        dispositivos_cycles.setObjectName("dispositivos_cycles")
        dispositivos_cycles.resize(395, 181)
        self.gridLayout = QtWidgets.QGridLayout(dispositivos_cycles)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.gridLayout.addItem(spacerItem, 14, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_cuda = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_cuda.setCheckable(True)
        self.btn_cuda.setObjectName("btn_cuda")
        self.horizontalLayout_2.addWidget(self.btn_cuda)
        self.btn_optix = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_optix.setCheckable(True)
        self.btn_optix.setObjectName("btn_optix")
        self.horizontalLayout_2.addWidget(self.btn_optix)
        self.btn_opencl = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_opencl.setCheckable(True)
        self.btn_opencl.setObjectName("btn_opencl")
        self.horizontalLayout_2.addWidget(self.btn_opencl)
        self.btn_solo_cpu = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_solo_cpu.setCheckable(True)
        self.btn_solo_cpu.setObjectName("btn_solo_cpu")
        self.horizontalLayout_2.addWidget(self.btn_solo_cpu)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.btn_ignorar = QtWidgets.QRadioButton(dispositivos_cycles)
        self.btn_ignorar.setObjectName("btn_ignorar")
        self.gridLayout.addWidget(self.btn_ignorar, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_distribuir = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_distribuir.setObjectName("btn_distribuir")
        self.horizontalLayout_3.addWidget(self.btn_distribuir)
        self.btns_confirmacion = QtWidgets.QDialogButtonBox(dispositivos_cycles)
        self.btns_confirmacion.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btns_confirmacion.setCenterButtons(False)
        self.btns_confirmacion.setObjectName("btns_confirmacion")
        self.horizontalLayout_3.addWidget(self.btns_confirmacion)
        self.gridLayout.addLayout(self.horizontalLayout_3, 17, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.chk_usar_todos = QtWidgets.QCheckBox(dispositivos_cycles)
        self.chk_usar_todos.setEnabled(False)
        self.chk_usar_todos.setObjectName("chk_usar_todos")
        self.gridLayout_2.addWidget(self.chk_usar_todos, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_averiguar_dispositivos = QtWidgets.QPushButton(dispositivos_cycles)
        self.btn_averiguar_dispositivos.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.btn_averiguar_dispositivos.setObjectName("btn_averiguar_dispositivos")
        self.horizontalLayout.addWidget(self.btn_averiguar_dispositivos)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 0, 1, 1)

        self.retranslateUi(dispositivos_cycles)
        QtCore.QMetaObject.connectSlotsByName(dispositivos_cycles)

    def retranslateUi(self, dispositivos_cycles):
        _translate = QtCore.QCoreApplication.translate
        dispositivos_cycles.setWindowTitle(_translate("dispositivos_cycles", "Dispositivos de render (Cycles)"))
        self.btn_cuda.setText(_translate("dispositivos_cycles", "CUDA"))
        self.btn_optix.setText(_translate("dispositivos_cycles", "OptiX"))
        self.btn_opencl.setText(_translate("dispositivos_cycles", "OpenCL"))
        self.btn_solo_cpu.setText(_translate("dispositivos_cycles", "Solo CPU"))
        self.btn_ignorar.setText(_translate("dispositivos_cycles", "Usar settings de blender y seleccion del blend"))
        self.btn_distribuir.setText(_translate("dispositivos_cycles", "Distribuir"))
        self.chk_usar_todos.setText(_translate("dispositivos_cycles", "Usar Todos"))
        self.btn_averiguar_dispositivos.setText(_translate("dispositivos_cycles", "Averiguar dispositivos disponibles"))
