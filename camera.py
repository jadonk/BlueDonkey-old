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
        #cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        [vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
        lefty = int((-x*vy/vx) + y)
        righty = int(((160-x)*vy/vx)+y)
        res = cv2.line(res, (159,righty), (0,lefty), (0,0,255), 2)
        cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
    
    time.sleep(0.2)

capture.release()
