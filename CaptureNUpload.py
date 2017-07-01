'''
Created on 2017. 5. 12.
@author: DJ, SJ
'''

import cv2
import boto3
import threading
from botocore.client import Config


class CapNUp(threading.Thread):
    def __init__(self, video):
        threading.Thread.__init__(self)
        self.fileNum = 0;
        self.S3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
        self.video = video

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
        while(True):
            # Capture Frame 
            ret, img = cap.read()
            rects = self.Dectection(img, cascade)
            vis = img.copy()
            if not nested.empty():
                for x1, y1, x2, y2 in rects:
                    roi = img[y1:y2, x1:x2]
                    vis_roi = vis[y1:y2, x1:x2]
                    subrects = self.Dectection(roi.copy(), nested)
                    self.UploadToS3(vis_roi, subrects)    
    # Detection Function
        
    def Dectection(self, img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)                                     
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
            
        return rects
            
    # Drawing Rectangle on Detected Image
    def UploadToS3(self, img, rects):
        self.fileNum = self.fileNum + 1
        cv2.imwrite('Img/{0}.jpg'.format(self.fileNum),img)
        data = open('Img/{0}.jpg'.format(self.fileNum),'rb')
        self.S3.put_object(ACL = 'public-read', Bucket = 'rainbow01', Key = str(self.fileNum)+'.jpg', Body = data)
            
