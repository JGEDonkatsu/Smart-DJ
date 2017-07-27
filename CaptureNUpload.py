'''
Created on 2017. 5. 12.
@author: DJ, SJ
'''
# coding=cp949
import cv2
import boto3
import os, time
from botocore.client import Config
from PyQt4.QtCore import QThread
from common import clock, draw_str

class CapNUp(QThread):
    tFlag = False
    cCounter = 0
    mCounter = 1
    counter = 0 #upload
    fileNum = 0
    def __init__(self, video):
        QThread.__init__(self)
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
       # self.Rekog = boto3.client('rekognition')
        self.video = video
        self.now = time.localtime()
        self.today = str(self.now.tm_year)+"."+str(self.now.tm_mon)+"."+str(self.now.tm_mday)

    def __del__(self):
        self.wait()
    
    def stop(self):
        print("END")
        self.tFlag = True

    def run(self):
        import sys, getopt
        args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
        try:
            video_src = video_src[0]
        except:
            video_src = 0
        args = dict(args)
        cascade_fn = args.get('--cascade', "data/haarcascades/haarcascade_frontalface_alt.xml")
        nested_fn  = args.get('--nested-cascade', "data/haarcascades/haarcascade_eye.xml")
    
        cascade = cv2.CascadeClassifier(cascade_fn)
        nested = cv2.CascadeClassifier(nested_fn)
            
        cap = self.video

        face_cascade = cv2.CascadeClassifier()
        face_cascade.load('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
        
        # Loop
        while(self.tFlag == False):
            if(self.cCounter == 5):
                self.cCounter = 0
                if self.counter != 0:
                    self.UploadToS3()
                break
            try:
                # Capture Frame 
                ret, img = cap.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                
                t = clock()
                rects = self.Dectection(gray, cascade)
                vis = img.copy()
                self.draw_rects(vis, rects, (0, 255, 0))
                if not nested.empty():
                    for x1, y1, x2, y2 in rects:
                        roi = gray[y1:y2, x1:x2]
                        vis_roi = vis[y1:y2, x1:x2]
                        self.fileNum += 1
                        self.counter += 1
                        cv2.imwrite('uploader/{0}.jpg'.format(self.fileNum),vis_roi)
                        print "OK"
                        #self.UploadToS3(vis_roi)
                        
                dt = clock() - t
                draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))

            except:
                pass
            self.cCounter = self.cCounter + 1
            print "cCounter: ",self.cCounter
            time.sleep(1)
        
    # Detection Function    
    def Dectection(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)                                     
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
            
        return rects
    
    # Drawing Rectangle on Detected Image
    def draw_rects(self, img, rects, color):
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    

    def UploadToS3(self):
        Num = self.fileNum - self.counter
        print("UPLOADING...")
        for i in range(Num, self.fileNum):
         #   path = str('uploader/{0}.jpg'.format(self.fileNum))
            data = open('uploader/{0}.jpg'.format(i+1),'rb')
            self.S3.put_object(ACL = 'public-read', Bucket = 'dgutest01', Key = '오늘'+'/'+str(i+1)+'.jpg', Body = data)
            
            print "file counter :", i+1
            data.close()
            #os.remove(path)
         #  if (self.fileNum == self.cLimit):
          #          self.mCounter = self.mCounter + 1
        self.counter = 0
        
        
