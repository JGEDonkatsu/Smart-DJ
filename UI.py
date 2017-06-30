'''
Created on 2017. 6. 30.

@author: DJ
'''

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(940, 710)
        
        self.Core = QtGui.QWidget(MainWindow)
        self.Core.setObjectName(_fromUtf8("Core"))
        
        self.Cam01 = QtGui.QLabel(self.Core)
        self.Cam01.setGeometry(QtCore.QRect(10, 10, 491, 341))
        self.Cam01.setObjectName(_fromUtf8("Cam01"))
        
        self.Cam02 = QtGui.QLabel(self.Core)
        self.Cam02.setGeometry(QtCore.QRect(10, 360, 491, 341))
        self.Cam02.setObjectName(_fromUtf8("Cam02"))
        
        self.MusicList = QtGui.QTableWidget(self.Core)
        self.MusicList.setGeometry(QtCore.QRect(520, 360, 411, 341))
        self.MusicList.setObjectName(_fromUtf8("MusicList"))
        self.MusicList.setColumnCount(3)
        self.MusicList.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.MusicList.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.MusicList.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.MusicList.setHorizontalHeaderItem(2, item) 
        self.MusicList.setColumnWidth(0, 40)
        self.MusicList.setColumnWidth(1, 220)
        self.MusicList.setColumnWidth(2, 149)

        MainWindow.setCentralWidget(self.Core)

        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Smart DJ", None, QtGui.QApplication.UnicodeUTF8))
        item = self.MusicList.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("MainWindow", "No.", None, QtGui.QApplication.UnicodeUTF8))
        item = self.MusicList.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("MainWindow", "Title", None, QtGui.QApplication.UnicodeUTF8))
        item = self.MusicList.horizontalHeaderItem(2)
        item.setText(QtGui.QApplication.translate("MainWindow", "Artist", None, QtGui.QApplication.UnicodeUTF8))