'''
Created on 2017. 7. 25.

@author: SJ
'''
import boto3
from botocore.client import Config
from PyQt4.QtCore import QThread
from CaptureNUpload import CapNUp

class Upload(QThread):
    upFileNum = 0
    
    def __init__(self):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
 
    def __del__(self):
        self.wait()
    
    def stop(self):
        print("END")
        self.tFlag = True   
            
    def run(self):
        while(True):
            if self.upFileNum < CapNUp.fileNum:
                print("UPLOADING...")
                self.upFileNum = self.upFileNum + 1
                path = str('uploader/{0}.jpg'.format(self.upFileNum))
                data = open('uploader/{0}.jpg'.format(self.upFileNum),'rb')
                self.S3.put_object(ACL = 'public-read', Bucket = 'dgutest01', Key = str(self.upFileNum)+'.jpg', Body = data)
                print "fileNum :", self.upFileNum
                data.close()
                #os.remove(path)
              #  if (self.fileNum == self.cLimit):
               #     self.mCounter = self.mCounter + 1
            else:
                pass
