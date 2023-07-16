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



#Light:

y1Light = 322
y2Light = 362
x1Light = 871    
x2Light = 914

#Car:

y1Car = 460
y2Car = 503
x1Car = 1480    
x2Car = 1535


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



if os.path.exists("CSVDATA/LiveStream-2-Cam-2-New-NL.csv") != True:
    with open("CSVDATA/LiveStream-2-Cam-2-New-NL.csv", 'w', newline='') as f:
        readFile = csv.writer(f)
        readFile.writerow(["Date","Time","Timer","Temperature","Condition","Light","Car","CarDuration"])
        f.close()

ret,frame = cap.read()
cv2.imwrite("testframe.jpg", frame)
base = cv2.imread('testframe.jpg')
crop_base = base[y1Car:y2Car, x1Car:x2Car]
# out frame index
currentFrame = 0 
while True:
    try:
        ret,frame = cap.read()
        cpos = cap.get(cv2.CAP_PROP_POS_MSEC)
        if (cpos%1000) == 0:
            dateonly = time.strftime("%Y-%m-%d")
            timeonly = datetime.now().strftime('%H-%M-%S.%f')[:-3]
            if ret: 
                # Light Detection
                crop_img = frame[y1Light:y2Light, x1Light:x2Light]
                crop_img_car = frame[y1Car:y2Car, x1Car:x2Car]
                hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
                

                lightOn = redCheck(hsv)

                #Car Detection
                errorL2 = cv2.norm(crop_base, crop_img_car, cv2.NORM_L2)
                similarity = 1 - errorL2 / ((y2Car-y1Car) * (x2Car - x1Car))
                if similarity < 0.50:
                    carCounter = carCounter + 1
                    print("CAR WAITING...")
                    cv2.imwrite("testcarcrop.jpg", crop_img_car)
                    cv2.imwrite("testcarcropbase.jpg", crop_base)
                #print("frame: ", cpos, "sim: ", similarity)



                print("FRAME: ", cpos, " GREENTIMER: ", timerGreen, " REDTIMER: ", timerRed)
                #If red is on, enter if statement
                if lightOn == True:
                    if timerGreen == 0:
                        timerRed = cpos - oldCpos
                        #print("red: ", timerRed)
                    else:
                        response = requests.get(weatherDataURL)
                        data = json.loads(response.text)
                        currentTemp = data["current"]["temp"]
                        currentCondition = data["current"]["weather"][0]["description"]
                        tempTimer = timerGreen // 1000
                        timerRed = 1000
                        oldCpos = cpos
                        timerGreen = 0
                        
                        with open("CSVDATA/LiveStream-2-Cam-2-New-NL.csv", 'a+', newline="") as f:
                            if carCounter > 2:
                                carThere = True
                            readFile = csv.writer(f)
                            readFile.writerow([dateonly,timeonly,tempTimer,currentTemp,currentCondition,"Green",carThere,carCounter])
                            carCounter = 0
                            carThere = False
                            f.close()
                            name = "Frames/LiveStream-2-Cam-2-New-NLL/" + "frame_" + str(cpos) + "_REDON.jpg"
                            cv2.imwrite(name, frame)
                        lightOn = False
                else:
                    if timerRed == 0:
                        timerGreen = cpos - oldCpos
                        #print(timerGreen)
                    else:
                        response = requests.get(weatherDataURL)
                        data = json.loads(response.text)
                        currentTemp = data["current"]["temp"]
                        currentCondition = data["current"]["weather"][0]["description"]
                        tempTimer = timerRed // 1000
                        timerGreen = 1000
                        oldCpos = cpos
                        timerRed = 0          
                        with open("CSVDATA/LiveStream-2-Cam-2-New-NL.csv", 'a+', newline="") as f:
                            if carCounter >= 2:
                                carThere = True
                            readFile = csv.writer(f)
                            readFile.writerow([dateonly,timeonly,tempTimer,currentTemp,currentCondition,"Red",carThere,carCounter])
                            carCounter = 0
                            carThere = False
                            f.close()
                            name = "Frames/LiveStream-2-Cam-2-New-NL/" + "frame_" + str(cpos) + "_REDOFF.jpg"
                            cv2.imwrite(name, frame)

            else:
                break
        if ((cpos%1000000) == 0) or atempt == True:
            if similarity > 0.85:
                print("NEW BASE")
                cv2.imwrite("testframe.jpg", frame)
                crop_base = frame[y1Car:y2Car, x1Car:x2Car]
                atempt = False
            else:
                atempt = True
    except Exception as e:
        print ("Exception raised @frame : " + str(currentFrame))
        print(e)
    finally:
        currentFrame +=1


# When everything done, release the video capture and video write objects
cap.release()
cv2.destroyAllWindows()