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

class CapNUp2(QThread):
    tFlag = False
    cCounter = 0
    mCounter = 1
    counter = 0 #upload
    fileNum = 0

    def __init__(self, video, fileName):
        print("IN THREAD")
        QThread.__init__(self)        
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.video = video
        self.fileName = unicode(fileName)
        self.slash = self.fileName.rfind('/')
        self.mp3 = self.fileName.rfind('.wmv')
        self.fileName = self.fileName[self.slash+1:self.mp3]
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
            if(self.cCounter == 15):
                self.cCounter = 0
                if self.counter != 0:
                    self.UploadToS3()
                print "cCounter END"
                break
            
            try:
                # Capture Frame 
                ret, img = cap.read()
                
                t = clock()
                rects = self.Dectection(img, cascade)
                
                vis = img.copy()
                if not nested.empty():
                    for x1, y1, x2, y2 in rects:
                        roi = img[y1:y2, x1:x2]
                        vis_roi = vis[y1:y2, x1:x2]
                        self.fileNum += 1
                        self.counter += 1
                        zoom = cv2.resize(vis_roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC) #Image Zoom
                        cv2.imwrite('uploader2/{0}.jpg'.format(self.fileNum), zoom)
                        #print "OK"
                        
                dt = clock() - t
                draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
                
            except:
                pass
            self.cCounter = self.cCounter + 1
            #print "Cam02 cCounter: ",self.cCounter
        
    # Detection Function    
    def Dectection(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)                                     
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
        return rects

    def UploadToS3(self):
        Num = self.fileNum - self.counter
        print("UPLOADING...")
        for i in range(Num, self.fileNum):
            data = open('uploader2/{0}.jpg'.format(i+1),'rb')
            self.S3.put_object(ACL = 'public-read', Bucket = 'dgutest02', Key = self.today+'/'+self.fileName+'/'+str(i+1)+'.jpg', Body = data)
            
            print "Cam02 uploading file :", i+1
            data.close()

        print "Cam01 uploading end"
        self.Deletion(Num, self.fileNum)
        
        
    def Deletion(self, start, end):
        for i in range(start, end):
            path = str('uploader2/{0}.jpg'.format(i+1))
            os.remove(path)
        