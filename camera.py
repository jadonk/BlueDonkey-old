#!/usr/bin/env python3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import cv2, time
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FPS, 10)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

import numpy

while(capture.isOpened()):
    ret, frame = capture.read()

    if ret:
        cv2.imwrite('camera.jpg', frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_yellow = numpy.array([0,180,180])
        upper_yellow = numpy.array([50,245,255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imwrite('filtered.jpg', res)
        
    time.sleep(0.5)

capture.release()
