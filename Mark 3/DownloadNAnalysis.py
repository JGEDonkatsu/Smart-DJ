# coding=cp949
'''
Created on 2017. 6. 7.

@author: DJ
'''
import boto3
import httplib, urllib
import xlwt
import os, time

from botocore.client import Config
from PyQt4.Qt import ws

class DownNAnalyze:
    
    def __init__(self):
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.fileNum = 0
        self.nStackNum = 0
        self.rNum = 1
        self.url = ""
        self.aBucket = ""
        self.mName = ""
        self.now = time.localtime()
        self.today = str(self.now.tm_year)+"."+str(self.now.tm_mon)+"."+str(self.now.tm_mday)
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


    def Stop(self):
        print("END")
        self.wb.save('uploader/'+str(self.today)+'.xls')
        dPath = str('uploader/'+str(self.today)+'.xls')
        wPath = 'uploader/Weather.xls'
        data = open('uploader/'+str(self.today)+'.xls','rb')
        self.S3.put_object(ACL = 'public-read', Bucket = 'dgutest01', Key = self.today+'/['+self.today+'] Result For {0} Songs.xls'.format(self.nStackNum), Body = data)
        data.close()
        os.remove(dPath)
        try:
            os.remove(wPath)
        except WindowsError:
            pass
        
        
    def Start(self, aBucket, mName):
        self.mName = mName
        self.aBucket = aBucket
        while(True):
            self.fileNum = self.fileNum + 1
            self.mName = unicode(self.mName)
            key = str(self.today) + '/' + self.mName + '/' + str(self.fileNum)
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
            key = str(self.today) + '/' + self.mName + '/' + '{0}.jpg'.format(self.fileNum)
            path = 'downloader/{0}.jpg'.format(self.fileNum)
            
            try: 
                self.S3.download_file(self.aBucket, key, path)
                self.RekognitionAPI(self.mName, key, url)
                os.remove(path)
            
            except Exception as e:
                print("ERROR")
                self.fileNum = 0
                break

        self.Stop()

        
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
                eAge = (eAgeL+eAgeH)/2
                eList = self.EmotionAPI(url)

                self.Excelization(fName, eGender, eAge, eList)
        
        #self.S3.delete_object(Bucket = self.aBucket, Key = key)
        
    def EmotionAPI(self, url):
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        
        headers = {
            # Key Input Area
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': 'd114f2dad42e4fcb9483b9a22de4ff87',
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
                #print [eList]
                return eList

        except:
            pass


    def Excelization(self, fName, eGen, eAge, eList):
        print eGen, eAge, eList
        
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
        
        self.rNum = self.rNum + 1
        self.nStackNum = self.nStackNum + 1

        
