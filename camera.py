#!/usr/bin/env python3
import os, sys
#if not os.geteuid() == 0:
#    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import cv2, time
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FPS, 10)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
capture.set(cv2.CAP_PROP_EXPOSURE, 0.005)

import numpy

while(capture.isOpened()):
    ret, frame = capture.read()

    if ret:
        cv2.imwrite('/run/bluedonkey/camera.jpg', frame)
        lower_yellow = numpy.array([0,160,160])
        upper_yellow = numpy.array([190,255,255])
        mask = cv2.inRange(frame, lower_yellow, upper_yellow)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
        
    time.sleep(0.2)

capture.release()
