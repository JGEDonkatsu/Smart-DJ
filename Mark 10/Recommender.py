# coding=cp949
'''
Created on 2017. 8. 28.

@author: DJ
'''
import operator, boto3
import numpy as np
import pandas as pd

from sklearn import svm
from botocore.client import Config
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from PyQt4.QtCore import QThread
from UI import Ui_MainWindow

class Recommendation(QThread):
    # ������ ���� �÷���
    tFlag = False
    def __init__(self):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        # Ʈ���̴� ��
        self.trainingSet = []
        # �帣 �ڵ尡 ����ִ� ����Ʈ
        self.codeSet = []
        # �� ���� ����ִ� ����Ʈ
        self.nameSet  = []
        self.sample = pd.read_csv('ExpList.csv')

        # �帣 ���赵
        self.gChart = [[0,1,0,0,0,0,0,0,0,0,1,0],
                       [1,0,1,0,0,0,0,0,0,0,0,0],
                       [0,1,0,1,0,0,0,0,0,0,0,0],
                       [0,0,1,0,1,0,1,0,0,0,1,0],
                       [0,0,0,1,0,1,0,0,0,0,0,0],
                       [0,0,0,0,1,0,0,0,0,0,0,0],
                       [0,0,0,1,0,0,0,1,0,0,0,0],
                       [0,0,0,0,0,0,1,0,1,0,0,0],
                       [0,0,0,0,0,0,0,1,0,1,0,0],
                       [0,0,0,0,0,0,0,0,1,0,1,0],
                       [1,0,0,1,0,0,0,0,0,1,0,1],
                       [0,0,0,0,0,0,0,0,0,0,1,0]]
        
    def stop(self):
        self.tFlag = True

    def run(self):
        while(self.tFlag == False):
            if(Ui_MainWindow.rFlag == True):
                self.trainingSet = []
                self.nameSet = []
                self.codeSet = []
                print "IN RECOM"
                # �̿��ϴ� �帣���� ���� ����Ʈ
                gNeighbors = []

                # �׽�Ʈ �� ����
                self.testSet = Ui_MainWindow.testSet
                        
                # �ӽŷ��� ���� �ε�
                self.season = Ui_MainWindow.season
                self.weather = Ui_MainWindow.weather
                self.daytime = Ui_MainWindow.daytime
        
                # Ʈ���̴� ��, �ε��� �� ����
                self.LoadTrainSet(self.trainingSet, self.codeSet)
                self.trainingSet = np.array(self.trainingSet)
                
                # SVM ���� �帣 ����
                    # �� �� ���� �� 0
                    # �ڵ� ���� �� 1
                gCode = self.SVM(self.trainingSet,self.testSet, 1)
                
                # �帣 ���赵�� ���� �̿��ϴ� �帣 ����
                gNeighbors = self.GenreNeighborFinder(gCode)
                
                # ����� �帣�� ��������� 1�� ��õ
                mName = self.SVMInGenres(gNeighbors)
                # ���� ����, ����, �ð��� ������� ���� �±� ����
                tag = self.GenieTagFinder(self.season, self.weather, self.daytime[1])
                # ���� �±׸� ������� ��õ�� 1�����κ��� Top5 ��õ
                Top5 = self.CSWithGenie(mName, tag)
                # ��õ�� Top5�� ������� �� �÷��� ����Ʈ���� ��õ
                pList = self.PlaylistGenerator(Top5)
                toUI = []
                print "�� õ �� ��"
                for i in range(len(pList.values())):
                    for j in range(len(pList.values()[i])):
                        toUI.append(pList.values()[i][j].decode('cp949'))
                
                Ui_MainWindow.pList = toUI
                Ui_MainWindow.rFlag = False
                Ui_MainWindow.aFlag = True
           
    def PlaylistGenerator(self, Top5):
        cData = {}
        # Top 5 � ���� ���� �ε�
        # URL ����            
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'TotalGenieList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # �Էµ� �� �� ���� ��Ÿ ������ �˻�
        tFile = pd.read_csv(url)
        
        for mName in Top5:
            tFileC = tFile[tFile['Title'] == mName][['Title', 'SignalMagnitude', 'SpectralCentroid',
                                                     'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
            cData.update(dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                     tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                     tFileC.MFCC, tFileC.Tempo,
                                                                     tFileC.Pitch, tFileC.Intensity)]))        
        # ���� �÷����� ���� ��Ÿ������ �ε�            
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'PlayList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # �Էµ� �� �� ���� ��Ÿ ������ �˻�
        tFile = pd.read_csv(url)
        tFileC = tFile[['Title', 'SignalMagnitude', 'SpectralCentroid',
                        'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
        pData = dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                 tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                 tFileC.MFCC, tFileC.Tempo,
                                                                 tFileC.Pitch, tFileC.Intensity)])
        # Cosine Similarity ���
        cDic = {} # { : {doc : cosine score}}
        
        for i in cData.keys():
            subDic = {}
            cDataArray = np.array(cData[i])
            cDataVector = cDataArray.reshape(1, -1)
            
            for j in pData.keys():
                pDataArray = np.array(pData[j])
                pDataVector = pDataArray.reshape(1, -1)
                CS = cosine_similarity(cDataVector, pDataVector)
                subDic[j] = CS
            cDic[i] = subDic
        
        # �� ���� �� Cosine Score�� ���� Doc ������ ����
        # { song1 : [song2 : cosine score] }
        
        sortedDic = {}
        
        for i in cDic.keys():
            sortedScore = sorted(cDic[i].items(),
                                 key = operator.itemgetter(1),
                                 reverse = True)
            sortList = []
            
            for j in range(len(sortedScore)):
                song = sortedScore[j][0]
                score = str(float(sortedScore[j][1]))
                eachList = [song, score]
                sortList.append(eachList)
            
            sortedDic[i] = sortList
        
        # Top 5 ����
        # { song1 : [ Top1, Top2, Top3, Top4, Top5 ] }
        
        Top5 = {}
        
        for i in sortedDic.keys():
            songList = []
            for j in range(0, 5):
                songList.append(sortedDic[i][j][0])
            
            Top5[i] = songList
        
        return Top5
                   
    def SVMInGenres(self, gNeighbors):
        # ���õ� �帣�� �̿� ������ �帣�� ���� �����͸��� ������ Ʈ���̴� ��
        genreTS = []
        self.nameSet = []
        
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'ExpList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # �Էµ� �� �� ���� ��Ÿ ������ �˻�
        tFile = pd.read_csv(url)
        for gName in gNeighbors:
            gCode = self.InverseCodeConverter(gName)
            dataset = tFile[tFile['GenreCode'] == gCode][['Gender','Age', 'CurrentTime', 'PositiveDif']]
            nameset = tFile[tFile['GenreCode'] == gCode][['Title']]
            dataset = dataset.values.tolist()
            nameset = nameset.values.tolist()
            for i in dataset:
                genreTS.append(i)
            for j in range(len(nameset)):
                for k in range(len(nameset[j])):
                    self.nameSet.append(nameset[j][k])
    
        # SVM ���� �� ����
            # �� �� ���� �� 0
            # �ڵ� ���� �� 1
        mName = self.SVM(genreTS,self.testSet, 0)
        return mName
        
        
    def GenieTagFinder(self, season, weather, time):
        tag = []
        tag.append(season + time)
        tag.append(season + weather)
        tag.append(weather + time)
        
        return tag
     
    def CSWithGenie(self, mName, tag):
        # URL �ε�             
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'TotalList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # �Էµ� �� �� ���� ��Ÿ ������ �˻�
        tFile = pd.read_csv(url)
        tFileC = tFile[tFile['Title'] == mName][['Title', 'SignalMagnitude', 'SpectralCentroid',
                                             'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
        cData = dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                 tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                 tFileC.MFCC, tFileC.Tempo,
                                                                 tFileC.Pitch, tFileC.Intensity)])
        # ���� �±׿� ���� ��Ÿ ������ ���� ����
        pData = {}
        
        for t in tag:
            # URL �ε�             
            url = self.S3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'csvdb',
                    'Key': 'Genie/' + t
                }
            )
            temp = url.split('?')
            url = temp[0]+'.csv'

            tFile = pd.read_csv(url)
            tFileC = tFile[['Title', 'SignalMagnitude', 'SpectralCentroid','SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
            pData.update(dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                     tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                     tFileC.MFCC, tFileC.Tempo,
                                                                     tFileC.Pitch, tFileC.Intensity)]))
        
        # Cosine Similarity ���
        cDic = {} # { : {doc : cosine score}}
        
        for i in cData.keys():
            subDic = {}
            cDataArray = np.array(cData[i])
            cDataVector = cDataArray.reshape(1, -1)
            
            for j in pData.keys():
                pDataArray = np.array(pData[j])
                pDataVector = pDataArray.reshape(1, -1)
                CS = cosine_similarity(cDataVector, pDataVector)
                subDic[j] = CS
            cDic[i] = subDic
        
        # �� ���� �� Cosine Score�� ���� Doc ������ ����
        # { song1 : [song2 : cosine score] }
        
        sortedDic = {}
        
        for i in cDic.keys():
            sortedScore = sorted(cDic[i].items(),
                                 key = operator.itemgetter(1),
                                 reverse = True)
            sortList = []
            
            for j in range(len(sortedScore)):
                song = sortedScore[j][0]
                score = str(float(sortedScore[j][1]))
                eachList = [song, score]
                sortList.append(eachList)
            
            sortedDic[i] = sortList
        
        # Top 5 ����
        # { song1 : [ Top1, Top2, Top3, Top4, Top5 ] }

        Top5 = {}
        
        for i in sortedDic.keys():
            songList = []
            for j in range(0, 5):
                songList.append(sortedDic[i][j][0])
            
            Top5[i] = songList

        return Top5.values()[0]
    # Ʈ���̴� �� ����
    def LoadTrainSet(self, trainingSet=[], codeSet=[]):

        # ���� ��� �� Ʈ���̴� ������ ��
        testCnt = len(self.testSet)

        ageSum = 0
        
        for i in range(testCnt):
            ageSum = ageSum + int(self.testSet[i][1])
            
        avgAge = round(float(ageSum)/float(testCnt))
        
        dataset = self.sample[(self.sample['Age'] == avgAge)][['Gender','Age','CurrentTime','PositiveDif','GenreCode']]
        dataset = dataset.values.tolist()
        
        for x in range(1, len(dataset)):
            for y in range(5):
                # ���� �� ���ڷ� ����
                if(y == 0):
                    dataset[x][y] = int(dataset[x][y])
                elif(y == 1):
                    dataset[x][y] = int(dataset[x][y])
                elif(y == 2):
                    dataset[x][y] = float(dataset[x][y])
                elif(y == 3):
                    dataset[x][y] = float(dataset[x][y])
                else:
                    codeSet.append(int(dataset[x][y]))              
            dataset[x].pop(4)
            # �迭 ����
            trainingSet.append(dataset[x])
            
    # SVM �Լ�            
    def SVM(self, trainingSet, tst, div):
        testSet = np.array(tst)
        
        if(div == 0):
            indexSet = self.nameSet
        else:
            indexSet = self.codeSet
        SVM = svm.SVC()

        predict = SVM.fit(trainingSet, indexSet).predict(testSet)
        
        """
                �����ؾ���
        """
        # ���� �󵵼� ���� ��ü ����
        cnt = Counter(predict)
        gCode = cnt.most_common(1)[0][0]
        
        """
                �����ؾ���
        """
        # �ڵ带 ���ϴ� ��� ��õ�� �ڵ带 �帣 ���絵�� ���� �ڵ� ������ ��ȯ
        if(div == 1):
            gCode = self.CodeConverter(int(gCode))

        return gCode
    
    # �帣�ڵ带 ��Ʈ�� �°� ��Ʈ �ڵ�� ��ȯ
    def CodeConverter(self, gCode):
        # �ڵ忡 �ش��ϴ� ��Ʈ �ڵ� ��ȯ, �������� ������ 'Unknown' ��ȯ
        return {116:0, 13:3, 131:2, 14:10, 17:6, 24:1, 3:7, 35:8, 7:9, 8:11, 80:4, 99:5}.get(gCode, 'Unknown')
    
    def InverseCodeConverter(self, gName):
        return {'Ballad':116, 'Pop':13, 'Indie':131, 'R&B':14, 'Rock':17, 'Soundtrack':24, 'Dance':3, 'Electronic':35, 'HipHop':7, 'Jazz':8, 'Folk':80, 'Trot':99}.get(gName, 'Unknown')
    
    # �帣�ڵ带 ��Ʈ�� �°� ��Ʈ �ڵ�� ��ȯ
    def GenreNameFinder(self, gCode):
        # �ڵ忡 �ش��ϴ� ��Ʈ �ڵ� ��ȯ, �������� ������ 'Unknown' ��ȯ
        return {0:'Ballad', 1:'Soundtrack', 2:'Indie', 3:'Pop', 4:'Folk', 5:'Trot', 6:'Rock', 7:'Dance', 8:'Electronic', 9:'HipHop', 10:'R&B', 11:'Jazz'}.get(gCode, 'Unknown')
    
    # �帣 ���赵�� ���� �̿��� �帣 ����
    def GenreNeighborFinder(self, gCode):
        gNeighbor = []
        h = self.GenreNameFinder(gCode)
        gNeighbor.append(h)
        for i in range(len(self.gChart)):
            if(self.gChart[gCode][i] == 1):
                j = self.GenreNameFinder(i)
                gNeighbor.append(j)
        
        return gNeighbor
