'''
Created on 2017. 6. 30.

@author: DJ
'''
# coding = cp949
import cv2

from PyQt4 import QtCore, QtGui
from PyQt4 import phonon
from PyQt4.phonon import Phonon
from CaptureNUpload import CapNUp
from CaptureNUpload2 import CapNUp2
from Weather import WeatherAPI

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(QtGui.QMainWindow):
    fName = "" # Music Name
    mArray = []
    vThreadVideo01 = cv2.VideoCapture(0)
    vThreadVideo01.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    vThreadVideo01.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    
    vThreadVideo02 = cv2.VideoCapture(1)
    vThreadVideo02.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    vThreadVideo02.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    
    vThread01 = CapNUp(vThreadVideo01, fName)
    vThread02 = CapNUp2(vThreadVideo02, fName)
    
    wThread = WeatherAPI()
    
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)
    
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)
        
        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.setupActions()
        
        self.setupUi(self)

        self.sources = []
        
    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Select Music Files",
                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if not files:
            return

        index = len(self.sources)

        for string in files:
            self.sources.append(Phonon.MediaSource(string))

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])


    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                        self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))
    """
    def tableClicked(self, row, column):
        wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)

        self.mediaObject.stop()
        self.mediaObject.clearQueue()

        self.mediaObject.setCurrentSource(self.sources[row])

        if wasPlaying:
            self.mediaObject.play()
        else:
            self.mediaObject.stop()
    """
    def sourceChanged(self, source):
        self.MusicList.selectRow(self.sources.index(source))
        self.timeLcd.display('00:00')
        self.mediaObject.play()
        print("START")
        self.fName = self.mediaObject.currentSource().fileName()
        self.vThread01 = CapNUp(self.vThreadVideo01, self.fName) # Insert Music Name In Thread
        self.vThread02 = CapNUp2(self.vThreadVideo02, self.fName)
        print "fname : ",unicode(self.fName)
        self.wThread.run()
        self.vThread01.start()
        self.vThread02.start()
        self.mArray.append(self.fName)
        
        
    def metaStateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            QtGui.QMessageBox.warning(self, "Error opening files",
                    self.metaInformationResolver.errorString())

            while self.sources and self.sources.pop() != self.metaInformationResolver.currentSource():
                pass

            return

        if newState != Phonon.StoppedState and newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return

        metaData = self.metaInformationResolver.metaData()

        title = metaData.get('TITLE', [''])[0]
        if not title:
            title = self.metaInformationResolver.currentSource().fileName()

        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

        artist = metaData.get('ARTIST', [''])[0]
        artistItem = QtGui.QTableWidgetItem(artist)
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)

        album = metaData.get('ALBUM', [''])[0]
        albumItem = QtGui.QTableWidgetItem(album)
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)

        year = metaData.get('DATE', [''])[0]
        yearItem = QtGui.QTableWidgetItem(year)
        yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)

        currentRow = self.MusicList.rowCount()
        self.MusicList.insertRow(currentRow)
        self.MusicList.setItem(currentRow, 0, titleItem)
        self.MusicList.setItem(currentRow, 1, artistItem)
        self.MusicList.setItem(currentRow, 2, albumItem)
        self.MusicList.setItem(currentRow, 3, yearItem)

        if not self.MusicList.selectedItems():
            self.MusicList.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        index = self.sources.index(self.metaInformationResolver.currentSource()) + 1

        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            self.MusicList.resizeColumnsToContents()
            if self.MusicList.columnWidth(0) > 300:
                self.MusicList.setColumnWidth(0, 300)
    
    def aboutToFinish(self):
        index = self.sources.index(self.mediaObject.currentSource()) + 1
        print index
        if index == len(self.sources):
            self.fName = "/LAST.wmv"
            self.vThread01 = CapNUp(self.vThreadVideo01, self.fName) # Insert Music Name In Thread
            self.vThread01.start()
            self.vThread02 = CapNUp2(self.vThreadVideo02, self.fName) # Insert Music Name In Thread
            self.vThread02.start()
            
            
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])
    
    def setupActions(self):

        self.playAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
                self, shortcut="Ctrl+P", enabled=False,
                triggered=self.mediaObject.play)

        self.pauseAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
                "Pause", self, shortcut="Ctrl+A", enabled=False,
                triggered=self.mediaObject.pause)

        self.stopAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
                self, shortcut="Ctrl+S", enabled=False,
                triggered=self.mediaObject.stop)

        self.nextAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward),
                "Next", self, shortcut="Ctrl+N")

        self.previousAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward),
                "Previous", self, shortcut="Ctrl+R")

        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1589, 885)
        
        self.Core = QtGui.QWidget(MainWindow)
        self.Core.setObjectName(_fromUtf8("Core"))
        
        self.Cam01 = QtGui.QLabel(self.Core)
        self.Cam01.setGeometry(QtCore.QRect(10, 10, 640, 480))
        self.Cam01.setObjectName(_fromUtf8("Cam01"))

        self.Cam02 = QtGui.QLabel(self.Core)
        self.Cam02.setGeometry(QtCore.QRect(500, 500, 640, 480))
        self.Cam02.setObjectName(_fromUtf8("Cam02"))
        
        
        self.MusicList = QtGui.QTableWidget(self.Core)
        self.MusicList.setObjectName(_fromUtf8("MusicList"))
        self.MusicList.setColumnCount(1)
        self.MusicList.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.MusicList.setHorizontalHeaderItem(0, item)
        self.MusicList.setColumnWidth(0, 309)
        self.MusicList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.MusicList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
     #   self.MusicList.cellPressed.connect(self.tableClicked)
        
        self.pushButton = QtGui.QPushButton(self.Core)
        self.pushButton.setGeometry(QtCore.QRect(830, 250, 100, 23))
        self.pushButton.clicked.connect(lambda: self.addFiles())
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.seekSlider = phonon.Phonon.SeekSlider(self.Core)
        self.seekSlider.setObjectName(_fromUtf8("seekSlider"))
        self.seekSlider.setMediaObject(self.mediaObject)
        
        self.timeLcd = QtGui.QLCDNumber(self.Core)
        self.timeLcd.setObjectName(_fromUtf8("Time LCD"))
        self.timeLcd.display("00:00")
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)
        self.timeLcd.setPalette(palette)
        
        self.volumeSlider = phonon.Phonon.VolumeSlider(self.Core)
        self.volumeSlider.setObjectName(_fromUtf8("volumeSlider"))
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)
        
        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))
        
        self.widget = QtGui.QToolBar(self.Core)
        self.widget.addAction(self.playAction)
        self.widget.addAction(self.pauseAction)
        self.widget.addAction(self.stopAction)
        self.widget.setObjectName(_fromUtf8("widget"))
        
        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(self.seekSlider)
        seekerLayout.addWidget(self.timeLcd)

        playbackLayout = QtGui.QHBoxLayout()
        playbackLayout.addWidget(self.widget)
        playbackLayout.addStretch()
        playbackLayout.addWidget(volumeLabel)
        playbackLayout.addWidget(self.volumeSlider)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.pushButton)
        mainLayout.addLayout(seekerLayout)
        mainLayout.addLayout(playbackLayout)
        mainLayout.addWidget(self.MusicList)

        self.Sub = QtGui.QWidget(self.Core)
        self.Sub.setGeometry(QtCore.QRect(1151, 100, 421, 751))
        self.Sub.setLayout(mainLayout)
        
        MainWindow.setCentralWidget(self.Core)

        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Smart DJ", None, QtGui.QApplication.UnicodeUTF8))
        item = self.MusicList.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("MainWindow", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Load Music", None, QtGui.QApplication.UnicodeUTF8))
    
