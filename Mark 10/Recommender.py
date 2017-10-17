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
    # 쓰레드 정지 플래그
    tFlag = False
    def __init__(self):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        # 트레이닝 셋
        self.trainingSet = []
        # 장르 코드가 들어있는 리스트
        self.codeSet = []
        # 곡 명이 들어있는 리스트
        self.nameSet  = []
        self.sample = pd.read_csv('ExpList.csv')

        # 장르 관계도
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
                # 이웃하는 장르까지 들어가는 리스트
                gNeighbors = []

                # 테스트 셋 정의
                self.testSet = Ui_MainWindow.testSet
                        
                # 머신러닝 변수 로드
                self.season = Ui_MainWindow.season
                self.weather = Ui_MainWindow.weather
                self.daytime = Ui_MainWindow.daytime
        
                # 트레이닝 셋, 인덱스 셋 생성
                self.LoadTrainSet(self.trainingSet, self.codeSet)
                self.trainingSet = np.array(self.trainingSet)
                
                # SVM 으로 장르 추출
                    # 곡 명 구할 때 0
                    # 코드 구할 때 1
                gCode = self.SVM(self.trainingSet,self.testSet, 1)
                
                # 장르 관계도에 의해 이웃하는 장르 추출
                gNeighbors = self.GenreNeighborFinder(gCode)
                
                # 추출된 장르를 기반으로한 1곡 추천
                mName = self.SVMInGenres(gNeighbors)
                # 현재 계절, 날씨, 시간을 기반으로 지니 태그 생성
                tag = self.GenieTagFinder(self.season, self.weather, self.daytime[1])
                # 지니 태그를 기반으로 추천된 1곡으로부터 Top5 추천
                Top5 = self.CSWithGenie(mName, tag)
                # 추천된 Top5를 기반으로 실 플레이 리스트에서 추천
                pList = self.PlaylistGenerator(Top5)
                toUI = []
                print "추 천 완 료"
                for i in range(len(pList.values())):
                    for j in range(len(pList.values()[i])):
                        toUI.append(pList.values()[i][j].decode('cp949'))
                
                Ui_MainWindow.pList = toUI
                Ui_MainWindow.rFlag = False
                Ui_MainWindow.aFlag = True
           
    def PlaylistGenerator(self, Top5):
        cData = {}
        # Top 5 곡에 대한 정보 로드
        # URL 생성            
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'TotalGenieList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # 입력된 곡 명에 대한 메타 데이터 검색
        tFile = pd.read_csv(url)
        
        for mName in Top5:
            tFileC = tFile[tFile['Title'] == mName][['Title', 'SignalMagnitude', 'SpectralCentroid',
                                                     'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
            cData.update(dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                     tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                     tFileC.MFCC, tFileC.Tempo,
                                                                     tFileC.Pitch, tFileC.Intensity)]))        
        # 실제 플레이할 음악 메타데이터 로드            
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'PlayList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # 입력된 곡 명에 대한 메타 데이터 검색
        tFile = pd.read_csv(url)
        tFileC = tFile[['Title', 'SignalMagnitude', 'SpectralCentroid',
                        'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
        pData = dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                 tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                 tFileC.MFCC, tFileC.Tempo,
                                                                 tFileC.Pitch, tFileC.Intensity)])
        # Cosine Similarity 계산
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
        
        # 각 음악 별 Cosine Score가 상위 Doc 순으로 나열
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
        
        # Top 5 선곡
        # { song1 : [ Top1, Top2, Top3, Top4, Top5 ] }
        
        Top5 = {}
        
        for i in sortedDic.keys():
            songList = []
            for j in range(0, 5):
                songList.append(sortedDic[i][j][0])
            
            Top5[i] = songList
        
        return Top5
                   
    def SVMInGenres(self, gNeighbors):
        # 선택된 장르와 이에 연관된 장르에 관한 데이터만을 가지는 트레이닝 셋
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
    
        # 입력된 곡 명에 대한 메타 데이터 검색
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
    
        # SVM 으로 곡 추출
            # 곡 명 구할 때 0
            # 코드 구할 때 1
        mName = self.SVM(genreTS,self.testSet, 0)
        return mName
        
        
    def GenieTagFinder(self, season, weather, time):
        tag = []
        tag.append(season + time)
        tag.append(season + weather)
        tag.append(weather + time)
        
        return tag
     
    def CSWithGenie(self, mName, tag):
        # URL 로드             
        url = self.S3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'csvdb',
                'Key': 'TotalList'
            }
        )
        temp = url.split('?')
        url = temp[0]+'.csv'
    
        # 입력된 곡 명에 대한 메타 데이터 검색
        tFile = pd.read_csv(url)
        tFileC = tFile[tFile['Title'] == mName][['Title', 'SignalMagnitude', 'SpectralCentroid',
                                             'SpectralFlux', 'MFCC', 'Tempo', 'Pitch', 'Intensity']]
        cData = dict([(i,[a,b,c,d,e,f,g]) for i,a,b,c,d,e,f,g in zip(tFileC.Title, tFileC.SignalMagnitude,
                                                                 tFileC.SpectralCentroid, tFileC.SpectralFlux,
                                                                 tFileC.MFCC, tFileC.Tempo,
                                                                 tFileC.Pitch, tFileC.Intensity)])
        # 현재 태그에 대한 메타 데이터 정보 생성
        pData = {}
        
        for t in tag:
            # URL 로드             
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
        
        # Cosine Similarity 계산
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
        
        # 각 음악 별 Cosine Score가 상위 Doc 순으로 나열
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
        
        # Top 5 선곡
        # { song1 : [ Top1, Top2, Top3, Top4, Top5 ] }

        Top5 = {}
        
        for i in sortedDic.keys():
            songList = []
            for j in range(0, 5):
                songList.append(sortedDic[i][j][0])
            
            Top5[i] = songList

        return Top5.values()[0]
    # 트레이닝 셋 생성
    def LoadTrainSet(self, trainingSet=[], codeSet=[]):

        # 나이 평균 및 트레이닝 데이터 셋
        testCnt = len(self.testSet)

        ageSum = 0
        
        for i in range(testCnt):
            ageSum = ageSum + int(self.testSet[i][1])
            
        avgAge = round(float(ageSum)/float(testCnt))
        
        dataset = self.sample[(self.sample['Age'] == avgAge)][['Gender','Age','CurrentTime','PositiveDif','GenreCode']]
        dataset = dataset.values.tolist()
        
        for x in range(1, len(dataset)):
            for y in range(5):
                # 숫자 값 숫자로 설정
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
            # 배열 삽입
            trainingSet.append(dataset[x])
            
    # SVM 함수            
    def SVM(self, trainingSet, tst, div):
        testSet = np.array(tst)
        
        if(div == 0):
            indexSet = self.nameSet
        else:
            indexSet = self.codeSet
        SVM = svm.SVC()

        predict = SVM.fit(trainingSet, indexSet).predict(testSet)
        
        """
                개선해야함
        """
        # 가장 빈도수 높은 개체 선택
        cnt = Counter(predict)
        gCode = cnt.most_common(1)[0][0]
        
        """
                개선해야함
        """
        # 코드를 구하는 경우 추천된 코드를 장르 유사도를 위한 코드 값으로 변환
        if(div == 1):
            gCode = self.CodeConverter(int(gCode))

        return gCode
    
    # 장르코드를 차트에 맞게 차트 코드로 변환
    def CodeConverter(self, gCode):
        # 코드에 해당하는 차트 코드 반환, 존재하지 않으면 'Unknown' 반환
        return {116:0, 13:3, 131:2, 14:10, 17:6, 24:1, 3:7, 35:8, 7:9, 8:11, 80:4, 99:5}.get(gCode, 'Unknown')
    
    def InverseCodeConverter(self, gName):
        return {'Ballad':116, 'Pop':13, 'Indie':131, 'R&B':14, 'Rock':17, 'Soundtrack':24, 'Dance':3, 'Electronic':35, 'HipHop':7, 'Jazz':8, 'Folk':80, 'Trot':99}.get(gName, 'Unknown')
    
    # 장르코드를 차트에 맞게 차트 코드로 변환
    def GenreNameFinder(self, gCode):
        # 코드에 해당하는 차트 코드 반환, 존재하지 않으면 'Unknown' 반환
        return {0:'Ballad', 1:'Soundtrack', 2:'Indie', 3:'Pop', 4:'Folk', 5:'Trot', 6:'Rock', 7:'Dance', 8:'Electronic', 9:'HipHop', 10:'R&B', 11:'Jazz'}.get(gCode, 'Unknown')
    
    # 장르 관계도에 의한 이웃한 장르 추출
    def GenreNeighborFinder(self, gCode):
        gNeighbor = []
        h = self.GenreNameFinder(gCode)
        gNeighbor.append(h)
        for i in range(len(self.gChart)):
            if(self.gChart[gCode][i] == 1):
                j = self.GenreNameFinder(i)
                gNeighbor.append(j)
        
        return gNeighbor
