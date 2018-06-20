#!/usr/bin/env python3
import os, sys
#if not os.geteuid() == 0:
#    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import cv2, time
#capture = cv2.VideoCapture(0)
#capture.set(cv2.CAP_PROP_FPS, 10)
#capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
#capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
#capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
#capture.set(cv2.CAP_PROP_EXPOSURE, 0.003)

import numpy

def capture_and_process_frame():
    #ret, frame = capture.read()
    frame = cv2.imread('camera01.jpg')
    ret = True

    if ret:
        cv2.imwrite('/run/bluedonkey/camera.jpg', frame)
        lower_yellow = numpy.array([0,160,160])
        upper_yellow = numpy.array([255,255,255])
        mask = cv2.inRange(frame, lower_yellow, upper_yellow)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        #cv2.rectangle(res, (0,0), (159,119), (0,0,0), 2)
        #cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        if True:
            blur = cv2.GaussianBlur(gray, (7, 7), 0)
            #edges = cv2.Canny(blur, 50, 150)
            dilation = cv2.dilate(blur, cv2.getStructuringElement(cv2.MORPH_DILATE, (5, 5)))
            erosion = cv2.erode(dilation, cv2.getStructuringElement(cv2.MORPH_ERODE, (3, 3)))
            #merge = gray + erosion
            lines = cv2.HoughLinesP(erosion, 2, numpy.pi/180, 9, numpy.array([]), minLineLength=30, maxLineGap=30)
            line_img = numpy.zeros((res.shape[0], res.shape[1], 3), dtype=numpy.uint8)
            for line in lines:
                for x1,y1,x2,y2 in line:
                    angle = numpy.arctan2(y2 - y1, x2 - x1) * 180. / numpy.pi
                    if ( (abs(angle) > 20.) and (abs(angle) < 90.)):
                        cv2.line(line_img, (x1, y1), (x2, y2), (0,0,255), 1)
            res = cv2.addWeighted(res, 0.8, line_img, 1, 0)
            gray_lines = cv2.cvtColor(line_img, cv2.COLOR_BGR2GRAY)
            pixelpoints = cv2.findNonZero(gray_lines)
        else:
            pixelpoints = cv2.findNonZero(gray)
        [vx,vy,x,y] = cv2.fitLine(pixelpoints, 4, 0, 0.01, 0.01)
        lefty = int((-x*vy/vx) + y)
        righty = int(((160-x)*vy/vx)+y)
        res = cv2.line(res, (159,righty), (0,lefty), (0,255,0), 2)
        cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
    
    time.sleep(0.2)

#while(capture.isOpened()):
#   capture_and_process_frame()
capture_and_process_frame()
#capture.release()
