# -*- coding: utf-8 -*-

'''
Created on 2017. 6. 7.

@author: DJ
'''
import boto3, httplib, urllib, time, os, gc, urllib2, _csv

from botocore.client import Config
from pyowm import OWM
from PyQt4.QtCore import QThread
from UI import Ui_MainWindow



class DownNAnalyze(QThread):
    
    rowSignal = 0
    tFlag = False
    wFlag = False
    bSong = ''
    song = []
    
    ePosAge = []
    eNegAge = []
    
    def __init__(self, aBucket, Key):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.aBucket = aBucket
        self.fileNum = 0
        self.now = time.localtime()
        self.today = str(self.now.tm_year)+"."+str(self.now.tm_mon)+"."+str(self.now.tm_mday)
        self.mArray = []
        self.mLength = 0
        self.fCounter = 0
        self.Emotion_key = Key
        self.OWM_key = '1f5aaef161771efd6c64b08553f03a31'
        self.url = ""
        self.fName = ""
        self.gender = 0
        self.age = 2
        self.ePos = 0.1
        self.eNeg = 0
        self.season = 'Summer'
        self.weather = 'Sunny'
        self.daytime = []
        self.eList = []
        self.eTemp = []
        self.tPos = 1
        self.tNeg = 0
        ################

        self.testSet = []
        
    def __del__(self):
        self.wait()

    def stop(self):
        self.tFlag = True
        
    def run(self):
        while(self.tFlag == False):
            if(self.wFlag == True):
                self.mArray = Ui_MainWindow.mArray
                #self.mLength = len(self.mArray)
                self.fCounter = Ui_MainWindow.cIndex
                #self.totalIndex = len(self.total)
                self.totalIndex = self.rowSignal
                print 'total: ', self.totalIndex
                print 'fCounter ', self.fCounter
                #for i in range(self.fCounter, self.mLength):
                i = self.fCounter
                fName = self.mArray[i]
                self.fName = unicode(fName)
                slash = self.fName.rfind('/')
                mp3 = self.fName.rfind('.mp3')
                self.fName = self.fName[slash+1:mp3]
                    
                self.testSet = []
                for j in range(0, 40):
                    
                    try:
                       
                        self.fileNum = j + 1
                        
                        key = unicode(self.today) + u'/' + self.fName + u'/' + unicode(self.fileNum)       
                        url = self.S3.generate_presigned_url(
                            ClientMethod='get_object',
                            Params={
                                'Bucket': self.aBucket,
                                'Key': key
                            }
                        )
                        
                        temp = url.split('?')
                        url = temp[0]+'.jpg'
                        key = unicode(self.today + '/' + self.fName + '/' + '{0}.jpg'.format(self.fileNum))
                        path = 'downloader/{0}.jpg'.format(self.fileNum)
                        self.S3.download_file(self.aBucket, key, path)
                        print "Download OK"
                   
                        try:
                            pos = 0
                            neg = 0         
                            self.gender, self.age, self.eList = self.RekognitionAPI(key, url)
                            self.gender, self.age, self.season, self.weather, self.daytime, self.eNeg, self.ePos = self.PreProcessing(self.gender, self.age, self.eList)
                            self.testSet.append([self.gender, self.age, self.daytime[0], self.ePos])
                            
                            for i in range(len(self.eList)):
                                if i < 5:
                                    neg = neg + self.eList[i]
                                else:
                                    pos = pos + self.eList[i]
                                    
                            self.eTemp.append([self.age, pos, neg])

                        except Exception as e:
                            print "ERROR"
                            self.S3.delete_object(Bucket = self.aBucket, Key = key)
                        
                     
                        os.remove(path)
                        
                    except Exception as e:
                        print str(e)
                        break
                
                oneE = 0
                oneN = 0
                twoE = 0
                twoN = 0
                threeE = 0                  
                threeN = 0
                fourE = 0
                fourN = 0
                fiveE = 0
                fiveN = 0                      
                co = 0
                ct = 0
                cth = 0
                cf = 0
                cfi = 0
                
                for i in range(len(self.eTemp)):
                    if self.eTemp[i][0] == 1:
                        oneE = oneE + self.eTemp[i][1]
                        oneN = oneN + self.eTemp[i][2]
                        co = co + 1
                    elif self.eTemp[i][0] == 2:
                        twoE = twoE + self.eTemp[i][1]
                        twoN = twoN + self.eTemp[i][2]
                        ct = ct + 1
                    elif self.eTemp[i][0] == 3:
                        threeE = threeE + self.eTemp[i][1]
                        threeN = threeN + self.eTemp[i][2]
                        cth = cth + 1
                    elif self.eTemp[i][0] == 4:
                        fourE = fourE + self.eTemp[i][1]
                        fourN = fourN + self.eTemp[i][2]
                        cf = cf + 1
                    else:
                        fiveE = fiveE + self.eTemp[i][1]
                        fiveN = fiveN + self.eTemp[i][2]
                        cfi = cfi + 1
                        
                if co == 0:
                    co = 1
                elif ct == 0:
                    ct = 1
                elif cth == 0:
                    cth = 1
                elif cf == 0:
                    cf = 1
                elif cfi == 0:
                    cfi = 1
                    
                if oneE == 0 or co == 0:
                    po = 0
                else:
                    po = oneE/co*100
                    
                if twoE == 0 or ct == 0:
                    pt = 0
                else:
                    pt = twoE/ct*100
                    
                if threeE == 0 or cth == 0:
                    pth = 0
                else:
                    pth = threeE/cth*100
                    
                if fourE == 0 or cf == 0:
                    pf = 0
                else:
                    pf = fourE/cf*100
                    
                if fiveE == 0 or cfi == 0:
                    pfi = 0
                else:
                    pfi = fiveE/cfi*100
                ##########################    
                if oneN == 0 or co == 0:
                    no = 0
                else:
                    no = oneN/co*100
                    
                if twoN == 0 or ct == 0:
                    nt = 0
                else:
                    nt = twoN/ct*100
                    
                if threeN == 0 or cth == 0:
                    nth = 0
                else:
                    nth = threeN/cth*100
                    
                if fourN == 0 or cf == 0:
                    nf = 0
                else:
                    nf = fourN/cf*100
                    
                if fiveN == 0 or cfi == 0:
                    nfi = 0
                else:
                    nfi = fiveN/cfi*100
                    
                self.ePosAge = [po, pt, pth, pf, pfi]
                self.eNegAge = [no, nt, nth, nf, nfi]
                
                tE = float(oneE + twoE + threeE + fourE + fiveE)/float(co + ct + cth + cf + cfi)
                tN = float(oneN + twoN + threeN + fourN + fiveN)/float(co + ct + cth + cf + cfi)
                
                Ui_MainWindow.ePosList.append(tE)
                Ui_MainWindow.eNegList.append(tN)
                
                Ui_MainWindow.ePosAgeList = self.ePosAge
                Ui_MainWindow.eNegAgeList = self.eNegAge
                                        
                print "total index : ", self.totalIndex
                index = self.totalIndex - self.fCounter
                print "cal index : ", index - 1
                
                if((index < 4) and (self.testSet != [])):
                    Ui_MainWindow.testSet = self.testSet
                    Ui_MainWindow.season = self.season
                    Ui_MainWindow.weather = self.weather
                    Ui_MainWindow.daytime = self.daytime
                    Ui_MainWindow.rFlag = True
                 
                else:#((index >= 4)): #and (float(self.ePosDiff[1]) - float(self.ePosDiff[0]) < 0) and (self.fCounter > 1)):
                    print'Checker'
                    cList = []
                    self.bSong = self.mArray[self.fCounter - 1]
                    self.bSong = unicode(self.bSong)
                    slash = self.bSong.rfind('/')
                    mp3 = self.bSong.rfind('.mp3')
                    self.bSong = self.bSong[slash+1:mp3]
                    for j in range(self.fCounter, self.totalIndex-1):
                        song = unicode(Ui_MainWindow.sources[j].url().toString())
                        self.song = unicode(song)
                        slash = self.song.rfind('/')
                        mp3 = self.song.rfind('.mp3')
                        self.song = self.song[slash+1:mp3]
                        cList.append(self.song)
                        
                    
                    Ui_MainWindow.xList = self.MObserver(cList, self.bSong)
                    print "UI : ", Ui_MainWindow.xList
                    Ui_MainWindow.dFlag = True
                self.totalIndex = 0
                
                key = ''
                #self.fCounter = self.fCounter + 1
                self.wFlag = False
                #gc.collect()     
                          
    def MObserver(self, curList, befSong):
        # 입력 리스트
        xList =[]
        
        # 대상 곡 명
        self.xSong = ''
        
        # 삭제할 음악 리스트
        xNList =[]
    
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
    
        # 다음 재생될 곡부터 마지막까지 곡 리스트
        xList = curList
        # 대상일 될 이전 곡 명
        # 이전 음악의 장르 파악, 삭제할 장르
        self.xSong = befSong
        xGenre = 0
        tG =[]
        for i in rdr:
            for j in xList:
                if i[0] == j.encode('cp949'):
                    tG.append([i[0],i[8]])
        
        for i in rdr:
            if i[0] == self.xSong:
                xGenre = i[8]
        
        for i in range(len(tG)):
            if(tG[i][1] == xGenre):
                tG[i].pop()
                
        for i in range(len(tG)):
            xNList.append(tG[i][0].decode('cp949'))
                
        return xNList
        
            
    def RekognitionAPI(self, key, url, attributes=['ALL'], region="us-east-1"):
        Rekog = boto3.client("rekognition", region)
    
        eResponse = Rekog.detect_faces(
            Image={
                "S3Object": {
                    "Bucket": self.aBucket,
                    "Name": key,
                }
            },
            Attributes=attributes,
        )
    
        for result in eResponse['FaceDetails']:

            if result['Sunglasses']['Value'] ==  True or result['Confidence'] < 90 :
                break
            else:
          
                eGender = str(result['Gender']['Value'])
                eAgeL = int(result['AgeRange']['Low'])
                eAgeH = int(result['AgeRange']['High'])
       
                if eAgeL < 18:
         
                    eAge = eAgeH
                else:
            
                    eAge = (eAgeL+eAgeH)/2
        eList = self.EmotionAPI(url)
        
        self.S3.delete_object(Bucket = self.aBucket, Key = key)
        
        
        if eList != 0:
            return eGender, eAge, eList

    def EmotionAPI(self, url):
        
        headers = {
    
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.Emotion_key,
        }
        
        params = urllib.urlencode({
        })
        
  
        body = "{ 'url': '"+url+"' }"
        
    
        try:
   
            conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()     
      
            a_idx = data.find("anger")
            c_idx = data.find("contempt")
            d_idx = data.find("disgust")
            f_idx = data.find("fear")
            h_idx = data.find("happiness")
            n_idx = data.find("neutral")
            sad_idx = data.find("sadness")
            sp_idx = data.find("surprise")
            end_idx = data.find("}}]")
            

            anger= float(data[a_idx+7:c_idx-2])
            contempt = float(data[c_idx+10:d_idx-2])
            disgust = float(data[d_idx+9:f_idx-2])
            fear = float(data[f_idx+6:h_idx-2])
            happiness = float(data[h_idx+11:n_idx-2])
            sadness = float(data[sad_idx+9:sp_idx-2])
            surprise = float(data[sp_idx+10:end_idx])
            
      
            eList = [anger, contempt, disgust, fear, sadness, happiness, surprise]
            return eList

        except Exception as e:
            return 0


    def PreProcessing(self, eGender, eAge, eList):
   
        if (eGender == 'Male'):
            gender = 0
        else:
            gender = 1
            
   
        if (eAge < 20):
            age = 1
        elif (eAge in range(20, 30)):
            age = 2
        elif (eAge in range(30, 40)):
            age = 3
        elif (eAge in range(40, 50)):
            age = 4
        else:
            age = 5
            

        eNeg = eList[0] + eList[1] + eList[2] + eList[3] + eList[4]
        ePos = eList[5] + eList[6]
        
        ePos = self.tPos - ePos
        eNeg = self.tNeg - eNeg 
        
   
        month = int(time.localtime().tm_mon)
        if (month in range(3, 6)):
            #season = 0.25
            season = 'Spring'
        elif (month in range(6, 10)):
            #season = 0.5
            season = 'Summer'
        elif (month in range(10, 12)):
            #season = 0.75
            season = 'Autumn'
        else:
            #season = 1
            season = 'Winter'
            

        ctime = int(time.localtime().tm_hour)
        day = []
        if (ctime in range(6, 12)):
            day.append(0.3)
            day.append('Morning')
        elif (ctime in range(12, 18)):
            day.append(0.6)
            day.append('Afternoon')
        else:
            day.append(0.9)
            day.append('Night')
        

        owm = OWM(self.OWM_key)
        obs = owm.weather_at_coords(37.566553, 126.977909)
        w = obs.get_weather()
        code = str(w.get_weather_code())
        wCode = int(code[0:1])
        if (wCode == 2):
            #wtr = 0
            wtr = 'Rain'
        elif (wCode == 3):
            #wtr = 1
            wtr = 'Rain'
        elif (wCode == 5):
            #wtr = 2
            wtr = 'Rain'
        elif (wCode == 6):
            #wtr = 3
            wtr = 'Snow'
        elif (wCode == 7):
            #wtr = 4
            wtr = 'Cloudy'
        elif (wCode == 8):
            #wtr = 5
            wtr = 'Sunny'
        else:
            #wtr = 6
            wtr = 'Rain'
        
        return gender, age, season, wtr, day, eNeg, ePos
    