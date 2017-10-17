# coding=cp949
'''
Created on 2017. 8. 28.

@author: SJ
'''
import boto3, _csv
import pandas as pd
import urllib2
from botocore.client import Config
from UI import Ui_MainWindow
from PyQt4.Qt import QThread
import numpy as np

class MObserver(QThread):
    tFlag = False
    def __init__(self):
        QThread.__init__(self)
        # 아마존 S3 접근
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.xNList = []
       
    # wait 함수
    def __del__(self):
        self.wait()

    # 쓰레드 정지 함수
    def stop(self):
        self.tFlag = True
        
    def run(self):
        while(self.tFlag == False):
            if(Ui_MainWindow.mFlag == True):
                # 입력 리스트
                self.xList =[]
                
                # 대상 곡 명
                self.xSong = ''
                
                # 삭제할 음악 리스트
                self.xNList =[]
            
                # 플레이 리스트 로드
                # URL 로드             
                url = self.S3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': 'csvdb',
                        'Key': 'PlayList'
                    }
                )
                temp = url.split('?')
                url = temp[0]+'.csv'
                rep=urllib2.urlopen(url)
                
                rdr = _csv.reader(rep)
            
                tFile = pd.read_csv(url)
                # 다음 재생될 곡부터 마지막까지 곡 리스트
                self.xList = Ui_MainWindow.cList
                # 대상일 될 이전 곡 명
                # 이전 음악의 장르 파악, 삭제할 장르
                self.xSong = Ui_MainWindow.bSong.encode('cp949')
                xGenre = 0
                tG =[]
                for i in rdr:
                    for j in self.xList:
                        if i[0] == j.encode('cp949'):
                            tG.append([i[0],i[8]])
                
                for i in rdr:
                    if i[0] == self.xSong:
                        xGenre = i[8]
                
                for i in range(len(tG)):
                    if(tG[i][1] == xGenre):
                        tG[i].pop()
                        
                for i in range(len(tG)):
                    self.xNList.append(tG[i][0])
                #틀 노래    
                print self.xNList
                #Ui_MainWindow.tttList = np.array(self.xNList[0])
                #Ui_MainWindow.temp(self, self.xNList)
                Ui_MainWindow.xList = self.xList
                Ui_MainWindow.mFlag = False
                Ui_MainWindow.dFlag = True
                