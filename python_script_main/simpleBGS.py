#!/usr/bin/python
import urllib.request
import cv2
import numpy as np
import matplotlib.pyplot as plt
import imutils
import time
import os

cdPath = os.path.dirname(os.path.abspath(__file__))

url='http://192.168.8.137/capture?_cb=1603632088523'

frameSizeUrl = 'http://192.168.8.137/control?var=framesize&val=6'
firstFrame = None

#cv2.namedWindow('RoomStream')
#upperBound = 60 lowerBound=120
def tiltCam(inStr):
    tiltUrl = 'http://192.168.8.137/control?var=pwm2&val='+str(inStr)
    try:
        imgResp=urllib.request.urlopen(tiltUrl)
    except:
        print("Servo Tilt Request Failed")
    #print(imgResp.read())


def move(up,down,shape):
    global currentServoPos
    if (up<40 or down < 40)and currentServoPos>=75:
        currentServoPos-=15
        print("changed tilt")
        print("Moving up")
        print(currentServoPos)
    elif (down > (shape[0]-20) or up >(shape[0]-20)) and currentServoPos<=105:
        currentServoPos+=15
        print("Moving down")
        print("changed tilt")
        print(currentServoPos)
    tiltCam(currentServoPos)
    

#cv2.createTrackbar('Val','RoomStream',60,120,tiltCam)

top = 0
bottom = 0
currentServoPos = 90
tiltCam(currentServoPos)
lastUpdate = time.time()
lastSaveTime = 0
#print(cdPath)
lastDetectedTime = 0

dateStr = time.strftime("%a_%d_%m_%Y")

#create todays folder
try:
    os.mkdir(cdPath+'/capture/'+dateStr)
except FileExistsError:
    pass

"""
try:
    urllib.request.urlopen(frameSizeUrl)
except Exception as e:
    f = open("report.txt", "a")
    f.write(str(e))
    f.close()
"""

def main():
    global firstFrame,lastSaveTime,lastDetectedTime,lastUpdate,currentServoPos,top,bottom
    while True:
        currentTime = time.time()
        try:
            imgResp=urllib.request.urlopen(url)
        except:
            continue
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)

        # get active foreground

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #cv2.imshow('gray',gray)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)
        #cv2.imshow('gaussianBlur',gray)
        
        if firstFrame is None:
            firstFrame = gray
            
        imgDif = cv2.absdiff(firstFrame,gray)
        #cv2.imshow('diff',imgDif)
        ret,thresh1 = cv2.threshold(imgDif,10,255,cv2.THRESH_BINARY)

        #dialated = cv2.dilate(thresh1, None, iterations=2)
        #cv2.imshow('dialated',dialated)
        
        # all the opencv processing is done here
        #cv2.imshow('activeForeground',thresh1)

        cnts = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        detected = False
        
        for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < 10000:
                        continue
                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                
                (x, y, w, h) = cv2.boundingRect(c)
                #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                top = y
                bottom = y+h
                detected = True
                lastDetectedTime = currentTime
                break  
        
        #cv2.imshow('RoomStream',img)
        if currentTime-lastSaveTime>60:    
            saveLoc = cdPath+'/capture/'+dateStr+'/'+time.strftime("%a_%d_%m_%Y_%H_%M_%S")+'.jpg'
            cv2.imwrite(saveLoc,img)
            lastSaveTime = currentTime
            
        firstFrame = gray

        if detected and (currentTime-lastUpdate>3):
            move(top,bottom,img.shape)
            lastUpdate = currentTime

        if currentTime-lastDetectedTime>5*60:
            currentServoPos = 90
            tiltCam(currentServoPos)
        
        if ord('q')==cv2.waitKey(10):
            break

try:
    main()
except Exception as e:
    f = open("report.txt", "a")
    f.write(str(e))
    f.close()

exit(0)   


