# -*- coding:utf-8 -*-
import numpy as np
import cv2
import dlib

def cv2facedetection():    
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    
    img = cv2.imread('p17.jpg')
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
       
    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def dlibfacedetection():
    face_detector=dlib.get_frontal_face_detector()  
    landmark_predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  

    bgrImg = cv2.imread('p17.jpg')
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)  
    facesrect = face_detector(rgbImg, 1)
    i=0
    for rect in facesrect:  
        i+=1
        left,right,top,bottom = rect.left(),rect.right(),rect.top(),rect.bottom()
        print 'face %d：(%d,%d),(%d,%d)'%(i,left,top,right,bottom)
        cv2.rectangle(bgrImg,(left,top),(right,bottom),(255,255,0),2)
        cv2.putText(bgrImg,str(i),(left,bottom),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
    cv2.imshow('img',bgrImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def dlibscore():
    detector = dlib.get_frontal_face_detector()
    img = cv2.imread('p6.jpg')
    dets, scores, idx = detector.run(img, 1)
    for i, d in enumerate(dets):
        print("Detection {}, score: {}, face_type:{}".format(d, scores[i], idx[i]))    
    
if __name__ == "__main__":
    #cv2facedetection()
    #dlibfacedetection()
    dlibscore()