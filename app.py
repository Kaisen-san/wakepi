import numpy as np
import cv2 as cv
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('haarcascade_eye.xml')
import time

cam = cv.VideoCapture(0)

try:
    while True:
        countWhite = 0
        countBlack = 0
        mean = ()

        ret, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            for (ex,ey,ew,eh) in eyes:
                cv.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                roi_gray2 = roi_gray[ey:ey+eh, ex:ex+ew]

                retval, threshold = cv.threshold(roi_gray2, 50, 255, 0)
                
                rec_xi = int(ew * 0.25)
                rec_xf = int(ew * 0.75)
                rec_yi = int(eh * 0.25)
                rec_yf = int(eh * 0.75)

                cv.rectangle(roi_color, (rec_xi+ex, rec_yi+ey), (rec_xf+ex, rec_yf+ey), (0,0,255),2)


                mean = cv.mean(threshold[rec_xi:rec_xf, rec_yi:rec_yf])

                countWhite = 0
                countBlack = 0

                for row in range(rec_yi, rec_yf):
                    for col in range(rec_xi, rec_xf):
                        if threshold[row][col] == 0:
                            countBlack += 1
                        else:
                            countWhite += 1

                #cv.imshow('threshold', threshold)

        cv.imshow('img',img)

        if (countBlack != 0):
            print('Mean: {0:.3f}\tWhite: {1}\tBlack: {2}\t Prop: {3}'.format(mean[0], countWhite, countBlack, countWhite/countBlack))

        #cam.release()

        c = cv.waitKey(0) 

        if 'q' == chr(c & 255):
            raise KeyboardInterrupt
        elif 'g' == chr(c & 255):
            pass
        
        #cam.open(0)

except KeyboardInterrupt:
    cv.destroyAllWindows()


