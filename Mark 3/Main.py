'''
Created on 2017. 7. 7.

@author: DJ
'''
import sys
import os
import cv2, time
import numpy as np

from PyQt4 import QtGui, QtCore
from UI import Ui_MainWindow
from DownloadNAnalysis import DownNAnalyze
from __builtin__ import int


class Video():
    def __init__(self,capture):
        self.capture = capture
        self.currentFrame=np.array([])
 
    def captureNextFrame(self):
        """     capture frame and reverse RBG BGR and return opencv image     """
        ret, readFrame=self.capture.read()
        if(ret==True):
            self.currentFrame=cv2.cvtColor(readFrame,cv2.COLOR_BGR2RGB)
 
    def convertFrame(self):
        """     converts frame to format suitable for QtGui     """
        try:
            height,width=self.currentFrame.shape[:2]
            img=QtGui.QImage(self.currentFrame,
                              width,
                              height,
                              QtGui.QImage.Format_RGB888)
            img=QtGui.QPixmap.fromImage(img)
            self.previousFrame = self.currentFrame
            return img
        except:
            return None
            

class ProgressPopup(QtGui.QDialog):
    Terminate = DownNAnalyze()
    nProgress = QtCore.pyqtSignal(int)
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Analyizing In Process")
        self.setGeometry(770,520,400,100)
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setGeometry(30,40,350,20)
        self.button = QtGui.QPushButton("Press To Exit", self)
        self.button.setGeometry(150,70,100,25)
        self.button.clicked.connect(self.onStart)
        self.qFlag = False

    def onStart(self):
        self.progressBar.setRange(0,100)
        self.progressBar.setValue(0)
        if(Ui_MainWindow.mArray == []):
            print ("ZERO")
        else:
            aLength = len(Ui_MainWindow.mArray)
            print aLength
            tBlock = 50/aLength
            print tBlock
            for i in Ui_MainWindow.mArray:
                self.Terminate.Start('dgutest01', i)
                self.progressBar.setValue(tBlock)
                tBlock = tBlock + tBlock
            for j in Ui_MainWindow.mArray:
                self.Terminate.Start('dgutest02', j)
                self.progressBar.setValue(tBlock)
                tBlock = tBlock + tBlock
        
        self.progressBar.setValue(100)
        QtGui.qApp.processEvents()
        exit()
    
    def closeEvent(self, event):
        if self.qFlag:
            super(QtGui.QDialog,self).closeEvent(event)
        else:
            event.ignore()
            
class Gui(QtGui.QMainWindow):
    video01 = Video(cv2.VideoCapture(0))
    video02 = Video(cv2.VideoCapture(1))
    
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
        
    def play(self):
        try:
            self.video01.captureNextFrame()
            self.ui.Cam01.setPixmap(
                self.video01.convertFrame())
            self.ui.Cam01.setScaledContents(True)
            
            self.video02.captureNextFrame()
            self.ui.Cam02.setPixmap(
                self.video02.convertFrame())
            self.ui.Cam02.setScaledContents(True)

        except TypeError:
            pass

    def closeEvent(self, event):
        self.Popup()
        Ui_MainWindow.vThread01.stop()
        Ui_MainWindow.vThread02.stop()
        self.Quit()
        
    def Quit(self):
        cv2.destroyAllWindows()
        Ui_MainWindow.vThreadVideo01.release()
        Ui_MainWindow.vThreadVideo02.release()
        QtCore.QCoreApplication.quit()
    
    def Popup(self):
        self.dialog = ProgressPopup()
        self.dialog.exec_()
    
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()
