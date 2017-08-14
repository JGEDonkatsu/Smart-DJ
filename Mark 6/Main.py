'''
Created on 2017. 7. 7.

@author: DJ
'''
import sys
import cv2
import numpy as np

from PyQt4 import QtGui, QtCore
from UI import Ui_MainWindow
from DownloadNAnalysis import DownNAnalyze


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
    video02 = Video(cv2.VideoCapture(1))
    
    aKey01 = 'd114f2dad42e4fcb9483b9a22de4ff87'
    aKey02 = '860000bba8cb4f55be0944b5ae3f52c6'
    
    aThread01 = DownNAnalyze('dgutest01', aKey01)
    aThread02 = DownNAnalyze('dgutest02', aKey02)
    
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
        self.aThread01.start()
        self.aThread02.start()
        
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
        self.aThread01.stop()
        self.aThread02.stop()
        Ui_MainWindow.vThread01.stop()
        Ui_MainWindow.vThread02.stop()

        self.Quit()
        
    def Quit(self):
        cv2.destroyAllWindows()
        Ui_MainWindow.vThreadVideo01.release()
        Ui_MainWindow.vThreadVideo02.release()
        QtCore.QCoreApplication.quit()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()
