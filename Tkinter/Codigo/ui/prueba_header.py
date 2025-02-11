# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'prueba_header.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(810, 590)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabla_status = QtWidgets.QListWidget(self.centralwidget)
        self.tabla_status.setGeometry(QtCore.QRect(60, 170, 611, 131))
        self.tabla_status.setObjectName("tabla_status")
        self.tree_status = QtWidgets.QTreeWidget(self.centralwidget)
        self.tree_status.setGeometry(QtCore.QRect(180, 360, 256, 192))
        self.tree_status.setObjectName("tree_status")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tree_status.headerItem().setText(0, _translate("MainWindow", "1"))
        self.tree_status.headerItem().setText(1, _translate("MainWindow", "New Column"))
        self.tree_status.headerItem().setText(2, _translate("MainWindow", "3"))

