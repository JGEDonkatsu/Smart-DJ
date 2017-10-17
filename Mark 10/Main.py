'''
Created on 2017. 7. 7.

@author: DJ
'''
import sys, gc
import cv2
import numpy as np

from PyQt4 import QtGui, QtCore
from UI import Ui_MainWindow
from DownloadNAnalysis import DownNAnalyze
from Recommender import Recommendation
from MusicObserver import MObserver

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
            
class Gui(QtGui.QMainWindow):
    video01 = Video(cv2.VideoCapture(0))
    
    aKey01 = '860000bba8cb4f55be0944b5ae3f52c6'
    
    aThread01 = DownNAnalyze('dgutest01', aKey01)
    
    vThread = Recommendation()

    mThread = MObserver()
    
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
        self.connect(self.ui, QtCore.SIGNAL('UI'), self.SignalChanger)
        self.connect(self.ui, QtCore.SIGNAL('ROW'), self.RowCounter)
        
        self.vThread.start()
        self.aThread01.start()
        #self.mThread.start()
    
    def RowCounter(self):
        if self.aThread01.rowSignal != 0:
            self.aThread01.rowSignal = 0
            self.aThread01.rowSignal = self.aThread01.rowSignal + 1
        else:
            self.aThread01.rowSignal = self.aThread01.rowSignal + 1
        
    def SignalChanger(self):
        self.aThread01.wFlag = True
        
    def play(self):
        try:
            """
            self.video01.captureNextFrame()
            self.ui.Cam01.setPixmap(
                self.video01.convertFrame())
            
            self.ui.Cam01.setScaledContents(True)
            """
            
        except TypeError:
            pass
        
    def closeEvent(self, event):
        self.vThread.stop()
        self.aThread01.stop()

        Ui_MainWindow.vThread01.stop()
        self.mThread.stop()
        self.Quit()
        
    def Quit(self):
        cv2.destroyAllWindows()
        Ui_MainWindow.vThreadVideo01.release()
        QtCore.QCoreApplication.quit()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()
