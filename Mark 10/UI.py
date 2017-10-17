# -*- coding: utf-8 -*-

'''
Created on 2017. 6. 30.

@author: DJ
'''
import cv2, boto3, functools
import urllib
import numpy as np
import pyqtgraph as pg

from pyqtgraph.Qt import QtGui, QtCore
from botocore.client import Config
from PyQt4 import QtCore, QtGui
from PyQt4 import phonon
from PyQt4.phonon import Phonon
from CaptureNUpload import CapNUp

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(QtGui.QMainWindow):
    
    ePosList = [0]
    eNegList = [0]
    ePosAgeList = [0.01,0.01,0.01,0.01,0.01]
    eNegAgeList = [0.01,0.01,0.01,0.01,0.01]
    
    fName = "" # Music Name
    mArray = []
    rCount = 0
    
    vThreadVideo01 = cv2.VideoCapture(0)
    vThreadVideo01.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
    vThreadVideo01.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
    vThread01 = CapNUp(vThreadVideo01, fName)

    mFlag = False
    rFlag = False
    aFlag = False
    dFlag = False
    
    # PlayList
    pList = []
    pList.append("싸이 (Psy)_BOMB (Feat BI & BOBBY)")
    ePos = 0
    season = ''
    weather = ''
    daytime = []
    testSet = []
    cIndex = 0
    totalIndex = 0
    sources = []
    xList = []

    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
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
        
        self.timeCounter = 0

        self.cList = []
        self.bSong = ''
        
        self.MusicList = QtGui.QTableWidget(self.Core)
       
        self.CKR = ''
        
    def addFiles(self, pList):
        index = len(self.sources)
                
        for i in pList:
            url = self.S3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'musicdb3139',
                    'Key': i
                }
            )
            temp = url.split('?')
            url = temp[0]+'.mp3'
        
            self.sources.append(Phonon.MediaSource(url))     
        
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
    
    def removeFiles(self, xList):
        self.sources = []
        self.mediaObject.stop()
        self.mediaObject.clear()
        self.MusicList.clearContents()
        self.MusicList.setRowCount(0)
        
        
        print "xList : ",xList
        index = len(self.sources)
        print "sources", self.sources
        print "index", index
        for i in xList:
            url = self.S3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'musicdb3139',
                    'Key': i
                }
            )
            temp = url.split('?')
            url = temp[0]+'.mp3'
        
            self.sources.append(Phonon.MediaSource(url))     
        print "Remove : ",self.sources
        print "len sources,", len(self.sources)
        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        
        self.dFlag = False
        
    def stateChanged(self, newState, oldState):

        if newState == Phonon.PlayingState:
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
        
        self.timeCounter = self.timeCounter + 1
        if self.timeCounter == 10:
            self.timeCounter = 0
            self.Plotter()
            print self.ePosList
            print self.eNegList
            
            
    def SignalChanger(self):
        self.emit(QtCore.SIGNAL('UI'))

    def sourceChanged(self, source):

        print self.CKR
        print "A"
        if self.mediaObject.isValid()== True:
            self.fName = unicode(urllib.unquote(unicode(self.mediaObject.currentSource().url().toString(),'cp949').encode('utf-8')),'utf-8')
            if self.sources != []:
                self.MusicList.selectRow(self.sources.index(source))
                print("START")
                print 'len ',len(self.sources)
                self.cIndex = self.sources.index(self.mediaObject.currentSource()) 
                self.mArray.append(self.fName)
                self.vThread01 = CapNUp(self.vThreadVideo01, self.fName) # Insert Music Name In Thread
                self.connect(self.vThread01, QtCore.SIGNAL('DnA'), self.SignalChanger)
                print "B"
                self.timeLcd.display('00:00')
                self.mediaObject.play()
                print self.mediaObject.currentSource().url().toString()
                if self.CKR != self.mediaObject.currentSource().url().toString():
                    self.vThread01.start()
                    self.CKR = self.mediaObject.currentSource().url().toString()
                if self.CKR == '':
                    self.CKR = self.mediaObject.currentSource().url().toString()
    def metaStateChanged(self, newState, oldState):
        
        if newState != Phonon.StoppedState and newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return
        
        metaData = self.metaInformationResolver.metaData()
        title = metaData.get(QtCore.QString('TITLE'), [QtCore.QString()])[0]
        if not title:
            title = self.metaInformationResolver.currentSource().fileName()

        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
        titleItem.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)

        artist = metaData.get(QtCore.QString('ARTIST'), [QtCore.QString()])[0]
        artistItem = QtGui.QTableWidgetItem(artist)
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
        artistItem.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)

        currentRow = self.MusicList.rowCount()
        self.MusicList.insertRow(currentRow)
        self.MusicList.setItem(currentRow, 0, titleItem)
        self.MusicList.setItem(currentRow, 1, artistItem)
        
        if not self.MusicList.selectedItems():
            self.MusicList.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        index = self.sources.index(self.metaInformationResolver.currentSource()) + 1
  
        
        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            if self.MusicList.columnWidth(0) > 300:
                self.MusicList.setColumnWidth(0, 300)
        
    def aboutToFinish(self):
        self.vThread01.stop()
        index = self.sources.index(self.mediaObject.currentSource()) + 1

        if(self.aFlag == True):
            self.addFiles(self.pList)
            index = self.sources.index(self.mediaObject.currentSource()) + 1
            self.aFlag = False
        
        if self.dFlag == True:
            self.removeFiles(self.xList)
        
            
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])
    """
    def finished(self):
        print "FIFIFIFIFI"
        if self.dFlag == True:
            self.removeFiles(self.xList)
            print "finished ", self.xList
    
    
    def temp(self, tList):
        self.xList = tList
        print "temp method ", self.xList, tList
    """
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

        
    def Plotter(self):
        self.win2.removeItem(self.bg1)
        self.win2.removeItem(self.bg2)
        self.p1.plot(self.ePosList, pen=(0,255,0), symbolBrush=(0,255,0), symbolPen='w')
        self.p1.plot(self.eNegList, pen=(255,0,0), symbolBrush=(255,0,0), symbolPen='w')
        
        self.bg1 = pg.BarGraphItem(x = np.array([12,22,32,42,52]), height = np.array(self.eNegAgeList),
                             width = 3.8, brush = 'r' )
        self.bg2 = pg.BarGraphItem(x = np.array([8,18,28,38,48]), height = np.array(self.ePosAgeList),
                             width = 3.8, brush = 'g' )
        self.win2.addItem(self.bg1)
        self.win2.addItem(self.bg2)
        
    def setupUi(self, MainWindow):
        global win1, win2
        
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1270, 915)
        
        self.Core = QtGui.QWidget(MainWindow)
        self.Core.setObjectName(_fromUtf8("Core"))
        
        self.win1 = pg.GraphicsWindow(title = "Emotion FlowChart")
        self.win2 = pg.plot(title = "Emotion Analysis Based on Age")
        
        pg.setConfigOptions(antialias = True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        self.p1 = self.win1.addPlot(title = "Positive, Negative Emotion Chart")
       
        self.p1.plot(self.ePosList, pen=(0,255,0), symbolBrush=(0,255,0), symbolPen='w')
        self.p1.plot(self.eNegList, pen=(255,0,0), symbolBrush=(255,0,0), symbolPen='w')
        
        self.bg1 = pg.BarGraphItem(x = np.array([12,22,32,42,52]), height = np.array(self.eNegAgeList),
                             width = 3.8, brush = 'r' )
        self.bg2 = pg.BarGraphItem(x = np.array([8,18,28,38,48]), height = np.array(self.ePosAgeList),
                             width = 3.8, brush = 'g' )
               
        self.win2.addItem(self.bg1)
        self.win2.addItem(self.bg2)

        self.Plot = QtGui.QHBoxLayout()
        self.Plot.addWidget(self.win1)
        
        self.Bar = QtGui.QHBoxLayout()
        self.Bar.addWidget(self.win2)
        
        self.FlowChart = QtGui.QWidget(self.Core)
        self.FlowChart.setLayout(self.Plot)
        self.FlowChart.setGeometry(QtCore.QRect(10, 450, 768, 432))
        
        self.BarChart = QtGui.QWidget(self.Core)
        self.BarChart.setLayout(self.Bar)
        self.BarChart.setGeometry(QtCore.QRect(10, 10, 768, 432))
        
        """
        self.Cam01 = QtGui.QLabel(self.Core)
        self.Cam01.setGeometry(QtCore.QRect(10, 10, 768, 432))
        self.Cam01.setObjectName(_fromUtf8("Cam01"))
        """
        
        self.LogoSpot = QtGui.QLabel(self.Core)
        self.LogoSpot.setGeometry(QtCore.QRect(1130,10,110,110))
        fLogo = QtGui.QImage("LogoPNG.png")
        self.Logo = QtGui.QPixmap.fromImage(fLogo)
        self.LogoSpot.setPixmap(self.Logo.scaled(self.LogoSpot.size(),QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))

        self.MusicList = QtGui.QTableWidget(self.Core)
        self.MusicList.setObjectName(_fromUtf8("MusicList"))
        self.MusicList.setColumnCount(2)
        self.MusicList.setRowCount(0)

        headers = (u"곡 제목", u"아티스트")
        self.MusicList.setHorizontalHeaderLabels(headers)
        hdr = self.MusicList.horizontalHeader()
        hdr.setResizeMode(0, QtGui.QHeaderView.Stretch)
        hdr.setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.MusicList.setColumnWidth(1, 150)

        self.MusicList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.MusicList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        self.pushButton = QtGui.QPushButton(self.Core)
        self.pushButton.setGeometry(QtCore.QRect(830, 250, 100, 23))
        self.pushButton.clicked.connect(functools.partial(self.addFiles,self.pList))
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
        self.Sub.setGeometry(QtCore.QRect(820, 130, 421, 751))
        self.Sub.setLayout(mainLayout)
        
        MainWindow.setCentralWidget(self.Core)

        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Smart DJ", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Start Process", None, QtGui.QApplication.UnicodeUTF8))

    
