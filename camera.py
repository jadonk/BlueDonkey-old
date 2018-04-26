#!/usr/bin/env python3

# http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html

import cv2 as cv
import time

cv.namedWindow("camera", 1)

capture = cv.VideoCapture(0)
capture.set(3, 160)
capture.set(4, 120)

while True:
    ret, img = capture.read()
    cv.imshow("camera", img)
    #gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #cv.imshow("camera", gray)
    if cv.waitKey(10) == 27:
        break

capture.release()
cv.destroyAllWindows()
