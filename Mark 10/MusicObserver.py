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
        # �Ƹ��� S3 ����
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.xNList = []
       
    # wait �Լ�
    def __del__(self):
        self.wait()

    # ������ ���� �Լ�
    def stop(self):
        self.tFlag = True
        
    def run(self):
        while(self.tFlag == False):
            if(Ui_MainWindow.mFlag == True):
                # �Է� ����Ʈ
                self.xList =[]
                
                # ��� �� ��
                self.xSong = ''
                
                # ������ ���� ����Ʈ
                self.xNList =[]
            
                # �÷��� ����Ʈ �ε�
                # URL �ε�             
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
                # ���� ����� ����� ���������� �� ����Ʈ
                self.xList = Ui_MainWindow.cList
                # ����� �� ���� �� ��
                # ���� ������ �帣 �ľ�, ������ �帣
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
                #Ʋ �뷡    
                print self.xNList
                #Ui_MainWindow.tttList = np.array(self.xNList[0])
                #Ui_MainWindow.temp(self, self.xNList)
                Ui_MainWindow.xList = self.xList
                Ui_MainWindow.mFlag = False
                Ui_MainWindow.dFlag = True
                