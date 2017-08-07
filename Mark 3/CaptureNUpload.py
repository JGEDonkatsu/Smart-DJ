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
    cCounter = 0 # while문 실행한 개수
    counter = 0 # 실제 캡처한 이미지 개수
    fileNum = 0
    def __init__(self, video, fileName):
        print("IN THREAD")
        QThread.__init__(self)        
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.video = video
        self.fileName = unicode(fileName) # 한글 노래명
        self.slash = self.fileName.rfind('/')
        self.mp3 = self.fileName.rfind('.mp3')
        self.fileName = self.fileName[self.slash+1:self.mp3]
        self.now = time.localtime()
        self.today = str(self.now.tm_year)+"."+str(self.now.tm_mon)+"."+str(self.now.tm_mday)

    def __del__(self):
        self.wait()
    
    def stop(self): #스레드 종료
        print("END")
        self.tFlag = True

    def run(self):
        # opencv 설정
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
            if(self.cCounter == 10): # while문 10번 돌리면
                self.cCounter = 0
                if self.counter != 0: # 얼굴 캡처 한번 이상 했으면 S3 업로드
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
                        zoom = cv2.resize(vis_roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC) # 이미지 세배 확대
                        cv2.imwrite('uploader/{0}.jpg'.format(self.fileNum), zoom) # 로컬PC에 저장
                        print "OK"
                        
                dt = clock() - t 
                draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000)) # 한 화면에서 한 번에 여러 사람들 캡처 가능
                
            except:
                pass
            self.cCounter = self.cCounter + 1
            print "Cam01 cCounter: ",self.cCounter
        
    # Detection Function    
    def Dectection(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(20, 20), flags=cv2.CASCADE_SCALE_IMAGE)                                     
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
        return rects
    
    # S3에 이미지 업로드
    def UploadToS3(self):
        Num = self.fileNum - self.counter
        print("UPLOADING...")
        for i in range(Num, self.fileNum):
            data = open('uploader/{0}.jpg'.format(i+1),'rb')
            self.S3.put_object(ACL = 'public-read', Bucket = 'dgutest01', Key = self.today+'/'+self.fileName+'/'+str(i+1)+'.jpg', Body = data)
            
            print "Cam01 file counter :", i+1
            data.close()
        self.counter = 0
        print "Cam01 uploading end"
        self.Deletion(Num, self.fileNum)
    
    # 로컬PC에서 업로드한 이미지 삭제
    def Deletion(self, start, end):
        for i in range(start, end):
            path = str('uploader/{0}.jpg'.format(i+1))
            os.remove(path)
        
        
