
#!/usr/bin/python
import urllib.request
import cv2
import numpy as np
import matplotlib.pyplot as plt
import imutils
import time
import os
import tflite_runtime.interpreter as tflite
import csv

cdPath = os.path.dirname(os.path.abspath(__file__))

url='http://192.168.43.176/capture?_cb=1603632088523'

frameSizeUrl = 'http://192.168.43.176/control?var=framesize&val=6'
firstFrame = None

modelPath = '/home/pi/Desktop/myActivityRecognition/activityRocognizer/model.tflite'
interpreter = tflite.Interpreter(
  model_path=modelPath, num_threads=None)
interpreter.allocate_tensors()

classes = ['eating', 'none', 'praying', 'sleeping', 'studying']


#cv2.namedWindow('RoomStream')
#upperBound = 60 lowerBound=120
def tiltCam(inStr):
    tiltUrl = 'http://192.168.43.176/control?var=pwm2&val='+str(inStr)
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
actions = [0,0,0,0,0]
dateStr = time.strftime("%a_%d_%m_%Y")

def recordCSV(upFile,time_str,activityList):
    fileStr = upFile + "/status.csv"
    with open(fileStr, 'a+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        writer.writerow([time_str]+activityList)
 

def makeFolder():
    global dateStr
    dateStr = time.strftime("%a_%d_%m_%Y")
    try:
        os.mkdir(cdPath+'/capture/'+dateStr)
        recordCSV(cdPath+'/capture/'+dateStr,"Time",classes)
    except FileExistsError:
        pass
    
makeFolder()

"""
try:
    urllib.request.urlopen(frameSizeUrl)
except Exception as e:
    f = open("report.txt", "a")
    f.write(str(e))
    f.close()
"""

def predict_action(img):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()


    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
    
    imgArr = []
    imgArr.append(img)
    imgArr = np.array(imgArr, dtype='float32')
    interpreter.set_tensor(input_details[0]['index'], imgArr)

    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)   
    return np.argmax(results)

   

def main():
    global firstFrame,lastSaveTime,lastDetectedTime,lastUpdate,currentServoPos,top,bottom,actions
    while True:
        currentTime = time.time()
        try:
            imgResp=urllib.request.urlopen(url)
        except:
            print("Failed to Connect")
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

        action_index = predict_action(img)
        actions[action_index]+=1
        #cv2.imshow('RoomStream',img)
        if currentTime-lastSaveTime>60:
            timeStr = time.strftime("%a_%d_%m_%Y_%H_%M_%S")
            saveLoc = cdPath+'/capture/'+dateStr+'/'+timeStr+'.jpg'
            cv2.imwrite(saveLoc,img)
            lastSaveTime = currentTime

            #print(actions)
            maxNum = np.argmax(actions)
            d_action = [ 1  if i==actions[maxNum] else 0 for i in actions]
            recordCSV(cdPath+'/capture/'+dateStr,timeStr,d_action)
            actions = [0,0,0,0,0]
            
        firstFrame = gray
        #print(currentTime-lastUpdate)
        if detected and (currentTime-lastUpdate>10):
            move(top,bottom,img.shape)
            lastUpdate = currentTime

        if currentTime-lastDetectedTime>5*60:
            currentServoPos = 90
            tiltCam(currentServoPos)

        if int(time.strftime("%H")) == 0:
            makeFolder()
        
        if ord('q')==cv2.waitKey(10):
            break


        
while 1:
    try:
        main()
    except Exception as e:
        f = open("report.txt", "a")
        error_str = str(e) + time.strftime("%a_%d_%m_%Y_%H_%M_%S") + "\n"
        f.write(str(e))
        f.close()

   


