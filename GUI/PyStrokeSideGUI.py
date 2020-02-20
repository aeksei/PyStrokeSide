# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI\app.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import json
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(607, 291)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 381, 251))
        self.tabWidget.setObjectName("tabWidget")
        self.erg_numeration = QtWidgets.QWidget()
        self.erg_numeration.setObjectName("erg_numeration")
        self.btn_number_all_ergs = QtWidgets.QPushButton(self.erg_numeration)
        self.btn_number_all_ergs.setGeometry(QtCore.QRect(20, 20, 121, 31))
        self.btn_number_all_ergs.setObjectName("btn_number_all_ergs")
        self.btn_number_missing_ergs = QtWidgets.QPushButton(self.erg_numeration)
        self.btn_number_missing_ergs.setGeometry(QtCore.QRect(20, 70, 121, 31))
        self.btn_number_missing_ergs.setObjectName("btn_number_missing_ergs")
        self.btn_number_done = QtWidgets.QPushButton(self.erg_numeration)
        self.btn_number_done.setGeometry(QtCore.QRect(20, 170, 121, 31))
        self.btn_number_done.setObjectName("btn_number_done")
        self.tabWidget.addTab(self.erg_numeration, "")
        self.race_definition = QtWidgets.QWidget()
        self.race_definition.setObjectName("race_definition")
        self.radioButton = QtWidgets.QRadioButton(self.race_definition)
        self.radioButton.setGeometry(QtCore.QRect(20, 20, 41, 17))
        self.radioButton.setObjectName("radioButton")
        self.textEdit_2 = QtWidgets.QTextEdit(self.race_definition)
        self.textEdit_2.setGeometry(QtCore.QRect(160, 10, 151, 31))
        self.textEdit_2.setObjectName("textEdit_2")
        self.tabWidget.addTab(self.race_definition, "")
        self.race_data = QtWidgets.QWidget()
        self.race_data.setObjectName("race_data")
        self.tabWidget.addTab(self.race_data, "")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(470, 10, 121, 31))
        self.lcdNumber.setObjectName("lcdNumber")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(390, 50, 201, 191))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 199, 189))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.textEdit = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 201, 191))
        self.textEdit.setObjectName("textEdit")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 607, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_number_all_ergs.setText(_translate("MainWindow", "number_all_ergs"))
        self.btn_number_missing_ergs.setText(_translate("MainWindow", "number_missing_ergs"))
        self.btn_number_done.setText(_translate("MainWindow", "done_numbering"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.erg_numeration), _translate("MainWindow", "erg_numeration"))
        self.radioButton.setText(_translate("MainWindow", "1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.race_definition), _translate("MainWindow", "race_definition"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.race_data), _translate("MainWindow", "race_data"))

