#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2 as cv
import RPi.GPIO as GPIO
import time
import signal
import sys
import traceback
import requests

def update(data):
    for item in data:
        url = 'https://industrial.api.ubidots.com/api/v1.6/devices/uc/' + item + '/values/'
        headers = { 'X-Auth-Token': 'BBFF-aUhoRzohc6kSdcE5ACFBjOHkNnEtEH', 'Content-Type': 'application/json' }

        json = { 'value': data[item] }

        response = requests.post(url=url, headers=headers, json=json)

def tryToUpdate(updateCount, data):
    if (updateCount % 30 == 0):
        update(data)

        return 0

    return updateCount

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('haarcascade_eye.xml')

cam = cv.VideoCapture(0)

buzzer = 18
led = 4

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(led, GPIO.OUT)

    sleepCount = 0
    isAwake = True
    waitTime = 100
    eyePropAvg = 0
    eyePropCount = 0
    updateCount = 0
    data = {}

    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(buzzer, GPIO.LOW)
    time.sleep(0.1)

    while True:
        updateCount += 1
        countWhite = 0
        countBlack = 0
        mean = ()
        faceThreshold = []
        eyeThreshold = []
        isToValidate = False

        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            data['facedetection'] = 0
            GPIO.output(led, GPIO.LOW)
            continue
        else:
            data['facedetection'] = 1
            GPIO.output(led, GPIO.HIGH)

        (x, y, w, h) = faces[0]
        cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        if len(eyes) == 0:
            continue

        (ex, ey, ew, eh) = eyes[0]
        cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        roi_gray2 = roi_gray[ey:ey+eh, ex:ex+ew]

        rec_xi = int(ew * 0.25)
        rec_xf = int(ew * 0.75)
        rec_yi = int(eh * 0.25)
        rec_yf = int(eh * 0.75)

        cv.rectangle(roi_color, (rec_xi+ex, rec_yi+ey), (rec_xf+ex, rec_yf+ey), (0, 0, 255), 2)

        imgMean = cv.mean(roi_gray)

        countWhite = 0
        countBlack = 0

        for row in range(0, h):
            for col in range(0, w):
                if roi_gray[row][col] < imgMean[0] * 0.8:
                    countBlack += 1
                else:
                    countWhite += 1

        countWhite = max(countWhite, 1)
        countBlack = max(countBlack, 1)

        faceProp = imgMean[0] * min(countWhite / countBlack, countBlack / countWhite)

        faceRetval, faceThreshold = cv.threshold(roi_gray, faceProp, 255, 0)
        eyeRetval, eyeThreshold = cv.threshold(roi_gray2, faceProp, 255, 0)

        data['luminosity'] = imgMean[0]

        countWhite = 0
        countBlack = 0

        for row in range(rec_yi, rec_yf):
            for col in range(rec_xi, rec_xf):
                if eyeThreshold[row][col] == 0:
                    countBlack += 1
                else:
                    countWhite += 1

        countWhite = max(countWhite, 1)
        countBlack = max(countBlack, 1)

        mean = cv.mean(eyeThreshold[rec_yi:rec_yf, rec_xi:rec_xf])
        currentEyeProp = mean[0] * countWhite / countBlack

        data['white'] = countWhite
        data['black'] = countBlack

        if eyePropCount < 10 or (eyePropAvg * 0.7 <= currentEyeProp <= eyePropAvg * 1.3):
            eyePropAvg = (eyePropAvg * eyePropCount + currentEyeProp) / (eyePropCount + 1)
            eyePropCount += 1

        if eyePropCount < 10:
            GPIO.output(led, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(led, GPIO.LOW)
            time.sleep(0.3)
        else:
            isToValidate = True

        cv.imshow('img', img)

        if len(eyeThreshold) > 0:
            cv.imshow('eye', eyeThreshold)
            cv.imshow('face', faceThreshold)

        if isToValidate:
            # Decide whether the driver is or not awake
            isAwake = True

            print('Current Eye Proportion: {0:.3f} Eye Proportion Average: {1:.3f}'.format(currentEyeProp, eyePropAvg))

            # If closed eyes, increment the counter
            if currentEyeProp > eyePropAvg * 1.15:
                sleepCount += 1
            else:
                sleepCount = 0

            data['sleep'] = sleepCount

        # If the counter passes a certain limit, the driver is determined to have fallen asleep
        if sleepCount > 3:
            isAwake = False

        # If they are asleep, wake them up (send a burst of sound every moment they're asleep)
        if not isAwake:
            data['driver'] = 0

            GPIO.output(buzzer, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(buzzer, GPIO.LOW)
            time.sleep(0.1)
            waitTime = 1 # Not sure if this is optimal
        else:
            data['driver'] = 1

            waitTime = 100

        updateCount = tryToUpdate(updateCount, data)
        cam.release()

        c = cv.waitKey(waitTime) 

        # Pause reading with p
        if 'p' == chr(c & 255):
            c = cv.waitKey(0)

        if 'q' == chr(c & 255):
            raise KeyboardInterrupt
            
        if 'z' == chr(c & 255):
            print('Olho aberto')

        if 'x' == chr(c & 255):
            print('Olho fechado')

        cam.open(0)
except KeyboardInterrupt:
    print('Bye!')
except Exception as e:
    print(traceback.format_exc())
finally:
    cv.destroyAllWindows()
    GPIO.cleanup()
    sys.exit(0)
