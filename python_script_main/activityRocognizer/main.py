import time
import numpy as np
import tflite_runtime.interpreter as tflite
import urllib.request
import cv2
url='http://192.168.8.137/capture?_cb=1603632088523'

modelPath = '/home/pi/Desktop/myActivityRecognition/activityRocognizer/model.tflite'
interpreter = tflite.Interpreter(
  model_path=modelPath, num_threads=None)
interpreter.allocate_tensors()

classes = ['eating', 'none', 'praying', 'sleeping', 'studying']


while 1:
    
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
    print(classes[np.argmax(results)])
    

    
cv2.DestroyAllWindows()
"""

import csv
with open('innovators.csv', 'a+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["SN", "Name", "Contribution"])
    writer.writerow([1, "Aaftab Naim", "Revolution"])
    writer.writerow([2, "Tim Berners-Lee", "World Wide Web"])
    writer.writerow([3, "Guido van Rossum", "Python Programming"])

    """
