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
        upper_yellow = numpy.array([220,255,255])
        mask = cv2.inRange(frame, lower_yellow, upper_yellow)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.rectangle(res, (0,0), (159,119), (0,0,0), 2)
        #cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        kernel = numpy.ones((3,3), numpy.uint8)
        #erosion = cv2.erode(gray, kernel, iterations = 1)
        dilation = cv2.dilate(gray, kernel, iterations = 1)
        ret, thresh = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)
        #cv2.imwrite('/run/bluedonkey/filtered.jpg', thresh)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #cnt = contours[1]
        cv2.drawContours(res, contours, -1, (255,0,0), 3)
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True;
        params.minArea = 10;
        params.maxArea = 1000000;
        params.filterByColor = True;
        params.blobColor = 255;
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(thresh)
        res = cv2.drawKeypoints(res, keypoints, numpy.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #[vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
        #lefty = int((-x*vy/vx) + y)
        #righty = int(((160-x)*vy/vx)+y)
        #res = cv2.line(res, (159,righty), (0,lefty), (0,255,0), 2)
        #edges = cv2.Canny(thresh, 5, 15, apertureSize = 3)
        #res = numpy.bitwise_or(res, edges[:,:,numpy.newaxis])
        #lines = cv2.HoughLines(edges, 1, numpy.pi/180, 100)
        #for rho,theta in lines[0]:
        #    a = np.cos(theta)
        #    b = np.sin(theta)
        #    x0 = a*rho
        #    y0 = b*rho
        #    x1 = int(x0 + 160*(-b))
        #    y1 = int(y0 + 120*(a))
        #    x2 = int(x0 - 160*(-b))
        #    y2 = int(y0 - 120*(a))
        #    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
        cv2.imwrite('/run/bluedonkey/filtered.jpg', res)
    
    time.sleep(0.2)

#while(capture.isOpened()):
#   capture_and_process_frame()
capture_and_process_frame()
#capture.release()
