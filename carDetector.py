from threading import Thread
import cv2, time
from datetime import datetime
import math
import csv
import pafy
import json
import os.path
import requests
import numpy as np
lower_1 = np.array([0, 100, 100], dtype = "uint8")
upper_1 = np.array([20, 255, 255], dtype = "uint8")
lower_2 = np.array([170, 100, 100], dtype = "uint8")
upper_2 = np.array([180, 255, 255], dtype = "uint8")
timerGreen = 0
carCounter = 0 
timerRed = 0
oldCpos = 0
lightOn = False
atempt = False
carThere = False
apiKey = "d24c55e6bf88feb04df32fdaf0c84f5c"
lat = "51.441111"
lon = "5.619444"
weatherDataURL = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, apiKey)
url = "https://www.youtube.com/watch?v=HrUMpcgLG78"

video = pafy.new(url)
best = video.getbest(preftype="mp4")
cap = cv2.VideoCapture(best.url)
cv2.CAP_PROP_FPS = 10
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

cascade_src = 'cars3.xml'
car_cascade = cv2.CascadeClassifier(cascade_src)

#Light:

y1Light = 520
y2Light = 553
x1Light = 1318    
x2Light = 1358

#Car:

y1Car = 974
y2Car = 1080
x1Car = 1604    
x2Car = 1920

min_contour_width = 40  
min_contour_height = 40  
offset = 10  
line_height = 550  
matches = []
cars = 0
 
 
def get_centrolid(x, y, w, h):
   x1 = int(w / 2)
   y1 = int(h / 2)
 
   cx = x + x1
   cy = y + y1
   return cx, cy

def redCheck(img_hsv):
    # lower mask (0-10)
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    # upper mask (170-180)
    lower_red = np.array([170,50,50])
    upper_red = np.array([180,255,255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    # join my masks
    mask = mask0+mask1

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    if len(contours):
        return True
    else:
        return False



if os.path.exists("CSVDATA/LiveStream-2-Cam-1-New-NL.csv") != True:
    with open("CSVDATA/LiveStream-2-Cam-1-New-NL.csv", 'w', newline='') as f:
        readFile = csv.writer(f)
        readFile.writerow(["Date","Time","Timer","Temperature","Condition","Light","Car","CarDuration"])
        f.close()
currentFrame = 0 
if cap.isOpened():
   ret, frame1 = cap.read()
else:
   ret = False
ret, frame1 = cap.read()
ret, frame2 = cap.read()
 
 
while ret:
   d = cv2.absdiff(frame1, frame2)
   grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)
 
   blur = cv2.GaussianBlur(grey, (5, 5), 0)
 
   ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
   dilated = cv2.dilate(th, np.ones((3, 3)))
   kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
 
  
   closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
   contours, h = cv2.findContours(
       closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
   for(i, c) in enumerate(contours):
       (x, y, w, h) = cv2.boundingRect(c)
       contour_valid = (w >= min_contour_width) and (
           h >= min_contour_height)
 
       if not contour_valid:
           continue
       cv2.rectangle(frame1, (x-10, y-10), (x+w+10, y+h+10), (255, 0, 0), 2)
 
       cv2.line(frame1, (0, line_height), (1200, line_height), (0, 255, 0), 2)
       centrolid = get_centrolid(x, y, w, h)
       matches.append(centrolid)
       cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
       cx, cy = get_centrolid(x, y, w, h)
       for (x, y) in matches:
           if y < (line_height+offset) and y > (line_height-offset):
               cars = cars+1
               matches.remove((x, y))
               # print(cars)
 
   cv2.putText(frame1, "Total Cars Detected: " + str(cars), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1,
               (0, 170, 0), 2)
 
 
 
   cv2.imshow("Vehicle Detection", frame1)
   #cv2.imshow("Difference" , th)
   if cv2.waitKey(1) == 27:
       break
   frame1 = frame2
   ret, frame2 = cap.read()
 
cv2.destroyAllWindows()
cap.release()


# When everything done, release the video capture and video write objects
cap.release()
cv2.destroyAllWindows()