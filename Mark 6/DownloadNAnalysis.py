# coding=cp949
'''
Created on 2017. 6. 7.

@author: DJ
'''
# -*- coding: utf-8 -*-
import boto3 
import httplib, urllib
import xlwt
import os, time

from botocore.client import Config
from PyQt4.QtCore import QThread
from UI import Ui_MainWindow

from pyowm import OWM

class DownNAnalyze(QThread):
    tFlag = False
    API_key = '1f5aaef161771efd6c64b08553f03a31'
    
    def __init__(self, aBucket, Key):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.fileNum = 0
        self.mLength = 0
        self.mArray = []
        self.aKey = Key
        self.fName = ""
        self.fCounter = 0
        self.rNum = 1
        self.url = ""
        self.k = 1
        self.aBucket = aBucket
        self.today = str(time.localtime().tm_year)+"."+str(time.localtime().tm_mon)+"."+str(time.localtime().tm_mday)
        
        self.wb = xlwt.Workbook(encoding="utf-8")
        self.ws = self.wb.add_sheet(self.today)
        self.ws.write(0,1,"Gender")
        self.ws.write(0,2,"Age")
        self.ws.write(0,3,"Anger")
        self.ws.write(0,4,"Contempt")
        self.ws.write(0,5,"Disgust")
        self.ws.write(0,6,"Fear")
        self.ws.write(0,7,"Happiness")
        self.ws.write(0,8,"Neutral")
        self.ws.write(0,9,"Sadness")
        self.ws.write(0,10,"Surprise")
        self.ws.write(0,11,"WeatherStatus")
        self.ws.write(0,12,"Temperature")
        self.ws.write(0,13,"Humidity")
        self.ws.write(0,14,"CurrnetTime")
        
        
    def __del__(self):
        self.wait()


    def stop(self):
        print("END")
        if self.mLength != 0:
            self.wb.save('uploader/'+str(self.today)+'.xls')
            dPath = str('uploader/'+str(self.today)+'.xls')
            data = open('uploader/'+str(self.today)+'.xls','rb')
            if Ui_MainWindow.LastFlag == True:
                self.mLength = self.mLength - 1
            self.S3.put_object(ACL = 'public-read', Bucket = self.aBucket, Key = self.today+'/['+self.today+'2:35] Result For {0} Songs.xls'.format(self.mLength), Body = data)
            data.close()
            os.remove(dPath)

        self.tFlag = True
        
        
    def run(self):
        while(self.tFlag == False):
            self.mArray = Ui_MainWindow.mArray
            self.mLength = len(self.mArray)       
            for i in range(self.fCounter, len(self.mArray)):
                fName = self.mArray[i]
                self.fName = unicode(fName)
                slash = self.fName.rfind('/')
                wmv = self.fName.rfind('.wmv')
                self.fName = self.fName[slash+1:wmv]
                time.sleep(30)
                for j in range(0, 50):
                    try:
                        self.fileNum = j
                        self.fileNum = self.fileNum + 1
                        key = str(self.today) + '/' + self.fName + '/' + str(self.fileNum)
                        print key
                    
                        url = self.S3.generate_presigned_url(
                            ClientMethod='get_object',
                            Params={
                                'Bucket': self.aBucket,
                                'Key': key
                            }
                        )
                        
                        temp = url.split('?')
                        url = temp[0]+'.jpg'
                        key = str(self.today) + '/' + self.fName + '/' + '{0}.jpg'.format(self.fileNum)
                        path = 'downloader/{0}.jpg'.format(self.fileNum)
                        self.S3.download_file(self.aBucket, key, path)
                        
                        try:
                            self.RekognitionAPI(self.fName, key, url)
                            os.remove(path)
                            print self.aBucket,"SUCCESS"
                        except Exception as e:
                            self.S3.delete_object(Bucket = self.aBucket, Key = key)
                            print self.aBucket, "RECOGNITION UNAVAILABLE"
                    except Exception as e:
                        print self.aBucket, "DOWNLOAD UNAVAILABLE"
                        break
                        


                if (self.fCounter == len(self.mArray)):
                    break
                else:
                    self.fCounter = self.fCounter + 1
                key = str(self.today) + '/' + self.fName
                self.S3.delete_object(Bucket = self.aBucket, Key = key)

                
    def RekognitionAPI(self, fName, key, url, attributes=['ALL'], region="us-east-1"):
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
                eGender = result['Gender']['Value']
                eAgeL = result['AgeRange']['Low']
                eAgeH = result['AgeRange']['High']
                if eAgeL < 18:
                    eAge = eAgeH
                else:
                    eAge = (eAgeL+eAgeH)/2
                eList = self.EmotionAPI(url)
                if eList != 0:
                    self.Excelization(fName, eGender, eAge, eList)
        
        self.S3.delete_object(Bucket = self.aBucket, Key = key)
        
        
    def EmotionAPI(self, url):
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        
        headers = {
            # Key Input Area
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.aKey,
        }
        
        params = urllib.urlencode({
        })
        
        # URL Input Area
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
            
            anger= data[a_idx+7:c_idx-2]
            contempt = data[c_idx+10:d_idx-2] 
            disgust = data[d_idx+9:f_idx-2]
            fear = data[f_idx+6:h_idx-2]
            happiness = data[h_idx+11:n_idx-2]
            neutral = data[n_idx+9:sad_idx-2]
            sadness = data[sad_idx+9:sp_idx-2]
            surprise = data[sp_idx+10:end_idx]
            
            # After Manipulation Process
            eList = [anger, contempt, disgust, fear, happiness, neutral, sadness, surprise]
            if neutral != "":
                return eList

        except:
            print "Emotion API Fail"
            return 0


    def Excelization(self, fName, eGen, eAge, eList):
        print eGen, eAge, eList
        
        ctime = str(time.localtime().tm_hour)+":"+str(time.localtime().tm_min)
        owm = OWM(self.API_key)
        obs = owm.weather_at_coords(37.566553, 126.977909)
        w = obs.get_weather()
        status = w.get_status()
        temp =  w.get_temperature(unit='celsius')['temp']
        humidity = w.get_humidity()
        
        self.ws.write(self.rNum, 0, fName)
        self.ws.write(self.rNum, 1, eGen)
        self.ws.write(self.rNum, 2, eAge)
        self.ws.write(self.rNum, 3, eList[0])
        self.ws.write(self.rNum, 4, eList[1])
        self.ws.write(self.rNum, 5, eList[2])
        self.ws.write(self.rNum, 6, eList[3])
        self.ws.write(self.rNum, 7, eList[4])
        self.ws.write(self.rNum, 8, eList[5])
        self.ws.write(self.rNum, 9, eList[6])
        self.ws.write(self.rNum, 10, eList[7])
        self.ws.write(self.rNum, 11, status)
        self.ws.write(self.rNum, 12, temp)
        self.ws.write(self.rNum, 13, humidity)
        self.ws.write(self.rNum, 14, ctime)
        
        self.rNum = self.rNum + 1

        
