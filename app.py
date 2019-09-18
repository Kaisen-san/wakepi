#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2 as cv
import RPi.GPIO as GPIO
import time
import signal
import sys

face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('haarcascade_eye.xml')

cam = cv.VideoCapture(0)

buzzer = 18
led = 4



try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(led, GPIO.OUT)

    limit = 175
    sleepCount = 0
    isAwake = True
    waitTime = 100

    while True:
        countWhite = 0
        countBlack = 0
        mean = ()
        faceMean = ()
        isToValidate = False

        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            # Check the overall light level with this
            # (handle the limit with this later or give up and go with the happy path?
            faceMean = cv.mean(roi_gray)

            for (ex, ey, ew, eh) in eyes:
                cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                roi_gray2 = roi_gray[ey:ey+eh, ex:ex+ew]
                retval, threshold = cv.threshold(roi_gray2, 50, 255, 0)

                rec_xi = int(ew * 0.25)
                rec_xf = int(ew * 0.75)
                rec_yi = int(eh * 0.25)
                rec_yf = int(eh * 0.75)

                cv.rectangle(roi_color, (rec_xi+ex, rec_yi+ey), (rec_xf+ex, rec_yf+ey), (0, 0, 255), 2)

                countWhite = 0
                countBlack = 0

                for row in range(rec_yi, rec_yf):
                    for col in range(rec_xi, rec_xf):
                        if threshold[row][col] == 0:
                            countBlack += 1
                        else:
                            countWhite += 1

                mean = cv.mean(threshold[rec_xi:rec_xf, rec_yi:rec_yf])
                
                isToValidate = True
                #cv.imshow('threshold', threshold)

        cv.imshow('img', img)

        if isToValidate:
            GPIO.output(led, GPIO.HIGH) # It was able to detect both face and eyes

#            print('Mean: {0:.3f}\tWhite: {1}\tBlack: {2}\t Prop: {3}'.format(mean[0], countWhite, countBlack, countWhite/countBlack))
            print('MProp: {0:.3f} FaceMean: {1:.3f}'.format(mean[0] * countWhite/countBlack, faceMean[0]))

            # Decide whether the driver is or not awake
            isAwake = True
            
            # Explode the readings for more precision between open/closed eyes
            currentReading = mean[0] * countWhite/countBlack
            # If closed eyes, increment the counter
            if currentReading > limit:
                sleepCount += 1
            else:
                sleepCount = 0
        else:
            GPIO.output(led, GPIO.LOW) # It was NOT able to detect either face or eyes

        # If the counter passes a certain limit, the driver is determined to have fallen asleep
        if sleepCount > 5:
            isAwake = False

        # If they are asleep, wake them up (send a burst of sound every moment they're asleep)
        if not isAwake:
            GPIO.output(buzzer, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(buzzer, GPIO.LOW)
            time.sleep(0.1)
            waitTime = 1 # Not sure if this is optimal
        else:
            waitTime = 100

        cam.release()

        c = cv.waitKey(waitTime) 

        # Pause reading with p
        if 'p' == chr(c & 255):
            c = cv.waitKey(0)

        if 'q' == chr(c & 255):
            raise KeyboardInterrupt
       
        cam.open(0)
except KeyboardInterrupt:
    print('Bye!')
except Exception as e:
    print('Error: {0}.'.format(e))
finally:
    cv.destroyAllWindows()
    GPIO.cleanup()
    sys.exit(0)
