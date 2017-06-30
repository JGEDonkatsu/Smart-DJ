import sys
import cv2
import numpy as np
from PyQt4 import QtGui, QtCore
from UI import Ui_MainWindow

class Video():
    def __init__(self,capture):
        self.capture = capture
        self.currentFrame=np.array([])
 
    def captureNextFrame(self):
        """                           
        capture frame and reverse RBG BGR and return opencv image                                      
        """
        ret, readFrame=self.capture.read()
        if(ret==True):
            self.currentFrame=cv2.cvtColor(readFrame,cv2.COLOR_BGR2RGB)
 
    def convertFrame(self):
        """     converts frame to format suitable for QtGui            """
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
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.video01 = Video(cv2.VideoCapture(0))
        self.video02 = Video(cv2.VideoCapture(1))
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
            print "No frame"
 
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()