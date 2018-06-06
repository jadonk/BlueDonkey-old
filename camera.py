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
ret, img = capture.read()

while True:
    cv2.imwrite('camera.jpg', img)
    time.sleep(0.1)

capture.release()
