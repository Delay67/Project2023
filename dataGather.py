import pafy
import cv2
import time
import datetime
import os
import time
import csv
import json
import requests
import numpy as np
from datetime import datetime

y1Light = 583
y2Light = 750
x1Light = 1424    
x2Light = 1470

y1CarOne = 433
y2CarOne = 838
x1CarOne = 484    
x2CarOne = 1123

y1CarTwo = 433
y2CarTwo = 838
x1CarTwo = 484    
x2CarTwo = 1123

lower_1 = np.array([200, 200, 200], dtype = "uint8")
upper_1 = np.array([250, 255, 255], dtype = "uint8")
timerGreen = 0
timerRed = 0
oldTime = 0

apiKey = "7329ef2606d1d893eaab7ebafa30d634"
lat = "51.441111"
lon = "5.619444"
weatherDataURL = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, apiKey)
url = "https://www.youtube.com/watch?v=HrUMpcgLG78"
video = pafy.new(url)
best = video.getbest(preftype="mp4")
cap = cv2.VideoCapture(best.url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
timeonly = time.strftime("%H%M%S")
dateonly = time.strftime("%Y%m%d")
timestr = dateonly + "-" + timeonly
while(True):
    ret, frame = cap.read()
    #testimage = cv2.imread("Frames/20210408-033653.jpg")
    crop_img = frame[y1Light:y2Light, x1Light:x2Light]
    mask = cv2.inRange(crop_img, lower_1, upper_1)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
 
    for cnt in contours:
        cnt_area = cv2.contourArea(cnt)
        
        cnt_area = (cnt_area / (11 * 11)) * 100
        if (time.time() - oldTime) > 60:
            response = requests.get(weatherDataURL)
            print(response.text)
            data = json.loads(response.text)
            #currentTemp = data["current"]["temp"]
            currentTemp = "temp"
            #currentCondition = data["current"]["weather"][0]["description"]
            currentCondition = "temp"
            oldTime = time.time()

        if cnt_area >= 10:
            if timerGreen == 0:
                timerRed += 1
            else:
                tempTimer = timerGreen
                timerGreen = 0
                timerRed += 1
                with open("CSVDATA/LiveStream-1-Cam-2-New.csv", "a") as f:
                    print("wrote1")
                    readFile = csv.writer(f)
                    readFile.writerow([dateonly,timeonly,tempTimer,currentTemp,currentCondition,"Green"])
                    f.close()
        else:
            if timerRed == 0:
                timerGreen += 1
            else:
                tempTimer = timerRed
                timerRed = 0
                timerGreen += 1                
                with open("CSVDATA/LiveStream-1-Cam-2-New.csv", "a") as f:
                    print("wrote2")
                    readFile = csv.writer(f)
                    readFile.writerow([dateonly,timeonly,tempTimer,currentTemp,currentCondition,"Red"])
                    f.close()
    timeonly = datetime.now().strftime("%H%M%S")
    dateonly = time.strftime("%Y%m%d")
    timestr = dateonly + "-" + timeonly
    cv2.imwrite("Frames/LiveStream-1-Cam-2-New/%s.jpg" % timestr, frame)   
